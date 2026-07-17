from django.db import models

class CSVUpload(models.Model):
    title = models.CharField("Título de la Carga", max_length=150)
    csv_file = models.FileField("Archivo CSV", upload_to='csv_uploads/')
    pdf_report = models.FileField("Reporte Clínico PDF", upload_to='pdf_reports/', null=True, blank=True)
    notebook_file = models.FileField("Cuaderno Jupyter .ipynb", upload_to='notebooks/', null=True, blank=True)
    
    total_records = models.IntegerField("Registros Totales", default=0)
    predicted_dropouts = models.IntegerField("Desertores Predichos", default=0)
    accuracy_estimate = models.FloatField("Estimación de Exactitud (%)", default=96.36)
    
    uploaded_at = models.DateTimeField("Fecha de Carga", auto_now_add=True)

    class Meta:
        verbose_name = "Carga de CSV Predictiva"
        verbose_name_plural = "Cargas de CSV Predictivas"
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.title} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
