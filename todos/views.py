from django.views.generic import (
    ListView,
    CreateView,
    UpdateView,
    DeleteView,
    View,
    DetailView,
)
import pandas as pd
from django.db.models.functions import Cast
from django.db.models import CharField, Value
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseRedirect
from django.db.models import Max
import pytz
from datetime import datetime
from django.utils import timezone
import json
from todos.routers import (
    DatabaseSynchronizer,
    DatabaseDownloader,
    ModificarProdutoRouter,
)

from .models import AtividadeP, Produtos, TipoAplicacao, Plantio, FichaCampo

from django.shortcuts import render

def muda_cod(request):
    response = ModificarProdutoRouter.modificar_produtos()

    return response

def sync_db_view(request):
    DatabaseSynchronizer.sync_db_atividade()
    DatabaseSynchronizer.sync_db_plantio()
    DatabaseSynchronizer.sync_db_produto()
    DatabaseSynchronizer.sync_db()
    return HttpResponseRedirect(reverse("ficha_list"))


def down_db_view(request):
    DatabaseDownloader.sync_db_atividadeb()
    return HttpResponseRedirect(reverse("ficha_list"))

class FichaFiltro(ListView):
    model = FichaCampo
    template_name = "fichadeaplicacao_list.html"
    context_object_name = "fichacampo_list"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["plantios"] = Plantio.objects.all()
        context["atividades"] = AtividadeP.objects.all()
        context["tipo_irrigadores"] = TipoAplicacao.objects.all()

        for ficha in context["fichacampo_list"]:
            for item in ficha.dados:
                if "produto" in item:
                    cod_produto = item["produto"]
                    produto = Produtos.objects.get(codigo=cod_produto)
                    item["nome_produto"] = produto.produto
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        
        atividade_filter = self.request.GET.get("atividade_filter")
        plantio_filter = self.request.GET.get("plantio_filter")
        status_filter = self.request.GET.get("status_filter")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if start_date and end_date:
            print(start_date, end_date)
            queryset = queryset.filter(data_criada__range=(start_date, end_date))
        else:
            if start_date:
                queryset = queryset.filter(data_criada__date=start_date)

        if atividade_filter:
            queryset = queryset.filter(atividade__id=atividade_filter)

        if plantio_filter:
            queryset = queryset.annotate(
                plantio_text=Cast('plantio', output_field=CharField())
            )
            
            queryset = queryset.filter(plantio_text__contains=plantio_filter)

        if status_filter is not None:
            if status_filter == "true":
                queryset = queryset.filter(pendente=False)
            elif status_filter == "false":
                queryset = queryset.filter(pendente=True)

        return queryset.order_by("data_aplicada")

    def get_template_names(self):
        if "relatorio" in self.request.path:
            return ["fichadeaplicacao_relatorio.html"]
        return ["fichadeaplicacao_list.html"]

def upload_excel_file(request):
    if request.method == "POST":
        excel_file = request.FILES["inputExcel"]

        if str(excel_file).split(".")[-1] in ["xls", "xlsx"]:
            data = pd.read_excel(excel_file)
            for _, row in data.iterrows():
                produto_cod = row[
                    "Cód."
                ]
                if (
                    pd.isna(produto_cod)
                    or pd.isna(row["Produto"])
                    or pd.isna(row["Cód."])
                    or pd.isna(row["Descrição"])
                ):
                    continue

                produto, created = Produtos.objects.get_or_create(codigo=produto_cod)
                produto.produto = row["Produto"]
                produto.codigo = row["Cód."]
                produto.descricao = row["Descrição"]
                produto.data_criada=datetime.now()
                produto.save()

            return HttpResponseRedirect(reverse("produtos_list"))
        else:
            pass
    else:
        pass


@csrf_exempt
def plantio_toggle_active(request, pk):
    plantio = get_object_or_404(Plantio, pk=pk)

    if request.method == "PUT" or request.method == "POST":
        plantio.data_atualizado = timezone.now().astimezone(pytz.timezone("Europe/London"))
        plantio.ativo = not plantio.ativo
        plantio.save()
        return JsonResponse({"ativo": plantio.ativo})
    else:
        return JsonResponse({"error": "Invalid request"})

@csrf_exempt
def ficha_toggle_active(request, pk):
    obj = get_object_or_404(FichaCampo, pk=pk)

    if request.method == "PUT" or request.method == "POST":
        obj.data_atualizado = timezone.now().astimezone(pytz.timezone("Europe/London"))
        obj.ativo = not obj.ativo
        obj.save()
        return JsonResponse({"ativo": obj.ativo})
    else:
        return JsonResponse({"error": "Invalid request"})


@csrf_exempt
def ficha_toggle_pendente(request, pk):
    print("obj")
    obj = get_object_or_404(FichaCampo, pk=pk)

    if request.method == "PUT" or request.method == "POST":
        obj.data_atualizado = timezone.now().astimezone(pytz.timezone("Europe/London"))
        obj.pendente = not obj.pendente
        obj.save()
        return JsonResponse({"ativo": obj.pendente})
    else:
        return JsonResponse({"error": "Invalid request"})


@csrf_exempt
def produto_toggle_active(request, pk):
    print("obj")
    obj = get_object_or_404(Produtos, pk=pk)

    if request.method == "PUT" or request.method == "POST":
        obj.data_atualizado = timezone.now().astimezone(pytz.timezone("Europe/London"))
        obj.ativo = not obj.ativo
        obj.save()
        return JsonResponse({"ativo": obj.ativo})
    else:
        return JsonResponse({"error": "Invalid request"})


def todo_home(request):
    ficha_aplicacao_count = FichaCampo.objects.aggregate(Max("id"))["id__max"]
    if ficha_aplicacao_count is None:
        ficha_aplicacao_count = 1
    else:
        ficha_aplicacao_count

    plantios = Plantio.objects.all()
    atividades = AtividadeP.objects.all()
    produtos = Produtos.objects.all().order_by("descricao")
    tipos_aplicacao = TipoAplicacao.objects.all()
    ran = [i for i in range(1, 10)]
    ran2 = [i for i in range(1, 5)]

    context = {
        "fcc": ficha_aplicacao_count+1,
        "plantios": plantios,
        "atividades": atividades,
        "produtos": produtos,
        "tipos_aplicacao": tipos_aplicacao,
        "range": ran,
        "range2":ran2,
    }

    return render(request, "todos/home_page.html", context)


def todo_repetir(request, pk):
    ficha_aplicacao = get_object_or_404(FichaCampo, pk=pk)
    plantios = Plantio.objects.all()
    atividades = AtividadeP.objects.all()
    produtos = Produtos.objects.all().order_by("descricao")
    tipos_aplicacao = TipoAplicacao.objects.all()
    ran = [i for i in range(1, 10)]
    ran2 = [i for i in range(1, 5)]
    pk_view = ficha_aplicacao.pk
    
    for item in ficha_aplicacao.dados:
        if "produto" in item:
            cod_produto = item["produto"]
            produto = Produtos.objects.get(codigo=cod_produto)
            item["nome_produto"] = produto.produto

    if len(ficha_aplicacao.dados) < 9:
        ficha_aplicacao.dados += [{}] * (9 - len(ficha_aplicacao.dados))
    if len(ficha_aplicacao.plantio) < 4:
        ficha_aplicacao.plantio += [{}] * (4 - len(ficha_aplicacao.plantio))

    context = {
        "ficha": ficha_aplicacao,
        "plantios": plantios,
        "atividades": atividades,
        "produtos": produtos,
        "tipos_aplicacao": tipos_aplicacao,
        "range": ran,
        "pk_view": pk_view+1,
    }

    return render(request, "todos/home_repetir.html", context)


def todo_update(request, pk):
    ficha_aplicacao = get_object_or_404(FichaCampo, pk=pk)
    plantios = Plantio.objects.all()
    atividades = AtividadeP.objects.all()
    produtos = Produtos.objects.all().order_by("descricao")
    tipos_aplicacao = TipoAplicacao.objects.all()
    ran = [i for i in range(1, 10)]
    ran2 = [i for i in range(1, 5)]
    
    for item in ficha_aplicacao.dados:
        if "produto" in item:
            cod_produto = item["produto"]
            produto = Produtos.objects.get(codigo=cod_produto)
            item["nome_produto"] = produto.produto

    if len(ficha_aplicacao.dados) < 9:
        ficha_aplicacao.dados += [{}] * (9 - len(ficha_aplicacao.dados))
    if len(ficha_aplicacao.plantio) < 4:
        ficha_aplicacao.plantio += [{}] * (4 - len(ficha_aplicacao.plantio))

    context = {
        "ficha": ficha_aplicacao,
        "plantios": plantios,
        "atividades": atividades,
        "produtos": produtos,
        "tipos_aplicacao": tipos_aplicacao,
        "range": ran,
    }

    return render(request, "todos/home_update.html", context)


@csrf_exempt
def receber_dados(request):
    if request.method == "POST" or request.method == "PUT":
        print(request.body)
        # Decodifique os bytes para uma string e carregue o JSON
        dados = json.loads(request.body.decode("utf-8"))

        # Agora você pode acessar os dados como um dicionário Python
        if request.method == "PUT":
            ficha_aplicacao = get_object_or_404(
                FichaCampo, pk=AtividadeP.objects.get(pk=(dados["ficha_pk"]))
            )
        atividade_id = AtividadeP.objects.get(pk=(dados["atividade_id"]))
        plantio = dados["dados_tabela2"]
        totalArea = dados["totalArea"]
        totalAreaAp = dados["totalAreaAp"]
        totalCalda = dados["totalCalda"]
        volume = dados["volume"]
        cap=dados["cap"]
        aplicacao_id = TipoAplicacao.objects.get(pk=(dados["aplicacao_id"]))
        dados_tabela = dados["dados_tabela"]
        obs = dados["obs"]
        tqn1 = dados["tqn1"]
        tqn2 = dados["tqn2"]
        tqn3 = dados["tqn3"]
        data_criada = timezone.now().astimezone(pytz.timezone("Europe/London"))
        
        data_aplicada = datetime.strptime(dados["data1"], "%Y-%m-%d")
        
        data_aplicada = pytz.timezone("Europe/London").localize(data_aplicada)
        
        ficha_aplicacao = FichaCampo(
            data_criada=data_criada,
            atividade=atividade_id,
            plantio=plantio,
            totalarea=totalArea,
            totalareaap=totalAreaAp,
            totalcalda=totalCalda,
            tqn1=tqn1,
            tqn2=tqn2,
            tqn3=tqn3,
            volume=volume,
            capacidade=cap,
            tipo_aplicacao=aplicacao_id,
            dados=dados_tabela,
            data_aplicada=data_aplicada,
            obs=obs,
        )
        ficha_aplicacao.save()

        return JsonResponse({"status": "success"}, safe=False)
    else:
        return JsonResponse({"status": "fail"}, safe=False)


@csrf_exempt
def atualizar_dados(request):
    if request.method == "PUT":
        print(request.body)
        # Decodifique os bytes para uma string e carregue o JSON
        dados = json.loads(request.body.decode("utf-8"))
        print(dados)
        # Obtenha a ficha existente pelo id
        ficha_aplicacao = get_object_or_404(FichaCampo, pk=dados["ficha_pk"])

        # Atualize os campos desejados
        ficha_aplicacao.atividade = AtividadeP.objects.get(pk=(dados["atividade_id"]))
        # ficha_aplicacao.area = dados["area"].replace(",", ".")
        ficha_aplicacao.totalarea = dados["totalArea"]
        ficha_aplicacao.totalareaap = dados["totalAreaAp"]
        ficha_aplicacao.totalcalda = dados["totalCalda"]
        ficha_aplicacao.tipo_aplicacao = TipoAplicacao.objects.get(
            pk=(dados["aplicacao_id"])
        )
        ficha_aplicacao.dados = dados["dados_tabela"]
        ficha_aplicacao.plantio = dados["dados_tabela2"]
        ficha_aplicacao.volume=dados["volume"]
        ficha_aplicacao.capacidade=dados["cap"]
        ficha_aplicacao.obs=dados["obs"]
        ficha_aplicacao.tqn1 = dados["tqn1"]
        ficha_aplicacao.tqn2 = dados["tqn2"]
        ficha_aplicacao.tqn3 = dados["tqn3"]
        ficha_aplicacao.data_aplicada = datetime.strptime(dados["data1"], "%Y-%m-%d")
        ficha_aplicacao.data_atualizado = timezone.now().astimezone(pytz.timezone("Europe/London"))

        ficha_aplicacao.data_aplicada = pytz.timezone("Europe/London").localize(
            ficha_aplicacao.data_aplicada
        )

        # Salve a instância para atualizar o banco de dados
        print(ficha_aplicacao)
        ficha_aplicacao.save()

        return JsonResponse({"status": "success"}, safe=False)
    else:
        return JsonResponse({"status": "fail"}, safe=False)


def ImprimirFicha(request, pk):
    ficha_aplicacao = get_object_or_404(FichaCampo, pk=pk)
    plantios = Plantio.objects.all()
    atividades = AtividadeP.objects.all()
    produtos = Produtos.objects.all()
    tipos_aplicacao = TipoAplicacao.objects.all()
    ran = [i for i in range(1, 10)]
    ran2 = [i for i in range(1, 5)]
    
    for item in ficha_aplicacao.dados:
        if "produto" in item:
            cod_produto = item["produto"]
            produto = Produtos.objects.get(codigo=cod_produto)
            item["nome_produto"] = produto.produto

    if len(ficha_aplicacao.dados) < 9:
        ficha_aplicacao.dados += [{}] * (9 - len(ficha_aplicacao.dados))
    if len(ficha_aplicacao.plantio) < 4:
        ficha_aplicacao.plantio += [{}] * (4 - len(ficha_aplicacao.plantio))

    context = {
        "ficha": ficha_aplicacao,
        "plantios": plantios,
        "atividades": atividades,
        "produtos": produtos,
        "tipos_aplicacao": tipos_aplicacao,
        "range": ran,
        "range2":ran2,
    }

    return render(request, "todos/fichadeaplicacao_detail.html", context)


def FichaView(request, pk):
    ficha_aplicacao = get_object_or_404(FichaCampo, pk=pk)
    plantios = Plantio.objects.all()
    atividades = AtividadeP.objects.all()
    produtos = Produtos.objects.all()
    tipos_aplicacao = TipoAplicacao.objects.all()
    ran = [i for i in range(1, 10)]
    ran2 = [i for i in range(1, 5)]
    
    for item in ficha_aplicacao.dados:
        if "produto" in item:
            cod_produto = item["produto"]
            produto = Produtos.objects.get(codigo=cod_produto)
            item["nome_produto"] = produto.produto

    if len(ficha_aplicacao.dados) < 9:
        ficha_aplicacao.dados += [{}] * (9 - len(ficha_aplicacao.dados))
    if len(ficha_aplicacao.plantio) < 4:
        ficha_aplicacao.plantio += [{}] * (4 - len(ficha_aplicacao.plantio))

    context = {
        "ficha": ficha_aplicacao,
        "plantios": plantios,
        "atividades": atividades,
        "produtos": produtos,
        "tipos_aplicacao": tipos_aplicacao,
        "range": ran,
        "range2":ran2,
    }

    return render(request, "todos/ficha_view.html", context)


class FichaListView(ListView):
    model = FichaCampo

    def get_queryset(self):
        queryset = FichaCampo.objects.all().order_by("data_aplicada")
    
        for ficha in queryset:
            print(ficha.pk)
            for item in ficha.dados:
                if "produto" in item:
                    cod_produto = item["produto"]
                    produto = Produtos.objects.get(codigo=cod_produto)

                    item["nome_produto"] = produto.produto

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["plantios"] = Plantio.objects.all()
        context["atividades"] = AtividadeP.objects.all()
        context["tipo_irrigadores"] = TipoAplicacao.objects.all()
        return context

    def get_template_names(self):
        # Verifique a parte da URL para decidir qual template usar
        if "relatorio" in self.request.path:
            return ["fichadeaplicacao_relatorio.html"]
        return ["fichadeaplicacao_list.html"]

class PlantioListView(ListView):
    model = Plantio

    
class PlantioCreateView(CreateView):
    model = Plantio
    fields = ["nome_pl", "cultura", "area", "fazenda", "pivo"]
    success_url = reverse_lazy("plantio_list")

    def form_valid(self, form):
        # Atualiza no banco de dados primário
        form.instance.data_criada = datetime.now()
        form.instance.save(using="default")
        # Atualiza no banco de dados secundário
        return super().form_valid(form)


class PlantioUpdateView(UpdateView):
    model = Plantio
    fields = ["nome_pl", "cultura", "area", "fazenda", "pivo"]
    success_url = reverse_lazy("plantio_list")

    def form_valid(self, form):
        # Atualiza no banco de dados primário
        form.instance.save(using="default")
        # Atualiza no banco de dados secundário
        return super().form_valid(form)


class PlantioDeleteView(DeleteView):
    model = Plantio


class AtividadePListView(ListView):
    model = AtividadeP


class AtividadePCreateView(CreateView):
    model = AtividadeP
    fields = ["nome"]
    success_url = reverse_lazy("atividade_list")

    def form_valid(self, form):
        # Atualiza no banco de dados primário
        form.instance.data_criada = datetime.now()
        form.instance.save(using="default")
        # Atualiza no banco de dados secundário
        return super().form_valid(form)


class AtividadePUpdateView(UpdateView):
    model = AtividadeP
    fields = ["nome"]
    success_url = reverse_lazy("atividade_list")

    def form_valid(self, form):
        # Atualiza no banco de dados primário
        form.instance.save(using="default")
        # Atualiza no banco de dados secundário
        return super().form_valid(form)


class AtividadePDeleteView(DeleteView):
    model = AtividadeP


class ProdutosListView(ListView):
    model = Produtos


class ProdutosCreateView(CreateView):
    model = Produtos
    fields = ["produto", "codigo", "descricao"]
    success_url = reverse_lazy("produtos_list")

    def form_valid(self, form):
        # Atualiza no banco de dados primário
        form.instance.data_criada = datetime.now()
        form.instance.save(using="default")
        # Atualiza no banco de dados secundário
        return super().form_valid(form)


class ProdutosUpdateView(UpdateView):
    model = Produtos
    fields = ["produto", "codigo", "descricao"]
    success_url = reverse_lazy("produtos_list")

    def form_valid(self, form):
        # Atualiza no banco de dados primário
        form.instance.save(using="default")
        # Atualiza no banco de dados secundário
        return super().form_valid(form)


class ProdutosDeleteView(DeleteView):
    model = Produtos


class TipoAplicacaoListView(ListView):
    model = TipoAplicacao
