from django.db import models
    
class Produtos(models.Model):
    data_criada = models.DateTimeField(
        verbose_name="Data de criação", blank=False, auto_now_add=False
    )
    data_atualizado = models.DateTimeField(
        verbose_name="Data da aplicação",
        auto_now=True,
        auto_now_add=False,
    )
    produto = models.CharField(
        verbose_name="Produto", max_length=50, null=False, blank=False
    )
    codigo = models.IntegerField(verbose_name="Codigo", null=False)
    descricao = models.CharField(
        verbose_name="Descrição", max_length=50, null=False, blank=False
    )
    ativo = models.BooleanField(default=True)


class Plantio(models.Model):
    data_criada = models.DateTimeField(
        verbose_name="Data de criação", blank=False, auto_now_add=False
    )
    data_atualizado = models.DateTimeField(
        verbose_name="Data da aplicação",
        auto_now=True,
        auto_now_add=False,
    )
    nome_pl = models.CharField(
        verbose_name="Plantio", max_length=50, null=False, blank=False
    )
    cultura = models.CharField(
        verbose_name="Cultura", max_length=50, null=False, blank=False
    )
    pivo = models.CharField(
        verbose_name="Pivo", max_length=10, null=False, blank=False
    )
    area = models.DecimalField(verbose_name="Área", decimal_places=4, max_digits=8)
    fazenda = models.CharField(
        verbose_name="fazenda", max_length=50, null=False, blank=False
    )
    ativo = models.BooleanField(default=True)


class AtividadeP(models.Model):
    data_criada = models.DateTimeField(
        verbose_name="Data de criação", blank=False, auto_now_add=False
    )
    data_atualizado = models.DateTimeField(
        verbose_name="Data da aplicação",
        auto_now=True,
        auto_now_add=False,
    )
    nome = models.CharField(
        verbose_name="Atividade", max_length=10, null=False, blank=False
    )
    # descicao = models.CharField(
    #    verbose_name="Descrição", max_length=100, null=False, blank=False
    # )
    ativo = models.BooleanField(default=True)



class TipoAplicacao(models.Model):
    nome_tipo = models.CharField(
        verbose_name="Irrigador", max_length=50, null=False, blank=False
    )
    ativo = models.BooleanField(default=True)


class FichaCampo(models.Model):
    data_criada = models.DateTimeField(
        verbose_name="Data de criação", blank=False, auto_now_add=False
    )
    data_atualizado = models.DateTimeField(
        verbose_name="Data de modificação",
        null=True,
        auto_now=True,
        auto_now_add=False,
    )
    data_aplicada = models.DateField(
        verbose_name="Data aplicação", blank=False, auto_now=False, auto_now_add=False
    )
    volume = models.IntegerField(verbose_name="Volume", null=False)
    totalarea = models.FloatField(verbose_name="totalArea", null=True)
    totalareaap = models.FloatField(verbose_name="totalAreaAp", null=True)
    totalcalda = models.FloatField(verbose_name="totalCalda", null=True)
    tqn1 = models.FloatField(verbose_name="tqn1", null=True)
    tqn2 = models.FloatField(verbose_name="tqn2", null=True)
    tqn3 = models.FloatField(verbose_name="tqn3", null=True)
    capacidade = models.IntegerField(verbose_name="Capacidade", null=False)
    plantio = models.JSONField()
    atividade = models.ForeignKey(AtividadeP, on_delete=models.CASCADE)
    tipo_aplicacao = models.ForeignKey(TipoAplicacao, on_delete=models.CASCADE)
    dados = models.JSONField()
    obs = models.TextField(null=True, blank=True)
    pendente = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)