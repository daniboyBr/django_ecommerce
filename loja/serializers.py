from rest_framework import serializers, pagination
from loja.models import Produto, Tag, PedidoCliente, Categoria, PedidoProduto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id','title','slug']
        ordering = ['-id']


class ProdutoSerializer(serializers.ModelSerializer):
    category_name = serializers.StringRelatedField(source='categoria', read_only=True)
    class Meta: 
        model = Produto
        fields = ['id', 'title', 'description', 'price', 'categoria', 'image', 'active', 'category_name','featured', 'slug', 'url']
        lookup_field = 'slug'
        extra_kwargs = {'url': {'lookup_field':'slug'}}
        ordering = ['-id']

class TagSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Tag
        fields = ['id', 'title', 'slug', 'active']
        ordering = ['-id']

class CarrinhoSerializer(serializers.Serializer):
    quantidade = serializers.IntegerField(default=1)
    produto_id = serializers.IntegerField(required=False)


class PedidoClienteSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    produtos = serializers.HyperlinkedIdentityField(view_name='pedidos-cliente-produtos')
    carrinho = serializers.ListField(child=CarrinhoSerializer(), write_only=True, required=True)

    class Meta:
        model = PedidoCliente
        fields = ['id', 'total', 'numero_confimacao', 'user', 'produtos', 'carrinho']
        ordering = ['-id']

    def __add_produdtos(self, produtos, pedido_id):
        for produto in produtos:
            if "quantidade" not in produto and "produto_id" not in produto:
                continue
            PedidoProduto.objects.create(
                pedido_cliente_id=pedido_id,
                produto_id=produto["produto_id"],
                quantidade=produto["quantidade"]
            )

    def create(self, validated_data):
        produtos = validated_data.pop('carrinho',[])
        pedido = PedidoCliente.objects.create(**validated_data)
        self.__add_produdtos(produtos, pedido.id)
        return pedido

class PedidoProdutoSerializer(serializers.ModelSerializer):
    produto = serializers.CharField(read_only=True, source="produto.title")
    slug = serializers.CharField(read_only=True, source="produto.slug")
    description = serializers.CharField(read_only=True, source="produto.description")
    price = serializers.CharField(read_only=True, source="produto.price")
    category_name = serializers.CharField(read_only=True, source="produto.categoria")
    image = serializers.SerializerMethodField("produto_img_url", read_only=True)
    url = serializers.SerializerMethodField("produto_url", read_only=True)

    class Meta:
        model = PedidoProduto
        fields = ['quantidade', 'produto','description','price','image','slug','url','category_name']
        ordering = ['-id']

    def produto_img_url(self, obj):
        request = self.context.get('request')
        produto_image = obj.produto.image.url
        return request.build_absolute_uri(produto_image)

    def produto_url(self, obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.produto.get_absolute_url())

