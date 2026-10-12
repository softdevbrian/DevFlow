import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Workspace(models.Model):
    """
    Top-level organizational tenant (e.g. 'Acme Corp', 'Personal').
    Contains members and projects.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="WorkspaceMember",
        related_name="workspaces",
    )

    class Meta:
        db_table = "projects_workspace"
        ordering = ["-created_at"]
        verbose_name = "Workspace"
        verbose_name_plural = "Workspaces"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "workspace"
            slug = base_slug
            counter = 1
            while Workspace.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class WorkspaceMember(models.Model):
    """
    Explicit junction table linking a User to a Workspace with role-based access.
    """

    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="workspace_memberships",
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.MEMBER,
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projects_workspace_member"
        ordering = ["joined_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "user"],
                name="unique_workspace_membership",
            )
        ]
        verbose_name = "Workspace Member"
        verbose_name_plural = "Workspace Members"

    def __str__(self):
        return f"{self.user.email} - {self.workspace.name} ({self.get_role_display()})"


class Project(models.Model):
    """
    Project container for issues, owned by a single Workspace.
    Has an issue key prefix (e.g. 'DEV' -> 'DEV-1', 'DEV-2').
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace,
        on_delete=models.CASCADE,
        related_name="projects",
    )
    name = models.CharField(max_length=100)
    key = models.CharField(
        max_length=10,
        help_text="Short uppercase prefix for issues (e.g., DEV, CORE, UI)",
    )
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects_project"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["workspace", "key"],
                name="unique_project_key_per_workspace",
            ),
            models.UniqueConstraint(
                fields=["workspace", "slug"],
                name="unique_project_slug_per_workspace",
            ),
        ]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def save(self, *args, **kwargs):
        self.key = self.key.upper().strip()
        if not self.slug:
            base_slug = slugify(self.name) or "project"
            slug = base_slug
            counter = 1
            while Project.objects.filter(workspace=self.workspace, slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.key})"
