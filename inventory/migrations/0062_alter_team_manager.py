# Generated by Django 5.2.2 on 2025-06-16 09:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0061_merge_20250616_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='team',
            name='manager',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='managed_teams', to='inventory.employee'),
        ),
    ]
