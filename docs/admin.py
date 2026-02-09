import fitz
from pdf2image import convert_from_path
from django.core.files.base import ContentFile
from django.core.files import File
from io import BytesIO
import qrcode
import os
import tempfile

from django.urls import reverse
from django.utils.html import format_html
from django.contrib import admin
from django import forms

from .models import Document


class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = '__all__'
        widgets = {
            'qr_x': forms.HiddenInput(),
            'qr_y': forms.HiddenInput(),
            'qr_size': forms.HiddenInput(),
        }


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    form = DocumentAdminForm
    readonly_fields = ('qr_position_preview',)
    fields = (
        'file', 'document_code', 'ducument_son',
        'ariza_berilgan', 'bergan_tashkilot', 'imzolagan', 'ijrochi',
        'eri_bergan', 'eri_amal_qilish_b', 'eri_tugash', 'imzolagan_h',
        'qr_position_preview', 'qr_x', 'qr_y', 'qr_size'
    )

    def qr_position_preview(self, obj):
        if not obj.pk:
            return "Hujjatni avval saqlang."
        if not obj.pdf_image:
            return "PDF rasm yo‘q. Faylni saqlab, qayta oching."
        if not obj.qr:
            return "QR rasm yo‘q."

        return format_html(
            (
                '<div class="qr-placement unset">'
                '  <div class="qr-toolbar">'
                '    <label class="qr-scale">'
                '      <span>QR size</span>'
                '      <input type="range" min="0.05" max="0.60" step="0.01" value="{}" class="qr-scale-input">'
                '      <span class="qr-scale-value"></span>'
                '    </label>'
                '  </div>'
                '  <img class="qr-placement-pdf" src="{}" alt="PDF preview">'
                '  <img class="qr-placement-qr" src="{}" alt="QR">'
                '  <div class="qr-placement-help">'
                '    QR joylashuvini tanlash: PDF ustiga bosing yoki QR ni sudrang. Slider bilan kattaligini o‘zgartiring.'
                '  </div>'
                '</div>'
            ),
            (obj.qr_size or 0.18),
            obj.pdf_image.url,
            obj.qr.url
        )


    qr_position_preview.short_description = "QR joylashuvi"

    class Media:
        css = {
            'all': ('documents/admin/qr_placement.css',)
        }
        js = ('documents/admin/qr_placement.js',)

    def save_model(self, request, obj, form, change):
        old_obj = None
        if change:
            old_obj = Document.objects.get(pk=obj.pk)

        super().save_model(request, obj, form, change)

        file_changed = not old_obj or old_obj.file != obj.file
        code_changed = not old_obj or old_obj.document_code != obj.document_code
        position_changed = not old_obj or (
            old_obj.qr_x != obj.qr_x or
            old_obj.qr_y != obj.qr_y or
            old_obj.qr_size != obj.qr_size
        )

        update_fields = []
        qr_content = None

        if code_changed or not obj.qr:
            if obj.qr:
                obj.qr.delete(save=False)

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
            update_fields.append('qr')
        else:
            try:
                obj.qr.open('rb')
                qr_content = obj.qr.read()
            except Exception:
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
                update_fields.append('qr')
            finally:
                try:
                    obj.qr.close()
                except Exception:
                    pass

        if obj.file and (file_changed or not obj.pdf_image):
            if obj.pdf_image:
                obj.pdf_image.delete(save=False)
            try:
                pages = convert_from_path(obj.file.path, dpi=150)
                if pages:
                    img_buf = BytesIO()
                    pages[0].save(img_buf, format='PNG')
                    obj.pdf_image.save(
                        f'doc_{obj.document_code}_preview.png',
                        ContentFile(img_buf.getvalue()),
                        save=False
                    )
                    update_fields.append('pdf_image')
            except Exception as e:
                print("Preview yaratishda xatolik:", e)

        has_position = (
            obj.qr_x is not None and
            obj.qr_y is not None and
            obj.qr_size is not None and
            float(obj.qr_size) > 0
        )


        if not has_position and (file_changed or code_changed):
            if obj.file_qr:
                obj.file_qr.delete(save=False)
                update_fields.append('file_qr')
            if obj.pdf_image_qr:
                obj.pdf_image_qr.delete(save=False)
                update_fields.append('pdf_image_qr')

        if obj.file and qr_content and has_position and (file_changed or code_changed or position_changed):
            if obj.file_qr:
                obj.file_qr.delete(save=False)
                update_fields.append('file_qr')
            if obj.pdf_image_qr:
                obj.pdf_image_qr.delete(save=False)
                update_fields.append('pdf_image_qr')

            try:
                pdf_path = obj.file.path
                doc = fitz.open(pdf_path)
                page = doc[0]

                w, h = page.rect.width, page.rect.height
                size = obj.qr_size * w
                size = max(1.0, min(size, w, h))

                cx = max(0.0, min(float(obj.qr_x), 1.0)) * w
                cy = max(0.0, min(float(obj.qr_y), 1.0)) * h

                x = cx - size / 2
                y = cy - size / 2

                x = max(0.0, min(x, w - size))
                y = max(0.0, min(y, h - size))

                rect = fitz.Rect(x, y, x + size, y + size)

                page.insert_image(rect, stream=qr_content)

                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    temp_pdf_path = tmp.name

                doc.save(temp_pdf_path, deflate=True)
                doc.close()

                with open(temp_pdf_path, 'rb') as processed_file:
                    obj.file_qr.save(
                        f'doc_{obj.document_code}.pdf',
                        File(processed_file),
                        save=False
                    )
                update_fields.append('file_qr')


                try:
                    pages = convert_from_path(temp_pdf_path, dpi=150)
                    if pages:
                        img_buf = BytesIO()
                        pages[0].save(img_buf, format='PNG')
                        obj.pdf_image_qr.save(
                            f'doc_{obj.document_code}_preview_qr.png',
                            ContentFile(img_buf.getvalue()),
                            save=False
                        )
                        update_fields.append('pdf_image_qr')
                except Exception as e:
                    print("QR preview yaratishda xatolik:", e)

                os.remove(temp_pdf_path)

            except Exception as e:
                print("PDF ga QR qo‘shishda xatolik:", e)

        if update_fields:
            obj.save(update_fields=list(dict.fromkeys(update_fields)))
