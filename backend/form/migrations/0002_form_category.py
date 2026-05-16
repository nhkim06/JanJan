from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("form", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="form",
            name="category",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
    ]
