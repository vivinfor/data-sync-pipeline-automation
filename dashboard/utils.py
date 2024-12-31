from datetime import timedelta
from django.db.models.functions import TruncMonth
from django.db.models import Min, Max, Avg, Count

from .models import WorkItem, WorkItemSummary


def business_days_between(start_date, end_date):
    """Calcula o número de dias úteis entre duas datas."""
    if not start_date or not end_date or start_date > end_date:
        return 0
    day_count = 0
    current_date = start_date
    while current_date <= end_date:
        if current_date.weekday() < 5:  # Segunda (0) a Sexta (4)
            day_count += 1
        current_date += timedelta(days=1)
    return day_count


def calculate_summary():
    """Calcula os dados de resumo para WorkItemSummary de forma genérica."""
    summaries = []

    # Obter dinamicamente os tipos únicos de WorkItems
    work_item_types = WorkItem.objects.values_list('type', flat=True).distinct()

    for item_type in work_item_types:
        # Resumo geral por tipo
        total_count = WorkItem.objects.filter(type=item_type).count()
        closed_count = WorkItem.objects.filter(type=item_type, resolved_date__isnull=False).count()
        active_count = total_count - closed_count

        # Calcular o tempo médio de resolução para os itens resolvidos
        resolved_items = WorkItem.objects.filter(type=item_type, resolved_date__isnull=False)
        lead_times = [
            business_days_between(item.created_date, item.resolved_date)
            for item in resolved_items
        ]
        average_lead_time = sum(lead_times) / len(lead_times) if lead_times else None

        # Criar resumo
        summaries.append(WorkItemSummary(
            type=item_type,
            total_count=total_count,
            active_count=active_count,
            closed_count=closed_count,
            closed_percentage=(closed_count / total_count * 100) if total_count else 0,
            average_lead_time=average_lead_time,
        ))

    return summaries


def calculate_monthly_summary():
    """Calcula os dados de resumo por tipo e mês de forma genérica."""
    summaries = []

    # Obter dinamicamente os tipos únicos de WorkItems
    work_item_types = WorkItem.objects.values_list('type', flat=True).distinct()

    for item_type in work_item_types:
        # Agrupar itens por mês
        grouped_items = WorkItem.objects.filter(
            type=item_type, resolved_date__isnull=False
        ).annotate(
            month=TruncMonth('resolved_date')
        ).values('month').annotate(
            total_count=Count('id'),
            closed_count=Count('id'),
        )

        for group in grouped_items:
            # Filtrar itens resolvidos no mês para cálculo do tempo médio
            resolved_items = WorkItem.objects.filter(
                type=item_type,
                resolved_date__month=group['month'].month,
                resolved_date__year=group['month'].year,
            )
            lead_times = [
                business_days_between(item.created_date, item.resolved_date)
                for item in resolved_items
            ]
            average_lead_time = sum(lead_times) / len(lead_times) if lead_times else None

            # Calcular total de itens ativos no mês
            active_count = WorkItem.objects.filter(
                type=item_type,
                resolved_date__isnull=True,
                created_date__month=group['month'].month,
                created_date__year=group['month'].year,
            ).count()

            summaries.append(WorkItemSummary(
                type=item_type,
                total_count=group['total_count'],
                active_count=active_count,
                closed_count=group['closed_count'],
                closed_percentage=(group['closed_count'] / group['total_count'] * 100) if group['total_count'] else 0,
                average_lead_time=average_lead_time,
                created_date=group['month'],
            ))

    return summaries


def update_lead_times():
    """Atualiza os valores de lead_time para todos os WorkItems com resolved_date preenchido."""
    work_items = WorkItem.objects.filter(resolved_date__isnull=False, lead_time__isnull=True)
    updated_count = 0

    for item in work_items:
        if item.created_date and item.resolved_date:
            # Calcular o lead time considerando dias úteis
            lead_time = business_days_between(item.created_date, item.resolved_date)
            item.lead_time = lead_time
            item.save(update_fields=['lead_time'])
            updated_count += 1

    print(f"{updated_count} registros atualizados com lead time.")



def calcular_lead_time():
    # Filtrando apenas os WorkItems resolvidos, onde resolved_date não é nulo
    work_items_resolvidos = WorkItem.objects.filter(resolved_date__isnull=False)

    # Calculando os valores mínimo, máximo e médio do lead time
    lead_time_min = work_items_resolvidos.aggregate(Min('lead_time'))['lead_time__min']
    lead_time_max = work_items_resolvidos.aggregate(Max('lead_time'))['lead_time__max']
    lead_time_avg = work_items_resolvidos.aggregate(Avg('lead_time'))['lead_time__avg']

    return lead_time_min, lead_time_max, lead_time_avg

