from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from .models import Post, Category, Tag
from .serializers import PostListSerializer, PostDetailSerializer, CategorySerializer, TagSerializer

from api.pagination import StandardResultsSetPagination

@extend_schema(tags=['Blog'], summary='List all published blog posts', description='Returns a paginated list of published posts with SEO summaries.')
class PostList(generics.ListAPIView):
    serializer_class = PostListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category__slug', 'tags__slug']
    search_fields = ['title', 'content', 'focus_keyword']
    ordering_fields = ['published_at']
    ordering = ['-published_at']

    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('category', 'author').prefetch_related('tags')

@extend_schema(tags=['Blog'], summary='Get single blog post', description='Returns full blog post content and SEO metadata for header injection.')
class PostDetail(generics.RetrieveAPIView):
    queryset = Post.objects.filter(status='published')
    serializer_class = PostDetailSerializer
    lookup_field = 'slug'

@extend_schema(tags=['Blog'], summary='List all categories')
class CategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = None

@extend_schema(tags=['Blog'], summary='List all tags')
class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
