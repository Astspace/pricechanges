from django.db import models
from django.urls import reverse


class Items(models.Model):
    id_wb = models.IntegerField(blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    brand = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id'])
        ]

    def get_absolute_url(self):
        return reverse('item', kwargs={'item_slug': self.slug})
