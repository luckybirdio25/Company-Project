# Generated by Django 5.1.3 on 2025-05-19 17:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0026_itasset_built_in_speakers_itasset_connection_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='company',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='employees', to='inventory.ownercompany'),
        ),
    ]
