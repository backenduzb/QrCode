from django.shortcuts import render, get_object_or_404
from django.conf import settings
from .models import Document
from .forms import CaptchaForm
from .utils import create_data

def access_doc(request, code):
    doc = get_object_or_404(Document, document_code=code)

    session_key = f"captcha_passed_{code}"
    captcha_passed = request.session.get(session_key, False)

    if not captcha_passed:
        if request.method == "POST":
            form = CaptchaForm(request.POST)
            if form.is_valid():
                request.session[session_key] = True
                captcha_passed = True
        else:
            form = CaptchaForm()

    if captcha_passed:
        ariza_berilgan = create_data(doc.ariza_berilgan) if doc.ariza_berilgan else None
        boshlash = create_data(doc.eri_amal_qilish_b) if doc.eri_amal_qilish_b else None
        tugash = create_data(doc.eri_tugash) if doc.eri_tugash else None

        pdf_preview = (doc.pdf_image_qr.url if doc.pdf_image_qr else (doc.pdf_image.url if doc.pdf_image else None))
        download_url = (doc.file_qr.url if doc.file_qr else doc.file.url)

        return render(request, "documents/view.html", {
            "doc": doc,
            "pdf_preview": pdf_preview,
            "download_url": download_url,
            "tugash": tugash,
            "boshlash": boshlash,
            "ariza_berilgan": ariza_berilgan,
        })

    return render(request, "documents/access.html", {
        "captcha_passed": False,
        "captcha": settings.RECAPTCHA_PUBLIC_KEY,
        "form": form,
    })
