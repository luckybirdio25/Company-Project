# Inventory Management System

A Django-based inventory management system for tracking IT assets, employees, and departments.

## Prerequisites

- Python 3.8 or higher
- PostgreSQL
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd inventory_app
```

2. Install required packages:
```bash
pip install django
pip install psycopg2
pip install openpyxl
```

## Database Setup

1. Create a PostgreSQL database:
```sql
CREATE DATABASE inventory_db_it;
```

2. Configure database settings in `inventory_app/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'inventory_db_it',
        'USER': 'postgres',
        'PASSWORD': 'P@ssw0rd',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## Initial Setup

1. Run migrations to create database tables:
```bash
python manage.py migrate
```

2. Create a superuser with admin role:
```bash
python manage.py createsuperuser
# Enter username (e.g., admin)
# Enter email (e.g., admin@example.com)
# Enter password (e.g., 123)
```

3. Set up admin role and profile:
```bash
python setup_admin.py
```

## Running the Project

### Local Development
To run the project locally:
```bash
python manage.py runserver
```
Access the application at: http://127.0.0.1:8000

### Network Access
To allow other computers in your network to access the application:

1. Find your IP address:
   - On Windows: Open CMD and type `ipconfig`
   - On Linux/Mac: Open terminal and type `ifconfig` or `ip addr`

2. Update `inventory_app/settings.py`:
```python
ALLOWED_HOSTS = ['your.ip.address', 'localhost', '127.0.0.1']
```

3. Run the server with your IP:
```bash
python manage.py runserver your.ip.address:8000
```

Other computers can access the application at: http://your.ip.address:8000

## Features

- IT Asset Management
- Employee Management
- Department Management
- Role-based Access Control
- Asset History Tracking
- Team Management
- User Management
- Data Import/Export

## Security Notes

- This is a development setup. For production:
  - Set DEBUG = False
  - Use a proper web server (e.g., Nginx, Apache)
  - Use a production-grade WSGI server (e.g., Gunicorn)
  - Change the default SECRET_KEY
  - Use strong passwords
  - Configure proper database security
