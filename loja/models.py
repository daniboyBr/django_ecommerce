from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from loja.managers import ProdutoManager
from loja.utils import unique_slug_generator
from accounts.models import User


class Categoria(models.Model):
    title = models.CharField(max_length=150, blank=False)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title


class Produto(models.Model):
    title       = models.CharField(max_length=150)
    description = models.TextField()
    price       = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    image       = models.ImageField(upload_to='products', null=True, blank=True)
    featured    = models.BooleanField(default=False)
    active      = models.BooleanField(default=True)
    slug        = models.SlugField(unique=True, blank=True)
    categoria   = models.ForeignKey(Categoria, blank=False, on_delete=models.DO_NOTHING, related_name='categoria')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ProdutoManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/produtos/{slug}/".format(slug=self.slug)


# Create your models here.
class Tag(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField()
    timestamp = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)
    products = models.ManyToManyField(Produto, blank=True)

    def __str__(self):
        return self.title


class PedidoCliente(models.Model):
    total = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    numero_confimacao = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user")
    produtos = models.ManyToManyField(Produto, related_name='produtos', through='PedidoProduto', through_fields=('pedido_cliente','produto'))
    created_at = models.DateTimeField(auto_now_add=True)


class PedidoProduto(models.Model):
    pedido_cliente = models.ForeignKey(PedidoCliente,related_name='pedido', on_delete=models.CASCADE)
    produto = models.ForeignKey(Produto, related_name='produto', on_delete=models.CASCADE)
    quantidade = models.IntegerField(default=1)


@receiver(pre_save, sender=Produto)
@receiver(pre_save, sender=Tag)
@receiver(pre_save, sender=Categoria)
def slug_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = unique_slug_generator(instance)

