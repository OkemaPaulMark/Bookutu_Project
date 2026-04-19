# Generated manually to fix bus schema conflicts

from django.db import migrations


def drop_legacy_bus_columns(apps, schema_editor):
    # Only run on PostgreSQL where these legacy columns may exist
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute("ALTER TABLE companies_bus DROP COLUMN IF EXISTS registration_number;")
    schema_editor.execute("ALTER TABLE companies_bus DROP COLUMN IF EXISTS manufacturer;")


def restore_legacy_bus_columns(apps, schema_editor):
    # Only run on PostgreSQL
    if schema_editor.connection.vendor != 'postgresql':
        return
    schema_editor.execute("ALTER TABLE companies_bus ADD COLUMN registration_number VARCHAR(50);")
    schema_editor.execute("ALTER TABLE companies_bus ADD COLUMN manufacturer VARCHAR(100);")


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_driver'),
    ]

    operations = [
        migrations.RunPython(drop_legacy_bus_columns, restore_legacy_bus_columns),
    ]
