from pdf2image import convert_from_path
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode
from django.urls import reverse
from django.utils.html import format_html
from .models import Document
from django.contrib import admin

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    readonly_fields = ('qr_preview', 'pdf_preview')
    fields = ('file', 'qr_preview', 'pdf_preview','document_code', 'ducument_son', 'ariza_berilgan',
              'bergan_tashkilot','imzolagan','ijrochi','eri_bergan','eri_amal_qilish_b','eri_tugash','imzolagan_h')

    def qr_preview(self, obj):
        if obj.qr:
            return format_html(
                '<img src="{}" style="max-width:200px; border:1px solid #ccc;" />',
                obj.qr.url
            )
        return "QR yo‘q"
    qr_preview.short_description = "QR kod"

    def pdf_preview(self, obj):
        if obj.pdf_image:
            return format_html(
                '<img src="{}" style="max-width:200px; border:1px solid #ccc;" />',
                obj.pdf_image.url
            )
        return "PDF rasm yo‘q"
    pdf_preview.short_description = "PDF Preview"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        url = request.build_absolute_uri(reverse('doc-access', args=[obj.id]))
        img = qrcode.make(url)
        buf = BytesIO()
        img.save(buf, format='PNG')
        obj.qr.save(f'doc_{obj.id}.png', ContentFile(buf.getvalue()), save=False)

        if obj.file:
            pages = convert_from_path(obj.file.path, dpi=150)  
            first_page = pages[0]
            buf_pdf = BytesIO()
            first_page.save(buf_pdf, format='PNG')
            obj.pdf_image.save(f'doc_{obj.id}_preview.png', ContentFile(buf_pdf.getvalue()), save=False)

        obj.save()
