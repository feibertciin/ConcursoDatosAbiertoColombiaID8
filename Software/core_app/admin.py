from django.contrib import admin
from .models import CSVUpload

@admin.register(CSVUpload)
class CSVUploadAdmin(admin.ModelAdmin):
    list_display = ('title', 'total_records', 'predicted_dropouts', 'accuracy_estimate', 'uploaded_at')
    list_filter = ('uploaded_at', 'accuracy_estimate')
    search_fields = ('title',)
    readonly_fields = ('total_records', 'predicted_dropouts', 'uploaded_at', 'pdf_report', 'notebook_file')
