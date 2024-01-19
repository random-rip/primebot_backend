from django.contrib import admin


class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        "comment_id",
        'match',
        'comment_parent_id',
        'content',
        'user_id',
        "comment_time",
        'created_at',
        'updated_at',
        "comment_edit_user_id",
        "comment_flag_staff",
        "comment_flag_official",
    ]
    list_filter = ['created_at', 'updated_at', "comment_edit_user_id", "comment_flag_official", "comment_flag_staff"]
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    search_fields = [
        'id',
        'match__id',
        'user_id',
    ]
