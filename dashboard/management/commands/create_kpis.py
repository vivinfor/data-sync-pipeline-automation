import logging
import calendar
from datetime import date

from django.core.management.base import BaseCommand

from dashboard.models import KPI


logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Cadastra os KPIs necessários para PerformanceView e DeliveriesView.'

    def handle(self, *args, **options):
        today = date.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = self.get_last_day_of_month(today)

        performance_kpis = [
            {
                "name": "Average Lead Time",
                "description": "Lead time médio neste mês.",
                "target_value": 10.00,
                "metric_type": "count",
                "work_item_type": None, 
            },
            {
                "name": "Minimum Lead Time",
                "description": "Menor lead time neste mês.",
                "target_value": 5.00,
                "metric_type": "count",
                "work_item_type": None,
            },
            {
                "name": "Maximum Lead Time",
                "description": "Maior lead time neste mês.",
                "target_value": 15.00,
                "metric_type": "count",
                "work_item_type": None,
            },
        ]

        deliveries_kpis = [
            {
                "name": "Rework Percentage",
                "description": "Proporção de bugs fechados em relação a user stories fechadas neste mês.",
                "target_value": 20.00,
                "metric_type": "percentage",
                "work_item_type": None,
            },
            {
                "name": "Minimum Rework Percentage",
                "description": "Menor % de rework neste mês.",
                "target_value": 5.00,
                "metric_type": "percentage",
                "work_item_type": None,
            },
            {
                "name": "Maximum Rework Percentage",
                "description": "Maior % de rework neste mês.",
                "target_value": 30.00,
                "metric_type": "percentage",
                "work_item_type": None,
            },
        ]

        all_kpis = performance_kpis + deliveries_kpis

        for kpi_data in all_kpis:
            try:
                kpi, created = KPI.objects.get_or_create(
                    name=kpi_data["name"],
                    start_date=first_day_of_month,
                    end_date=last_day_of_month,
                    defaults={
                        "description": kpi_data["description"],
                        "target_value": kpi_data["target_value"],
                        "metric_type": kpi_data["metric_type"],
                        "current_value": 0.0,  
                        "work_item_type": kpi_data["work_item_type"],
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"KPI '{kpi.name}' criado com sucesso."))
                else:
                    self.stdout.write(self.style.WARNING(f"KPI '{kpi.name}' já existe para este mês."))
            except Exception as e:
                logger.error(f"Erro ao criar KPI '{kpi_data['name']}': {e}")
                self.stdout.write(self.style.ERROR(f"Erro ao criar KPI '{kpi_data['name']}': {e}"))

        self.stdout.write(self.style.SUCCESS('Todos os KPIs necessários foram cadastrados.'))

    def get_last_day_of_month(self, any_day):
        last_day = calendar.monthrange(any_day.year, any_day.month)[1]
        return any_day.replace(day=last_day)
