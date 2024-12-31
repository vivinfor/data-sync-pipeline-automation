from datetime import datetime
from django.utils.timezone import now
from django.db import models

class WorkItem(models.Model):
    WORK_ITEM_TYPES = [
        ('Task', 'Task'),
        ('Bug', 'Bug'),
        ('UserStory', 'User Story'),
        ('Incident', 'Incident'),
    ]

    id = models.AutoField(primary_key=True)
    external_id = models.IntegerField(unique=True, db_index=True)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=50, choices=WORK_ITEM_TYPES)
    state = models.CharField(max_length=50)
    created_date = models.DateField()
    changed_date = models.DateField()
    resolved_date = models.DateField(null=True, blank=True)
    lead_time = models.IntegerField(null=True, blank=True)
    archived = models.BooleanField(default=False)
    assigned_to = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['type']),
            models.Index(fields=['state']),
            models.Index(fields=['created_date']),
        ]
        verbose_name = "Work Item"
        verbose_name_plural = "Work Items"

    def __str__(self):
        return f"{self.title} ({self.type})"


class WorkItemHistory(models.Model):
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name="history")
    state = models.CharField(max_length=50)
    changed_date = models.DateField()

    class Meta:
        indexes = [
            models.Index(fields=['changed_date']),
        ]
        verbose_name = "Work Item History"
        verbose_name_plural = "Work Item Histories"

    def __str__(self):
        return f"History for {self.work_item.title} - {self.state}"


class WorkItemSummary(models.Model):
    WORK_ITEM_TYPES = [
        ('Task', 'Task'),
        ('Bug', 'Bug'),
        ('UserStory', 'User Story'),
        ('Incident', 'Incident'),
    ]

    type = models.CharField(max_length=50, choices=WORK_ITEM_TYPES)
    total_count = models.IntegerField(default=0)  
    average_lead_time = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    closed_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    rework_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    month = models.IntegerField()  
    year = models.IntegerField()  

    class Meta:
        unique_together = ('type', 'year', 'month')

    def __str__(self):
        return f"WorkItemSummary for {self.type} ({self.month}-{self.year})"

class DeliveryProgress(models.Model):
    month = models.DateField() 
    year = models.IntegerField()  
    type = models.CharField(max_length=50, null=True, choices=WorkItem.WORK_ITEM_TYPES) 
    total_items = models.IntegerField()
    closed_items = models.IntegerField()

    class Meta:
        verbose_name = "Delivery Progress"
        verbose_name_plural = "Delivery Progresses"
        unique_together = ('month', 'year', 'type')

    def __str__(self):
        return f"Delivery Progress ({self.month}-{self.year}, {self.type})"

    def save(self, *args, **kwargs):
        if not self.year:
            self.year = self.month.year  
        super(DeliveryProgress, self).save(*args, **kwargs)

class WorkItemReopen(models.Model):
    work_item = models.ForeignKey(WorkItem, on_delete=models.CASCADE, related_name="reopen_history")
    reopen_count = models.IntegerField(default=0)
    created_date = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Work Item Reopen"
        verbose_name_plural = "Work Item Reopens"
        unique_together = ('work_item', 'created_date')

    def __str__(self):
        return f"Reopen count for {self.work_item.title} on {self.created_date}"
    
class BacklogSummary(models.Model):
    WORK_ITEM_TYPES = [
        ('UserStory', 'User Story'),
        ('Incident', 'Incident'),
        ('Bug', 'Bug'),
        ('Task', 'Task'),
    ]
    
    type = models.CharField(max_length=50, choices=WORK_ITEM_TYPES)
    backlog_count = models.IntegerField(default=0)  # Contagem de backlog para o mês
    month = models.DateField()  # Mês do backlog
    year = models.IntegerField()  # Ano do backlog

    class Meta:
        unique_together = ('type', 'year', 'month')

    def __str__(self):
        return f"Backlog for {self.type} ({self.month}-{self.year})"


class KPI(models.Model):
    METRIC_TYPES = [
        ("percentage", "Percentage"),
        ("currency", "Currency"),
        ("count", "Count"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    target_value = models.DecimalField(max_digits=15, decimal_places=2, help_text="Target value for the KPI.")
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES, default="count", help_text="Type of metric (e.g., %, R$, count).")
    current_value = models.DecimalField(max_digits=15, decimal_places=2, default=0.0, help_text="Current calculated value.")
    work_item_type = models.CharField(max_length=50, choices=WorkItem.WORK_ITEM_TYPES, null=True, blank=True)
    start_date = models.DateField(help_text="Start date of the KPI period.")
    end_date = models.DateField(default=now)
    calculated_date = models.DateField(auto_now=True, help_text="Last calculation date.")

    class Meta:
        verbose_name = "KPI"
        verbose_name_plural = "KPIs"
        unique_together = ('name', 'start_date', 'end_date')
        ordering = ['-start_date', 'name'] 

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date}) - {self.metric_type} - {self.current_value}/{self.target_value}"

    def progress_percentage(self):
        """Calculates progress as a percentage towards the target."""
        if self.target_value == 0:
            return 0
        return round((self.current_value / self.target_value) * 100, 2)

    def is_target_achieved(self):
        """Checks if the KPI target has been achieved."""
        return self.current_value >= self.target_value

    def is_active(self, date=None):
        """Checks if the KPI is active for the given date or today."""
        date = date or datetime.today().date()
        return self.start_date <= date <= self.end_date