# Generated by Django 2.2.2 on 2019-06-28 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('race', '0002_auto_20190628_1535'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cpprotocol',
            name='number',
            field=models.IntegerField(unique=True),
        ),
    ]
