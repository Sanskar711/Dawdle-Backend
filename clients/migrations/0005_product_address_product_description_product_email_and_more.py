# Generated by Django 4.2.14 on 2024-08-08 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("clients", "0004_remove_product_use_cases_usecase_product"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="address",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="product",
            name="description",
            field=models.TextField(default=""),
        ),
        migrations.AddField(
            model_name="product",
            name="email",
            field=models.EmailField(default="", max_length=254),
        ),
        migrations.AddField(
            model_name="product",
            name="linkedin_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="location",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="product",
            name="logo_url",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="product",
            name="organization",
            field=models.CharField(default="", max_length=255),
        ),
        migrations.AddField(
            model_name="product",
            name="phone",
            field=models.CharField(default="", max_length=20),
        ),
        migrations.AddField(
            model_name="product",
            name="website_url",
            field=models.URLField(default=""),
        ),
        migrations.CreateModel(
            name="Video",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                ("url", models.URLField()),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="videos",
                        to="clients.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ReferenceSite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("url", models.URLField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reference_sites",
                        to="clients.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="DownloadableResource",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("url", models.URLField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="resources",
                        to="clients.product",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ActionButton",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=50)),
                ("url", models.URLField()),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="action_buttons",
                        to="clients.product",
                    ),
                ),
            ],
        ),
    ]
