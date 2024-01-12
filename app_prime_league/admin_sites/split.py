from django.contrib import admin


# TODO count matches
class SplitAdmin(admin.ModelAdmin):
    list_display = [
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
    ]
    list_filter = ['created_at', 'updated_at']
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = [
        'name',
    ]
