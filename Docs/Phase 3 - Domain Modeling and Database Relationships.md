# Phase 3: Domain Modeling and Database Relationships

Welcome to Phase 3 of **DevFlow**. In this phase, we design and implement the relational domain models that power our workspace, project, and issue-tracking features.

We scaffold two dedicated Django apps—`projects` and `issues`—and establish the relationships, constraints, auto-generation hooks, and Django Admin interfaces.

---

## 1. Domain Entities & Relational Hierarchy

DevFlow's domain is organized into a clean hierarchical model:

```
Tenant & Project Hierarchy:
Workspace (Top-level multi-tenant container)
 ├── WorkspaceMember (Junction linking Users with Roles: OWNER, ADMIN, MEMBER)
 └── Project (Scoped under Workspace, has key prefix like 'DEV')
      ├── Tag (Labels scoped to Project, e.g., 'Backend', 'Bug')
      └── Issue (Work items with sequential keys: DEV-1, DEV-2)
           ├── Comments (Discussion threads)
           └── Tags (Many-to-Many association)
```

---

## 2. Django Model Fields & Relationships in Depth

### 2.1 Model Fields Used in DevFlow
- **`UUIDField(primary_key=True, default=uuid.uuid4, editable=False)`**: Guaranteed non-enumerable primary keys across distributed systems.
- **`SlugField`**: URL-friendly identifiers (e.g., `/workspaces/devflow-engineering`).
- **`CharField`**: Fixed-length text (`max_length` strictly required). Used for names, keys, status codes, and hex colors.
- **`TextField`**: Arbitrary-length text for descriptions and markdown comments.
- **`PositiveIntegerField`**: Used for `sequence_id` to ensure issue numbers are strictly non-negative integers.
- **`models.TextChoices`**: Type-safe Python enums for statuses, priorities, and membership roles.

### 2.2 Relational Connections & Cascade Rules
Django provides three primary relationship types:
1. **One-to-Many (`models.ForeignKey`)**:
   - `Project.workspace`: A project belongs to exactly one workspace; a workspace contains multiple projects.
   - `Issue.project`: An issue belongs to one project; a project contains many issues.
2. **Many-to-Many with Intermediate Table (`ManyToManyField(through=...)`)**:
   - `Workspace.members`: Users and Workspaces have a Many-to-Many relationship. Instead of Django generating an opaque join table, we explicitly declare `through='WorkspaceMember'` to store additional metadata: the user's `role` (`OWNER`, `ADMIN`, `MEMBER`) and `joined_at` timestamp.
3. **Many-to-Many Direct (`models.ManyToManyField`)**:
   - `Issue.tags`: An issue can have multiple tags, and a tag can label multiple issues. Django manages the underlying junction table (`issues_issue_tags`).

### 2.3 The Three Cascade Policies
Choosing the correct `on_delete` policy is vital for database integrity:
- **`CASCADE`**: When the parent record is deleted, delete this child record.
  - *Used on*: `Project.workspace`, `Issue.project`, `Comment.issue`. Deleting a project purges its issues.
- **`SET_NULL`**: When the parent record is deleted, set the child's foreign key to `NULL` (requires `null=True`).
  - *Used on*: `Issue.assignee`. If a developer deletes their account, their assigned issues remain active and transition to unassigned.
- **`PROTECT`**: Blocks deletion of the parent if any child records point to it (`ProtectedError`).
  - *Used on*: `Issue.reporter`. A user who authored historical issues cannot be silently wiped without reassigning or archiving their reported issues.

---

## 3. Code Breakdown: `projects` App

### 3.1 `projects/models.py`
```python
import uuid
from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Workspace(models.Model):
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
```
- **Auto-slug collision handler**: If another workspace already uses `devflow`, the subsequent workspace automatically receives `devflow-1`, `devflow-2`, etc.

```python
class WorkspaceMember(models.Model):
    class Role(models.TextChoices):
        OWNER = "OWNER", "Owner"
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="workspace_memberships")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "projects_workspace_member"
        constraints = [
            models.UniqueConstraint(fields=["workspace", "user"], name="unique_workspace_membership")
        ]
```
- **`UniqueConstraint`**: Prevents duplicate membership records for the same user in a single workspace.

```python
class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=100)
    key = models.CharField(max_length=10, help_text="Short uppercase prefix (e.g. DEV, CORE)")
    slug = models.SlugField(max_length=120, blank=True)
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects_project"
        constraints = [
            models.UniqueConstraint(fields=["workspace", "key"], name="unique_project_key_per_workspace"),
            models.UniqueConstraint(fields=["workspace", "slug"], name="unique_project_slug_per_workspace"),
        ]

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
```
- **Scoped uniqueness**: Project keys (`DEV`, `API`) and slugs must be unique *within the same workspace*, but different workspaces can reuse the same project key.

---

## 4. Code Breakdown: `issues` App

### 4.1 Auto-Incrementing Project Issue Keys (`DEV-1`, `DEV-2`)
Jira and Linear generate issue identifiers scoped per project. When an issue is saved, we automatically calculate the highest existing `sequence_id` for that project and increment it by 1:

```python
class Issue(models.Model):
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
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="issues")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO)
    priority = models.CharField(max_length=20, choices=Priority.choices, default=Priority.MEDIUM)
    sequence_id = models.PositiveIntegerField(editable=False)
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="reported_issues")
    assignee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_issues")
    tags = models.ManyToManyField(Tag, blank=True, related_name="issues")
    due_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

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
```

---

## 5. Django Admin Customization

In [`projects/admin.py`](file:///c:/My_Projects/%23%20Django%20Projects/DEVFLOW/backend/projects/admin.py) and [`issues/admin.py`](file:///c:/My_Projects/%23%20Django%20Projects/DEVFLOW/backend/issues/admin.py):
- **`WorkspaceMemberInline`**: Manage members and their roles directly inside the Workspace edit page.
- **`CommentInline`**: Read and manage discussion threads on the Issue edit page.
- **Computed List Display Columns**:
  - `get_members_count` & `get_projects_count` on `WorkspaceAdmin`.
  - `get_issue_key` (e.g. `DEV-1`) displayed as a sortable column on `IssueAdmin`.
- **Search & Filters**: Multi-field search across related foreign keys (`project__key`, `workspace__name`, `author__email`).

---

## 6. How the Migrations Engine Works

When running:
```powershell
python manage.py makemigrations projects issues
python manage.py migrate
```

1. **State Analysis**: Django compares the Python classes in `models.py` with its in-memory migration history.
2. **Dependency Resolution**: `issues.0001_initial` depends on `projects.0001_initial` and `accounts.0001_initial`. Django automatically sequences operations so referenced models exist before foreign keys are added.
3. **DDL Execution**: Django generates SQL `CREATE TABLE` and `CREATE CONSTRAINT` statements and executes them in an atomic transaction.
4. **`django_migrations` Record**: Django inserts records into the `django_migrations` table so operations are never executed twice.

---

## 7. Phase Completion Checklist

- [x] `projects` and `issues` apps scaffolded and registered in `settings.INSTALLED_APPS`
- [x] `Workspace`, `WorkspaceMember`, and `Project` domain models implemented
- [x] Auto-slug generation and unique project key constraints configured
- [x] `Tag`, `Issue`, and `Comment` models implemented
- [x] Auto-incrementing project issue key logic (`issue_key` property and `sequence_id` calculation)
- [x] Explicit cascade policies configured (`CASCADE`, `SET_NULL`, `PROTECT`)
- [x] Django Admin dashboards enhanced with inlines and computed columns
- [x] Migrations generated and cleanly applied to SQLite database
- [x] Verified full relational pipeline in Django shell

---

*Proceed to **Phase 4: Serialization Mechanics & JSON Transformation** to transform these Python ORM model instances into validated JSON for our REST API using DRF ModelSerializers.*
