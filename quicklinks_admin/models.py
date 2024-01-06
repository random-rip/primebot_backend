from django.contrib.auth.models import Group
from django.db import models

# Create your models here.


class Quicklink(models.Model):
    title = models.CharField(max_length=255)
    help_text = models.CharField(max_length=255, blank=True, default='')
    url = models.URLField(max_length=255)
    order = models.IntegerField(default=0)
    is_internal = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    icon = models.ImageField(upload_to='quicklinks', null=True, blank=True, help_text="Icons should be 40x40 pixels.")
    groups = models.ManyToManyField(Group, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ('order', 'title')
