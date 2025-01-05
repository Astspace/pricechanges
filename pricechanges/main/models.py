from django.contrib.auth import get_user_model
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
        return super().get_queryset().filter(active=True)


class Items(models.Model):
    owner = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, related_name='items', null=True, default=None)
    id_item = models.IntegerField(blank=True, null=True, verbose_name='ID')
    name = models.CharField(max_length=255, verbose_name='Наименование')
    name_for_user = models.CharField(max_length=255, blank=True, null=True, verbose_name='Свое наименование')
    rating = models.FloatField(blank=True, null=True, verbose_name='Рейтинг')
    feedbacks = models.IntegerField(blank=True, null=True, verbose_name='Отзывы')
    volume = models.IntegerField(blank=True, null=True, verbose_name='Остатки на складе')
    slug = models.SlugField(max_length=255, unique=True, db_index=True)
    brand = models.CharField(max_length=255, verbose_name='Бренд')
    price = models.IntegerField(blank=True, null=True, verbose_name='Стоимость')
    last_price = models.IntegerField(blank=True, null=True, verbose_name='Последняя стоимость')
    mtplace = models.ForeignKey('Marketplace', null=True, blank=True, on_delete=models.SET_NULL, related_name='items', verbose_name='Маркетплейс')
    tags = models.ManyToManyField('TagItem', blank=True, related_name='items')
    item_url = models.URLField(max_length=255, blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления')
    out = models.BooleanField(default=False, verbose_name='Закончился')
    active = models.BooleanField(default=True)

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


class ItemsChanges(models.Model):
    item_relations = models.ForeignKey('Items', null=True, blank=True, on_delete=models.CASCADE, related_name='item_changes', verbose_name='Основной товар')
    time_create = models.DateTimeField(auto_now_add=True, verbose_name='Время добавления изменения')
    name = models.CharField(max_length=255, verbose_name='Наименование')
    slug = models.SlugField(max_length=255)
    feedbacks = models.IntegerField(blank=True, null=True, verbose_name='Обновленные отзывы')
    price = models.IntegerField(blank=True, null=True, verbose_name='Измененная стоимость')
    rating = models.FloatField(blank=True, null=True, verbose_name='Обновленный рейтинг')
    volume = models.IntegerField(blank=True, null=True, verbose_name='Обновленные остатки на складе')

    objects = models.Manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Обновленные товары'
        verbose_name_plural = 'Обновленные товары'
        ordering = ['-id']
        indexes = [
            models.Index(fields=['-id'])
        ]

    def get_absolute_url(self):
        return reverse('item', kwargs={'item_slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(translit_to_eng(self.name))
        super().save(*args, **kwargs)


class Profile(models.Model):
    user_relations = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='profile')
    telegram_id = models.IntegerField(blank=True, null=True, verbose_name='Telegram ID')
