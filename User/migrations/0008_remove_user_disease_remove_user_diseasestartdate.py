# Generated by Django 5.1.1 on 2024-09-30 22:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("User", "0007_disease"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="disease",
        ),
        migrations.RemoveField(
            model_name="user",
            name="diseaseStartDate",
        ),
    ]
