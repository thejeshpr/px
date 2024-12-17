from django.db import models
import uuid

from django.template.defaultfilters import slugify
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        super(Category, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('crawler:category-detail', kwargs={"pk": self.pk})


class SiteConf(models.Model):
    base_url = models.CharField(max_length=250, blank=True, null=True, db_index=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, related_name='site_confs', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    enabled = models.BooleanField(default=True, db_index=True)
    extra_data_json = models.TextField(blank=True, null=True, default="{}")
    icon = models.CharField(max_length=50, default='las la-question-circle', blank=True, null=True)
    is_locked = models.BooleanField(default=False, db_index=True)
    name = models.CharField(max_length=50, unique=True, db_index=True)
    slug = models.SlugField(max_length=50, unique=True, db_index=True)
    notes = models.TextField(blank=True, null=True)
    ns_flag = models.BooleanField(default=False, db_index=True)
    scraper_name = models.CharField(max_length=25, blank=True, null=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return f'<SiteConf: {self.name}>'

    def save(self, *args, **kwargs):
        self.name = self.name.lower()
        self.slug = slugify(self.name)
        super(SiteConf, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('crawler:siteconf-detail', kwargs={'pk': self.pk})


class Job(models.Model):
    JOB_STATUS = (
        ('NEW', 'NEW'),
        ('WAITING', 'WAITING'),
        ('RUNNING', 'RUNNING'),
        ('SUCCESS', 'SUCCESS'),
        ('ERROR', 'ERROR'),
        ('NO-ITEM', 'NO-ITEM')
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    error = models.TextField(blank=True, null=True)
    elapsed_time = models.IntegerField(blank=True, null=True)
    site_conf = models.ForeignKey('SiteConf', on_delete=models.CASCADE, related_name='jobs', db_index=True)
    status = models.CharField(max_length=20, choices=JOB_STATUS, default="NEW", db_index=True)

    class Meta:
        indexes = [
            models.Index(fields=['status', 'site_conf']),  # Composite index for filtering by status/site_conf
        ]

    def get_absolute_url(self):
        return reverse('crawler:job-detail', kwargs={'pk': self.pk})


class Item(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    data = models.TextField(blank=True, null=True)
    is_bookmarked = models.BooleanField(default=False, db_index=True)
    job = models.ForeignKey('Job', on_delete=models.CASCADE, related_name='items', db_index=True)
    name = models.CharField(max_length=500, db_index=True)
    site_conf = models.ForeignKey('SiteConf', on_delete=models.CASCADE, related_name='items', db_index=True)
    unique_key = models.CharField(max_length=2500, unique=True)
    updated_at = models.DateTimeField(auto_now=True)
    url = models.URLField(blank=True, null=True, max_length=2500, db_index=True)

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'<Item: {self.name}>'

    class Meta:
        indexes = [
            models.Index(fields=['is_bookmarked', 'site_conf']),  # Composite index for filtering
            models.Index(fields=['name', 'created_at']),  # Sorting/filtering by name and creation time
        ]


# class ExtraItemData(models.Model):
#     created_at = models.DateTimeField(auto_now_add=True, db_index=True)
#     item = models.ForeignKey('Item', on_delete=models.CASCADE, related_name='extra_data', db_index=True)
#     data = models.CharField(max_length=2000, blank=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True)


class ConfigValues(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    key = models.CharField(max_length=20, blank=True, null=True, unique=True, db_index=True)
    val = models.CharField(max_length=250, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.key

    def __repr__(self):
        return f'<ConfigValue: {self.key}>'

    def save(self, *args, **kwargs):
        self.key = self.key.lower()
        super(ConfigValues, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('crawler:config-value-detail', kwargs={'pk': self.pk})
