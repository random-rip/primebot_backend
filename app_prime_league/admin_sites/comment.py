from django.contrib import admin


class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'match', 'comment_parent_id', 'content', 'user_id', 'created_at', 'updated_at',
                    "comment_edit_user_id", "comment_flag_staff", "comment_flag_official"]
    list_filter = ["match", "user_id", 'created_at', 'updated_at']
    readonly_fields = ("created_at", "updated_at",)
    # search_fields = ['name', 'team__id', 'team__name', 'summoner_name']
