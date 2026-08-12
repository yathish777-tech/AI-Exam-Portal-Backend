"""
app/api/v1/router.py
====================
Top-level API v1 router.

Register all v1 sub-routers here. Each sub-router should be in its
own file under app/api/v1/.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.health import router as health_router

# Phase 3: Core exam portal routers
from app.api.v1.exams import router as exams_router
from app.api.v1.questions import router as questions_router
from app.api.v1.attempts import router as attempts_router
from app.api.v1.results import router as results_router
from app.api.v1.admins import router as admins_router
from app.api.v1.students import router as students_router
from app.api.v1.interviewers import router as interviewers_router
from app.api.v1.notifications import router as notifications_router
from app.api.v1.proctoring import router as proctoring_router
from app.api.v1.analytics import router as analytics_router
from app.api.v1.reports import router as reports_router

# The main v1 router — prefix is applied in main.py
api_v1_router = APIRouter(prefix="/api/v1")

# Phase 1: Auth + Health
api_v1_router.include_router(auth_router)
api_v1_router.include_router(health_router)

# Phase 3: Exam portal
api_v1_router.include_router(exams_router)
api_v1_router.include_router(questions_router)
api_v1_router.include_router(attempts_router)
api_v1_router.include_router(results_router)

# Phase 4: Dashboards, notifications, proctoring, analytics, reports
api_v1_router.include_router(admins_router)
api_v1_router.include_router(students_router)
api_v1_router.include_router(interviewers_router)
api_v1_router.include_router(notifications_router)
api_v1_router.include_router(proctoring_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(reports_router)
