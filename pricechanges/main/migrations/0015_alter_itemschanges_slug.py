# Generated by Django 5.1.2 on 2024-12-05 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_alter_items_name_itemschanges'),
    ]

    operations = [
        migrations.AlterField(
            model_name='itemschanges',
            name='slug',
            field=models.SlugField(max_length=255),
        ),
    ]
