# Generated by Django 5.1.2 on 2025-01-05 12:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_alter_itemschanges_item_relations'),
    ]

    operations = [
        migrations.AddField(
            model_name='items',
            name='out',
            field=models.BooleanField(default=False, verbose_name='Закончился'),
        ),
    ]
