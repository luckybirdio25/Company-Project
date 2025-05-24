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

