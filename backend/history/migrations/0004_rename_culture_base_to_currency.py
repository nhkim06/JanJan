from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("history", "0003_history_received_date_rename_category"),
    ]

    operations = [
        migrations.RenameField(
            model_name="history",
            old_name="culture_base",
            new_name="currency",
        ),
    ]
