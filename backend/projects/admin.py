from django.contrib import admin
from .models import Workspace, WorkspaceMember, Project


class WorkspaceMemberInline(admin.TabularInline):
    model = WorkspaceMember
    extra = 1
    fields = ("user", "role", "joined_at")
    readonly_fields = ("joined_at",)


@admin.register(Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "get_members_count", "get_projects_count", "created_at")
    search_fields = ("name", "slug")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [WorkspaceMemberInline]

    @admin.display(description="Members")
    def get_members_count(self, obj):
        return obj.members.count()

    @admin.display(description="Projects")
    def get_projects_count(self, obj):
        return obj.projects.count()


@admin.register(WorkspaceMember)
class WorkspaceMemberAdmin(admin.ModelAdmin):
    list_display = ("user", "workspace", "role", "joined_at")
    list_filter = ("role", "workspace")
    search_fields = ("user__email", "user__username", "workspace__name")
    readonly_fields = ("id", "joined_at")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "key", "workspace", "slug", "created_at")
    list_filter = ("workspace",)
    search_fields = ("name", "key", "workspace__name")
    readonly_fields = ("id", "created_at", "updated_at")
