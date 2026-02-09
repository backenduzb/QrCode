from django.shortcuts import render, get_object_or_404, redirect
from .models import Document
from .forms import CaptchaForm
from django.conf import settings
from .utils import create_data

def access_doc(request, pk):
    doc = get_object_or_404(Document, document_code=pk)
    error = None

    session_key = f'captcha_passed_{pk}'
    captcha_passed = request.session.get(session_key, False)

    if not captcha_passed:
        if request.method == 'POST':
            form = CaptchaForm(request.POST)
            if form.is_valid():
                ariza_berilgan = create_data(doc.ariza_berilgan)
                eri_amal_qilish_b = create_data(doc.eri_amal_qilish_b)
                eri_tugash = create_data(doc.eri_tugash)
                request.session[session_key] = True
                request.session.pop(session_key, None)
                return render(request, 'documents/view.html', {
                    'doc': doc,
                    'pdf_preview': doc.pdf_image.url,
                    'tugash': eri_tugash,
                    'boshlash': eri_amal_qilish_b,
                    'ariza_berilgan': ariza_berilgan,
                })  
        return render(request, 'documents/access.html', {
            'captcha_passed': False,
            'captcha': settings.RECAPTCHA_PUBLIC_KEY
        })
    return render(request, 'documents/access.html', {
        'captcha_passed': True,
        'error': error
    })
