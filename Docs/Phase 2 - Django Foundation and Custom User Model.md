# Phase 2: Django Foundation and Custom User Model

Welcome to Phase 2 of **DevFlow**. In this phase, we transition from architectural theory to our initial backend implementation. We configure the Python virtual environment, scaffold the Django project, and implement the most critical foundational model in any Django project: the **Custom User Model**.

---

## 1. Virtual Environments and Dependency Isolation

### 1.1 Why Virtual Environments Matter
In Python development, installing packages globally into your operating system's Python distribution creates "dependency collision":
- Project A requires Django 4.2 LTS, while Project B requires Django 5.2.
- A global `pip install` overwrites packages, breaking projects.

By creating an isolated virtual environment at `backend/.venv/`, DevFlow manages its own packages, binaries, and Python interpreter independently of any other project on your machine.

### 1.2 Our Core Backend Stack (`backend/requirements.txt`)
```text
Django>=5.1.0,<6.0.0
djangorestframework>=3.15.2
djangorestframework-simplejwt>=5.3.1
django-cors-headers>=4.4.0
python-dotenv>=1.0.1
```
- **`Django`**: Modern web framework providing ORM, migrations, URL routing, and security.
- **`djangorestframework`**: The standard toolkit for building RESTful Web APIs in Django.
- **`djangorestframework-simplejwt`**: JSON Web Token (JWT) authentication for headless/decoupled clients.
- **`django-cors-headers`**: Manages HTTP CORS headers so Next.js on `localhost:3000` can access the API on `localhost:8000`.
- **`python-dotenv`**: Loads configuration and secrets from `.env` files into environment variables.

---

## 2. Anatomy of the Django Backend Project

We scaffolded the project structure as follows:
```text
backend/
├── .venv/                         # Isolated Python virtual environment (ignored in git)
├── devflow_core/                  # Core project configuration package
│   ├── __init__.py                # Signals to Python that this directory is a package
│   ├── settings.py                # Global settings (apps, DB, auth, middleware)
│   ├── urls.py                    # Root URL router
│   ├── wsgi.py                    # WSGI entrypoint for synchronous web servers (e.g., Gunicorn)
│   └── asgi.py                    # ASGI entrypoint for asynchronous servers (e.g., Uvicorn)
├── accounts/                      # DevFlow Identity & Auth app
│   ├── migrations/                # Database migration history
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── admin.py                   # Custom User configuration for Django Admin
│   ├── apps.py                    # App metadata and registry
│   ├── models.py                  # Custom User model and UserManager
│   ├── tests.py                   # Test suites
│   └── views.py                   # (Will house authentication views in Phase 6)
├── requirements.txt               # Pinned dependencies
├── manage.py                      # Django CLI utility script
└── db.sqlite3                     # Local SQLite database (ignored in git)
```

### The Role of `manage.py`
`manage.py` is the operational command-line tool for your Django project. It sets the `DJANGO_SETTINGS_MODULE` environment variable to `devflow_core.settings` and delegates commands (`runserver`, `makemigrations`, `migrate`, `createsuperuser`, `shell`) to `django.core.management`.

---

## 3. Deep Dive: The Custom User Model Trap

### 3.1 Why Starting with `AbstractUser` is Mandatory
Django ships with a default `django.contrib.auth.models.User` model. However, **Django's official documentation explicitly warns:**

> *"If you start your project using the default `User` model and later decide you need custom fields (such as email authentication, UUID keys, or profile pictures), switching to a custom user model mid-project is extraordinarily difficult and often requires wiping the database."*

Why is switching later so difficult?
1. Django's default migrations create foreign keys in `admin`, `auth`, and `sessions` pointing directly to `auth_user`.
2. Swapping the user model after migrations exist creates circular dependencies in the migration graph.
3. Every third-party library that references `settings.AUTH_USER_MODEL` gets confused by existing foreign key constraints.

**Best Practice:** Always declare a Custom User Model inheriting from `AbstractUser` before running `python manage.py migrate` for the first time.

### 3.2 UUID Primary Keys vs Auto-Incrementing Integers
By default, Django models use auto-incrementing integers (`1, 2, 3...`) for primary keys (`id`).
In DevFlow, our `User` model uses a **UUID v4**:
- **Prevents Enumeration Attacks**: An attacker cannot inspect `/api/v1/users/1/` and know that user ID `2` exists, or deduce how many users DevFlow has registered.
- **Decentralized Generation**: Client apps or distributed services can generate unique IDs without round-tripping to a central database sequence.

---

## 4. Line-by-Line Code Breakdown

### 4.1 Custom `User` Model & `UserManager` (`backend/accounts/models.py`)
```python
import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """
    Custom manager for DevFlow User model where email is the unique identifier.
    """

    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not username:
            raise ValueError("The Username field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)  # Hashes password using PBKDF2/SHA256
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, username, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for DevFlow.
    Features:
    - UUID4 as non-enumerable primary key
    - Unique email as primary authentication field
    - Distinct username preserved for team mentions (@username)
    - avatar_url for user profile images
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, verbose_name="email address")
    avatar_url = models.URLField(max_length=500, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        db_table = "accounts_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.username} ({self.email})"
```

#### Key Technical Decisions:
- `USERNAME_FIELD = "email"`: Users log in using their email address rather than an arbitrary username.
- `REQUIRED_FIELDS = ["username"]`: Django's `createsuperuser` CLI will prompt for `email`, `username`, and `password`.
- `objects = UserManager()`: Custom manager ensures `create_user` normalizes email addresses and hashes passwords properly.

---

### 4.2 Django Admin Configuration (`backend/accounts/admin.py`)
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "username", "first_name", "last_name", "is_staff", "is_active")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("username", "first_name", "last_name", "avatar_url")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password", "first_name", "last_name"),
            },
        ),
    )
```
- By subclassing `BaseUserAdmin`, we maintain secure password hashing in the admin panel while customizing the fieldsets to include `email`, `avatar_url`, and the UUID primary key display.

---

### 4.3 Core Settings Adjustments (`backend/devflow_core/settings.py`)

1. **Registered Apps**:
   ```python
   INSTALLED_APPS = [
       ...
       # Third-party apps
       'rest_framework',
       'corsheaders',

       # Local apps
       'accounts',
   ]
   ```
2. **CORS Middleware** (Must be placed before `CommonMiddleware`):
   ```python
   MIDDLEWARE = [
       'corsheaders.middleware.CorsMiddleware',
       'django.middleware.security.SecurityMiddleware',
       ...
   ]
   ```
3. **Declared User Model**:
   ```python
   AUTH_USER_MODEL = 'accounts.User'
   ```
4. **DRF & CORS Settings**:
   ```python
   REST_FRAMEWORK = {
       'DEFAULT_AUTHENTICATION_CLASSES': (
           'rest_framework_simplejwt.authentication.JWTAuthentication',
       ),
       'DEFAULT_PERMISSION_CLASSES': (
           'rest_framework.permissions.IsAuthenticated',
       ),
   }

   CORS_ALLOWED_ORIGINS = [
       "http://localhost:3000",
       "http://127.0.0.1:3000",
   ]
   ```

---

## 5. Migrations Execution

We executed:
```powershell
python manage.py makemigrations accounts
python manage.py migrate
```
Django generated `accounts/migrations/0001_initial.py` and cleanly applied it as the primary auth model alongside `contenttypes`, `auth`, `admin`, and `sessions`.

A superuser account was initialized for local inspection:
- **Email**: `admin@devflow.local`
- **Username**: `admin`

---

## 6. Troubleshooting & Common Pitfalls

| Problem | Cause | Solution |
| :--- | :--- | :--- |
| `TypeError: UserManager.create_user() missing 1 required argument: 'username'` | The default `UserManager` expects `(username, email=None)` rather than email first. | Implement custom `UserManager` overriding both `create_user` and `create_superuser`. |
| `ValueError: Dependency on app with no migrations` | Referencing `accounts.User` in foreign keys before `makemigrations accounts` was run. | Always run `makemigrations <app_name>` explicitly for new apps. |
| CORS Errors in browser | Missing `corsheaders.middleware.CorsMiddleware` or incorrect order. | Place `CorsMiddleware` as the top-most middleware in `settings.MIDDLEWARE`. |

---

## 7. Phase Completion Checklist

- [x] Python virtual environment created and dependencies installed (`Django`, `DRF`, `SimpleJWT`, `CORS`)
- [x] Django project `devflow_core` scaffolded
- [x] Custom `User` model created with UUID primary key and email authentication
- [x] Custom `UserManager` implemented for clean superuser and user creation
- [x] `AUTH_USER_MODEL = 'accounts.User'` registered in `settings.py`
- [x] Initial migrations executed (`0001_initial.py`)
- [x] Superuser account created and verified in Django shell

---

*Proceed to **Phase 3: Domain Modeling & Database Relationships** to scaffold the `projects` and `issues` apps, define ForeignKeys, Many-to-Many relationships, auto-slug generation, and cascade rules.*
