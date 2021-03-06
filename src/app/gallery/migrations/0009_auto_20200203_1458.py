# Generated by Django 3.0.3 on 2020-02-03 14:58

import app.gallery.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0008_auto_20200202_2130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gallery',
            name='name',
            field=models.CharField(help_text='Name of the gallery. Must be unique.', max_length=1024, unique=True, validators=[app.gallery.models.validate_gallery_name], verbose_name='Name'),
        ),
    ]
