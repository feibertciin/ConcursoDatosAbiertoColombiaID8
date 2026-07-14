# Formulario de Registro Oficial: Desarrollo Web
**Investigador Principal:** FEIBERT ALIRIO GUZMAN  
**Proyecto de Investigación Vinculado:** *Integración de Técnicas Estadísticas, Inteligencia Artificial y Gamificación para el Análisis de Datos Empresariales e Investigativos: Desarrollo de una Metodología Innovadora y Prototipo Funcional (En curso: 2026-CIMC02)*

---

## 📋 Información General del Producto

*   **Nombre del Producto:** Pagina Web: Framework Inteligente de Machine Learning
*   **Año:** 2026
*   **Mes:** Julio
*   **Ciudad / Ubicación:** Colombia - ANTIOQUIA - MEDELLÍN
*   **Medio de Verificación (URL):** https://feibertciin.github.io/ConcursoDatosAbiertoColombiaID8/
*   **Público Objetivo:** Juvenil, Adulto, Estado (entidades gubernamentales), Empresarios y/o empresa.
*   **Tipo de Producto:** Página web
*   **Componente Digital:** Soporte web
*   **Ruta de Circulación Propuesta:** Con cobertura sobre todo el territorio nacional (alianzas estratégicas con universidades públicas y privadas, observatorios de educación superior y portales oficiales del Estado).

---

## 🎨 Enfoque Diferencial

*   **Población víctima del conflicto armado:** Sí
*   **Población en condición de discapacidad:** Ninguna
*   **Grupo étnico:** Ningún grupo étnico
*   **Sexo:** Mujer, Hombre, Intersexual
*   **Grupo etario:** Juventud (14 - 26 años), Adultez (27 - 59 años)

---

## 📝 Campos de Texto Específicos (Diligenciamiento Detallado)

### 👥 Descripción del público objetivo
El público objetivo está compuesto por tres grupos clave dentro de la educación superior colombiana:
1. **Juventud (14-26 años) y Adultez (27-59 años)**: Estudiantes matriculados e inscritos en universidades, con especial énfasis en aquellos en condiciones de vulnerabilidad socioeconómica y académica (estratos 1, 2 y 3).
2. **Directivos y Orientadores Universitarios (Empresarios/Estado)**: Profesionales de Bienestar Universitario encargados de diseñar políticas de acompañamiento, tutorías y apoyos financieros dirigidos a mitigar la deserción escolar.
3. **Entidades Gubernamentales (Estado)**: Funcionarios del Ministerio de Educación Nacional (MEN) y planeadores de política pública educativa que requieren monitorear en tiempo real las tasas de permanencia agregadas por departamentos y programas.

---

### 🖥️ Conceptualización del formato
Se seleccionó el formato de **Plataforma Web Interactiva y Dashboard Ejecutivo** debido a las siguientes razones de diseño y usabilidad:
*   **Accesibilidad y Multiplataforma**: Al ser un soporte web, elimina barreras de instalación y permite el acceso universal desde cualquier navegador en computadoras de escritorio o dispositivos móviles.
*   **Consumo Dinámico de APIs**: Permite la integración directa mediante solicitudes HTTPS con el portal nacional de **Datos Abiertos Colombia** (SODA API), garantizando datos transparentes y reales actualizados.
*   **Interactividad en Tiempo Real**: Facilita la exploración visual mediante mapas coropléticos interactivos (Leaflet.js) y gráficos ejecutivos que se recalculan dinámicamente según filtros aplicados por el usuario.

---

### 📖 Descripción del género en el que se enmarca
El desarrollo web se enmarca en el género de **Plataforma Científica de Analítica de Datos y Soporte de Decisiones (Decision Support System - DSS)**. Combina elementos informativos de una Landing Page de divulgación científica con una interfaz técnica (Dashboard) que procesa modelos de Inteligencia Artificial (Algoritmos Supervisados como XGBoost y Gradient Boosting). Su propósito no es únicamente mostrar información, sino guiar la toma de decisiones institucionales a través de analítica prescriptiva y predictiva interpretables (XAI).

---

### 🔄 ¿Cómo se integra el usuario dentro de la experiencia?
La participación activa y la experiencia del usuario se estructuran bajo un modelo híbrido de tres niveles:
1. **Nivel Informativo-Divulgativo (Landing Page)**: El usuario explora los fundamentos conceptuales de la metodología de permanencia, visualiza la arquitectura limpia del sistema (Clean Architecture) e identifica las metas del proyecto.
2. **Nivel Operativo-Predictivo (Dashboard Ejecutivo)**:
    *   **Inferencia en un Clic**: El usuario puede cargar un archivo de datos local en formato `.csv` o pegar un enlace dinámico de API gubernamental para procesar las predicciones.
    *   **Interactividad y Visualización**: Filtra geográficamente la información a través de los segmentadores y manipula el alternador dinámico de temas (Modo Claro/Oscuro) para adaptar el contraste visual.
3. **Nivel de Retroalimentación y Exportación**: El usuario descarga reportes clínicos formales en formato PDF para comités internos y cuadernos de código Jupyter (`.ipynb`) para la auditoría y replicabilidad científica de los modelos de ML.

---

### 🎨 Wireframe o esquema de página o plano de pantalla
La estructura visual y flujo del desarrollo web se compone de dos interfaces acopladas:
1. **Landing Page Pública (`landing_page/index.html`)**:
    *   *Hero Section*: Título principal, descripción del framework y botones de acción rápida.
    *   *Sección Arquitectura*: Tarjetas animadas que explican la separación de capas (Dominio, Aplicación, Infraestructura).
    *   *Sección Metodológica*: Infografía interactiva y flujo de las fases del framework.
2. **Dashboard de Datos (`Software/templates/core_app/dashboard.html`)**:
    *   *Barra Lateral Izquierda (Sidebar)*: Contiene el logotipo institucional generado con IA, las pestañas de navegación (Consola Predictiva, Métricas & Modelos, Guía & Documentos) y el conmutador de contraste.
    *   *Panel Principal*: Mapea las tarjetas de métricas agregadas. Incluye la consola de ingesta (campo de carga de archivos CSV y campo de URL de API Abierta).
    *   *Visor Geográfico e Historial*: Contiene el mapa de calor Leaflet.js de Colombia en el cuerpo central y la tabla de auditoría con botones de previsualización en línea de PDF e IPYNB en la base.

---

### 📚 Lineamientos conceptuales
El desarrollo web se sustenta en tres marcos conceptuales y metodológicos de la ciencia de datos y la educación superior:
*   **CRISP-ML(Q) (Cross-Industry Standard Process for Machine Learning)**: Proceso estándar que rige el ciclo de vida del proyecto, asegurando el control de calidad desde la comprensión del problema y los datos, el modelamiento, hasta el despliegue del software.
*   **Teoría de Deserción Universitaria (Vincent Tinto)**: Fundamento pedagógico que establece que la permanencia de un estudiante está determinada por su integración académica (promedios, materias perdidas) y su integración social/socioeconómica (ingreso familiar, estrato).
*   **Inteligencia Artificial Explicable (XAI)**: Enfoque teórico que exige que las decisiones de un modelo de caja negra (como conjuntos de árboles de decisión) sean interpretables a nivel local e institucional (mediante SHAP y LIME).

---

### 💡 Referentes creativos
Se tomaron como referentes de diseño e interacción dos plataformas líderes en el sector:
1.  **ESI Agrarias (ESI Agrarias Platform)**: Referente principal para el desarrollo de la interfaz de usuario de Django, inspirando la distribución espacial limpia, el uso de tarjetas estilizadas y la integración de visualizaciones geográficas interactivas.
2.  **Oracle Analytics Cloud & IBM Cognos Dashboard**: Referentes conceptuales para la estructuración de la consola de software. De ellos se adoptó la sobriedad en la tipografía (Inter/Outfit), el uso de indicadores clave de rendimiento (KPIs) minimalistas en bloques superiores y tablas de auditoría limpias sin elementos de distracción visual.

---

### 🔧 Características técnicas
*   **Arquitectura de Backend**: Django 5.0 y Python 3.11, implementando el mapeador objeto-relacional (ORM) integrado para la base de datos SQLite.
*   **Estilos y Maquetación**: Tailwind CSS con fuentes variables de alta legibilidad (`Outfit` e `Inter`) y Lucide Icons.
*   **Visualización Espacial**: Mapa de calor georeferenciado implementado en Javascript mediante Leaflet.js con capas de mosaicos oscuras (CartoDB DarkMatter) y claras (CartoDB Light).
*   **Motor de Inferencia**: Integración de modelos entrenados (Scikit-Learn y XGBoost) cargados en memoria mediante `joblib`.
*   **Exportación de Documentos**: Reportes PDF auto-generados dinámicamente usando ReportLab, y cuadernos Jupyter `.ipynb` estructurados y serializados dinámicamente en formato JSON.

---

### 🗺️ Estructura narrativa
El contenido y la interacción están narrados bajo un enfoque inductivo-operativo:
1.  **Introducción y Justificación (¿Por qué?)**: La Landing Page introduce al usuario en el problema de la deserción universitaria en Colombia y describe la necesidad de un framework basado en IA.
2.  **Transparencia Científica (¿Cómo?)**: El usuario puede acceder a la pestaña de "Métricas & Modelos" para comprender el desempeño del clasificador antes de realizar pruebas.
3.  **Auditoría y Ejecución (Acción)**: La consola predictiva guía al usuario para ingresar datos y visualizar los resultados agregados y geográficos.
4.  **Prescripción (Resultados)**: El sistema culmina emitiendo directrices e de intervención específicas en los reportes PDF descargables.
