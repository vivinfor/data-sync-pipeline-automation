from django.core.management.base import BaseCommand
from django.db.models import Count, Avg, F, Q
from django.utils.timezone import now
from dashboard.models import WorkItem, WorkItemSummary
from datetime import date

class Command(BaseCommand):
    help = 'Atualiza os resumos de WorkItems para refletir os dados mais recentes.'

    def handle(self, *args, **options):
        self.stdout.write("Iniciando a limpeza e carga dos dados de WorkItemSummary...")

        # Passo 1: Limpeza dos resumos existentes
        self.stdout.write("Limpando dados antigos na WorkItemSummary...")
        WorkItemSummary.objects.all().delete()
        self.stdout.write("Dados antigos limpos com sucesso!")

        # Passo 2: Cálculo dos novos dados agregados
        self.stdout.write("Calculando dados agregados...")

        # Filtro para obter apenas itens resolvidos
        work_items = WorkItem.objects.filter(archived=False, resolved_date__isnull=False)
        
        # Agregando dados por tipo de WorkItem e por mês (usando a data de resolução)
        summaries = work_items.annotate(
            year=F('resolved_date__year'),
            month=F('resolved_date__month')
        ).values('type', 'year', 'month').annotate(
            total_count=Count('id'),
            closed_count=Count('id', filter=Q(state='Resolved')),
            average_lead_time=Avg('lead_time', filter=Q(state='Resolved')),
        )

        # Passo 3: Inserção ou atualização dos dados agregados na tabela WorkItemSummary
        for summary in summaries:
            year = summary['year']
            month = summary['month']
            work_type = summary['type']

            # Calcular a porcentagem de itens fechados
            closed_percentage = (summary['closed_count'] / summary['total_count']) * 100 if summary['total_count'] > 0 else 0.0

            # Calcular a porcentagem de rework (reabertos e resolvidos novamente)
            rework_count = WorkItem.objects.filter(
                type=work_type,
                state='Resolved',
                resolved_date__year=year,
                resolved_date__month=month,
                archived=False
            ).filter(Q(state='Reopened')).count()
            rework_percentage = (rework_count / summary['total_count']) * 100 if summary['total_count'] > 0 else 0.0

            # Criar ou atualizar os resumos
            WorkItemSummary.objects.update_or_create(
                type=work_type,
                year=year,
                month=month,
                defaults={
                    'total_count': summary['total_count'],
                    'average_lead_time': summary['average_lead_time'] or 0.0,
                    'closed_percentage': closed_percentage,
                    'rework_percentage': rework_percentage
                }
            )

        self.stdout.write("Dados agregados carregados com sucesso!")
