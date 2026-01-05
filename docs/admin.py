import fitz 
from pdf2image import convert_from_path
from django.core.files.base import ContentFile
from io import BytesIO
import qrcode
import os

from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin

from .models import Document


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
        old_obj = None
        if change:
            old_obj = Document.objects.get(pk=obj.pk)

        super().save_model(request, obj, form, change)

        regenerate = False

        if not old_obj:
            regenerate = True
        else:
            if old_obj.document_code != obj.document_code:
                regenerate = True
            if old_obj.file != obj.file:
                regenerate = True

        if not regenerate:
            return

        if obj.qr:
            obj.qr.delete(save=False)

        if obj.pdf_image:
            obj.pdf_image.delete(save=False)

        url = request.build_absolute_uri(
            reverse('doc-access', args=[obj.document_code])
        ).replace("http://", "https://")

        qr_img = qrcode.make(url)
        qr_buf = BytesIO()
        qr_img.save(qr_buf, format='PNG')
        qr_content = qr_buf.getvalue()

        obj.qr.save(
            f'doc_{obj.document_code}.png',
            ContentFile(qr_content),
            save=False
        )

        if obj.file:
            pdf_path = obj.file.path

            try:
                doc = fitz.open(pdf_path)

                temp_pdf_path = pdf_path.replace('.pdf', '_temp.pdf')
                page = doc[0]

                w, h = page.rect.width, page.rect.height
                qr_size = 110

                rect = fitz.Rect(
                    (w - qr_size) / 1.9,
                    h - qr_size - 5,
                    (w + qr_size) / 1.9,
                    h - 5
                )

                page.insert_image(rect, stream=qr_content)

                doc.save(temp_pdf_path, deflate=True)
                doc.close()

                os.replace(temp_pdf_path, pdf_path)

            except Exception as e:
                print("PDF ga QR qo‘shishda xatolik:", e)

            try:
                pages = convert_from_path(pdf_path, dpi=150)
                if pages:
                    img_buf = BytesIO()
                    pages[0].save(img_buf, format='PNG')

                    obj.pdf_image.save(
                        f'doc_{obj.document_code}_preview.png',
                        ContentFile(img_buf.getvalue()),
                        save=False
                    )
            except Exception as e:
                print("Preview yaratishda xatolik:", e)

        obj.save(update_fields=['qr', 'pdf_image'])
