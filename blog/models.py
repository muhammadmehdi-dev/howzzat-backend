from django.db import models
from django.utils.text import slugify
from django.conf import settings
from django_ckeditor_5.fields import CKEditor5Field
from bs4 import BeautifulSoup

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Post(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )

    # Core content
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='blog_posts')
    content = CKEditor5Field('Text', config_name='default')
    excerpt = models.TextField(blank=True, help_text="Short description used on blog list pages.")
    featured_image = models.ImageField(upload_to='blog/images/', blank=True, null=True)
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)

    # SEO Metadata
    focus_keyword = models.CharField(max_length=100, blank=True)
    meta_title = models.CharField(max_length=255, blank=True, help_text="Defaults to post title if left empty")
    meta_description = models.TextField(blank=True)
    canonical_url = models.URLField(blank=True)

    # SEO Analysis (Auto-calculated read-only fields)
    word_count = models.PositiveIntegerField(default=0, editable=False)
    read_time_minutes = models.PositiveIntegerField(default=0, editable=False)
    internal_links_count = models.PositiveIntegerField(default=0, editable=False)
    external_links_count = models.PositiveIntegerField(default=0, editable=False)
    seo_score = models.PositiveIntegerField(default=0, editable=False, help_text="Rank Math style score 0-100")

    class Meta:
        ordering = ['-published_at', '-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)

        if not self.meta_title:
            self.meta_title = self.title

        self._analyze_content()
        super().save(*args, **kwargs)

    def _analyze_content(self):
        """Analyze content for SEO and readability like Rank Math."""
        if not self.content:
            self.word_count = 0
            self.read_time_minutes = 0
            self.internal_links_count = 0
            self.external_links_count = 0
            self.seo_score = 0
            return

        soup = BeautifulSoup(self.content, 'html.parser')
        text = soup.get_text()
        words = text.split()
        
        # Word count & Read time
        self.word_count = len(words)
        self.read_time_minutes = max(1, self.word_count // 200) # Avg 200 wpm

        # Links counting
        internal_count = 0
        external_count = 0
        app_domain = 'howzzat.pk' # Hardcoded domain for internal link check

        for link in soup.find_all('a'):
            href = link.get('href', '')
            if href.startswith('/') or app_domain in href:
                internal_count += 1
            elif href.startswith('http'):
                external_count += 1

        self.internal_links_count = internal_count
        self.external_links_count = external_count

        # Basic SEO Scoring (0-100)
        score = 0
        if self.focus_keyword:
            keyword_lower = self.focus_keyword.lower()
            
            # Keyword in Title (20 pts)
            if keyword_lower in self.title.lower():
                score += 20
                
            # Keyword in Meta Description (20 pts)
            if self.meta_description and keyword_lower in self.meta_description.lower():
                score += 20
                
            # Content length > 300 words (20 pts)
            if self.word_count > 300:
                score += 20
                
            # Has internal links (10 pts)
            if self.internal_links_count > 0:
                score += 10
                
            # Has external links (10 pts)
            if self.external_links_count > 0:
                score += 10
                
            # Has featured image (20 pts)
            if self.featured_image:
                score += 20
        else:
            # If no focus keyword, give points for general good practices
            if self.word_count > 300: score += 40
            if self.internal_links_count > 0: score += 20
            if self.external_links_count > 0: score += 20
            if self.featured_image: score += 20

        self.seo_score = min(100, score)

    def __str__(self):
        return self.title
