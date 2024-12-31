from django.contrib import admin
from .models import WorkItemHistory, KPI, DeliveryProgress, BacklogSummary

# Admin para WorkItem
class WorkItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'title', 'type', 'state', 'created_date', 'resolved_date', 'lead_time')
    list_filter = ('type', 'state', 'archived', 'created_date', 'changed_date', 'resolved_date')
    search_fields = ('title', 'external_id', 'type', 'state')
    ordering = ('-created_date',)
    date_hierarchy = 'created_date'

# Admin para WorkItemHistory
@admin.register(WorkItemHistory)
class WorkItemHistoryAdmin(admin.ModelAdmin):
    list_display = ('work_item', 'state', 'changed_date')
    list_filter = ('state', 'changed_date')
    search_fields = ('work_item__title', 'state')
    ordering = ('-changed_date',)
    raw_id_fields = ('work_item',)

# Admin para KPI
@admin.register(KPI)
class KPIAdmin(admin.ModelAdmin):
    list_display = ('name', 'metric_type', 'current_value', 'target_value', 'work_item_type', 'start_date', 'end_date', 'calculated_date')
    list_filter = ('metric_type', 'work_item_type', 'start_date', 'end_date')
    search_fields = ('name', 'work_item_type', 'description')
    ordering = ('-start_date', 'name')
    readonly_fields = ('calculated_date',)

# Admin para DeliveryProgress
@admin.register(DeliveryProgress)
class DeliveryProgressAdmin(admin.ModelAdmin):
    list_display = ('month', 'type', 'total_items', 'closed_items')
    list_filter = ('month', 'type')
    search_fields = ('type',)
    ordering = ('-month',)

# Admin para BacklogSummary
@admin.register(BacklogSummary)
class BacklogSummaryAdmin(admin.ModelAdmin):
    list_display = ('type', 'month', 'year', 'backlog_count')
    list_filter = ('type', 'month', 'year')
    search_fields = ('type',)
    ordering = ('-year', '-month')
