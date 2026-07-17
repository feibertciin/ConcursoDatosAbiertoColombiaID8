# Framework Inteligente de ML Multimodelo para la Permanencia Estudiantil 🎓

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111.0-green.svg)](https://fastapi.tiangolo.com)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35.0-red.svg)](https://streamlit.io)
[![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![XGBoost](https://img.shields.io/badge/XGBoost-%23150458.svg?style=flat)](https://xgboost.readthedocs.io/)
[![MLflow](https://img.shields.io/badge/mlflow-%23d9efff.svg?style=flat)](https://mlflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Framework Inteligente de Machine Learning Multimodelo para Analítica Predictiva y Prescriptiva aplicada a la Permanencia Estudiantil y Pertinencia Curricular mediante integración de **SNIES**, **DANE**, **OLE** y **Datos Abiertos Colombia**.

---

## 🔗 Enlaces de Documentación y Aplicaciones

A continuación se presentan los accesos directos principales a las aplicaciones desplegadas, código fuente y documentación del proyecto:

| Recurso / Aplicación          | Tipo              | Descripción                                                                               | Enlace de Acceso                                                                           |
| :----------------------------- | :---------------- | :----------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------- |
| **Streamlit App**        | Aplicación Cloud | Dashboard interactivo con georeferenciación, mapa de calor y motor prescriptivo regional. | [Lanzar App en Streamlit Cloud](https://concursodatosabiertocolombiaid8.streamlit.app/)     |
| **Código en GitHub**    | Repositorio       | Código fuente del framework, landing page y configuraciones de MLOps.                     | [Ver Repositorio en GitHub](https://feibertciin.github.io/ConcursoDatosAbiertoColombiaID8/) |
| **Engine de Inferencia** | Django Software   | Servidor web local de predicciones masivas por CSV/API con exportación de reportes PDF.   | [Explorar Módulo (/Software)]([Software/](https://pharmaceuticals-contest-sizes-phil.trycloudflare.com/))                                                   |
| **Presentación** | Soporte   | Presentación del proyecto.   | [Ver](https://drive.google.com/file/d/1SPHocT8hiw10sWt7krW29HEDCH2NYCKb/view?usp=drive_link)                                                   |
| **Soporte Técnico** | Documento   | Informe del proyecto.   | [Ver](https://docs.google.com/document/d/140gnSxJ5CotqG7DWM9EKO46qHcn_PNh2/edit?usp=drive_link&ouid=107643151803452107423&rtpof=true&sd=true)                                                   |

https://pharmaceuticals-contest-sizes-phil.trycloudflare.com/
---

## 🏗️ Arquitectura del Sistema

El proyecto está construido utilizando **Clean Architecture** (Arquitectura Hexagonal), separando estrictamente la lógica de dominio de las dependencias externas (bases de datos, frameworks de interfaz y librerías de ML).

```
Framework-ML-SNIES/
├── config/              # Parámetros de Hydra y Logging
├── src/
│   ├── domain/          # Entidades y reglas de negocio puras
│   ├── application/     # Pipeline de ETL, features y entrenamiento
│   └── infrastructure/  # SQLAlchemy ORM, persistencia
├── api/                 # Endpoint de inferencia con FastAPI
├── streamlit/           # Frontend interactivo para consejeros académicos
├── landing_page/        # Landing page web moderna
└── notebooks/           # Notebooks de experimentación CRISP-ML(Q)
```

---

## 📊 Resultados de Entrenamiento

Durante el pipeline de entrenamiento automatizado, obtuvimos las siguientes métricas comparativas:

| Modelo                     |    Accuracy    |    Precision    |     Recall     |    F1-Score    |
| :------------------------- | :-------------: | :-------------: | :-------------: | :-------------: |
| **XGBoost (Activo)** | **93.0%** | **81.2%** | **76.5%** | **78.8%** |
| RandomForest               |      92.0%      |      80.0%      |      70.6%      |      75.0%      |
| LightGBM                   |      92.5%      |      80.6%      |      73.5%      |      76.9%      |
| GradientBoosting           |      93.0%      |      85.7%      |      70.6%      |      77.4%      |

---

## 🛠️ Instalación y Uso

### 1. Clonar el repositorio y acceder a la carpeta

```bash
git clone https://github.com/usuario/Framework-ML-SNIES.git
cd Framework-ML-SNIES
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
pip install -e .
```

### 3. Ejecutar inicialización de Base de Datos y ETL

```bash
python -m src.infrastructure.database.init_db
python -m src.application.training
```

### 4. Lanzar la aplicación Streamlit

```bash
streamlit run app.py
```

### 5. Lanzar la API FastAPI

```bash
uvicorn api.main:app --reload
```

---

## 📖 Autores y Citación

### Investigadores:

- **Feibert Alirio Guzmán Pérez** - Magíster en Educación, Especialista en Gerencia Informática, Ingeniero de Sistemas. Corporación Universitaria Lasallista (UNILASALLISTA), Facultad de Ingenierías, Grupo de Investigación G-3IN.
- **Jonathan Berthel Castro** - Magíster en Ingeniería con Énfasis en Ingeniería de Sistemas y Computación, Especialista en BD y Telecomunicaciones. Corporación Universitaria Lasallista (UNILASALLISTA), Facultad de Ingenierías, Grupo de Investigación G-3IN.
- **Doris María Vásquez González** - Administradora de Empresas y Finanzas, Tecnóloga en Gestión Empresarial y Financiera, Técnica en Almacenamiento y Distribución Logística. Contratista del DANE e Independiente.

### Cómo Citar:

Para citar este framework en investigaciones científicas o publicaciones académicas:

```bibtex
@software{framework_ml_snies_2026,
  author       = {Guzmán-Pérez, Feibert Alirio and Berthel-Castro, Jonathan and Vásquez-González, Doris María},
  title        = {Framework Inteligente de Machine Learning Multimodelo para la Permanencia Estudiantil e Integración SNIES/DANE},
  month        = jul,
  year         = 2026,
  publisher    = {Datos Abiertos Colombia},
  doi          = {10.5281/zenodo.xxxxxx}
}
```
