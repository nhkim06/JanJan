from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("history", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="history",
            name="culture_base",
            field=models.CharField(default="ko", max_length=20),
        ),
    ]
