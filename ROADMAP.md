# DevFlow: Mastering Django REST Framework & Next.js

Welcome to your personalized, production-grade learning journey. You will build **DevFlow**—a modern Project & Issue Tracking Workspace (similar to Linear or Jira)—from scratch.

This curriculum is structured to take you from knowing zero Django to mastering full-stack decoupled architecture using Django REST Framework (DRF) as the robust backend API and Next.js (App Router, TypeScript, Tailwind CSS) as the modern frontend.

---

## 🗺️ Curriculum Roadmap & Progress Tracker

- [x] **Phase 1: Project Blueprint, System Architecture & The Decoupled Mental Model**
  - [x] Understand Monolithic (Django Templates/MVT) vs Decoupled (DRF + Next.js) Architecture
  - [x] Grasp the Request-Response Lifecycle: Next.js -> HTTP -> Django URL -> View -> Serializer -> DB
  - [x] Deconstruct DevFlow System Design: Workspaces, Projects, Issues, and Team Roles
  - [x] Understand Django Apps philosophy: Why and how to separate concerns
  - [x] Entity Relationship Diagram (ERD) & Database Schema Design
  - [x] Set up local Git repository and production-ready `.gitignore`

- [ ] **Phase 2: Django & DRF Foundation – Virtual Environments, Settings & Custom User Model**
  - [ ] Understand Python virtual environments (`venv`) and dependency isolation
  - [ ] Install Django, Django REST Framework, and supporting libraries
  - [ ] Scaffold the Django backend project and understand project structure (`manage.py`, `settings.py`, `urls.py`, `asgi.py`/`wsgi.py`)
  - [ ] Deep dive: Why a Custom User Model is mandatory before the first migration
  - [ ] Build the `accounts` app and implement the Custom User Model
  - [ ] Run initial migrations and configure Django Admin superuser

- [ ] **Phase 3: Domain Modeling & Relationships – Workspaces, Projects & Issues**
  - [ ] Scaffold domain apps: `projects` and `issues`
  - [ ] Understand Django Model fields: CharField, TextField, SlugField, DateTimeField, Choices
  - [ ] Model relationships in depth: One-to-Many (`ForeignKey`), Many-to-Many (`ManyToManyField`), cascade rules
  - [ ] Auto-slug generation and string representations (`__str__`)
  - [ ] Django Migrations engine explained: `makemigrations` vs `migrate` and internal state
  - [ ] Customize Django Admin for rich model inspection and filtering

- [ ] **Phase 4: Serialization Mechanics – Bridging Python Objects and JSON**
  - [ ] What is Serialization and Deserialization in Web APIs?
  - [ ] DRF `ModelSerializer` fundamentals: Fields, read-only fields, extra keyword arguments
  - [ ] Data validation: Field-level validation, object-level validation, custom validators
  - [ ] Handling nested representations: Flat IDs vs nested object details vs `SerializerMethodField`
  - [ ] Write serializers for Users, Projects, Issues, and Comments

- [ ] **Phase 5: Views, ViewSets & Routing – Exposing RESTful Endpoints**
  - [ ] The evolution of Django Views: FBV -> CBV -> `APIView` -> `GenericAPIView` -> `ModelViewSet`
  - [ ] When to use `APIView` vs `ModelViewSet`
  - [ ] RESTful URL design best practices & HTTP status codes
  - [ ] DRF Routers (`DefaultRouter`) and automatic URL generation
  - [ ] Query optimization: Preventing N+1 queries using `select_related` and `prefetch_related`
  - [ ] Exploring and testing endpoints with DRF Browsable API

- [ ] **Phase 6: Authentication, Authorization & Security – JWT & Permissions**
  - [ ] Session-based vs Token-based vs JWT (JSON Web Token) authentication
  - [ ] Implement JWT with `djangorestframework-simplejwt` (Access & Refresh tokens)
  - [ ] DRF Permissions framework (`IsAuthenticated`, `AllowAny`)
  - [ ] Write custom object-level permissions (`IsProjectMember`, `IsIssueAuthorOrAdmin`)
  - [ ] Configure Cross-Origin Resource Sharing (CORS) with `django-cors-headers`

- [ ] **Phase 7: Next.js Foundation & Decoupled Frontend Setup**
  - [ ] The modern Next.js mental model: App Router, Server Components vs Client Components
  - [ ] Initialize Next.js project with TypeScript, Tailwind CSS, and Lucide icons
  - [ ] Understand Next.js folder structure: `layout.tsx`, `page.tsx`, route groups, dynamic routes
  - [ ] Build a centralized, type-safe API client utility (`lib/api.ts`)
  - [ ] Configure environment variables for backend API endpoints

- [ ] **Phase 8: Frontend Authentication & Route Protection**
  - [ ] Secure JWT management in Next.js (cookie storage vs localStorage strategies)
  - [ ] Build Login and Registration forms with validation
  - [ ] Create an Authentication Context / Hook for global user state
  - [ ] Implement Next.js Middleware for protected route redirects

- [ ] **Phase 9: Building Core Features – Dashboard, Projects & Kanban Board**
  - [ ] Server Component data fetching: Fetching user workspaces and projects
  - [ ] Project Overview page with dynamic routing (`/projects/[slug]`)
  - [ ] Build an interactive Kanban / Issue board with Client Components
  - [ ] Issue creation and status editing with optimistic UI updates
  - [ ] Form handling, error boundaries, and loading skeletons

- [ ] **Phase 10: Advanced Features, Search, Filtering & Full-Stack Mastery**
  - [ ] Backend filtering, sorting, and search with `django-filter` and DRF SearchFilter
  - [ ] DRF pagination strategies (`PageNumberPagination`)
  - [ ] Next.js URL query parameter synchronization for search and filters
  - [ ] End-to-end integration testing and troubleshooting checklist
  - [ ] Production deployment concepts (Docker, PostgreSQL, Vercel/Railway, CORS in production)

---

## 📁 Documentation Structure

Every phase will have a dedicated comprehensive guide stored inside the `Docs/` directory:
- `Docs/Phase 1 - Project Blueprint and System Architecture.md`
- `Docs/Phase 2 - Django Foundation and Custom User Model.md`
- `Docs/Phase 3 - Domain Modeling and Database Relationships.md`
- `Docs/Phase 4 - Serialization Mechanics and JSON Transformation.md`
- `Docs/Phase 5 - Views ViewSets and RESTful Routing.md`
- `Docs/Phase 6 - JWT Authentication and Custom Permissions.md`
- `Docs/Phase 7 - Next js App Router Architecture and Setup.md`
- `Docs/Phase 8 - Frontend Authentication and Session Protection.md`
- `Docs/Phase 9 - Core Dashboard Projects and Kanban Interface.md`
- `Docs/Phase 10 - Advanced Filtering Pagination and Full Stack Integration.md`
