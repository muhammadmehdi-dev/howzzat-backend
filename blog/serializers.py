from rest_framework import serializers
from .models import Category, Tag, Post

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']

class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image', 
            'category', 'tags', 'author_name', 'published_at', 
            'read_time_minutes'
        ]

class PostDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'featured_image', 
            'category', 'tags', 'author_name', 'published_at',
            'focus_keyword', 'meta_title', 'meta_description', 'canonical_url',
            'word_count', 'read_time_minutes', 'seo_score'
        ]
