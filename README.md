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

2. Create a superuser:
   **Note:** The `createsuperuser` command is now protected. It will prevent you from creating more than one superuser and will automatically assign the correct role and permissions.
```bash
python manage.py createsuperuser
# Follow the prompts to enter username, email, and password.
```

3. Set up admin role and profile:
   This step is no longer necessary as the `createsuperuser` command handles it automatically.
```bash
# python setup_admin.py (No longer needed)
```

4. Run the Project
```bash
python manage.py runserver
```

5. Access the application:
   Open your browser and navigate to `http://127.0.0.1:8000/`. Log in with the credentials you just created.