# Generated by Django 4.1.7 on 2023-03-07 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("meleapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="post",
            name="slug",
            field=models.SlugField(max_length=250, unique_for_date="publish"),
        ),
    ]
