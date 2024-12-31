import os
from django.contrib.auth.models import User
from dashboard.models import KPI

def create_super_user():
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@example.com", "adminpassword")
        print("Superuser created successfully.")

def populate_kpis():
    default_kpis = [
        {"name": "Delivery Trend", "description": "Track delivery trends over time."},
        {"name": "Lead Time", "description": "Measure lead times by work item type."},
        {"name": "Rework Cost", "description": "Calculate the cost of rework."}
    ]
    for kpi in default_kpis:
        KPI.objects.get_or_create(name=kpi["name"], defaults={"description": kpi["description"]})
    print("KPIs populated successfully.")

if __name__ == "__main__":
    print("Initializing database...")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")
    import django
    django.setup()
    create_super_user()
    populate_kpis()
    print("Database initialized successfully!")
