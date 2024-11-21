from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse


def translit_to_eng(s: str) -> str:
    d = {'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
         'е': 'e', 'ё': 'yo', 'ж': 'zh', 'з': 'z', 'и': 'i', 'к': 'k',
         'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r',
         'с': 's', 'т': 't', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch',
         'ш': 'sh', 'щ': 'shch', 'ь': '', 'ы': 'y', 'ъ': '', 'э': 'r', 'ю': 'yu', 'я': 'ya'}

    return "".join(map(lambda x: d[x] if d.get(x, False) else x, s.lower()))

class ActualItemsManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(id_item__isnull=False)


class Items(models.Model):
    id_item = models.IntegerField(blank=True, null=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Наиванование')
    content = models.CharField(max_length=255, blank=True, verbose_name='Описание')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    brand = models.CharField(max_length=255, verbose_name='Бренд')
    mtplace = models.ForeignKey('Marketplace', on_delete=models.PROTECT, related_name='items', verbose_name='Маркетплейс')
    tags = models.ManyToManyField('TagItem', blank=True, related_name='items')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')

    objects = models.Manager()
    actual = ActualItemsManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Товары'
        verbose_name_plural = 'Товары'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id'])
        ]

    def get_absolute_url(self):
        return reverse('item', kwargs={'item_slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(translit_to_eng(self.name))
        super().save(*args, **kwargs)

class Marketplace(models.Model):
    name = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Маркетплейсы'
        verbose_name_plural = 'Маркетплейсы'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id'])
        ]

class TagItem(models.Model):
    tag = models.CharField(max_length=100, db_index=True, verbose_name='Тэг')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)

    def __str__(self):
        return self.tag

    def get_absolute_url(self):
        return reverse('tag', kwargs={'tag_slug': self.slug})

    class Meta:
        verbose_name = 'Тэги'
        verbose_name_plural = 'Тэги'