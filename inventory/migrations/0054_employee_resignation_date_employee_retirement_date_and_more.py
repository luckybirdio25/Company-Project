# Generated by Django 5.2.2 on 2025-06-11 08:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0053_remove_employee_is_active_employee_employment_status_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='resignation_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Resignation'),
        ),
        migrations.AddField(
            model_name='employee',
            name='retirement_date',
            field=models.DateField(blank=True, null=True, verbose_name='Date of Retirement'),
        ),
        migrations.AddField(
            model_name='employee',
            name='training_end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Training End Date'),
        ),
        migrations.AddField(
            model_name='employee',
            name='training_start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Training Start Date'),
        ),
        migrations.AlterField(
            model_name='employee',
            name='employment_status',
            field=models.CharField(choices=[('employed', 'Employed'), ('retired', 'Retired'), ('resigned', 'Resigned'), ('training', 'Training')], default='employed', max_length=10, verbose_name='Employment Status'),
        ),
    ]
