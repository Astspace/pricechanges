# Generated by Django 5.1.2 on 2024-12-23 12:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_alter_items_owner'),
    ]

    operations = [
        migrations.AlterField(
            model_name='items',
            name='mtplace',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='items', to='main.marketplace', verbose_name='Маркетплейс'),
        ),
    ]
