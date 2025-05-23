# Generated by Django 5.2.1 on 2025-05-21 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0030_assethistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assethistory',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('assigned', 'Assigned'), ('maintenance', 'Under Maintenance'), ('return', 'Return'), ('retired', 'Retired')], max_length=20),
        ),
        migrations.AlterField(
            model_name='itasset',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('assigned', 'Assigned'), ('maintenance', 'Under Maintenance'), ('return', 'Return'), ('retired', 'Retired')], default='available', max_length=20),
        ),
    ]
