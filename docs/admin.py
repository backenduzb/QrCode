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
        'file', 'qr_preview', 'pdf_preview', 'document_code', 'ducument_son',
        'ariza_berilgan', 'bergan_tashkilot', 'imzolagan', 'ijrochi',
        'eri_bergan', 'eri_amal_qilish_b', 'eri_tugash', 'imzolagan_h'
    )

    def qr_preview(self, obj):
        if obj.qr:
            return format_html(
                '<img src="{}" style="max-width:200px;border:1px solid #ccc;">',
                obj.qr.url
            )
        return "QR yo‘q"

    def pdf_preview(self, obj):
        if obj.pdf_image:
            return format_html(
                '<img src="{}" style="max-width:200px;border:1px solid #ccc;">',
                obj.pdf_image.url
            )
        return "PDF rasm yo‘q"

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # 🔁 Agar QR allaqachon bor bo‘lsa, qayta qo‘shmaymiz
        if obj.qr and obj.pdf_image:
            return

        # 1. QR yaratish
        url = request.build_absolute_uri(
            reverse('doc-access', args=[obj.id])
        )

        qr_img = qrcode.make(url)
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format='PNG')
        qr_buf.seek(0)

        obj.qr.save(
            f'doc_{obj.id}.png',
            ContentFile(qr_buf.getvalue()),
            save=False
        )

        # 2. PDFga QR joylashtirish
        if obj.file:
            pdf_path = obj.file.path
            doc = fitz.open(pdf_path)
            page = doc[0]

            w, h = page.rect.width, page.rect.height
            qr_size = 120

            rect = fitz.Rect(
                (w - qr_size) / 2,
                h - qr_size - 40,
                (w + qr_size) / 2,
                h - 40
            )

            page.insert_image(rect, stream=qr_buf.getvalue())

            doc.save(pdf_path, incremental=True, deflate=True)
            doc.close()

            # 3. Preview rasm
            pages = convert_from_path(pdf_path, dpi=150)
            img_buf = BytesIO()
            pages[0].save(img_buf, format='PNG')

            obj.pdf_image.save(
                f'doc_{obj.id}_preview.png',
                ContentFile(img_buf.getvalue()),
                save=False
            )

        # ❗ oxirgi save — faqat bir marta
        obj.save(update_fields=['qr', 'pdf_image'])
