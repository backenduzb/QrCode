from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='docs/')),
                ('file_qr', models.FileField(blank=True, upload_to='docs_qr/')),
                ('qr', models.ImageField(blank=True, upload_to='qr/')),
                ('pdf_image', models.ImageField(blank=True, upload_to='pdf_preview/')),
                ('pdf_image_qr', models.ImageField(blank=True, upload_to='pdf_preview_qr/')),
                ('qr_x', models.FloatField(blank=True, null=True)),
                ('qr_y', models.FloatField(blank=True, null=True)),
                ('qr_size', models.FloatField(default=0.18)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('document_code', models.CharField(max_length=256, unique=True)),
                ('ducument_son', models.IntegerField(blank=True, null=True)),
                ('ariza_berilgan', models.DateField(blank=True, null=True)),
                ('bergan_tashkilot', models.CharField(blank=True, max_length=1024, null=True)),
                ('imzolagan', models.CharField(blank=True, max_length=512, null=True)),
                ('ijrochi', models.CharField(blank=True, max_length=512, null=True)),
                ('eri_bergan', models.CharField(blank=True, max_length=512, null=True)),
                ('eri_amal_qilish_b', models.DateField(blank=True, null=True)),
                ('eri_tugash', models.DateField(blank=True, null=True)),
                ('imzolagan_h', models.CharField(blank=True, max_length=256, null=True)),
            ],
        ),
    ]
