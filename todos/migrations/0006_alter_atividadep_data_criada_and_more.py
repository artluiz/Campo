# Generated by Django 4.2.9 on 2024-02-14 09:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("todos", "0005_rename_totalarea_fichacampo_totalarea_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="atividadep",
            name="data_criada",
            field=models.DateTimeField(verbose_name="Data de criação"),
        ),
        migrations.AlterField(
            model_name="fichacampo",
            name="data_criada",
            field=models.DateTimeField(verbose_name="Data de criação"),
        ),
        migrations.AlterField(
            model_name="plantio",
            name="data_criada",
            field=models.DateTimeField(verbose_name="Data de criação"),
        ),
        migrations.AlterField(
            model_name="produtos",
            name="data_criada",
            field=models.DateTimeField(verbose_name="Data de criação"),
        ),
    ]
