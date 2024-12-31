
import logging
import plotly.io as pio
from datetime import datetime
import calendar

from django.db.models import Sum, Max, Min, F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView

from app.mixins import SidebarContextMixin
from dashboard.utils.plotly_charts import create_chart
from .models import BacklogSummary, WorkItemSummary

logger = logging.getLogger(__name__)


class DeliveriesView(SidebarContextMixin, TemplateView):
    """Dashboard de Deliveries com Gráficos de User Stories e Incidentes."""

    template_name = "dashboard/deliveries.html"

    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # ------------------------------
        # 1. Cards de Lead Time Médio
        # ------------------------------

        # Backlog Total
        backlog_user_story = BacklogSummary.objects.filter(type="UserStory").first()
        backlog_incident = BacklogSummary.objects.filter(type="Incident").first()
        total_backlog = (backlog_user_story.backlog_count if backlog_user_story else 0) + (
            backlog_incident.backlog_count if backlog_incident else 0
        )
        
        context['backlog_user_story'] = backlog_user_story.backlog_count if backlog_user_story else 0
        context['backlog_incident'] = backlog_incident.backlog_count if backlog_incident else 0

        # Proporção de Retrabalho
        context['rework_percentage'] = (
            (context['backlog_incident'] / total_backlog * 100) if total_backlog > 0 else 0
        )

        # ------------------------------
        # 2. Gráfico: Total de Entregas Mensalmente (User Story)
        # ------------------------------
        user_story_deliveries = WorkItemSummary.objects.filter(type='UserStory').order_by('year', 'month')
        delivery_months = [f"{calendar.month_abbr[p.month]}/{p.year}" for p in user_story_deliveries]
        total_deliveries = [p.total_count for p in user_story_deliveries]

        logger.debug(f"user_story_deliveries count: {user_story_deliveries.count()}")
        logger.debug(f"delivery_months: {delivery_months}")
        logger.debug(f"total_deliveries: {total_deliveries}")

        # Calcular o acumulado mês a mês
        accumulated_deliveries = []
        cumulative = 0
        for count in total_deliveries:
            cumulative += count
            accumulated_deliveries.append(cumulative)

        logger.debug(f"accumulated_deliveries: {accumulated_deliveries}")

        # Criar o gráfico combinado para User Stories
        user_story_fig = create_chart(
            chart_type='bar',
            x=delivery_months,
            y=total_deliveries,
            title="Total de Entregas Realizadas (User Story)",
            color='#3B82F6',
            trace_name='Entregas Realizadas',
            legend_position='top center'
        )

        user_story_fig = create_chart(
            chart_type='line',
            x=delivery_months,
            y=accumulated_deliveries,
            title="Total de Entregas Realizadas (User Story)",
            color='#1F2937',
            trace_name='Acumulado',
            secondary_y=True,
            fig=user_story_fig,

        )

        context['user_story_plot'] = pio.to_html(user_story_fig, full_html=False)

        # ------------------------------
        # 3. Gráfico: Total de Incidentes Resolvidos (Incident)
        # ------------------------------
        incident_deliveries = WorkItemSummary.objects.filter(type='Incident').order_by('year', 'month')
        incident_months = [f"{calendar.month_abbr[p.month]}/{p.year}" for p in incident_deliveries]
        total_incidents = [p.total_count for p in incident_deliveries]

        logger.debug(f"incident_deliveries count: {incident_deliveries.count()}")
        logger.debug(f"incident_months: {incident_months}")
        logger.debug(f"total_incidents: {total_incidents}")

        # Calcular o acumulado mês a mês
        accumulated_incidents = []
        cumulative_incident = 0
        for count in total_incidents:
            cumulative_incident += count
            accumulated_incidents.append(cumulative_incident)

        logger.debug(f"accumulated_incidents: {accumulated_incidents}")

        # Criar o gráfico combinado para Incidentes
        incident_fig = create_chart(
            chart_type='bar',
            x=incident_months,
            y=total_incidents,
            title="Total de Incidentes Resolvidos (Incident)",
            color='#3B82F6',
            trace_name='Incidentes Resolvidos',
            legend_position='top center'

        )

        incident_fig = create_chart(
            chart_type='line',
            x=incident_months,
            y=accumulated_incidents,
            title="Total de Incidentes Resolvidos (Incident)",
            color='#1F2937',
            trace_name='Acumulado',
            secondary_y=True,
            fig=incident_fig,

        )

        context['incident_plot'] = pio.to_html(incident_fig, full_html=False)

        return context

    def get_last_day_of_month(self, any_day):
        last_day = calendar.monthrange(any_day.year, any_day.month)[1]
        return any_day.replace(day=last_day)


class PerformanceView(SidebarContextMixin, TemplateView):
    """Dashboard de Performance com gráficos combinados e KPIs."""

    template_name = "dashboard/performance.html"

    @method_decorator(cache_page(60 * 15))  # Cache por 15 minutos
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Verifica o mês mais recente disponível
        latest_summary = WorkItemSummary.objects.order_by('-year', '-month').first()
        if latest_summary:
            latest_year = latest_summary.year
            latest_month = latest_summary.month
        else:
            today = datetime.today()
            latest_year = today.year
            latest_month = today.month

        # ------------------------------
        # Cards de KPIs
        # ------------------------------
        work_item_summaries = WorkItemSummary.objects.filter(
            year=latest_year,
            month=latest_month
        )

        if work_item_summaries.exists():
            # KPIs de Lead Time para User Story
            lead_time_summaries_user_story = work_item_summaries.filter(type='UserStory')
            if lead_time_summaries_user_story.exists():
                weighted_sum_user_story = lead_time_summaries_user_story.aggregate(
                    weighted_sum=Sum(F('average_lead_time') * F('total_count'))
                )['weighted_sum'] or 0
                total_counts_user_story = lead_time_summaries_user_story.aggregate(
                    total=Sum('total_count')
                )['total'] or 1  # Evitar divisão por zero
                kpi_avg_lead_time_user_story = weighted_sum_user_story / total_counts_user_story

                kpi_min_lead_time_user_story = lead_time_summaries_user_story.aggregate(
                    min_lead=Min('average_lead_time')
                )['min_lead'] or 0

                kpi_max_lead_time_user_story = lead_time_summaries_user_story.aggregate(
                    max_lead=Max('average_lead_time')
                )['max_lead'] or 0
            else:
                kpi_avg_lead_time_user_story = 0
                kpi_min_lead_time_user_story = 0
                kpi_max_lead_time_user_story = 0

            # KPIs de Lead Time para Incident
            lead_time_summaries_incident = work_item_summaries.filter(type='Incident')
            if lead_time_summaries_incident.exists():
                weighted_sum_incident = lead_time_summaries_incident.aggregate(
                    weighted_sum=Sum(F('average_lead_time') * F('total_count'))
                )['weighted_sum'] or 0
                total_counts_incident = lead_time_summaries_incident.aggregate(
                    total=Sum('total_count')
                )['total'] or 1  # Evitar divisão por zero
                kpi_avg_lead_time_incident = weighted_sum_incident / total_counts_incident

                kpi_min_lead_time_incident = lead_time_summaries_incident.aggregate(
                    min_lead=Min('average_lead_time')
                )['min_lead'] or 0

                kpi_max_lead_time_incident = lead_time_summaries_incident.aggregate(
                    max_lead=Max('average_lead_time')
                )['max_lead'] or 0
            else:
                kpi_avg_lead_time_incident = 0
                kpi_min_lead_time_incident = 0
                kpi_max_lead_time_incident = 0

            # Adiciona os KPIs ao contexto
            context['kpi_avg_lead_time_user_story'] = kpi_avg_lead_time_user_story
            context['kpi_min_lead_time_user_story'] = kpi_min_lead_time_user_story
            context['kpi_max_lead_time_user_story'] = kpi_max_lead_time_user_story
            context['kpi_avg_lead_time_incident'] = kpi_avg_lead_time_incident
            context['kpi_min_lead_time_incident'] = kpi_min_lead_time_incident
            context['kpi_max_lead_time_incident'] = kpi_max_lead_time_incident

        # ------------------------------
        # Gráfico de Lead Time Médio Mensal
        # ------------------------------
        lead_time_summaries_user_story = WorkItemSummary.objects.filter(type='UserStory').order_by('year', 'month')
        lead_time_summaries_incident = WorkItemSummary.objects.filter(type='Incident').order_by('year', 'month')

        months = [f"{calendar.month_abbr[p.month]}/{p.year}" for p in lead_time_summaries_user_story]
        average_lead_times_user_story = [p.average_lead_time for p in lead_time_summaries_user_story]
        average_lead_times_incident = [p.average_lead_time for p in lead_time_summaries_incident]

        # Criar o gráfico de Lead Time Médio Mensal
        lead_time_fig = create_chart(
            chart_type='bar',
            x=months,
            y=average_lead_times_user_story,
            title="Lead Time Médio Mensal",
            x_title="Mês",
            y_title="Lead Time Médio (dias)",
            color='#1F2937',
            trace_name='User Story',
            legend_position='top center'
        )

        lead_time_fig = create_chart(
            chart_type='bar',
            x=months,
            y=average_lead_times_incident,
            title="Lead Time Médio Mensal",
            x_title="",
            y_title="",
            color='#3B82F6',
            trace_name='Incident',
            fig=lead_time_fig
        )

        context['lead_time_plot'] = pio.to_html(lead_time_fig, full_html=False)

        # ------------------------------
        # Gráfico de Backlog Mensal
        # ------------------------------
        backlog_summaries_user_story = BacklogSummary.objects.filter(type='UserStory').order_by('year', 'month')
        backlog_summaries_incident = BacklogSummary.objects.filter(type='Incident').order_by('year', 'month')

        backlog_months = [f"{calendar.month_abbr[p.month.month]}/{p.year}" for p in backlog_summaries_user_story]
        backlog_counts_user_story = [p.backlog_count for p in backlog_summaries_user_story]
        backlog_counts_incident = [p.backlog_count for p in backlog_summaries_incident]

        # Criar o gráfico de Backlog Mensal
        backlog_fig = create_chart(
            chart_type='bar',
            x=backlog_months,
            y=backlog_counts_user_story,
            title="Backlog Mensal",
            x_title="Mês",
            y_title="Backlog",
            color='#1F2937',
            trace_name='User Story',
            legend_position='top center'  # Definir a posição da legenda
        )

        backlog_fig = create_chart(
            chart_type='bar',
            x=backlog_months,
            y=backlog_counts_incident,
            title="Backlog Mensal",
            x_title="",
            y_title="",
            color='#3B82F6',
            trace_name='Incident',
            fig=backlog_fig
        )

        context['backlog_plot'] = pio.to_html(backlog_fig, full_html=False)

        return context