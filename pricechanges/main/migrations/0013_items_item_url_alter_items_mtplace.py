# Generated by Django 5.1.2 on 2024-12-01 20:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_items_mtplace'),
    ]

    operations = [
        migrations.AddField(
            model_name='items',
            name='item_url',
            field=models.URLField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='items',
            name='mtplace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='main.marketplace', verbose_name='Маркетплейс'),
        ),
    ]