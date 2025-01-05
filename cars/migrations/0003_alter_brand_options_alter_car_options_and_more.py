# Generated by Django 5.1.4 on 2025-01-05 09:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("cars", "0002_alter_car_name_alter_car_unique_together"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="brand",
            options={"ordering": ["name"]},
        ),
        migrations.AlterModelOptions(
            name="car",
            options={"ordering": ["brand", "name"]},
        ),
        migrations.AlterModelOptions(
            name="engine",
            options={
                "ordering": ["-cylinder_layout", "-cylinder_count", "-aspiration"]
            },
        ),
        migrations.AlterModelOptions(
            name="fueltype",
            options={"ordering": ["fuel_type"]},
        ),
        migrations.AlterModelOptions(
            name="tag",
            options={"ordering": ["category", "value"]},
        ),
        migrations.AlterModelOptions(
            name="tagcategory",
            options={"ordering": ["name"]},
        ),
        migrations.AlterUniqueTogether(
            name="tag",
            unique_together={("category", "value")},
        ),
    ]
