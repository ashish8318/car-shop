# Generated by Django 4.2.2 on 2023-06-25 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='country',
            name='gst_chrages',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='state',
            name='gst_chrages',
            field=models.FloatField(default=0),
        ),
    ]
