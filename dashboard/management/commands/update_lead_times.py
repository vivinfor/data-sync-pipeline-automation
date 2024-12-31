from django.core.management.base import BaseCommand

from dashboard.utils import update_lead_times

class Command(BaseCommand):
    help = 'Atualiza os valores de lead_time para WorkItems existentes'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando atualização de lead time...")
        update_lead_times()
        self.stdout.write("Atualização concluída!")
