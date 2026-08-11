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

# The main v1 router — prefix is applied in main.py
api_v1_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_v1_router.include_router(auth_router)

# Future routers (uncomment as modules are implemented):
# from app.api.v1.admins import router as admins_router
# from app.api.v1.students import router as students_router
# from app.api.v1.interviewers import router as interviewers_router
# from app.api.v1.exams import router as exams_router
# from app.api.v1.questions import router as questions_router
# from app.api.v1.attempts import router as attempts_router
# api_v1_router.include_router(admins_router)
# api_v1_router.include_router(students_router)
# api_v1_router.include_router(interviewers_router)
# api_v1_router.include_router(exams_router)
# api_v1_router.include_router(questions_router)
# api_v1_router.include_router(attempts_router)
