# Generated manually to fix bus schema conflicts

from django.db import migrations


def drop_legacy_bus_columns(apps, schema_editor):
    # Only for legacy PostgreSQL databases that ended up with BOTH the old and
    # new columns. On a fresh database the old columns are still needed:
    # migration 0004 renames registration_number -> license_plate and
    # manufacturer -> make, so dropping them here would break it.
    if schema_editor.connection.vendor != 'postgresql':
        return
    with schema_editor.connection.cursor() as cursor:
        cols = {c.name for c in schema_editor.connection.introspection.get_table_description(
            cursor, 'companies_bus')}
    if 'license_plate' in cols and 'registration_number' in cols:
        schema_editor.execute("ALTER TABLE companies_bus DROP COLUMN registration_number;")
    if 'make' in cols and 'manufacturer' in cols:
        schema_editor.execute("ALTER TABLE companies_bus DROP COLUMN manufacturer;")


def restore_legacy_bus_columns(apps, schema_editor):
    pass  # nothing to restore: forward step only removes duplicate columns


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_driver'),
    ]

    operations = [
        migrations.RunPython(drop_legacy_bus_columns, restore_legacy_bus_columns),
    ]
