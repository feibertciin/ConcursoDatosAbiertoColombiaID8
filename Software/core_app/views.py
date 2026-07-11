import os
import json
import io
from pathlib import Path
import pandas as pd
import numpy as np
import joblib
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.conf import settings
from django.core.files.base import ContentFile
from .models import CSVUpload

# Rutas de modelos entrenados en el proyecto
BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = os.path.join(BASE_DIR, "models", "randomforest_model.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "models", "preprocessor.pkl")

# ReportLab imports para generación de PDF profesional
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def dashboard_home(request):
    """Vista principal del Dashboard del Software"""
    uploads = CSVUpload.objects.all()
    
    # Calcular estadísticas acumulativas
    total_uploads = uploads.count()
    total_records_sum = sum(u.total_records for u in uploads)
    total_dropouts_sum = sum(u.predicted_dropouts for u in uploads)
    
    rate = 0.0
    if total_records_sum > 0:
        rate = (total_dropouts_sum / total_records_sum) * 100
        
    context = {
        'uploads': uploads,
        'total_uploads': total_uploads,
        'total_records_sum': total_records_sum,
        'total_dropouts_sum': total_dropouts_sum,
        'dropout_rate': round(rate, 1)
    }
    return render(request, 'core_app/dashboard.html', context)

def upload_csv_view(request):
    """Procesa la carga de archivos CSV o enlaces de API, ejecuta inferencia de modelos, genera PDF e IPYNB"""
    if request.method == 'POST':
        title = request.POST.get('title', 'Carga Predictiva')
        api_url = request.POST.get('api_url', '').strip()
        csv_file = request.FILES.get('csv_file')
        
        df = None
        upload = None
        
        if api_url:
            import requests
            try:
                # Query open data API
                response = requests.get(api_url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    # Si viene como objeto con resultados o lista
                    if isinstance(data, dict) and 'results' in data:
                        data = data['results']
                    df = pd.DataFrame(data)
                    
                    # Guardamos el CSV generado por la API
                    csv_io = io.StringIO()
                    df.to_csv(csv_io, index=False)
                    csv_content = csv_io.getvalue().encode('utf-8')
                    
                    upload = CSVUpload(title=title)
                    upload.csv_file.save(f"api_data_{pd.Timestamp.now().strftime('%Y%m%d%H%M%S')}.csv", ContentFile(csv_content), save=False)
                    upload.save()
            except Exception as e:
                print(f"Error cargando API Abierta: {str(e)}")
                
        elif csv_file:
            upload = CSVUpload(title=title, csv_file=csv_file)
            upload.save()
            try:
                df = pd.read_csv(upload.csv_file.path)
            except Exception as e:
                print(f"Error leyendo archivo CSV cargado: {str(e)}")
                
        if df is not None and upload is not None:
            # Cargar modelos y preprocesador
            preprocessor = joblib.load(PREPROCESSOR_PATH)
            model = joblib.load(MODEL_PATH)
            
            # Validar y alinear columnas con las variables de entrenamiento
            # Si el CSV no contiene las columnas necesarias, asignamos valores por defecto
            required_cols = ['genero', 'departamento_origen', 'estrato_socioeconomico', 'tipo_colegio', 
                             'programa_academico', 'edad', 'puntaje_saber11', 'promedio_acumulado', 
                             'materias_reprobadas', 'ingreso_familiar']
            
            for col in required_cols:
                if col not in df.columns:
                    if col in ['estrato_socioeconomico', 'edad', 'puntaje_saber11', 'promedio_acumulado', 'materias_reprobadas', 'ingreso_familiar']:
                        df[col] = 0
                    else:
                        df[col] = 'DESCONOCIDO'
            
            # Castear a numérico para evitar fallos de tipos de datos en la API SODA
            numeric_cols = ['estrato_socioeconomico', 'edad', 'puntaje_saber11', 'promedio_acumulado', 'materias_reprobadas', 'ingreso_familiar']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Preprocesar e Inferencia
            proc_data = preprocessor.transform(df)
            predictions = model.predict(proc_data)
            probabilities = model.predict_proba(proc_data)[:, 1]
            
            df['desertor_predicho'] = predictions
            df['probabilidad_desercion'] = probabilities
            
            # Calcular agregaciones
            total_records = len(df)
            predicted_dropouts = int(predictions.sum())
            
            upload.total_records = total_records
            upload.predicted_dropouts = predicted_dropouts
            
            # --- GENERACIÓN DEL PDF REPORTE CLÍNICO (ReportLab) ---
            pdf_buffer = io.BytesIO()
            doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, 
                textColor=colors.HexColor('#0f172a'), spaceAfter=20, alignment=1
            )
            body_style = ParagraphStyle(
                'BodyStyle', parent=styles['BodyText'], fontName='Helvetica', fontSize=10.5, 
                textColor=colors.HexColor('#334155'), leading=14, spaceAfter=10
            )
            h2_style = ParagraphStyle(
                'H2Style', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, 
                textColor=colors.HexColor('#0284c7'), spaceBefore=15, spaceAfter=8
            )
            
            story = []
            story.append(Paragraph("📋 Reporte Clínico de Permanencia Universitaria", title_style))
            story.append(Paragraph(f"<b>Carga Predictiva:</b> {title}", body_style))
            story.append(Paragraph(f"<b>Fecha de Emisión:</b> {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", body_style))
            story.append(Spacer(1, 10))
            
            # Metricas Tabla
            data_metrics = [
                ["Indicador Analítico", "Valor Obtenido"],
                ["Estudiantes Analizados", f"{total_records:,}"],
                ["Casos en Alto Riesgo (Alertas)", f"{predicted_dropouts:,}"],
                ["Tasa de Deserción Estimada", f"{(predicted_dropouts / total_records * 100):.1f}%"],
                ["Confiabilidad del Modelo (Accuracy)", "96.36%"]
            ]
            t_metrics = Table(data_metrics, colWidths=[250, 150])
            t_metrics.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e293b')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 8),
                ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#f8fafc')),
                ('GRID', (0,0), (-1,-1), 1, colors.HexColor('#cbd5e1')),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
            ]))
            story.append(t_metrics)
            story.append(Spacer(1, 20))
            
            story.append(Paragraph("💡 Plan de Acción Prescriptivo Sugerido", h2_style))
            story.append(Paragraph(
                "1. **Tutorías Inmediatas**: Para los estudiantes clasificados con alta probabilidad, programar tutorías prioritarias con bienestar universitario.<br/>"
                "2. **Auxilio de Sostenimiento**: Cruzar el listado de alertas de estrato 1 y 2 con oficinas de becas.<br/>"
                "3. **Plan de Flexibilización**: Identificar materias críticas compartidas por los alumnos en alerta.",
                body_style
            ))
            
            # Listado de Alertas (Top 10)
            story.append(Spacer(1, 15))
            story.append(Paragraph("🚨 Top 10 Estudiantes con Mayor Probabilidad de Riesgo", h2_style))
            
            top_risk = df.sort_values(by='probabilidad_desercion', ascending=False).head(10)
            data_risk = [["Nombre", "Programa Académico", "Promedio", "Riesgo"]]
            for idx, r in top_risk.iterrows():
                data_risk.append([
                    str(r.get('nombre', f'Estudiante {idx}')),
                    str(r.get('programa_academico', 'N/A'))[:25],
                    f"{float(r.get('promedio_acumulado', 0.0)):.2f}",
                    f"{(float(r.get('probabilidad_desercion', 0.0)) * 100):.1f}%"
                ])
            t_risk = Table(data_risk, colWidths=[120, 170, 60, 70])
            t_risk.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#7f1d1d')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                ('ALIGN', (2,1), (-1,-1), 'CENTER'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
                ('FONTSIZE', (0,0), (-1,-1), 9),
            ]))
            story.append(t_risk)
            
            doc.build(story)
            pdf_data = pdf_buffer.getvalue()
            pdf_buffer.close()
            
            # Guardar reporte PDF en el FileField
            upload.pdf_report.save(f"reporte_{upload.id}.pdf", ContentFile(pdf_data), save=False)
            
            # --- GENERACIÓN DEL CUADERNO .ipynb DINÁMICO ---
            # Guardamos el CSV resultante de predicciones en la carpeta media para que el cuaderno lo lea
            result_csv_name = f"predicciones_{upload.id}.csv"
            result_csv_path = os.path.join(settings.MEDIA_ROOT, "csv_uploads", result_csv_name)
            os.makedirs(os.path.dirname(result_csv_path), exist_ok=True)
            df.to_csv(result_csv_path, index=False)
            
            notebook_data = {
                "cells": [
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": [
                            f"# 📓 Cuaderno de Análisis Predictivo Automatizado\n",
                            f"**Carga del Proyecto:** {title}\n",
                            f"**Registros Analizados:** {total_records}\n",
                            "Este cuaderno fue generado automáticamente por la aplicación Django para permitir el análisis interactivo de las predicciones."
                        ]
                    },
                    {
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": [
                            "import pandas as pd\n",
                            "import matplotlib.pyplot as plt\n",
                            "import seaborn as sns\n",
                            "\n",
                            "# Cargar los resultados procesados\n",
                            f"df = pd.read_csv('{result_csv_path.replace(chr(92), '/')}')\n",
                            "print(f'Registros cargados: {df.shape[0]}')\n",
                            "df.head()"
                        ]
                    },
                    {
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": [
                            "# Distribución de probabilidades de deserción\n",
                            "plt.figure(figsize=(8, 4))\n",
                            "sns.histplot(data=df, x='probabilidad_desercion', kde=True, color='purple')\n",
                            "plt.title('Distribución del Porcentaje de Riesgo de Deserción')\n",
                            "plt.xlabel('Probabilidad')\n",
                            "plt.show()"
                        ]
                    }
                ],
                "metadata": {
                    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                    "language_info": {"name": "python"}
                },
                "nbformat": 4,
                "nbformat_minor": 2
            }
            notebook_json = json.dumps(notebook_data, indent=2, ensure_ascii=False)
            upload.notebook_file.save(f"analisis_{upload.id}.ipynb", ContentFile(notebook_json.encode('utf-8')), save=False)
            
            # Guardamos todo
            upload.save()
            
        return redirect('dashboard_home')
        
    return redirect('dashboard_home')

def clear_history_view(request):
    """Elimina todos los registros de cargas en base de datos y sus archivos asociados"""
    if request.method == 'POST':
        uploads = CSVUpload.objects.all()
        for u in uploads:
            if u.csv_file:
                try:
                    if os.path.exists(u.csv_file.path):
                        os.remove(u.csv_file.path)
                except: pass
            if u.pdf_report:
                try:
                    if os.path.exists(u.pdf_report.path):
                        os.remove(u.pdf_report.path)
                except: pass
            if u.notebook_file:
                try:
                    if os.path.exists(u.notebook_file.path):
                        os.remove(u.notebook_file.path)
                except: pass
        uploads.delete()
    return redirect('dashboard_home')
