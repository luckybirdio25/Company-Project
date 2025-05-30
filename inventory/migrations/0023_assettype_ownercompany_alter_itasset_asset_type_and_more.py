# Generated by Django 5.1.3 on 2025-05-18 18:26

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0022_alter_employee_phone_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('display_name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Asset Type',
                'verbose_name_plural': 'Asset Types',
                'ordering': ['display_name'],
            },
        ),
        migrations.CreateModel(
            name='OwnerCompany',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Owner Company',
                'verbose_name_plural': 'Owner Companies',
                'ordering': ['name'],
            },
        ),
        migrations.AlterField(
            model_name='itasset',
            name='asset_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.assettype'),
        ),
        migrations.AlterField(
            model_name='itasset',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='inventory.ownercompany'),
        ),
    ]
