# Generated by Django 4.2.13 on 2024-06-06 21:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Matma', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mathformula',
            name='formula',
            field=models.TextField(help_text='Comma-separated formulas'),
        ),
    ]
