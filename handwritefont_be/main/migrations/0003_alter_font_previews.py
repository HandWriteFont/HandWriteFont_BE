# Generated by Django 4.0.4 on 2022-06-08 06:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='font',
            name='previews',
            field=models.ManyToManyField(blank=True, related_name='preview', to='main.preview'),
        ),
    ]