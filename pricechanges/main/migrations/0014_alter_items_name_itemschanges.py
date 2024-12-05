# Generated by Django 5.1.2 on 2024-12-05 06:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_items_item_url_alter_items_mtplace'),
    ]

    operations = [
        migrations.AlterField(
            model_name='items',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Наименование'),
        ),
        migrations.CreateModel(
            name='ItemsChanges',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_create', models.DateTimeField(auto_now_add=True, verbose_name='Время добавления изменения')),
                ('name', models.CharField(max_length=255, verbose_name='Наименование')),
                ('slug', models.SlugField(max_length=255, unique=True)),
                ('feedbacks', models.IntegerField(blank=True, null=True, verbose_name='Обновленные отзывы')),
                ('price', models.IntegerField(blank=True, null=True, verbose_name='Измененная стоимость')),
                ('rating', models.FloatField(blank=True, null=True, verbose_name='Обновленный рейтинг')),
                ('volume', models.IntegerField(blank=True, null=True, verbose_name='Обновленные остатки на складе')),
                ('item_relations', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='main.items', verbose_name='Основной товар')),
            ],
            options={
                'verbose_name': 'Обновленные товары',
                'verbose_name_plural': 'Обновленные товары',
                'ordering': ['-id'],
                'indexes': [models.Index(fields=['-id'], name='main_itemsc_id_bb4196_idx')],
            },
        ),
    ]