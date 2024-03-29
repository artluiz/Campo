# Generated by Django 4.2.9 on 2024-02-08 12:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("todos", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AtividadeP",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "data_criada",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de criação"
                    ),
                ),
                (
                    "data_atualizado",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Data da aplicação"
                    ),
                ),
                ("nome", models.CharField(max_length=10, verbose_name="Atividade")),
                ("ativo", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Plantio",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "data_criada",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Data de criação"
                    ),
                ),
                (
                    "data_atualizado",
                    models.DateTimeField(
                        auto_now=True, verbose_name="Data da aplicação"
                    ),
                ),
                ("nome_pl", models.CharField(max_length=50, verbose_name="Plantio")),
                ("cultura", models.CharField(max_length=50, verbose_name="Cultura")),
                ("pivo", models.CharField(max_length=10, verbose_name="Pivo")),
                (
                    "area",
                    models.DecimalField(
                        decimal_places=4, max_digits=8, verbose_name="Área"
                    ),
                ),
                ("fazenda", models.CharField(max_length=50, verbose_name="fazenda")),
                ("ativo", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="TipoAplicacao",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nome_tipo",
                    models.CharField(max_length=50, verbose_name="Irrigador"),
                ),
                ("ativo", models.BooleanField(default=True)),
            ],
        ),
    ]
