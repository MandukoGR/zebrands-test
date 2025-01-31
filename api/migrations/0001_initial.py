# Generated by Django 5.1.2 on 2024-10-16 02:45

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "sku",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("brand", models.CharField(max_length=255)),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("views", models.IntegerField(default=0)),
            ],
        ),
    ]
