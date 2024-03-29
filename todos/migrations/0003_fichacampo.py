# Generated by Django 4.2.9 on 2024-02-08 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("todos", "0002_atividadep_plantio_tipoaplicacao"),
    ]

    operations = [
        migrations.CreateModel(
            name="FichaCampo",
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
                    models.DateField(
                        auto_now=True, null=True, verbose_name="Data de modificação"
                    ),
                ),
                ("data_aplicada", models.DateField(verbose_name="Data aplicação")),
                ("volume", models.IntegerField(verbose_name="Volume")),
                ("totalArea", models.FloatField(null=True, verbose_name="totalArea")),
                (
                    "totalAreaAp",
                    models.FloatField(null=True, verbose_name="totalAreaAp"),
                ),
                ("totalCalda", models.FloatField(null=True, verbose_name="totalCalda")),
                ("tqn1", models.FloatField(null=True, verbose_name="tqn1")),
                ("tqn2", models.FloatField(null=True, verbose_name="tqn2")),
                ("tqn3", models.FloatField(null=True, verbose_name="tqn3")),
                ("capacidade", models.IntegerField(verbose_name="Capacidade")),
                ("plantio", models.JSONField()),
                ("dados", models.JSONField()),
                ("obs", models.TextField(blank=True, null=True)),
                ("pendente", models.BooleanField(default=False)),
                ("ativo", models.BooleanField(default=True)),
                (
                    "atividade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="todos.atividadep",
                    ),
                ),
                (
                    "tipo_aplicacao",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="todos.tipoaplicacao",
                    ),
                ),
            ],
        ),
    ]
