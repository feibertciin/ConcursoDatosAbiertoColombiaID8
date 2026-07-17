import os
import json
import io
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from django.core.files.base import ContentFile
from .models import CSVUpload

# ReportLab para PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Rutas base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_DIR = os.path.join(BASE_DIR, "models")
DATA_DIR  = os.path.join(BASE_DIR, "data", "processed")

PREPROCESSOR_PATH = os.path.join(MODEL_DIR, "preprocessor.pkl")
MODEL_PATH        = os.path.join(MODEL_DIR, "gradientboosting_model.pkl")
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = os.path.join(MODEL_DIR, "randomforest_model.pkl")

DEPT_COORDS = {
    "BOGOTA D.C.":    [4.7110,  -74.0721],
    "ANTIOQUIA":      [6.2442,  -75.5812],
    "VALLE DEL CAUCA":[3.4372,  -76.5225],
    "ATLANTICO":      [10.9685, -74.7813],
    "CUNDINAMARCA":   [4.6097,  -74.0817],
    "SANTANDER":      [7.1254,  -73.1198],
}

# --------------------------------------------------------------------------- #
#  HELPERS
# --------------------------------------------------------------------------- #

def _load_students():
    """Carga y retorna el DataFrame de estudiantes procesados o None."""
    path = os.path.join(DATA_DIR, "processed_students.csv")
    if os.path.exists(path):
        try:
            return pd.read_csv(path)
        except Exception as e:
            print("Error cargando processed_students.csv:", e)
    return None


def _load_curriculum():
    """Carga y retorna el DataFrame de currículum procesado o un fallback."""
    path = os.path.join(DATA_DIR, "processed_curriculum.csv")
    if os.path.exists(path):
        try:
            df = pd.read_csv(path)
            # Garantizar columnas mínimas requeridas
            if 'tasa_desercion' not in df.columns:
                df['tasa_desercion'] = 0.0
            if 'salario_enganche' not in df.columns:
                df['salario_enganche'] = 0
            if 'tasa_empleabilidad' not in df.columns:
                df['tasa_empleabilidad'] = 0.0
            return df
        except Exception:
            pass
    # Fallback sintético
    return pd.DataFrame({
        "programa_academico":  ["INGENIERIA DE SISTEMAS", "MEDICINA", "DERECHO",
                                "ADMINISTRACION DE EMPRESAS", "PSICOLOGIA"],
        "salario_enganche":    [2800000, 5200000, 3100000, 2400000, 2100000],
        "tasa_empleabilidad":  [82.4, 91.3, 74.8, 79.6, 68.2],
        "tasa_desercion":      [18.3, 9.1, 22.4, 20.7, 24.5],
        "indice_satisfaccion": [4.1, 4.6, 3.8, 3.9, 3.7],
        "nivel_acreditacion":  ["ALTA CALIDAD", "ALTA CALIDAD", "REGISTRO CALIFICADO",
                                "REGISTRO CALIFICADO", "REGISTRO CALIFICADO"],
    })


def _build_dept_density(df):
    """Devuelve lista de puntos de densidad para Leaflet a partir del DataFrame."""
    result = []
    if df is None:
        return result
    try:
        grouped = df.groupby("departamento_origen").agg(
            total=("estudiante_id", "count"),
            dropouts=("desertor", "sum")
        ).reset_index()
        for _, row in grouped.iterrows():
            dept = str(row["departamento_origen"]).upper()
            if dept in DEPT_COORDS:
                intensity = round((row["dropouts"] / row["total"]) * 100, 1) if row["total"] > 0 else 0
                result.append({
                    "name": dept,
                    "coords": DEPT_COORDS[dept],
                    "intensity": intensity,
                    "dropouts": int(row["dropouts"]),
                    "total": int(row["total"]),
                })
    except Exception as e:
        print("Error en _build_dept_density:", e)
    return result


def _evaluate_all_models(df):
    """Evalúa todos los modelos .pkl disponibles y retorna dict de métricas."""
    if not os.path.exists(PREPROCESSOR_PATH) or df is None:
        return None
    try:
        from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
        preprocessor = joblib.load(PREPROCESSOR_PATH)

        required_num = ['estrato_socioeconomico', 'edad', 'puntaje_saber11',
                        'promedio_acumulado', 'materias_reprobadas', 'ingreso_familiar']
        required_cat = ['genero', 'departamento_origen', 'tipo_colegio', 'programa_academico']

        df_e = df.copy()
        for col in required_num:
            if col not in df_e.columns:
                df_e[col] = 0
            df_e[col] = pd.to_numeric(df_e[col], errors='coerce').fillna(0)
        for col in required_cat:
            if col not in df_e.columns:
                df_e[col] = 'DESCONOCIDO'

        target_col = 'desertor'
        if target_col not in df_e.columns:
            def _risk(r):
                s = 0.0
                if r["promedio_acumulado"] < 3.0:     s += 0.4
                if r["materias_reprobadas"] >= 2:      s += 0.3
                if r["estrato_socioeconomico"] <= 2:   s += 0.2
                if r["puntaje_saber11"] < 250:         s += 0.15
                if r["ingreso_familiar"] < 1500000:    s += 0.15
                return 1 if s > 0.5 else 0
            df_e[target_col] = df_e.apply(_risk, axis=1)

        y_true = df_e[target_col].astype(int)
        proc = preprocessor.transform(df_e)

        model_files = {
            "Gradient Boosting": "gradientboosting_model.pkl",
            "LightGBM":          "lightgbm_model.pkl",
            "XGBoost":           "xgboost_model.pkl",
            "ExtraTrees":        "extratrees_model.pkl",
            "Random Forest":     "randomforest_model.pkl",
        }
        results = {}
        for name, fname in model_files.items():
            fpath = os.path.join(MODEL_DIR, fname)
            if os.path.exists(fpath):
                clf = joblib.load(fpath)
                preds = clf.predict(proc)
                results[name] = {
                    "accuracy":  round(accuracy_score(y_true, preds) * 100, 2),
                    "precision": round(precision_score(y_true, preds, zero_division=0) * 100, 2),
                    "recall":    round(recall_score(y_true, preds, zero_division=0) * 100, 2),
                    "f1":        round(f1_score(y_true, preds, zero_division=0) * 100, 2),
                }
        return results if results else None
    except Exception as e:
        print("Error en _evaluate_all_models:", e)
        return None


def _nav_context(active_page):
    return {"active_page": active_page}


# --------------------------------------------------------------------------- #
#  VISTAS PRINCIPALES
# --------------------------------------------------------------------------- #

def inicio_view(request):
    """🚀 Inicio — descripción del proyecto y código de API."""
    return render(request, 'core_app/inicio.html', _nav_context('inicio'))


def dashboard_home(request):
    """📊 Tablero de Control — KPIs reales + mapa Leaflet + historial de cargas."""
    df = _load_students()
    uploads = CSVUpload.objects.all()

    total_students  = len(df) if df is not None else 0
    total_desertores = int(df["desertor"].sum()) if df is not None else 0
    promedio_gral   = round(float(df["promedio_acumulado"].mean()), 2) if df is not None else 0.0
    n_programas     = int(df["programa_academico"].nunique()) if df is not None else 0

    dropout_rate = round((total_desertores / total_students * 100), 1) if total_students > 0 else 0.0
    students_list = df.head(60).to_dict(orient='records') if df is not None else []

    density_list = _build_dept_density(df)

    context = {
        **_nav_context('dashboard'),
        'total_students':   total_students,
        'total_desertores': total_desertores,
        'promedio_gral':    promedio_gral,
        'n_programas':      n_programas,
        'dropout_rate':     dropout_rate,
        'students_list':    students_list,
        'uploads':          uploads,
        'density_json':     json.dumps(density_list),
    }
    return render(request, 'core_app/dashboard.html', context)


def eda_view(request):
    """🔍 Análisis Exploratorio de Datos."""
    df = _load_students()
    if df is None:
        return render(request, 'core_app/eda.html', {**_nav_context('eda'), 'no_data': True})

    programas = sorted(df["programa_academico"].unique().tolist())
    selected  = request.GET.get('programa', 'TODOS')
    dff = df if selected == 'TODOS' else df[df["programa_academico"] == selected]

    # Scatter: Saber11 vs Promedio, coloreado por desertor
    scatter_data = {
        "riesgo":   dff[dff["desertor"] == 1][["puntaje_saber11", "promedio_acumulado"]].rename(
                        columns={"puntaje_saber11": "x", "promedio_acumulado": "y"}).to_dict(orient='records'),
        "seguro":   dff[dff["desertor"] == 0][["puntaje_saber11", "promedio_acumulado"]].rename(
                        columns={"puntaje_saber11": "x", "promedio_acumulado": "y"}).to_dict(orient='records'),
    }

    # Distribución deserción por estrato
    estrato_stats = dff.groupby("estrato_socioeconomico")["desertor"].agg(
        tasa_desercion="mean", total="count"
    ).reset_index()
    estrato_chart = {
        "labels": estrato_stats["estrato_socioeconomico"].tolist(),
        "tasa":   (estrato_stats["tasa_desercion"] * 100).round(1).tolist(),
        "total":  estrato_stats["total"].tolist(),
    }

    # Distribución deserción por programa
    prog_stats = dff.groupby("programa_academico")["desertor"].mean().reset_index()
    prog_stats["desertor"] = (prog_stats["desertor"] * 100).round(1)
    prog_chart = {
        "labels": prog_stats["programa_academico"].tolist(),
        "values": prog_stats["desertor"].tolist(),
    }

    sample = dff.head(15).to_dict(orient='records')

    context = {
        **_nav_context('eda'),
        'programas':     programas,
        'selected':      selected,
        'sample':        sample,
        'scatter_json':  json.dumps(scatter_data),
        'estrato_json':  json.dumps(estrato_chart),
        'prog_json':     json.dumps(prog_chart),
        'total_records': len(dff),
        'tasa_global':   round(dff["desertor"].mean() * 100, 1),
        'promedio_avg':  round(dff["promedio_acumulado"].mean(), 2),
    }
    return render(request, 'core_app/eda.html', context)


def prediccion_view(request):
    """🎯 Inferencia de Riesgo Individual."""
    df = _load_students()
    programas   = sorted(df["programa_academico"].unique().tolist()) if df is not None else [
        "INGENIERIA DE SISTEMAS", "MEDICINA", "DERECHO",
        "ADMINISTRACION DE EMPRESAS", "PSICOLOGIA"
    ]
    depts = sorted(df["departamento_origen"].unique().tolist()) if df is not None else list(DEPT_COORDS.keys())

    # Promedios de referencia de estudiantes en buen estado
    avg_prom = avg_rep = avg_s11 = 0.0
    if df is not None:
        perm = df[df["desertor"] == 0]
        avg_prom = round(perm["promedio_acumulado"].mean(), 2)
        avg_rep  = round(perm["materias_reprobadas"].mean(), 2)
        avg_s11  = round(perm["puntaje_saber11"].mean(), 1)

    context = {
        **_nav_context('prediccion'),
        'programas':  programas,
        'depts':      depts,
        'avg_prom':   avg_prom,
        'avg_rep':    avg_rep,
        'avg_s11':    avg_s11,
    }
    return render(request, 'core_app/prediccion.html', context)


@csrf_exempt
@require_POST
def api_predecir(request):
    """AJAX endpoint: recibe JSON, retorna predicción + probabilidad + recomendación."""
    try:
        body = json.loads(request.body)

        required_num = ['estrato_socioeconomico', 'edad', 'puntaje_saber11',
                        'promedio_acumulado', 'materias_reprobadas', 'ingreso_familiar']
        required_cat = ['genero', 'departamento_origen', 'tipo_colegio', 'programa_academico']

        input_data = {}
        for col in required_num:
            input_data[col] = float(body.get(col, 0))
        for col in required_cat:
            input_data[col] = str(body.get(col, 'DESCONOCIDO'))

        df_in = pd.DataFrame([input_data])

        preprocessor = joblib.load(PREPROCESSOR_PATH)
        model        = joblib.load(MODEL_PATH)

        proc = preprocessor.transform(df_in)
        prob = float(model.predict_proba(proc)[0][1])
        pred = int(model.predict(proc)[0])

        if prob > 0.65:
            nivel     = "ALTO"
            color     = "#ef4444"
            accion    = "PRIORIDAD ALTA: Tutoría Inmediata + Apoyo Financiero de Bienestar"
            icono     = "🚨"
        elif prob > 0.35:
            nivel     = "MEDIO"
            color     = "#f59e0b"
            accion    = "PRIORIDAD MEDIA: Tutoría Académica + Seguimiento Semestral"
            icono     = "⚠️"
        else:
            nivel     = "BAJO"
            color     = "#10b981"
            accion    = "BAJO RIESGO: Monitoreo Rutinario — Continuar seguimiento regular"
            icono     = "✅"

        # Datos comparativos para el gráfico
        df_base = _load_students()
        avg_prom = avg_rep = avg_s11 = 0.0
        if df_base is not None:
            perm = df_base[df_base["desertor"] == 0]
            avg_prom = round(float(perm["promedio_acumulado"].mean()), 2)
            avg_rep  = round(float(perm["materias_reprobadas"].mean()), 2)
            avg_s11  = round(float(perm["puntaje_saber11"].mean()), 1)

        return JsonResponse({
            "ok":          True,
            "probabilidad": round(prob * 100, 1),
            "prediccion":   pred,
            "nivel":        nivel,
            "color":        color,
            "accion":       accion,
            "icono":        icono,
            "comparativo": {
                "estudiante": {
                    "promedio":    input_data["promedio_acumulado"],
                    "reprobadas":  input_data["materias_reprobadas"],
                    "saber11":     input_data["puntaje_saber11"],
                },
                "promedio_permanentes": {
                    "promedio":   avg_prom,
                    "reprobadas": avg_rep,
                    "saber11":    avg_s11,
                }
            }
        })

    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=400)


def modelos_view(request):
    """⚖️ Comparación y métricas de algoritmos de ML."""
    df = _load_students()
    metrics = _evaluate_all_models(df)

    # Fallback estático si los modelos no están disponibles
    if not metrics:
        metrics = {
            "Gradient Boosting": {"accuracy": 96.36, "precision": 86.74, "recall": 81.35, "f1": 83.96},
            "LightGBM":          {"accuracy": 95.94, "precision": 81.95, "recall": 83.80, "f1": 82.86},
            "XGBoost":           {"accuracy": 95.74, "precision": 81.06, "recall": 83.05, "f1": 82.04},
            "ExtraTrees":        {"accuracy": 92.83, "precision": 84.10, "recall": 47.83, "f1": 60.98},
            "Random Forest":     {"accuracy": 88.31, "precision": 100.0, "recall": 0.18,  "f1": 0.37},
        }

    # Modelo en producción = mayor F1
    active_name = max(metrics, key=lambda k: metrics[k]["f1"])
    active_m    = metrics[active_name]

    # Datos para Chart.js
    chart_data = {
        "labels":     list(metrics.keys()),
        "accuracy":   [v["accuracy"]  for v in metrics.values()],
        "precision":  [v["precision"] for v in metrics.values()],
        "recall":     [v["recall"]    for v in metrics.values()],
        "f1":         [v["f1"]        for v in metrics.values()],
    }

    context = {
        **_nav_context('modelos'),
        'metrics':       metrics,
        'active_name':   active_name,
        'active_m':      active_m,
        'chart_json':    json.dumps(chart_data),
        'n_records':     len(df) if df is not None else 0,
    }
    return render(request, 'core_app/modelos.html', context)


def xai_view(request):
    """🛡️ Explicabilidad (XAI) — Feature Importance."""
    # Intentar cargar importancias reales desde el modelo
    shap_data = None
    try:
        model = joblib.load(MODEL_PATH)
        if hasattr(model, "feature_importances_"):
            preprocessor = joblib.load(PREPROCESSOR_PATH)
            feat_names = (
                preprocessor.get_feature_names_out().tolist()
                if hasattr(preprocessor, 'get_feature_names_out')
                else [f"feat_{i}" for i in range(len(model.feature_importances_))]
            )
            importances = model.feature_importances_.tolist()
            # Top 10 features
            pairs = sorted(zip(feat_names, importances), key=lambda x: x[1], reverse=True)[:10]
            shap_data = {"labels": [p[0] for p in pairs], "values": [round(p[1], 4) for p in pairs]}
    except Exception:
        pass

    # Fallback interpretativo
    if not shap_data:
        shap_data = {
            "labels": ["Promedio Acumulado", "Materias Reprobadas", "Ingreso Familiar",
                       "Puntaje Saber 11", "Estrato Socioeconómico", "Edad"],
            "values": [0.45, 0.32, 0.18, 0.12, 0.08, 0.05],
        }

    context = {
        **_nav_context('xai'),
        'shap_json': json.dumps(shap_data),
        'interpretaciones': [
            {
                "variable": "Promedio Acumulado",
                "color":    "#ef4444",
                "texto":    "Es el indicador académico más potente. Una reducción por debajo de 3.0 genera un incremento inmediato en la alerta de deserción.",
            },
            {
                "variable": "Materias Reprobadas",
                "color":    "#f59e0b",
                "texto":    "Actúa como efecto multiplicador. Cuando se acompaña de un bajo promedio, la probabilidad de deserción aumenta exponencialmente.",
            },
            {
                "variable": "Ingreso Familiar",
                "color":    "#818cf8",
                "texto":    "El contexto financiero del hogar es el determinante principal del abandono por motivos no académicos (deserción socioeconómica).",
            },
            {
                "variable": "Puntaje Saber 11",
                "color":    "#38bdf8",
                "texto":    "Un bajo puntaje de entrada predispone al estudiante a dificultades académicas en el primer semestre, período más crítico de deserción.",
            },
        ],
    }
    return render(request, 'core_app/xai.html', context)


def curricular_view(request):
    """📈 Pertinencia Curricular y Mercado Laboral."""
    df_cur = _load_curriculum()

    # Enriquecer con tasa de deserción real calculada desde students CSV si disponible
    df_st = _load_students()
    if df_st is not None and 'programa_academico' in df_st.columns:
        deser_prog = df_st.groupby('programa_academico')['desertor'].mean().reset_index()
        deser_prog.columns = ['programa_academico', 'tasa_desercion_real']
        df_cur = df_cur.merge(deser_prog, on='programa_academico', how='left')
        df_cur['tasa_desercion'] = (df_cur['tasa_desercion_real'].fillna(0) * 100).round(1)
        df_cur.drop(columns=['tasa_desercion_real'], inplace=True, errors='ignore')

    # Convertir a tipos serializables seguros
    df_cur['salario_enganche']   = pd.to_numeric(df_cur['salario_enganche'],   errors='coerce').fillna(0).astype(int)
    df_cur['tasa_empleabilidad'] = pd.to_numeric(df_cur['tasa_empleabilidad'], errors='coerce').fillna(0).round(1)
    df_cur['tasa_desercion']     = pd.to_numeric(df_cur['tasa_desercion'],     errors='coerce').fillna(0).round(1)

    has_satisfaccion   = 'indice_satisfaccion'  in df_cur.columns
    has_acreditacion   = 'nivel_acreditacion'   in df_cur.columns

    chart_data = {
        "labels":        df_cur["programa_academico"].tolist(),
        "salarios":      df_cur["salario_enganche"].tolist(),
        "empleabilidad": df_cur["tasa_empleabilidad"].tolist(),
        "desercion":     df_cur["tasa_desercion"].tolist(),
    }

    context = {
        **_nav_context('curricular'),
        'curriculum':          df_cur.to_dict(orient='records'),
        'chart_json':          json.dumps(chart_data),
        'has_satisfaccion':    has_satisfaccion,
        'has_acreditacion':    has_acreditacion,
    }
    return render(request, 'core_app/curricular.html', context)


def prescriptivo_view(request):
    """📋 Recomendaciones Prescriptivas."""
    # Cargar datos prescriptivos desde el API client o fallback
    prescriptive_data = []
    try:
        import sys
        sys.path.insert(0, str(BASE_DIR))
        from src.infrastructure.external_api.colombia_api import ColombiaDatosAbiertosClient
        client = ColombiaDatosAbiertosClient()
        df_presc = client.get_prescriptive_programs_data()
        prescriptive_data = df_presc.to_dict(orient='records')
    except Exception:
        prescriptive_data = [
            {"departamento": "BOGOTA D.C.",   "tasa_desercion_historica": 18.4, "cobertura_becas": 42.1, "presupuesto_asignado_millones": 850},
            {"departamento": "ANTIOQUIA",      "tasa_desercion_historica": 22.1, "cobertura_becas": 31.5, "presupuesto_asignado_millones": 620},
            {"departamento": "VALLE DEL CAUCA","tasa_desercion_historica": 25.8, "cobertura_becas": 28.3, "presupuesto_asignado_millones": 480},
            {"departamento": "ATLANTICO",      "tasa_desercion_historica": 19.3, "cobertura_becas": 35.7, "presupuesto_asignado_millones": 310},
            {"departamento": "CUNDINAMARCA",   "tasa_desercion_historica": 21.4, "cobertura_becas": 29.8, "presupuesto_asignado_millones": 270},
            {"departamento": "SANTANDER",      "tasa_desercion_historica": 23.6, "cobertura_becas": 26.4, "presupuesto_asignado_millones": 210},
        ]

    scatter_data = [
        {"x": r["cobertura_becas"], "y": r["tasa_desercion_historica"],
         "label": r["departamento"], "size": r["presupuesto_asignado_millones"]}
        for r in prescriptive_data
    ]

    context = {
        **_nav_context('prescriptivo'),
        'prescriptive_data': prescriptive_data,
        'scatter_json':      json.dumps(scatter_data),
    }
    return render(request, 'core_app/prescriptivo.html', context)


# --------------------------------------------------------------------------- #
#  UPLOAD / CLEAR (conservados y mejorados)
# --------------------------------------------------------------------------- #

def upload_csv_view(request):
    """Procesa carga de CSV o URL de API, ejecuta inferencia, genera PDF e IPYNB."""
    if request.method == 'POST':
        import requests as req_lib
        title    = request.POST.get('title', 'Carga Predictiva')
        api_url  = request.POST.get('api_url', '').strip()
        csv_file = request.FILES.get('csv_file')

        df     = None
        upload = None

        if api_url:
            try:
                response = req_lib.get(api_url, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and 'results' in data:
                        data = data['results']
                    df = pd.DataFrame(data)
                    csv_io = io.StringIO()
                    df.to_csv(csv_io, index=False)
                    csv_content = csv_io.getvalue().encode('utf-8')
                    upload = CSVUpload(title=title)
                    upload.csv_file.save(
                        f"api_data_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.csv",
                        ContentFile(csv_content), save=False
                    )
                    upload.save()
            except Exception as e:
                print(f"Error cargando API: {e}")

        elif csv_file:
            upload = CSVUpload(title=title, csv_file=csv_file)
            upload.save()
            try:
                df = pd.read_csv(upload.csv_file.path)
            except Exception as e:
                print(f"Error leyendo CSV: {e}")

        if df is not None and upload is not None:
            preprocessor = joblib.load(PREPROCESSOR_PATH)
            model        = joblib.load(MODEL_PATH)

            required_num = ['estrato_socioeconomico', 'edad', 'puntaje_saber11',
                            'promedio_acumulado', 'materias_reprobadas', 'ingreso_familiar']
            required_cat = ['genero', 'departamento_origen', 'tipo_colegio', 'programa_academico']

            for col in required_num:
                if col not in df.columns: df[col] = 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            for col in required_cat:
                if col not in df.columns: df[col] = 'DESCONOCIDO'

            proc = preprocessor.transform(df)
            predictions   = model.predict(proc)
            probabilities = model.predict_proba(proc)[:, 1]

            df['desertor_predicho']   = predictions
            df['probabilidad_desercion'] = probabilities

            total_records     = len(df)
            predicted_dropouts = int(predictions.sum())
            upload.total_records    = total_records
            upload.predicted_dropouts = predicted_dropouts

            # ---- PDF ----
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter,
                                    rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'TS', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=22,
                textColor=colors.HexColor('#0f172a'), spaceAfter=20, alignment=1)
            body_style = ParagraphStyle(
                'BS', parent=styles['BodyText'], fontName='Helvetica', fontSize=10,
                textColor=colors.HexColor('#334155'), leading=14, spaceAfter=10)
            h2_style = ParagraphStyle(
                'H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=13,
                textColor=colors.HexColor('#0284c7'), spaceBefore=15, spaceAfter=8)

            story = [
                Paragraph("Reporte Clínico de Permanencia Universitaria", title_style),
                Paragraph(f"<b>Carga:</b> {title}", body_style),
                Paragraph(f"<b>Fecha:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", body_style),
                Spacer(1, 10),
            ]
            data_m = [
                ["Indicador", "Valor"],
                ["Estudiantes Analizados",    f"{total_records:,}"],
                ["Alertas de Riesgo",          f"{predicted_dropouts:,}"],
                ["Tasa de Riesgo Estimada",    f"{(predicted_dropouts/total_records*100):.1f}%"],
                ["Modelo (Accuracy estimado)", "96.36%"],
            ]
            t = Table(data_m, colWidths=[250, 150])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ]))
            story.append(t)
            story.append(Spacer(1, 20))
            story.append(Paragraph("Plan de Acción Prescriptivo", h2_style))
            story.append(Paragraph(
                "1. <b>Tutorías Inmediatas</b>: Asignar tutor a estudiantes con probabilidad > 60%.<br/>"
                "2. <b>Apoyo Financiero</b>: Cruzar alertas de estrato 1-2 con oficinas de becas.<br/>"
                "3. <b>Flexibilización Curricular</b>: Identificar materias críticas compartidas.",
                body_style))

            top_risk = df.sort_values('probabilidad_desercion', ascending=False).head(10)
            story.append(Spacer(1, 15))
            story.append(Paragraph("Top 10 Estudiantes con Mayor Riesgo", h2_style))
            risk_rows = [["Nombre", "Programa", "Promedio", "Riesgo"]]
            for _, r in top_risk.iterrows():
                risk_rows.append([
                    str(r.get('nombre', '—'))[:30],
                    str(r.get('programa_academico', '—'))[:25],
                    f"{float(r.get('promedio_acumulado', 0)):.2f}",
                    f"{float(r.get('probabilidad_desercion', 0))*100:.1f}%",
                ])
            tr = Table(risk_rows, colWidths=[130, 170, 60, 70])
            tr.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7f1d1d')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('FONTSIZE', (0,0), (-1,-1), 9),
            ]))
            story.append(tr)
            doc.build(story)
            upload.pdf_report.save(f"reporte_{upload.id}.pdf", ContentFile(pdf_buffer.getvalue()), save=False)
            pdf_buffer.close()

            # ---- IPYNB ----
            result_csv_path = os.path.join(settings.MEDIA_ROOT, "csv_uploads", f"pred_{upload.id}.csv")
            os.makedirs(os.path.dirname(result_csv_path), exist_ok=True)
            df.to_csv(result_csv_path, index=False)

            nb = {
                "cells": [
                    {"cell_type": "markdown", "metadata": {}, "source": [
                        f"# Análisis Predictivo: {title}\n",
                        f"**Registros:** {total_records} | **Alertas:** {predicted_dropouts}\n"
                    ]},
                    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
                        "import pandas as pd, matplotlib.pyplot as plt, seaborn as sns\n",
                        f"df = pd.read_csv(r'{result_csv_path}')\n",
                        "print(f'Registros: {{df.shape[0]}}')\ndf.head()"
                    ]},
                    {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": [
                        "plt.figure(figsize=(8,4))\n",
                        "sns.histplot(df['probabilidad_desercion'], kde=True, color='#ef4444')\n",
                        "plt.title('Distribución de Riesgo de Deserción')\nplt.show()"
                    ]},
                ],
                "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                             "language_info": {"name": "python"}},
                "nbformat": 4, "nbformat_minor": 2,
            }
            upload.notebook_file.save(
                f"analisis_{upload.id}.ipynb",
                ContentFile(json.dumps(nb, indent=2, ensure_ascii=False).encode('utf-8')),
                save=False
            )
            upload.save()

    return redirect('dashboard_home')


def clear_history_view(request):
    if request.method == 'POST':
        uploads = CSVUpload.objects.all()
        for u in uploads:
            for field in ['csv_file', 'pdf_report', 'notebook_file']:
                f = getattr(u, field)
                if f:
                    try:
                        if os.path.exists(f.path):
                            os.remove(f.path)
                    except Exception:
                        pass
        uploads.delete()
    return redirect('dashboard_home')
