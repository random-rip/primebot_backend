from django import forms
from django.contrib import admin

from app_prime_league.models import Split


class SplitForm(forms.ModelForm):
    id = forms.IntegerField(
        label="ID",
        required=False,
        help_text="ID of the Prime League Split",
    )

    class Meta:
        model = Split
        fields = (
            "id",
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

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if self.instance and self.instance.pk:
    #         self.fields["pk"].disabled = True
    #     else:
    #         self.fields["pk"].disabled = False

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
        'created_at',
        "updated_at",
        # "matches_count", TODO
        # "teams_count", TODO
    ]
    list_filter = ['created_at', 'updated_at']
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = [
        'name',
    ]
