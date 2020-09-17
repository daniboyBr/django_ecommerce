from rest_framework import viewsets, filters, status
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination


from loja.models import Produto, Tag, PedidoCliente, Categoria, PedidoProduto
from loja.serializers import ProdutoSerializer, TagSerializer, PedidoClienteSerializer, CategoriaSerializer, PedidoProdutoSerializer
from loja.permissions import CreanteAndReadOnly, IsAdminOrReadOnly

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
      serializer = self.get_serializer(page, context={'request': request}, many=True)
      return self.get_paginated_response(serializer.data)


   @action(detail=False)
   def active(self, request):
      produtos = Produto.objects.active()
      page = self.paginate_queryset(queryset=produtos)
      serializer = self.get_serializer(page, context={'request': request}, many=True)
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
      queryset = Produto.objects.filter(categoria__slug=self.kwargs['categoria_slug'])
      if not queryset:
         raise NotFound()

      page = self.paginate_queryset(queryset=queryset)
      serializer = self.get_serializer(page, context={'request': request}, many=True)
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
      serializer = PedidoProdutoSerializer(page, context={'request': request}, many=True)
      return self.get_paginated_response(serializer.data)

class CategoriasViewSet(viewsets.ModelViewSet):
   queryset = Categoria.objects.all()
   serializer_class = CategoriaSerializer
   permission_classes = [IsAdminUser, IsAuthenticated]
