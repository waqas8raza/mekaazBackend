# Generated by Django 5.1.1 on 2024-10-02 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("User", "0008_remove_user_disease_remove_user_diseasestartdate"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="relationWithPatient",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
