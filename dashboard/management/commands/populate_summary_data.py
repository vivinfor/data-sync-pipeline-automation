from django.core.management.base import BaseCommand
from django.db.models import Count, Q, F
from django.db.models.functions import TruncMonth
from datetime import datetime
from ...models import WorkItem, DeliveryProgress, BacklogSummary


class Command(BaseCommand):
    help = 'Popula as tabelas DeliveryProgress e BacklogSummary com base em WorkItem'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando a carga de dados agregados...'))

        # Limpar dados antigos
        self.stdout.write('Limpando dados antigos...')
        DeliveryProgress.objects.all().delete()
        self.stdout.write('Dados antigos da tabela DeliveryProgress limpos.')

        BacklogSummary.objects.all().delete()
        self.stdout.write('Dados antigos da tabela BacklogSummary limpos.')

        # Populando DeliveryProgress
        self.stdout.write('Populando DeliveryProgress...')
        self._populate_delivery_progress()

        # Populando BacklogSummary
        self.stdout.write('Populando BacklogSummary...')
        self._populate_backlog_summary()

    def _populate_delivery_progress(self):
        """Popula a tabela DeliveryProgress com base nos WorkItems"""
        # Agregando dados por mês e tipo de WorkItem
        current_year = datetime.today().year
        work_items = WorkItem.objects.filter(
            archived=False, 
            resolved_date__isnull=False,
            created_date__year=current_year  # Filtro pelo ano
        )

        # Truncando a data de `created_date` e `resolved_date` para comparar apenas ano e mês
        summaries = work_items.annotate(
            created_month=TruncMonth('created_date'),  # Truncando para o mês de criação
            resolved_month=TruncMonth('resolved_date')  # Truncando para o mês de resolução
        ).values('resolved_month', 'type').annotate(
            total_items=Count('id', filter=Q(created_month=F('resolved_month'))),
            closed_items=Count('id', filter=Q(resolved_month=F('resolved_month')))
        )

        # Inserindo ou atualizando os dados agregados
        for summary in summaries:
            # Salvar ou atualizar a tabela DeliveryProgress
            DeliveryProgress.objects.update_or_create(
                month=summary['resolved_month'],  # Utilizando o mês de resolução
                type=summary['type'],
                defaults={
                    'total_items': summary['total_items'],
                    'closed_items': summary['closed_items']
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Tabela DeliveryProgress populada!'))

    def _populate_backlog_summary(self):
        """Popula a tabela BacklogSummary com base nos WorkItems"""
        current_year = datetime.today().year
        work_items = WorkItem.objects.filter(
            archived=False, 
            resolved_date__isnull=False,
            created_date__year=current_year
        )

        # Agregando backlog por mês e tipo
        summaries = work_items.annotate(
            month=TruncMonth('created_date')
        ).values('month', 'type').annotate(
            backlog_count=Count('id')
        )

        # Inserindo ou atualizando os dados agregados
        for summary in summaries:
            BacklogSummary.objects.update_or_create(
                month=summary['month'],
                type=summary['type'],
                year=current_year,
                defaults={
                    'backlog_count': summary['backlog_count']
                }
            )
        
        self.stdout.write(self.style.SUCCESS('Tabela BacklogSummary populada!'))
