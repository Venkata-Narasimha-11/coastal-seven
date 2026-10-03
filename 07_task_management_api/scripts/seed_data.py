"""Database seeding script populating enterprise demo data for Day 7."""

import asyncio
from datetime import datetime, timedelta, timezone
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from sqlalchemy import select
from app.core.config import settings
from app.core.security import get_password_hash
from app.core.workflow import TaskPriority, TaskStatus
from app.db.base import Base
from app.db.session import AsyncSessionLocal, async_engine
from app.models.audit_log import TaskAuditLog
from app.models.project import Project, ProjectMember, ProjectMemberRole, ProjectStatus
from app.models.task import Task
from app.models.user import User, UserRole


async def seed():
    """Seed users, projects, tasks, and historical audit logs."""
    print("🌱 Seeding database for Day 7 Mini-Project 2 Task Management API...")

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✨ Clean schema initialized.")

    async with AsyncSessionLocal() as session:
        now = datetime.now(timezone.utc)

        # --------------------------------------------------------------------------
        # 1. USERS: Admin, Managers, Developers, and Viewer
        # --------------------------------------------------------------------------
        print("👤 Creating users...")
        users_data = [
            {
                "username": settings.FIRST_SUPERUSER_USERNAME,
                "email": settings.FIRST_SUPERUSER_EMAIL,
                "password": settings.FIRST_SUPERUSER_PASSWORD,
                "full_name": "System Administrator",
                "role": UserRole.ADMIN,
            },
            {
                "username": "alice_pm",
                "email": "alice@taskmanager.io",
                "password": "Password123!",
                "full_name": "Alice Johnson",
                "role": UserRole.MANAGER,
            },
            {
                "username": "bob_lead",
                "email": "bob@taskmanager.io",
                "password": "Password123!",
                "full_name": "Bob Martinez",
                "role": UserRole.MANAGER,
            },
            {
                "username": "charlie_dev",
                "email": "charlie@taskmanager.io",
                "password": "Password123!",
                "full_name": "Charlie Davis",
                "role": UserRole.DEVELOPER,
            },
            {
                "username": "diana_dev",
                "email": "diana@taskmanager.io",
                "password": "Password123!",
                "full_name": "Diana Prince",
                "role": UserRole.DEVELOPER,
            },
            {
                "username": "evan_dev",
                "email": "evan@taskmanager.io",
                "password": "Password123!",
                "full_name": "Evan Wright",
                "role": UserRole.DEVELOPER,
            },
            {
                "username": "fiona_viewer",
                "email": "fiona@taskmanager.io",
                "password": "Password123!",
                "full_name": "Fiona Gallagher",
                "role": UserRole.VIEWER,
            },
        ]

        users = {}
        for u in users_data:
            user = User(
                username=u["username"],
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                full_name=u["full_name"],
                role=u["role"],
                is_active=True,
            )
            session.add(user)
            await session.flush()
            users[u["username"]] = user

        # --------------------------------------------------------------------------
        # 2. PROJECTS: Multi-domain collaborative initiatives
        # --------------------------------------------------------------------------
        print("📁 Creating projects...")
        projects_data = [
            {
                "key": "cloud_migration",
                "name": "Cloud Infrastructure Migration",
                "description": "Migration of on-premise Kubernetes clusters to AWS with automated Terraform and GitOps pipelines.",
                "status": ProjectStatus.ACTIVE,
                "owner": users["alice_pm"],
                "members": [
                    (users["alice_pm"], ProjectMemberRole.LEAD),
                    (users["charlie_dev"], ProjectMemberRole.CONTRIBUTOR),
                    (users["diana_dev"], ProjectMemberRole.CONTRIBUTOR),
                    (users["fiona_viewer"], ProjectMemberRole.OBSERVER),
                ],
            },
            {
                "key": "mobile_app",
                "name": "Mobile Client Application Redesign",
                "description": "Flutter-based cross-platform rewrite focusing on dark mode styling, push notifications, and offline caching.",
                "status": ProjectStatus.ACTIVE,
                "owner": users["bob_lead"],
                "members": [
                    (users["bob_lead"], ProjectMemberRole.LEAD),
                    (users["diana_dev"], ProjectMemberRole.CONTRIBUTOR),
                    (users["evan_dev"], ProjectMemberRole.CONTRIBUTOR),
                ],
            },
            {
                "key": "analytics_dash",
                "name": "Executive Real-Time Analytics Dashboard",
                "description": "Real-time KPI aggregation and streaming analytics engine using FastAPI, Redis, and TimescaleDB.",
                "status": ProjectStatus.PLANNING,
                "owner": users["alice_pm"],
                "members": [
                    (users["alice_pm"], ProjectMemberRole.LEAD),
                    (users["charlie_dev"], ProjectMemberRole.CONTRIBUTOR),
                ],
            },
        ]

        projects = {}
        for p in projects_data:
            project = Project(
                name=p["name"],
                description=p["description"],
                status=p["status"],
                owner_id=p["owner"].id,
            )
            session.add(project)
            await session.flush()
            projects[p["key"]] = project

            # Add memberships
            for user_obj, role in p["members"]:
                member = ProjectMember(
                    project_id=project.id,
                    user_id=user_obj.id,
                    role=role,
                )
                session.add(member)

        # --------------------------------------------------------------------------
        # 3. TASKS: Workflow statuses, priorities, assignments, and due dates
        # --------------------------------------------------------------------------
        print("📝 Creating tasks with workflow statuses & due dates...")
        tasks_data = [
            # Project 1: Cloud Migration
            {
                "title": "Configure Terraform AWS Provider & Remote State S3 Bucket",
                "description": "Establish encrypted state lock DynamoDB table and S3 bucket with strict IAM policy.",
                "status": TaskStatus.COMPLETED,
                "priority": TaskPriority.HIGH,
                "due_date": now - timedelta(days=2),
                "project": projects["cloud_migration"],
                "assignee": users["charlie_dev"],
                "creator": users["alice_pm"],
                "history": [
                    (None, TaskStatus.TODO.value, "Task created by PM", users["alice_pm"]),
                    (TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value, "Started Terraform script development", users["charlie_dev"]),
                    (TaskStatus.IN_PROGRESS.value, TaskStatus.REVIEW.value, "PR #102 submitted for review", users["charlie_dev"]),
                    (TaskStatus.REVIEW.value, TaskStatus.COMPLETED.value, "Approved and deployed to staging", users["alice_pm"]),
                ],
            },
            {
                "title": "Provision Managed PostgreSQL Aurora Cluster",
                "description": "Configure RDS Multi-AZ PostgreSQL instance with connection pooling and automated backups.",
                "status": TaskStatus.IN_PROGRESS,
                "priority": TaskPriority.URGENT,
                "due_date": now + timedelta(days=3),
                "project": projects["cloud_migration"],
                "assignee": users["charlie_dev"],
                "creator": users["alice_pm"],
                "history": [
                    (None, TaskStatus.TODO.value, "Task created", users["alice_pm"]),
                    (TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value, "Beginning VPC peering and security group config", users["charlie_dev"]),
                ],
            },
            {
                "title": "Setup Ingress Controller & Let's Encrypt TLS Automation",
                "description": "Deploy Traefik or NGINX Ingress controller with Cert-Manager for automatic SSL certificate renewals.",
                "status": TaskStatus.REVIEW,
                "priority": TaskPriority.HIGH,
                "due_date": now + timedelta(days=5),
                "project": projects["cloud_migration"],
                "assignee": users["diana_dev"],
                "creator": users["alice_pm"],
                "history": [
                    (None, TaskStatus.TODO.value, "Created task", users["alice_pm"]),
                    (TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value, "Helm chart configuration written", users["diana_dev"]),
                    (TaskStatus.IN_PROGRESS.value, TaskStatus.REVIEW.value, "Ready for peer review and staging smoke test", users["diana_dev"]),
                ],
            },
            {
                "title": "Perform Security Compliance and Penetration Testing",
                "description": "Execute OWASP ZAP automated scan and verify least-privilege IAM policies across all VPC microservices.",
                "status": TaskStatus.TODO,
                "priority": TaskPriority.MEDIUM,
                "due_date": now + timedelta(days=14),
                "project": projects["cloud_migration"],
                "assignee": users["diana_dev"],
                "creator": users["alice_pm"],
                "history": [
                    (None, TaskStatus.TODO.value, "Task scheduled for Sprint 3", users["alice_pm"]),
                ],
            },
            {
                "title": "Decommission Legacy Bare-Metal Rack #4",
                "description": "Power down and sanitize storage drives on legacy physical servers.",
                "status": TaskStatus.CANCELLED,
                "priority": TaskPriority.LOW,
                "due_date": now + timedelta(days=30),
                "project": projects["cloud_migration"],
                "assignee": None,
                "creator": users["alice_pm"],
                "history": [
                    (None, TaskStatus.TODO.value, "Task created", users["alice_pm"]),
                    (TaskStatus.TODO.value, TaskStatus.CANCELLED.value, "Cancelled: vendor contract handles decommissioning", users["alice_pm"]),
                ],
            },
            # Project 2: Mobile App
            {
                "title": "Figma Wireframes & Material 3 Design Token Export",
                "description": "Finalize typography, color tokens, and responsive mobile mockups.",
                "status": TaskStatus.COMPLETED,
                "priority": TaskPriority.HIGH,
                "due_date": now - timedelta(days=5),
                "project": projects["mobile_app"],
                "assignee": users["diana_dev"],
                "creator": users["bob_lead"],
                "history": [
                    (None, TaskStatus.TODO.value, "Task initiated", users["bob_lead"]),
                    (TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value, "Designing mockups in Figma", users["diana_dev"]),
                    (TaskStatus.IN_PROGRESS.value, TaskStatus.REVIEW.value, "Design tokens exported", users["diana_dev"]),
                    (TaskStatus.REVIEW.value, TaskStatus.COMPLETED.value, "Design approved by design lead", users["bob_lead"]),
                ],
            },
            {
                "title": "Implement Offline SQLite Sync & Local Storage Cache",
                "description": "Cache recent feed items locally using Drift/SQLite for offline browsing experience.",
                "status": TaskStatus.IN_PROGRESS,
                "priority": TaskPriority.MEDIUM,
                "due_date": now + timedelta(days=4),
                "project": projects["mobile_app"],
                "assignee": users["evan_dev"],
                "creator": users["bob_lead"],
                "history": [
                    (None, TaskStatus.TODO.value, "Assigned to Evan", users["bob_lead"]),
                    (TaskStatus.TODO.value, TaskStatus.IN_PROGRESS.value, "Implementing SQLite schema and repository", users["evan_dev"]),
                ],
            },
            {
                "title": "Integrate Firebase Cloud Messaging for Push Notifications",
                "description": "Handle foreground, background, and notification tap deep-links.",
                "status": TaskStatus.TODO,
                "priority": TaskPriority.URGENT,
                "due_date": now + timedelta(days=7),
                "project": projects["mobile_app"],
                "assignee": users["evan_dev"],
                "creator": users["bob_lead"],
                "history": [
                    (None, TaskStatus.TODO.value, "Task assigned for sprint 2", users["bob_lead"]),
                ],
            },
            {
                "title": "Prepare App Store & Google Play Graphic Assets",
                "description": "Export screenshots for 6.7 inch, 6.1 inch, and 12.9 inch iPad display sizes.",
                "status": TaskStatus.TODO,
                "priority": TaskPriority.LOW,
                "due_date": now + timedelta(days=21),
                "project": projects["mobile_app"],
                "assignee": None,
                "creator": users["bob_lead"],
                "history": [
                    (None, TaskStatus.TODO.value, "Task created in backlog", users["bob_lead"]),
                ],
            },
            # Project 3: Analytics Dashboard
            {
                "title": "Draft Technical Architecture & Data Ingestion Specification",
                "description": "Define data schema for event streaming via Kafka and aggregate query latency thresholds.",
                "status": TaskStatus.TODO,
                "priority": TaskPriority.MEDIUM,
                "due_date": now + timedelta(days=10),
                "project": projects["analytics_dash"],
                "assignee": users["charlie_dev"],
                "creator": users["alice_pm"],
                "history": [
                    (None, TaskStatus.TODO.value, "Created for planning phase", users["alice_pm"]),
                ],
            },
        ]

        for t in tasks_data:
            task = Task(
                title=t["title"],
                description=t["description"],
                status=t["status"],
                priority=t["priority"],
                due_date=t["due_date"],
                project_id=t["project"].id,
                assignee_id=t["assignee"].id if t["assignee"] else None,
                creator_id=t["creator"].id,
            )
            session.add(task)
            await session.flush()

            # Add historical audit trail
            for old_st, new_st, note, user_obj in t["history"]:
                audit = TaskAuditLog(
                    task_id=task.id,
                    changed_by_id=user_obj.id,
                    old_status=old_st,
                    new_status=new_st,
                    notes=note,
                )
                session.add(audit)

        await session.commit()
        print("✅ Database seeding completed successfully!")
        print("\n🔑 Demo User Credentials:")
        print("--------------------------------------------------------------------------")
        print(f"  • Administrator : {settings.FIRST_SUPERUSER_USERNAME} / {settings.FIRST_SUPERUSER_PASSWORD}")
        print("  • Manager (PM)  : alice_pm / Password123!")
        print("  • Manager (Lead): bob_lead / Password123!")
        print("  • Developer     : charlie_dev / Password123!")
        print("  • Developer     : diana_dev / Password123!")
        print("  • Developer     : evan_dev / Password123!")
        print("  • Viewer        : fiona_viewer / Password123!")
        print("--------------------------------------------------------------------------")


if __name__ == "__main__":
    asyncio.run(seed())
