# Generated by Django 2.1.15 on 2020-09-13 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('loja', '0002_auto_20200913_0912'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pedidocliente',
            name='numero_confimacao',
            field=models.IntegerField(blank=True),
        ),
    ]
