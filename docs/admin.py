import fitz  # PyMuPDF
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
    fields = (
        'file', 'qr_preview', 'pdf_preview','document_code', 'ducument_son',
        'ariza_berilgan','bergan_tashkilot','imzolagan','ijrochi',
        'eri_bergan','eri_amal_qilish_b','eri_tugash','imzolagan_h'
    )

    def qr_preview(self, obj):
        if obj.qr:
            return format_html(
                '<img src="{}" style="max-width:200px; border:1px solid #ccc;" />',
                obj.qr.url
            )
        return "QR yo‘q"

    def pdf_preview(self, obj):
        if obj.pdf_image:
            return format_html(
                '<img src="{}" style="max-width:200px; border:1px solid #ccc;" />',
                obj.pdf_image.url
            )
        return "PDF rasm yo‘q"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 1. QR kodni generatsiya qilish
        url = request.build_absolute_uri(reverse('doc-access', args=[obj.id]))
        qr_img = qrcode.make(url)
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format='PNG')

        obj.qr.save(f'doc_{obj.id}.png', ContentFile(qr_buf.getvalue()), save=False)

        # 2. QRni PDFning pastki o‘rtasiga joylashtirish
        if obj.file:
            pdf_path = obj.file.path
            doc = fitz.open(pdf_path)

            page = doc[0]  # 1-sahifa
            qr_pix = fitz.Pixmap(qr_buf.getvalue())

            # QRni joylash koordinatasi
            width = page.rect.width
            height = page.rect.height

            qr_size = 120  # px
            x = (width - qr_size) / 2  
            y = height - qr_size - 40     # pastdan 40px tepa tomonga

            rect = fitz.Rect(x, y, x + qr_size, y + qr_size)

            page.insert_image(rect, stream=qr_buf.getvalue())

            # PDFni qayta yozish
            doc.save(pdf_path, deflate=True)
            doc.close()

            # 3. PDF preview — 1 sahifadan rasm olish
            pages = convert_from_path(pdf_path, dpi=150)
            first_page = pages[0]
            buf_pdf_img = BytesIO()
            first_page.save(buf_pdf_img, format='PNG')

            obj.pdf_image.save(
                f'doc_{obj.id}_preview.png',
                ContentFile(buf_pdf_img.getvalue()),
                save=False
            )

        obj.save()
