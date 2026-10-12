from django.contrib import admin
from .models import Tag, Issue, Comment


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0
    fields = ("author", "body", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color_hex", "project")
    list_filter = ("project",)
    search_fields = ("name", "project__key", "project__name")
    readonly_fields = ("id",)


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = (
        "get_issue_key",
        "title",
        "project",
        "status",
        "priority",
        "reporter",
        "assignee",
        "created_at",
    )
    list_filter = ("status", "priority", "project")
    search_fields = ("title", "description", "project__key")
    readonly_fields = ("id", "sequence_id", "created_at", "updated_at")
    inlines = [CommentInline]

    @admin.display(description="Key", ordering="sequence_id")
    def get_issue_key(self, obj):
        return obj.issue_key


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("issue", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("body", "author__username", "author__email", "issue__title")
    readonly_fields = ("id", "created_at", "updated_at")
