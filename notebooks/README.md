# 📓 Guía de Cuadernos Interactivos (Notebooks)

Este directorio contiene los **18 cuadernos secuenciales** de Jupyter que implementan el ciclo de vida completo de ciencia de datos del **Framework Inteligente de ML - SNIES**, desarrollado para el concurso *Datos al Ecosistema 2026*.

A continuación se detalla el orden de ejecución, propósito y salidas generadas por cada uno:

---

## 🗺️ Mapa de Ejecución Secuencial

Para reproducir el análisis completo, ejecuta los cuadernos en el orden numérico indicado:

```
[01 a 04: Ingesta] ➔ [05: ETL] ➔ [06: EDA] ➔ [07: Preprocesamiento] ➔ [08: Variables] ➔ [09 a 12: Modelado] ➔ [13 y 14: XAI] ➔ [15: Evaluación] ➔ [16: Prescriptivo] ➔ [17 y 18: Dashboard y DevOps]
```

---

## 📋 Detalle de Cuadernos

### 1. Ingesta de Datos (Fase de APIs)
*   **[01_Descarga_SNIES.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/01_Descarga_SNIES.ipynb)**:
    - **Función**: Se conecta por HTTPS a la API SODA de `datos.gov.co` (dataset `ddau-8cy9`) para descargar registros académicos de estudiantes matriculados en IES.
    - **Salida**: Muestra la estructura cruda de los datos académicos.
*   **[02_Descarga_DANE.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/02_Descarga_DANE.ipynb)**:
    - **Función**: Consulta e integra información demográfica, de estratificación socioeconómica y salarios de hogares por departamento.
*   **[03_Descarga_OLE.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/03_Descarga_OLE.ipynb)**:
    - **Función**: Descarga índices de empleabilidad y salarios promedio de inserción laboral de graduados universitarios en Colombia.
*   **[04_Datos_Abiertos.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/04_Datos_Abiertos.ipynb)**:
    - **Función**: Enseña a utilizar el cliente genérico de Python `ColombiaDatosAbiertosClient` para automatizar peticiones a APIs de datos gubernamentales.

### 2. Procesamiento y Análisis (Fase ETL/EDA)
*   **[05_ETL.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/05_ETL.ipynb)**:
    - **Función**: Ejecuta el pipeline ETL unificando las tres fuentes (SNIES, DANE, OLE) en una base de datos local SQLite y archivos CSV estructurados.
    - **Salida**: Archivos procesados en `data/processed/`.
*   **[06_EDA.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/06_EDA.ipynb)**:
    - **Función**: Análisis exploratorio estadístico. Muestra histogramas de deserción y gráficos de correlación entre promedios académicos y condiciones financieras.

### 3. Machine Learning (Fase de Inteligencia)
*   **[07_Feature_Engineering.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/07_Feature_Engineering.ipynb)**:
    - **Función**: Escala variables numéricas con `StandardScaler` y codifica variables de texto con `OneHotEncoder` de scikit-learn.
    - **Salida**: Genera el preprocesador serializado `models/preprocessor.pkl`.
*   **[08_Seleccion_Variables.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/08_Seleccion_Variables.ipynb)**:
    - **Función**: Evalúa y selecciona las características (features) con mayor peso de decisión usando un bosque aleatorio.
*   **[09_Modelos_Supervisados.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/09_Modelos_Supervisados.ipynb)**:
    - **Función**: Entrena, ajusta e instrumenta el clasificador de Random Forest para predecir alertas de deserción en nuevos alumnos.
    - **Salida**: Genera el modelo clasificador en `models/randomforest_model.pkl`.
*   **[10_Modelos_NoSupervisados.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/10_Modelos_NoSupervisados.ipynb)**:
    - **Función**: Agrupa de forma no supervisada (K-Means) a los estudiantes en tres perfiles de riesgo académico.
*   **[11_PyCaret_AutoML.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/11_PyCaret_AutoML.ipynb)** y **[12_FLAML.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/12_FLAML.ipynb)**:
    - **Función**: Implementa optimizadores automáticos para entrenar múltiples clasificadores y seleccionar el mejor (XGBoost / LightGBM) en menor tiempo de cómputo.

### 4. Explicabilidad y Acción (Fase Humana y Prescriptiva)
*   **[13_XAI_SHAP.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/13_XAI_SHAP.ipynb)** y **[14_XAI_LIME.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/14_XAI_LIME.ipynb)**:
    - **Función**: Implementa algoritmos de interpretabilidad clínica de IA. Permite auditar y justificar por qué la IA emitió una alerta para cada estudiante.
*   **[15_Evaluacion.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/15_Evaluacion.ipynb)**:
    - **Función**: Evalúa confiabilidad, curvas ROC, matrices de confusión y precisión de los modelos registrados.
*   **[16_Analitica_Prescriptiva.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/16_Analitica_Prescriptiva.ipynb)**:
    - **Función**: Aplica lógica prescriptiva sobre el dataset del concurso para sugerir la reasignación de subsidios de transporte y becas universitarias.

### 5. Interfaz y Operación (Fase de Producción)
*   **[17_Streamlit.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/17_Streamlit.ipynb)**:
    - **Función**: Documenta los parámetros de visualización y ejecución de la interfaz de usuario en local.
*   **[18_Despliegue.ipynb](file:///c:/Users/Feibert/OneDrive/Documents/UFHEC/ConcursoDatosAbiertoColombiaID8/Framework-ML-SNIES/notebooks/18_Despliegue.ipynb)**:
    - **Función**: Guía para la orquestación del proyecto mediante contenedores y tracking de experimentos con MLflow.

---

## 🛠️ Requisitos de Ejecución

Antes de ejecutar los cuadernos, asegúrate de instalar las dependencias del proyecto:

```bash
pip install -r requirements.txt
pip install -e .
```
