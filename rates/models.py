from django.db import models


class Rate(models.Model):
    title = models.CharField(max_length=255, verbose_name='Rate Name')
    description = models.TextField(max_length=2000, blank=True, null=True, verbose_name='Rate description')
    days_count = models.SmallIntegerField(
        blank=True,
        null=True,
        verbose_name='Days Count',
        help_text='If days count = 0, access is indefinite and ends at the end of the last available week'
    )

    class Meta:
        verbose_name = "Rate"
        verbose_name_plural = "Rates"
        ordering = ['id']

    def __str__(self):
        return f'({self.id}) {self.title}'
