# Generated by Django 2.1.5 on 2019-01-13 23:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0002_auto_20190113_2317'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartentry',
            name='cost',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
