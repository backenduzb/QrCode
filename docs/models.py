import random
from django.db import models

def gen_pin():
    return f"{random.randint(0, 999999):06d}"

class Document(models.Model):
    file = models.FileField(upload_to='docs/')
    pin = models.CharField(max_length=6, default=gen_pin, editable=False)
    qr = models.ImageField(upload_to='qr/', blank=True)
    pdf_image = models.ImageField(upload_to='pdf_preview/', blank=True) 
    created = models.DateTimeField(auto_now_add=True)
    document_code = models.CharField(max_length=10, null=False, blank=True)
    ducument_son = models.IntegerField(null=True, blank=True)
    ariza_berilgan = models.DateField(null=True, blank=True)
    bergan_tashkilot = models.CharField(max_length=1024, null=True, blank=True)
    imzolagan = models.CharField(max_length=512, null=True, blank=True)
    ijrochi = models.CharField(max_length=512, null=True, blank=True)
    eri_bergan = models.CharField(max_length=512, null=True, blank=True)
    eri_amal_qilish_b = models.DateField(null=True, blank=True)
    eri_tugash = models.DateField(null=True, blank=True)
    imzolagan_h = models.CharField(max_length=256, null=True, blank=True)
    def __str__(self):
        return f"Doc #{self.id}"

