from django.db import models


class ReportTime(models.Model):

    user_id = models.IntegerField(verbose_name='ID Employee')
    first_name = models.CharField(verbose_name='First Name', max_length=50, blank=True, null=True)
    last_name = models.CharField(verbose_name='Last Name', max_length=50, blank=True, null=True)
    roles = models.CharField(verbose_name='Roles', max_length=100, blank=True, null=True)
    start_date_report = models.DateField(verbose_name='Start Date Report')
    end_date_report = models.DateField(verbose_name='End Date Report')
    total_hours = models.FloatField(verbose_name='Total Hours', blank=True, null=True)
    hours_work_in_vacations = models.FloatField(verbose_name='Holiday working hours', blank=True, null=True)
    hours_work_in_sick_leave = models.FloatField(verbose_name='Working hours in sickness', blank=True, null=True)
    time_in_vacations = models.TextField(verbose_name='Vacation time', blank=True, null=True)
    time_in_sick_leave = models.TextField(verbose_name='Time in sickness', blank=True, null=True)
    created_at = models.DateTimeField(verbose_name='Created report', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Updated report', auto_now=True)

    def __str__(self):
        return str(self.user_id)

    class Meta:
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        get_latest_by = "created_at"
