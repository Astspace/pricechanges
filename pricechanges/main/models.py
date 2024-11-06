from django.db import models
from django.urls import reverse


class ActualItemsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(id_item__isnull=False)


class Items(models.Model):
    id_item = models.IntegerField(blank=True)
    name = models.CharField(max_length=255)
    content = models.CharField(max_length=255, blank=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    brand = models.CharField(max_length=255)
    mtplace = models.ForeignKey('Marketplace', on_delete=models.PROTECT, related_name='items')
    tags = models.ManyToManyField('TagItem', blank=True, related_name='items')

    objects = models.Manager()
    actual = ActualItemsManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id'])
        ]

    def get_absolute_url(self):
        return reverse('item', kwargs={'item_slug': self.slug})

class Marketplace(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id'])
        ]

class TagItem(models.Model):
    tag = models.CharField(max_length=100, db_index=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})