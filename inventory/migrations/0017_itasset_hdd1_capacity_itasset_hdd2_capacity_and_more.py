# Generated by Django 5.1.3 on 2025-05-12 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0016_alter_itasset_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='itasset',
            name='hdd1_capacity',
            field=models.CharField(blank=True, help_text='Primary Storage', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='itasset',
            name='hdd2_capacity',
            field=models.CharField(blank=True, help_text='Secondary Storage', max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='itasset',
            name='operating_system',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='itasset',
            name='os_version',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='itasset',
            name='processor',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='itasset',
            name='ram_size',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]
