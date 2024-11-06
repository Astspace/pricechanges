# Generated by Django 5.1.2 on 2024-11-06 06:59

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_marketplace_items_mt_place'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='items',
            name='mt_place',
        ),
        migrations.AddField(
            model_name='items',
            name='mtplace',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='main.marketplace'),
            preserve_default=False,
        ),
    ]
