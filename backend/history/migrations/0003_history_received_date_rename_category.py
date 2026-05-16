from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("history", "0002_history_culture_base"),
    ]

    operations = [
        migrations.RenameField(
            model_name="history",
            old_name="description",
            new_name="category",
        ),
        migrations.AddField(
            model_name="history",
            name="received",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="history",
            name="date",
            field=models.DateField(default=django.utils.timezone.localdate),
        ),
    ]
