from django import forms
from django.contrib import admin
from django.db.models import Count

from app_prime_league.models import Split


class SplitForm(forms.ModelForm):
    class Meta:
        model = Split
        fields = (
            "name",
            "registration_start",
            "registration_end",
            "calibration_stage_start",
            "calibration_stage_end",
            "group_stage_start",
            "group_stage_start_monday",
            "group_stage_end",
            "playoffs_start",
            "playoffs_end",
        )

    def clean(self):
        cleaned_data = super().clean()
        self.validate_date_gt('registration_start', 'registration_end')
        self.validate_date_gt('calibration_stage_start', 'calibration_stage_end')
        self.validate_date_gt('group_stage_start', 'group_stage_start_monday')
        self.validate_date_gt('group_stage_start_monday', 'group_stage_end')
        self.validate_date_gt('playoffs_start', 'playoffs_end')

        split_data = Split.calculate(
            registration_start=cleaned_data.get('registration_start'),
            registration_end=cleaned_data.get('registration_end'),
        )
        for field, value in split_data.items():
            if not cleaned_data.get(field):
                cleaned_data[field] = value
        return cleaned_data

    def validate_date_gt(self, field1, field2):
        if not self.cleaned_data.get(field1) or not self.cleaned_data.get(field2):
            return
        if self.cleaned_data[field1] > self.cleaned_data[field2]:
            self.add_error(field1, f'{field1} must be before {field2}')


class SplitAdmin(admin.ModelAdmin):
    form = SplitForm
    list_display = [
        "id",
        "name",
        'registration_start',
        'registration_end',
        'calibration_stage_start',
        'calibration_stage_end',
        'group_stage_start',
        'group_stage_end',
        'playoffs_start',
        'playoffs_end',
        "matches_count",
        "teams_count",
        'created_at',
        "updated_at",
    ]
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ("created_at", "updated_at")
    search_fields = ("name",)
    list_display_links = ("id", "name")

    @admin.display(description='#Teams', ordering="_teams_count")
    def teams_count(self, obj: Split) -> int:
        return obj._teams_count

    @admin.display(description='#Matches', ordering="_matches_count")
    def matches_count(self, obj: Split) -> int:
        return obj._matches_count

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _matches_count=Count("matches", distinct=True),
            _teams_count=Count("teams", distinct=True),
        )
        return queryset
