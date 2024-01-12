from django.db import models


class SplitManager(models.Manager):
    def get_current_split(self):
        return self.model.objects.order_by("-registration_start").first()


class Split(models.Model):
    name = models.CharField(max_length=20, unique=True)
    registration_start = models.DateField()
    registration_end = models.DateField()
    calibration_stage_start = models.DateField(null=True, blank=True)
    calibration_stage_end = models.DateField(null=True, blank=True)
    group_stage_start = models.DateField(null=True, blank=True)
    group_stage_end = models.DateField(null=True, blank=True)
    playoffs_start = models.DateField(null=True, blank=True)
    playoffs_end = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = SplitManager()

    class Meta:
        db_table = "splits"
        verbose_name = "Split"
        verbose_name_plural = "Splits"
