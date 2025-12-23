from django.shortcuts import render, get_object_or_404
from .models import Document
from .forms import AccessForm, CaptchaForm

def access_doc(request, pk):
    doc = get_object_or_404(Document, pk=pk)
    error = None

    captcha_passed = request.session.get(f'captcha_passed_{pk}', False)

    if not captcha_passed:
        # Captcha formasi
        if request.method == 'POST':
            form = CaptchaForm(request.POST)
            if form.is_valid():
                request.session[f'captcha_passed_{pk}'] = True
                captcha_passed = True
        else:
            form = CaptchaForm()
        return render(request, 'documents/access.html', {
            'form': form,
            'captcha_passed': captcha_passed
        })

    # PIN formasi
    if request.method == 'POST':
        form = AccessForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['pin'] == doc.pin:
                return render(request, 'documents/view.html', {
                    'doc': doc,
                    'pdf_preview': doc.pdf_image.url
                })
            else:
                error = "PIN noto‘g‘ri"
    else:
        form = AccessForm()

    return render(request, 'documents/access.html', {
        'form': form,
        'captcha_passed': True,
        'error': error
    })
