import uuid
from django.conf import settings
from django.db import models


class Tag(models.Model):
    """
    Categorical labels scoped to a Project (e.g. 'Bug', 'Feature', 'Frontend').
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="tags",
    )
    name = models.CharField(max_length=50)
    color_hex = models.CharField(
        max_length=7,
        default="#6B7280",
        help_text="Hex color code (e.g. #3B82F6)",
    )

    class Meta:
        db_table = "issues_tag"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "name"],
                name="unique_tag_name_per_project",
            )
        ]
        verbose_name = "Tag"
        verbose_name_plural = "Tags"

    def __str__(self):
        return f"{self.name} ({self.project.key})"


class Issue(models.Model):
    """
    Core work item entity belonging to a Project.
    Features:
    - Auto-incrementing project sequence identifier (e.g. DEV-42)
    - Standard Kanban status lifecycle
    - Prioritization
    - Reporter (PROTECT) and optional Assignee (SET_NULL)
    """

    class Status(models.TextChoices):
        BACKLOG = "BACKLOG", "Backlog"
        TODO = "TODO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        IN_REVIEW = "IN_REVIEW", "In Review"
        DONE = "DONE", "Done"
        CANCELED = "CANCELED", "Canceled"

    class Priority(models.TextChoices):
        LOW = "LOW", "Low"
        MEDIUM = "MEDIUM", "Medium"
        HIGH = "HIGH", "High"
        URGENT = "URGENT", "Urgent"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="issues",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    sequence_id = models.PositiveIntegerField(
        editable=False,
        help_text="Project-scoped sequential ID for issue keys (e.g. DEV-1)",
    )
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="reported_issues",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="issues",
    )
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "issues_issue"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["project", "sequence_id"],
                name="unique_issue_sequence_per_project",
            )
        ]
        verbose_name = "Issue"
        verbose_name_plural = "Issues"

    @property
    def issue_key(self):
        return f"{self.project.key}-{self.sequence_id}"

    def save(self, *args, **kwargs):
        if not self.sequence_id:
            max_seq = Issue.objects.filter(project=self.project).aggregate(
                models.Max("sequence_id")
            )["sequence_id__max"]
            self.sequence_id = (max_seq or 0) + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.issue_key} - {self.title}"


class Comment(models.Model):
    """
    Discussion threads attached to an Issue.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    issue = models.ForeignKey(
        Issue,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="issue_comments",
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "issues_comment"
        ordering = ["created_at"]
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.author.username} on {self.issue.issue_key}"
