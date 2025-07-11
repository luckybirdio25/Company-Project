# Generated by Django 5.2.1 on 2025-05-25 13:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0050_alter_assethistory_date_alter_department_created_at_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='role',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='userprofile',
            options={'ordering': ['user__username']},
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='employee',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='last_activity',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='last_login',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='department',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.department'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='team',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.team'),
        ),
        migrations.AlterField(
            model_name='role',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='role',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='inventory.role'),
        ),
    ]
