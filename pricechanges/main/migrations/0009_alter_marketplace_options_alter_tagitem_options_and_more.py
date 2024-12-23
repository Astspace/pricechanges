# Generated by Django 5.1.2 on 2024-11-21 13:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_alter_items_options_items_time_create'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='marketplace',
            options={'ordering': ['-id'], 'verbose_name': 'Маркетплейсы', 'verbose_name_plural': 'Маркетплейсы'},
        ),
        migrations.AlterModelOptions(
            name='tagitem',
            options={'verbose_name': 'Тэги', 'verbose_name_plural': 'Тэги'},
        ),
        migrations.AlterField(
            model_name='items',
            name='brand',
            field=models.CharField(max_length=255, verbose_name='Бренд'),
        ),
        migrations.AlterField(
            model_name='items',
            name='content',
            field=models.CharField(blank=True, max_length=255, verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='items',
            name='id_item',
            field=models.IntegerField(blank=True, null=True, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='items',
            name='mtplace',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='items', to='main.marketplace', verbose_name='Маркетплейс'),
        ),
        migrations.AlterField(
            model_name='items',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Наиванование'),
        ),
        migrations.AlterField(
            model_name='items',
            name='time_create',
            field=models.DateTimeField(auto_now_add=True, verbose_name='Время добавления'),
        ),
        migrations.AlterField(
            model_name='marketplace',
            name='name',
            field=models.CharField(max_length=255, verbose_name='Наименование'),
        ),
        migrations.AlterField(
            model_name='tagitem',
            name='tag',
            field=models.CharField(db_index=True, max_length=100, verbose_name='Тэг'),
        ),
    ]
