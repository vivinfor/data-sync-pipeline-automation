import calendar
from datetime import date, timedelta
from django.db.models import Count, Q
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from .models import WorkItem, WorkItemHistory, WorkItemSummary, DeliveryProgress


@receiver(pre_save, sender=WorkItem)
def track_state_change(sender, instance, **kwargs):
    """
    Verifica se houve alteração no estado do WorkItem para atualizar WorkItemHistory.
    """
    if instance.pk:
        try:
            previous = WorkItem.objects.get(pk=instance.pk)
            if previous.state != instance.state:
                WorkItemHistory.objects.create(
                    work_item=instance,
                    state=instance.state,
                    changed_date=instance.changed_date
                )
        except WorkItem.DoesNotExist:
            pass


@receiver(post_save, sender=WorkItem)
def calculate_lead_time(sender, instance, created, **kwargs):
    """
    Calcula o lead_time para um WorkItem resolvido, se ainda não calculado.
    """
    if instance.resolved_date and not instance.lead_time:
        created_date = instance.created_date
        resolved_date = instance.resolved_date
        if created_date and resolved_date and created_date <= resolved_date:
            lead_time = sum(1 for day in range((resolved_date - created_date).days + 1)
                            if (created_date + timedelta(days=day)).weekday() < 5)  # Exclui fins de semana
            WorkItem.objects.filter(pk=instance.pk).update(lead_time=lead_time)


@receiver(post_save, sender=WorkItem)
def update_workitemsummary_and_deliveryprogress(sender, instance, created, **kwargs):
    """
    Atualiza ou cria entradas em WorkItemSummary e DeliveryProgress com base no WorkItem salvo.
    """
    # Determinar o mês de resolução (para agregação)
    if instance.resolved_date:
        resolved_month = instance.resolved_date.replace(day=1)  # Definindo o mês para agregação

        # Atualizar ou criar o resumo na tabela WorkItemSummary
        summary, created = WorkItemSummary.objects.get_or_create(
            type=instance.type,
            created_date=resolved_month
        )
        
        # Atualizar o total de WorkItems por tipo
        summary.total_count = WorkItem.objects.filter(type=instance.type, resolved_date__month=resolved_month.month).count()
        summary.active_count = WorkItem.objects.filter(type=instance.type, state='Active', resolved_date__month=resolved_month.month).count()
        summary.closed_count = WorkItem.objects.filter(type=instance.type, state='Closed', resolved_date__month=resolved_month.month).count()
        
        # Recalcular o percentual de fechamento (closed_percentage)
        total_items = summary.total_count
        closed_items = summary.closed_count
        if total_items > 0:
            summary.closed_percentage = (closed_items / total_items) * 100
        else:
            summary.closed_percentage = 0
        
        # Salvar o resumo
        summary.save()

        # Atualizar a tabela DeliveryProgress
        # Cria ou atualiza a entrada de DeliveryProgress para o mês
        delivery_progress, created = DeliveryProgress.objects.get_or_create(
            month=resolved_month,
            type=instance.type
        )

        # Atualizar progresso
        delivery_progress.total_items = WorkItem.objects.filter(
            type=instance.type,
            resolved_date__month=resolved_month.month
        ).count()

        delivery_progress.closed_items = WorkItem.objects.filter(
            type=instance.type,
            state='Closed',
            resolved_date__month=resolved_month.month
        ).count()

        # Salvar a entrega progressiva
        delivery_progress.save()

