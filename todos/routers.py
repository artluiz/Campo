from django.db import connections, models
from .models import Plantio, AtividadeP, Produtos, FichaCampo
from django.core.management import call_command
from .models import FichaCampo
from django.utils.timezone import make_aware
from django.utils import timezone
import pytz
import json
from datetime import datetime, date
from django.http import JsonResponse


class ModificarProdutoRouter:
    @staticmethod
    def modificar_produto(dados):
        dados_modificados = []

        # Iterar sobre os dados e modificar o campo 'produto' conforme especificado
        for item in dados:
            if "produto" in item:
                produto = (
                    item["produto"]
                    .replace("i", "")
                    .replace("l", "")
                    .replace(" ", "")
                    .replace("a", "")
                    .strip()[-5:]
                )
                item["produto"] = produto
            dados_modificados.append(item)

        return dados_modificados

    @classmethod
    def modificar_produtos(cls):
        try:
            # Obter todas as fichas do banco de dados
            fichas = FichaCampo.objects.all()

            # Modificar o campo 'produto' de todas as fichas
            for ficha in fichas:
                ficha.dados = cls.modificar_produto(ficha.dados)
                ficha.save()

            return JsonResponse(
                {
                    "success": True,
                    "message": "Dados atualizados com sucesso para todas as fichas.",
                }
            )
        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


class FichaCampoRouter:

    def db_for_read(self, model, **hints):
        if model == FichaCampo:
            return "default"
        return None


class DatabaseSynchronizer:
    @staticmethod
    def sync_db():
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT * FROM todos_fichacampo ORDER BY id;")
            rows = cursor.fetchall()

        with connections["secondary"].cursor() as cursor:
            latest_date_in_database = FichaCampo.objects.using(
                "secondary"
            ).aggregate(models.Max("data_criada"))["data_criada__max"]
            if latest_date_in_database:
                latest_date_in_database = latest_date_in_database
                timezone1 = latest_date_in_database.tzinfo
            for row in rows:
                ficha_data_criada = row[18]
                ficha_data_atualizado = datetime.combine(row[1], datetime.min.time())
                if (
                    not latest_date_in_database
                    or ficha_data_criada > latest_date_in_database
                ):
                    data_aplicada = datetime.combine(row[2], datetime.min.time())
                    volume = row[3] if row[3] is not None else 0
                    tqn1 = row[4] if row[4] is not None else 0.0
                    tqn2 = row[5] if row[5] is not None else 0.0
                    tqn3 = row[6] if row[6] is not None else 0.0
                    capacidade = row[7] if row[7] is not None else 0
                    plantio = json.loads(row[8] if row[8] is not None else {})
                    dados = json.loads(row[9] if row[9] is not None else {})
                    obs = row[10] if row[10] is not None else ""
                    pendente = row[11] if row[11] is not None else False
                    ativo = row[12] if row[12] is not None else False
                    atividade = row[13] if row[13] is not None else 0
                    tipo_aplicação = row[14] if row[14] is not None else 0
                    totalArea = row[15] if row[15] is not None else 0.0
                    totalAreaAp = row[16] if row[16] is not None else 0.0
                    totalCalda = row[17] if row[17] is not None else 0.0

                    FichaCampo.objects.using("secondary").create(
                        data_criada=ficha_data_criada,
                        data_atualizado=ficha_data_atualizado,
                        totalarea=totalArea,
                        totalareaap=totalAreaAp,
                        totalcalda=totalCalda,
                        tqn1=tqn1,
                        tqn2=tqn2,
                        tqn3=tqn3,
                        dados=dados,
                        plantio=plantio,
                        capacidade=capacidade,
                        data_aplicada=data_aplicada,
                        atividade_id=atividade,
                        volume=volume,
                        tipo_aplicacao_id=tipo_aplicação,
                        ativo=ativo,
                        pendente=pendente,
                        obs=obs,
                    )
            for row in rows:
                id_default = row[0]
                data_atualizacao_default = row[1]

                cursor.execute(
                    "SELECT * FROM todos_fichacampo WHERE id = %s", [id_default]
                )
                row_secondary = cursor.fetchone()

                if row_secondary:
                    data_atualizacao_secondary = row_secondary[2]

                    data_atualizacao_default = data_atualizacao_default
                    timezone1 = data_atualizacao_default.tzinfo
                    data_atualizacao_secondary = data_atualizacao_secondary.replace(
                        tzinfo=timezone1
                    )

                    if data_atualizacao_default > data_atualizacao_secondary:
                        dados_jsonb = json.dumps(row[8]) if row[8] is not None else None
                        dados_jsonb = json.loads(dados_jsonb)
                        dados_jsonb_plantio = json.dumps(row[9]) if row[9] is not None else None
                        dados_jsonb_plantio = json.loads(dados_jsonb_plantio)
                        dados_jsonb_obs = json.dumps(row[10]) if row[10] is not None else None
                        dados_jsonb_obs = json.loads(dados_jsonb_obs)
                        cursor.execute(
                            "UPDATE todos_fichacampo SET "
                            "data_criada = %s, "
                            "data_atualizado = %s, "
                            "data_aplicada = %s, "
                            "volume = %s, "
                            "tqn1 = %s, "
                            "tqn2 = %s, "
                            "tqn3 = %s, "
                            "capacidade = %s, "
                            "plantio = %s, "
                            "dados = %s, "
                            "obs = %s, "
                            "pendente = %s, "
                            "ativo = %s, "
                            "atividade_id = %s, "
                            "tipo_aplicacao_id = %s1 "
                            "totalarea = %s, "
                            "totalareaap = %s, "
                            "totalcalda = %s "
                            "WHERE id = %s",
                            [
                                row[18],
                                row[1],
                                datetime.combine(row[2], datetime.min.time()),
                                row[3],
                                row[4],
                                row[5],
                                row[6],
                                row[7],
                                row[8],
                                row[9],
                                row[10],
                                dados_jsonb_plantio,
                                dados_jsonb,
                                dados_jsonb_obs,
                                row[14],
                                row[15],
                                row[16],
                                row[17],
                                id_default,
                            ],
                        )

    #########################################################################################################

    @staticmethod
    def sync_db_produto():
        with connections["default"].cursor() as cursor_default:
            cursor_default.execute("SELECT * FROM todos_produtos")
            rows = cursor_default.fetchall()

        with connections["secondary"].cursor() as cursor:
            cursor.execute("SELECT codigo FROM todos_produtos")
            existing_product_codes = {row[0] for row in cursor.fetchall()}

            if not existing_product_codes:
                existing_product_codes = set()

            for row in rows:
                product_code = row[3]
                if product_code not in existing_product_codes:
                    produto = row[2] if row[2] is not None else 0
                    codigo = row[3] if row[3] is not None else ""
                    descricao = row[4] if row[4] is not None else ""
                    ativo = row[5] if row[5] is not None else 0
                    Produtos.objects.using("secondary").create(
                        data_criada=row[6],
                        data_atualizado=row[1],
                        codigo=codigo,
                        descricao=descricao,
                        ativo=ativo,
                        produto=produto,
                    )
            for row in rows:
                cod_default = row[3]
                data_atualizacao_default = row[1]

                cursor.execute(
                    "SELECT * FROM todos_produtos WHERE id = %s", [cod_default]
                )
                row_secondary = cursor.fetchone()

                if row_secondary:
                    data_atualizacao_secondary = row_secondary[5]

                    data_atualizacao_default = data_atualizacao_default
                    timezone1 = data_atualizacao_default.tzinfo
                    data_atualizacao_secondary = data_atualizacao_secondary.replace(
                        tzinfo=timezone1
                    )

                    if data_atualizacao_default > data_atualizacao_secondary:
                        cursor.execute(
                            "UPDATE todos_produtos SET "
                            "data_criada = %s, "
                            "data_atualizado = %s, "
                            "produto = %s, "
                            "codigo = %s, "
                            "descricao = %s, "
                            "ativo = %s "
                            "WHERE codigo = %s",
                            [
                                datetime.combine(row[1], datetime.min.time()),
                                datetime.combine(row[2], datetime.min.time()),
                                row[3],
                                row[4],
                                row[5],
                                row[6],
                                cod_default,
                            ],
                        )

    #########################################################################################################

    @staticmethod
    def sync_db_plantio():
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT * FROM todos_plantio ORDER BY id;")
            rows = cursor.fetchall()

        with connections["secondary"].cursor() as cursor:
            latest_date_in_database = Plantio.objects.using("secondary").aggregate(
                models.Max("data_criada")
            )["data_criada__max"]
            if latest_date_in_database:
                latest_date_in_database = latest_date_in_database
                timezone1 = latest_date_in_database.tzinfo
            for row in rows:
                ficha_data_criada = row[8].replace(tzinfo=timezone1)

                if (
                    not latest_date_in_database
                    or ficha_data_criada > latest_date_in_database
                ):
                    nome_pl = row[2] if row[2] is not None else ""
                    cultura = row[3] if row[3] is not None else ""
                    pivo = row[4] if row[4] is not None else ""
                    area = row[5] if row[5] is not None else 0.0
                    fazenda = row[6] if row[6] is not None else ""
                    ativo = row[7] if row[7] is not None else True

                    Plantio.objects.using("secondary").create(
                        data_criada=ficha_data_criada,
                        data_atualizado=row[1],
                        nome_pl=nome_pl,
                        cultura=cultura,
                        pivo=pivo,
                        area=area,
                        fazenda=fazenda,
                        ativo=ativo,
                    )
            for row in rows:
                id_default = row[0]
                data_atualizacao_default = row[1]

                cursor.execute("SELECT * FROM todos_plantio WHERE id = %s", [id_default])
                row_secondary = cursor.fetchone()

                if row_secondary:
                    data_atualizacao_secondary = row_secondary[2]

                    data_atualizacao_default = data_atualizacao_default
                    timezone1 = data_atualizacao_default.tzinfo
                    data_atualizacao_secondary = data_atualizacao_secondary.replace(
                        tzinfo=timezone1
                    )

                    if data_atualizacao_default > data_atualizacao_secondary:
                        cursor.execute(
                            "UPDATE todos_plantio SET "
                            "data_atualizado = %s, "
                            "nome_pl = %s, "
                            "cultura = %s, "
                            "pivo = %s, "
                            "area = %s, "
                            "fazenda = %s, "
                            "ativo = %s, "
                            "data_criada = %s "
                            "WHERE id = %s",
                            [
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                                row[5],
                                row[6],
                                row[7],
                                row[8],
                                id_default,
                            ],
                        )

    #########################################################################################################

    @staticmethod
    def sync_db_atividade():
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT * FROM todos_atividadep ORDER BY id;")
            rows = cursor.fetchall()

        with connections["secondary"].cursor() as cursor:
            latest_date_in_database = AtividadeP.objects.using("secondary").aggregate(
                models.Max("data_criada")
            )["data_criada__max"]
            if latest_date_in_database:
                latest_date_in_database = latest_date_in_database
                timezone1 = latest_date_in_database.tzinfo
            for row in rows:
                ficha_data_criada = row[4]

                if (
                    not latest_date_in_database
                    or ficha_data_criada > latest_date_in_database
                ):
                    nome = row[2] if row[2] is not None else ""
                    ativo = row[3] if row[3] is not None else True

                    AtividadeP.objects.using("secondary").create(
                        data_criada=ficha_data_criada,
                        data_atualizado=row[1],
                        nome=nome,
                        ativo=ativo,
                    )
            for row in rows:
                id_default = row[0]
                data_atualizacao_default = row[1]

                cursor.execute(
                    "SELECT * FROM todos_atividadep WHERE id = %s", [id_default]
                )
                row_secondary = cursor.fetchone()

                if row_secondary:
                    data_atualizacao_secondary = row_secondary[2]

                    data_atualizacao_default = data_atualizacao_default
                    timezone1 = data_atualizacao_default.tzinfo
                    data_atualizacao_secondary = data_atualizacao_secondary.replace(
                        tzinfo=timezone1
                    )

                    if data_atualizacao_default > data_atualizacao_secondary:
                        cursor.execute(
                            "UPDATE todos_atividadep SET "
                            "data_atualizado = %s, "
                            "nome = %s, "
                            "ativo = %s, "
                            "data_criada = %s "
                            "WHERE id = %s",
                            [
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                                id_default,
                            ],
                        )


#########################################################################################################


class DatabaseDownloader:
    @staticmethod
    def sync_db():
        with connections["secondary"].cursor() as cursor:
            cursor.execute("SELECT * FROM todos_fichacampo ORDER BY id;")
            rows = cursor.fetchall()

        with connections["default"].cursor() as cursor:
            latest_date_in_database = FichaCampo.objects.using(
                "default"
            ).aggregate(models.Max("data_criada"))["data_criada__max"]
            if latest_date_in_database:
                latest_date_in_database = latest_date_in_database
                print(latest_date_in_database)
                timezone1 = latest_date_in_database.tzinfo
            for row in rows:
                ficha_data_criada = row[1].replace(tzinfo=timezone1)
                print(ficha_data_criada)
                ficha_data_atualizado = datetime.combine(row[2], datetime.min.time())
                if (
                    not latest_date_in_database
                    or ficha_data_criada > latest_date_in_database
                ):
                    data_aplicada = datetime.combine(row[3], datetime.min.time())
                    volume = row[4] if row[4] is not None else 0
                    totalArea = row[5] if row[5] is not None else 0.0
                    totalAreaAp = row[6] if row[6] is not None else 0.0
                    totalCalda = row[7] if row[7] is not None else 0.0
                    tqn1 = row[8] if row[8] is not None else 0.0
                    tqn2 = row[9] if row[9] is not None else 0.0
                    tqn3 = row[10] if row[10] is not None else 0.0
                    capacidade = row[11] if row[11] is not None else 0
                    plantio = json.loads(row[12] if row[12] is not None else {})
                    dados = json.loads(row[13] if row[13] is not None else {})
                    obs = row[14] if row[14] is not None else ""
                    pendente = row[15] if row[15] is not None else False
                    ativo = row[16] if row[16] is not None else False
                    atividade = row[17] if row[17] is not None else 0
                    tipo_aplicação = row[18] if row[18] is not None else 0

                    FichaCampo.objects.using("default").create(
                        data_criada=ficha_data_criada,
                        data_atualizado=ficha_data_atualizado,
                        totalarea=totalArea,
                        totalareaap=totalAreaAp,
                        totalcalda=totalCalda,
                        tqn1=tqn1,
                        tqn2=tqn2,
                        tqn3=tqn3,
                        dados=dados,
                        plantio=plantio,
                        capacidade=capacidade,
                        data_aplicada=data_aplicada,
                        atividade_id=atividade,
                        volume=volume,
                        tipo_aplicacao_id=tipo_aplicação,
                        ativo=ativo,
                        pendente=pendente,
                        obs=obs,
                    )

            for row in rows:
                id_secondary = row[0]
                data_atualizacao_secondary = row[2]

                cursor.execute(
                    "SELECT * FROM todos_fichacampo WHERE id = %s", [id_secondary]
                )
                row_default = cursor.fetchone()

                if row_default:
                    data_atualizacao_default = row_default[1]

                    data_atualizacao_default = data_atualizacao_default
                    timezone1 = data_atualizacao_default.tzinfo
                    data_atualizacao_secondary = data_atualizacao_secondary.replace(
                        tzinfo=timezone1
                    )

                    if data_atualizacao_secondary > data_atualizacao_default:
                        dados_jsonb = json.dumps(row[13]) if row[13] is not None else None
                        dados_jsonb = json.loads(dados_jsonb)
                        dados_jsonb_plantio = json.dumps(row[12]) if row[12] is not None else None
                        dados_jsonb_plantio = json.loads(dados_jsonb)
                        cursor.execute(
                            "UPDATE todos_fichacampo SET "
                            "data_criada = %s, "
                            "data_atualizado = %s, "
                            "data_aplicada = %s, "
                            "volume = %s, "
                            "totalarea = %s, "
                            "totalareaap = %s, "
                            "totalcalda = %s, "
                            "tqn1 = %s, "
                            "tqn2 = %s, "
                            "tqn3 = %s, "
                            "capacidade = %s, "
                            "plantio = %s, "
                            "dados = %s, "
                            "obs = %s, "
                            "pendente = %s, "
                            "ativo = %s, "
                            "atividade_id = %s, "
                            "tipo_aplicacao_id = %s "
                            "WHERE id = %s",
                            [
                                row[1],
                                row[2],
                                datetime.combine(row[3], datetime.min.time()),
                                row[4],
                                row[5],
                                row[6],
                                row[8],
                                row[9],
                                row[10],
                                row[11],
                                dados_jsonb_plantio,
                                dados_jsonb,
                                row[14],
                                row[15],
                                row[16],
                                row[17],
                                row[18],
                                id_secondary,
                            ],
                        )

    #########################################################################################################

    def sync_db_produto():
        with connections["secondary"].cursor() as cursor_secondary:
            cursor_secondary.execute("SELECT * FROM todos_produtos")
            rows = cursor_secondary.fetchall()

        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT codigo FROM todos_produtos")
            existing_product_codes = {row[0] for row in cursor.fetchall()}

            if not existing_product_codes:
                existing_product_codes = set()

            for row in rows:
                product_code = row[2]
                if product_code not in existing_product_codes:
                    produto = row[1] if row[1] is not None else 0
                    codigo = row[2] if row[2] is not None else ""
                    descricao = row[3] if row[3] is not None else ""
                    ativo = row[4] if row[4] is not None else 0
                    Produtos.objects.using("default").create(
                        data_criada=row[6],
                        data_atualizado=row[5],
                        codigo=codigo,
                        descricao=descricao,
                        ativo=ativo,
                        produto=produto,
                    )

            for row in rows:
                cod_secondary = row[2]
                data_atualizacao_secondary = row[5]

                cursor.execute(
                    "SELECT * FROM todos_produtos WHERE codigo = %s", [cod_secondary]
                )
                row_default = cursor.fetchone()

                if row_default:
                    data_atualizacao_default = row_default[1]

                    data_atualizacao_default = data_atualizacao_default
                    timezone1 = data_atualizacao_default.tzinfo
                    data_atualizacao_secondary = data_atualizacao_secondary.replace(
                        tzinfo=timezone1
                    )

                    if data_atualizacao_secondary > data_atualizacao_default:
                        cursor.execute(
                            "UPDATE todos_produtos SET "
                            "produto = %s, "
                            "codigo = %s, "
                            "descricao = %s, "
                            "ativo = %s, "
                            "data_criada = %s, "
                            "data_atualizado = %s "
                            "WHERE codigo = %s",
                            [
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                                datetime.combine(row[5], datetime.min.time()),
                                datetime.combine(row[6], datetime.min.time()),
                                cod_secondary,
                            ],
                        )

    #########################################################################################################
    def sync_db_plantio():
        with connections["secondary"].cursor() as cursor:
            cursor.execute("SELECT * FROM todos_plantio ORDER BY id;")
            rows = cursor.fetchall()

        with connections["default"].cursor() as cursor:
            latest_date_in_database = Plantio.objects.using("default").aggregate(
                models.Max("data_criada")
            )["data_criada__max"]
            if latest_date_in_database:
                latest_date_in_database = latest_date_in_database
                timezone1 = latest_date_in_database.tzinfo
            for row in rows:
                ficha_data_criada = row[1].replace(tzinfo=timezone1)

                if (
                    not latest_date_in_database
                    or ficha_data_criada > latest_date_in_database
                ):
                    nome_pl = row[3] if row[3] is not None else ""
                    cultura = row[4] if row[4] is not None else ""
                    pivo = row[5] if row[5] is not None else ""
                    area = row[6] if row[6] is not None else 0.0
                    fazenda = row[7] if row[7] is not None else ""
                    ativo = row[8] if row[8] is not None else True

                    Plantio.objects.using("default").create(
                        data_criada=ficha_data_criada,
                        data_atualizado=row[2],
                        nome_pl=nome_pl,
                        cultura=cultura,
                        pivo=pivo,
                        area=area,
                        fazenda=fazenda,
                        ativo=ativo,
                    )

            for row in rows:
                id_secondary = row[0]
                data_atualizacao_secondary = row[2]

                cursor.execute(
                    "SELECT * FROM todos_plantio WHERE id = %s", [id_secondary]
                )
                row_default = cursor.fetchone()

                if row_default:
                    data_atualizacao_default = row_default[1]

                    data_atualizacao_default = data_atualizacao_default
                    timezone1 = data_atualizacao_default.tzinfo
                    data_atualizacao_secondary = data_atualizacao_secondary.replace(
                        tzinfo=timezone1
                    )

                    if data_atualizacao_secondary > data_atualizacao_default:
                        cursor.execute(
                            "UPDATE todos_plantio SET "
                            "data_criada = %s, "
                            "data_atualizado = %s, "
                            "nome_pl = %s, "
                            "cultura = %s, "
                            "pivo = %s, "
                            "area = %s, "
                            "fazenda = %s, "
                            "ativo = %s "
                            "WHERE id = %s",
                            [
                                row[1],
                                row[2],
                                row[3],
                                row[4],
                                row[5],
                                row[6],
                                row[7],
                                row[8],
                                id_secondary,
                            ],
                        )

    #########################################################################################################
    def sync_db_atividadeb():
        with connections["secondary"].cursor() as cursor:
            cursor.execute("SELECT * FROM todos_atividadep ORDER BY id;")
            rows = cursor.fetchall()

        with connections["default"].cursor() as cursor:
            print("passou")
            latest_date_in_database = AtividadeP.objects.using("default").aggregate(
                models.Max("data_criada")
            )["data_criada__max"]
            if latest_date_in_database:
                latest_date_in_database = latest_date_in_database
                timezone1 = latest_date_in_database.tzinfo
                print(latest_date_in_database)
            for row in rows:
                ficha_data_criada = row[1].replace(tzinfo=timezone1)
                print(ficha_data_criada)

                if (
                    not latest_date_in_database
                    or ficha_data_criada > latest_date_in_database
                ):
                    nome = row[3] if row[3] is not None else ""
                    ativo = row[4] if row[4] is not None else True

                    AtividadeP.objects.using("default").create(
                        data_criada=ficha_data_criada,
                        data_atualizado=row[2],
                        nome=nome,
                        ativo=ativo,
                    )

            for row in rows:
                id_secondary = row[0]
                data_atualizacao_secondary = row[2]

                cursor.execute(
                    "SELECT * FROM todos_atividadep WHERE id = %s", [id_secondary]
                )
                row_default = cursor.fetchone()

                if row_default:
                    data_atualizacao_default = row_default[1]

                    data_atualizacao_default = data_atualizacao_default
                    timezone1 = data_atualizacao_default.tzinfo
                    data_atualizacao_secondary = data_atualizacao_secondary.replace(
                        tzinfo=timezone1
                    )

                    if data_atualizacao_secondary > data_atualizacao_default:
                        cursor.execute(
                            "UPDATE todos_atividadep SET "
                            "data_criada = %s, "
                            "data_atualizado = %s, "
                            "nome = %s, "
                            "ativo = %s "
                            "WHERE id = %s",
                            [
                                row[1],
                                row[2],
                                row[4],
                                row[3],
                                id_secondary,
                            ],
                        )
