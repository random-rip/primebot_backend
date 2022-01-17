from django.contrib import admin


class CommentAdmin(admin.ModelAdmin):
    list_display = ['match', 'comment_id', 'parent', 'content', 'author_name', 'author_id', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    # search_fields = ['name', 'team__id', 'team__name', 'summoner_name']
