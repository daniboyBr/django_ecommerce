import stripe
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from loja.models import Categoria, PedidoCliente, PedidoProduto, Produto, Tag
from loja.permissions import CreanteAndReadOnly, IsAdminOrReadOnly
from loja.serializers import (CategoriaSerializer, PedidoClienteSerializer,
                              PedidoProdutoSerializer, ProdutoSerializer,
                              TagSerializer)

stripe.api_key = 'sk_test_51HaB87Da9E4DnCFSMiyzyadqE4ExcvMrzl7AgYaqGGe5AN6q4uGVmICsu1oybOgzflFfwu1Tmsv6dTvm5Hbpd3Nh003VtznFL0'


class ProdutosViewSet(viewsets.ModelViewSet):
    queryset = Produto.objects.all()
    serializer_class = ProdutoSerializer
    lookup_field = 'slug'
    filter_backends = (filters.SearchFilter,)
    search_fields = ['title', 'description']
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination

    @action(detail=False)
    def featured(self, request):
        produtos = Produto.objects.featured()
        page = self.paginate_queryset(queryset=produtos)
        serializer = self.get_serializer(
            page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False)
    def active(self, request):
        produtos = Produto.objects.active()
        page = self.paginate_queryset(queryset=produtos)
        serializer = self.get_serializer(
            page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False)
    def search(self, request):
        search = request.GET.get('q', None)
        produtos = []
        if search is not None:
            produtos = Produto.objects.search(search)
        produtos = produtos if produtos else Produto.objects.featured()
        page = self.paginate_queryset(queryset=produtos)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'], url_path='categoria/(?P<categoria_slug>[^/.]+)')
    def categoria(self, request, *args, **kwargs):
        queryset = Produto.objects.filter(
            categoria__slug=self.kwargs['categoria_slug'])
        if not queryset:
            raise NotFound()

        page = self.paginate_queryset(queryset=queryset)
        serializer = self.get_serializer(
            page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]


class PedidosViewSet(viewsets.ModelViewSet):
    serializer_class = PedidoClienteSerializer
    permission_classes = [IsAuthenticated, CreanteAndReadOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        if not self.request.user.is_superuser:
            return PedidoCliente.objects.all().filter(user=self.request.user)
        return PedidoCliente.objects.all()

    @action(detail=True, methods=['GET'])
    def produtos(self, request, pk=None):
        query = {"pedido_cliente_id": pk}
        if not self.request.user.is_superuser:
            query["pedido_cliente__user"] = self.request.user

        queryset = PedidoProduto.objects.filter(**query)

        if not queryset:
            raise NotFound()

        page = self.paginate_queryset(queryset=queryset)
        serializer = PedidoProdutoSerializer(
            page, context={'request': request}, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['POST'], name='Create Checkout Session', url_path='create-checkout-session')
    def create_checkout_session(self, request):
        produtos = Produto.objects.filter(
            id__in=map(lambda x: x['id_produto'], request.data))
        stripe_products = list(map(lambda prod: get_stripe_product(
            prod, request.data), produtos))
        print(stripe_products)
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=stripe_products,   
            mode='payment',
            success_url='http://localhost:3000/pagamento/sucesso',
            cancel_url='http://localhost:3000/pagamento/falha',
        )

        return Response({"session_id": session.id})


class CategoriasViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]


def get_stripe_product(produto, listagem):
    return {
        'price_data': {
            'currency': 'brl',
            'product_data': {
                'name': produto.title,
            },
            'unit_amount': int(float(produto.price) * 100),
        },
        'quantity': find_elment(produto.id, listagem)['quantidade'],
    }


def find_elment(id, product_list):
    for produto in product_list:
        if produto['id_produto'] == id:
            return produto
    produto = {'id_produto': id}
    product_list.append(produto)
    return produto
