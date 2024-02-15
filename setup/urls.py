from django.contrib import admin
from django.urls import path
from todos.views import (
    todo_home,
    todo_repetir,
    todo_update,
    FichaView,
    receber_dados,
    atualizar_dados,
    ficha_toggle_pendente,
    ficha_toggle_active,
    produto_toggle_active,
    plantio_toggle_active,
    upload_excel_file,
    ImprimirFicha,
    muda_cod,
    sync_db_view,
    down_db_view,
    FichaFiltro,
    FichaListView,
    PlantioListView,
    PlantioCreateView,
    PlantioUpdateView,
    PlantioDeleteView,
    AtividadePListView,
    AtividadePCreateView,
    AtividadePUpdateView,
    AtividadePDeleteView,
    ProdutosCreateView,
    ProdutosListView,
    ProdutosUpdateView,
    ProdutosDeleteView,
    TipoAplicacaoListView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", todo_home, name="home_page"),
    path("ficha/toggle/<int:pk>", ficha_toggle_active, name="ficha_toggle_active"),
    path(
        "ficha/toggle_p/<int:pk>", ficha_toggle_pendente, name="ficha_toggle_pendente"
    ),
    path("upload_excel/", upload_excel_file, name="upload_excel"),
    path("sync/", sync_db_view, name="sync_db_view"),
    path("down/", down_db_view, name="down_db_view"),
    path("sync/", muda_cod, name="muda_cod"),
    path("ficha/view/<int:pk>/", FichaView, name="ficha_view"),
    path("ficha/imprimir/<int:pk>/", ImprimirFicha, name="imprimir_ficha"),
    path("update/<int:pk>", todo_update, name="ficha_update"),
    path("repetir/<int:pk>", todo_repetir, name="ficha_repetir"),
    path("receber_dados/", receber_dados, name="receber_dados"),
    path("atualizar_dados/", atualizar_dados, name="atualizar_dados"),
    path("ficha/", FichaListView.as_view(), name="ficha_list"),
    path("ficha/relatorio/", FichaListView.as_view(), name="ficha_relatorio"),
    path("ficha_filtro/", FichaFiltro.as_view(), name="ficha_filtro"),
    path(
        "ficha_filtro/relatorio/", FichaFiltro.as_view(), name="ficha_filtro_relatorio"
    ),
    path("plantio", PlantioListView.as_view(), name="plantio_list"),
    path("plantio/create/", PlantioCreateView.as_view(), name="plantio_create"),
    path("plantio/update/<int:pk>", PlantioUpdateView.as_view(), name="plantio_update"),
    path("plantio/toggle/<int:pk>", plantio_toggle_active, name="plantio_toggle_active"),
    path("plantio/delete/<int:pk>", PlantioDeleteView.as_view(), name="plantio_delete"),
    path("atividade", AtividadePListView.as_view(), name="atividade_list"),
    path("atividade/create/", AtividadePCreateView.as_view(), name="atividade_create"),
    path(
        "atividade/update/<int:pk>",
        AtividadePUpdateView.as_view(),
        name="atividade_update",
    ),
    path(
        "atividade/delete/<int:pk>",
        AtividadePDeleteView.as_view(),
        name="atividade_delete",
    ),
    path("produto", ProdutosListView.as_view(), name="produtos_list"),
    path("produto/create/", ProdutosCreateView.as_view(), name="produtos_create"),
    path(
        "produtos/update/<int:pk>",
        ProdutosUpdateView.as_view(),
        name="produtos_update",
    ),
    path(
        "produto/toggle/<int:pk>", produto_toggle_active, name="produto_toggle_active"
    ),
    path(
        "produtos/delete/<int:pk>", ProdutosDeleteView.as_view(), name="produtos_delete"
    ),
    path("aplicacoes", TipoAplicacaoListView.as_view(), name="aplicacao_list"),
]
