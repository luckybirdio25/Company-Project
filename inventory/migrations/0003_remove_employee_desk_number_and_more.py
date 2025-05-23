# Generated by Django 5.1.3 on 2025-05-10 09:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0002_department_alter_itasset_options_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='desk_number',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='office_location',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='system_password',
        ),
        migrations.RemoveField(
            model_name='employee',
            name='system_username',
        ),
        migrations.AlterField(
            model_name='department',
            name='name',
            field=models.CharField(choices=[('warehouse', 'Warehouse'), ('hr', 'HR'), ('purchasing', 'Purchasing'), ('finance', 'Finance'), ('production', 'Production'), ('maintenance', 'Maintenance'), ('it', 'IT')], max_length=100),
        ),
        migrations.AlterField(
            model_name='itasset',
            name='name',
            field=models.CharField(default='Unknown Asset', max_length=100),
        ),
    ]
