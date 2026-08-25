from django.contrib import admin
from .models import Category, Tag, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'seo_score', 'published_at')
    list_filter = ('status', 'category', 'created_at')
    search_fields = ('title', 'content', 'focus_keyword')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('author', 'category', 'tags')
    
    # Organize fields into logical sections just like WordPress/Rank Math
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'author', 'content', 'excerpt', 'featured_image')
        }),
        ('Taxonomy', {
            'fields': ('category', 'tags')
        }),
        ('Publishing', {
            'fields': ('status', 'published_at')
        }),
        ('SEO Configuration (Rank Math Style)', {
            'fields': ('focus_keyword', 'meta_title', 'meta_description', 'canonical_url'),
            'classes': ('collapse',)
        }),
        ('SEO Analysis (Read-Only)', {
            'fields': ('seo_score', 'word_count', 'read_time_minutes', 'internal_links_count', 'external_links_count'),
            'description': 'These metrics are automatically calculated when the post is saved.',
            'classes': ('collapse',)
        }),
    )

    readonly_fields = ('seo_score', 'word_count', 'read_time_minutes', 'internal_links_count', 'external_links_count')
