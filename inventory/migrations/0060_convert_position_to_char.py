from django.db import migrations, models

def convert_position_to_char(apps, schema_editor):
    Employee = apps.get_model('inventory', 'Employee')
    Position = apps.get_model('inventory', 'Position')
    
    for employee in Employee.objects.all():
        if employee.position_id:  # If there's a position ID
            try:
                position = Position.objects.get(id=employee.position_id)
                employee.position = position.name
            except Position.DoesNotExist:
                employee.position = "Unknown Position"
        else:
            employee.position = "No Position"
        employee.save()

class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0058_alter_employee_options_alter_team_options_and_more'),
    ]

    operations = [
        migrations.RunPython(convert_position_to_char),
        migrations.AlterField(
            model_name='employee',
            name='position',
            field=models.CharField(max_length=100),
        ),
    ] 