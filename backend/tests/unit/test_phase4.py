from __future__ import annotations

import uuid
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch



import httpx
import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from pydantic import ValidationError as PydanticValidationError

from app.core.constants import RoleName
from app.core.exceptions import AuthorizationError, NotFoundError
from app.database.dependencies import get_db
from app.dependencies.auth import get_current_user
from app.schemas.admin import AdminRoleChangeRequest, AdminUserUpdate, SystemSettingUpdate
from app.schemas.proctoring_warning import WarningCreate
from app.services.analytics_service import AnalyticsService
from app.services.interviewer_service import InterviewerService
from app.services.notification_service import NotificationService
from app.services.proctoring_service import ProctoringService
from app.services.report_service import ReportService
from app.services.student_service import StudentService


ADMIN_ID = uuid.UUID("10000000-0000-0000-0000-000000000001")
INTERVIEWER_A_ID = uuid.UUID("20000000-0000-0000-0000-000000000001")
INTERVIEWER_B_ID = uuid.UUID("20000000-0000-0000-0000-000000000002")
STUDENT_A_ID = uuid.UUID("30000000-0000-0000-0000-000000000001")
STUDENT_B_ID = uuid.UUID("30000000-0000-0000-0000-000000000002")
EXAM_A_ID = uuid.UUID("40000000-0000-0000-0000-000000000001")
EXAM_B_ID = uuid.UUID("40000000-0000-0000-0000-000000000002")
ATTEMPT_A_ID = uuid.UUID("50000000-0000-0000-0000-000000000001")
ATTEMPT_B_ID = uuid.UUID("50000000-0000-0000-0000-000000000002")
RESULT_B_ID = uuid.UUID("60000000-0000-0000-0000-000000000002")
NOTIFICATION_B_ID = uuid.UUID("70000000-0000-0000-0000-000000000002")


def _user(user_id: uuid.UUID, role: RoleName) -> SimpleNamespace:
    return SimpleNamespace(
        id=user_id,
        email=f"{role.value.lower()}-{user_id}@example.test",
        role=SimpleNamespace(name=role.value),
        is_active=True,
        created_at=datetime.now(timezone.utc),
        last_login_at=None,
    )


import pytest_asyncio

@pytest.fixture()
def admin_user() -> SimpleNamespace:
    return _user(ADMIN_ID, RoleName.ADMIN)


@pytest.fixture()
def interviewer_user() -> SimpleNamespace:
    return _user(INTERVIEWER_A_ID, RoleName.INTERVIEWER)


@pytest.fixture()
def student_user() -> SimpleNamespace:
    return _user(STUDENT_A_ID, RoleName.CANDIDATE)


@pytest_asyncio.fixture()
async def phase4_client(
    app: FastAPI,
    admin_user: SimpleNamespace,
) -> AsyncClient:
    db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: db
    app.dependency_overrides[get_current_user] = lambda: admin_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


def test_phase4_routers_are_registered_once() -> None:
    route_paths = list(
        __import__("app.main", fromlist=["create_app"]).create_app().openapi()["paths"]
    )

    expected_paths = {
        "/api/v1/admin/dashboard",
        "/api/v1/admin/users",
        "/api/v1/admin/students",
        "/api/v1/admin/interviewers",
        "/api/v1/admin/analytics",
        "/api/v1/admin/warnings",
        "/api/v1/admin/activity-logs",
        "/api/v1/admin/settings",
        "/api/v1/student/dashboard",
        "/api/v1/student/exams/upcoming",
        "/api/v1/student/exams/completed",
        "/api/v1/student/profile",
        "/api/v1/student/notifications",
        "/api/v1/student/exam-history",
        "/api/v1/student/results",
        "/api/v1/student/performance",
        "/api/v1/interviewer/dashboard",
        "/api/v1/interviewer/exams/{exam_id}/candidates",
        "/api/v1/interviewer/exams/{exam_id}/warnings",
        "/api/v1/interviewer/attempts/{attempt_id}/activity",
        "/api/v1/interviewer/exams/{exam_id}/results/publish",
        "/api/v1/interviewer/exams/{exam_id}/reports",
        "/api/v1/notifications",
        "/api/v1/proctoring/attempts/{attempt_id}/warnings",
        "/api/v1/proctoring/attempts/{attempt_id}/warnings/summary",
        "/api/v1/analytics/platform",
        "/api/v1/analytics/exams/{exam_id}",
        "/api/v1/reports/exams/{exam_id}",
        "/api/v1/reports/candidates/{candidate_id}",
    }

    for path in expected_paths:
        assert route_paths.count(path) == 1


@pytest.mark.asyncio
async def test_swagger_openapi_exposes_phase4_routes(client: AsyncClient) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    for prefix in (
        "/api/v1/admin/",
        "/api/v1/student/",
        "/api/v1/interviewer/",
        "/api/v1/notifications",
        "/api/v1/proctoring/",
        "/api/v1/analytics/",
        "/api/v1/reports/",
    ):
        assert any(path.startswith(prefix) for path in paths)


@pytest.mark.asyncio
async def test_admin_dashboard_and_management_endpoints(
    phase4_client: AsyncClient,
) -> None:
    with (
        patch.object(AnalyticsService, "get_platform_stats", new=AsyncMock(return_value=_platform_stats())),
        patch("app.services.admin_service.AdminService.list_users", new=AsyncMock(return_value=_admin_list())),
        patch("app.services.admin_service.AdminService.list_activity_logs", new=AsyncMock(return_value=_page())),
        patch("app.services.admin_service.AdminService.list_settings", new=AsyncMock(return_value=[])),
        patch("app.services.proctoring_service.ProctoringService.list_all", new=AsyncMock(return_value=_warning_list())),
    ):
        for path in (
            "/api/v1/admin/dashboard",
            "/api/v1/admin/users",
            "/api/v1/admin/students",
            "/api/v1/admin/interviewers",
            "/api/v1/admin/analytics",
            "/api/v1/admin/warnings",
            "/api/v1/admin/activity-logs",
            "/api/v1/admin/settings",
        ):
            response = await phase4_client.get(path)
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_student_dashboard_profile_notifications_history_results_performance(
    app: FastAPI,
    student_user: SimpleNamespace,
) -> None:
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_current_user] = lambda: student_user
    with (
        patch.object(StudentService, "list_assigned_exams", new=AsyncMock(return_value=_student_exam_list())),
        patch.object(StudentService, "list_results", new=AsyncMock(return_value=_student_result_list())),
        patch.object(StudentService, "get_profile", new=AsyncMock(return_value=_profile(STUDENT_A_ID, RoleName.CANDIDATE))),
        patch.object(NotificationService, "list_for_user", new=AsyncMock(return_value=_notification_list())),
        patch.object(AnalyticsService, "get_candidate_analytics", new=AsyncMock(return_value=_candidate_analytics())),
    ):
        async with AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://testserver",
        ) as ac:
            for path in (
                "/api/v1/student/dashboard",
                "/api/v1/student/exams/upcoming",
                "/api/v1/student/exams/completed",
                "/api/v1/student/profile",
                "/api/v1/student/notifications",
                "/api/v1/student/exam-history",
                "/api/v1/student/results",
                "/api/v1/student/performance",
            ):
                response = await ac.get(path)
                assert response.status_code == 200
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_interviewer_dashboard_candidates_warnings_activity_publish_reports(
    app: FastAPI,
    interviewer_user: SimpleNamespace,
) -> None:
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_current_user] = lambda: interviewer_user
    with (
        patch.object(InterviewerService, "list_my_exams", new=AsyncMock(return_value=_interviewer_exam_list())),
        patch.object(InterviewerService, "list_my_candidates", new=AsyncMock(return_value=_candidate_list())),
        patch.object(InterviewerService, "verify_exam_owner", new=AsyncMock()),
        patch.object(InterviewerService, "list_attempt_activity", new=AsyncMock(return_value=_page())),
        patch.object(InterviewerService, "publish_results", new=AsyncMock(return_value={"message": "Results published.", "published_count": 1})),
        patch.object(ProctoringService, "list_all", new=AsyncMock(return_value=_warning_list())),
        patch.object(ReportService, "generate_exam_report", new=AsyncMock(return_value=_exam_report())),
    ):
        async with AsyncClient(
            transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
            base_url="http://testserver",
        ) as ac:
            for method, path in (
                ("GET", "/api/v1/interviewer/dashboard"),
                ("GET", f"/api/v1/interviewer/exams/{EXAM_A_ID}/candidates"),
                ("GET", f"/api/v1/interviewer/exams/{EXAM_A_ID}/warnings"),
                ("GET", f"/api/v1/interviewer/attempts/{ATTEMPT_A_ID}/activity"),
                ("POST", f"/api/v1/interviewer/exams/{EXAM_A_ID}/results/publish"),
                ("GET", f"/api/v1/interviewer/exams/{EXAM_A_ID}/reports"),
            ):
                response = await ac.request(method, path)
                assert response.status_code == 200
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_notifications_analytics_reports_and_proctoring_endpoints(
    phase4_client: AsyncClient,
) -> None:
    with (
        patch.object(NotificationService, "list_for_user", new=AsyncMock(return_value=_notification_list())),
        patch.object(NotificationService, "get_unread_count", new=AsyncMock(return_value=SimpleNamespace(unread_count=1))),
        patch.object(AnalyticsService, "get_platform_stats", new=AsyncMock(return_value=_platform_stats())),
        patch.object(AnalyticsService, "get_exam_analytics", new=AsyncMock(return_value=_exam_analytics())),
        patch.object(ReportService, "generate_exam_report", new=AsyncMock(return_value=_exam_report())),
        patch.object(ReportService, "generate_candidate_report", new=AsyncMock(return_value=_candidate_report())),
        patch.object(ProctoringService, "list_by_attempt", new=AsyncMock(return_value=_warning_list())),
        patch.object(ProctoringService, "get_attempt_summary", new=AsyncMock(return_value=_warning_summary())),
    ):
        for path in (
            "/api/v1/notifications",
            "/api/v1/notifications/unread-count",
            "/api/v1/analytics/platform",
            f"/api/v1/analytics/exams/{EXAM_A_ID}",
            f"/api/v1/reports/exams/{EXAM_A_ID}",
            f"/api/v1/reports/candidates/{STUDENT_A_ID}",
            f"/api/v1/proctoring/attempts/{ATTEMPT_A_ID}/warnings",
            f"/api/v1/proctoring/attempts/{ATTEMPT_A_ID}/warnings/summary",
        ):
            response = await phase4_client.get(path)
            assert response.status_code == 200


@pytest.mark.asyncio
async def test_rbac_rejects_wrong_roles(app: FastAPI, student_user: SimpleNamespace) -> None:
    app.dependency_overrides[get_db] = lambda: AsyncMock()
    app.dependency_overrides[get_current_user] = lambda: student_user
    async with AsyncClient(
        transport=httpx.ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://testserver",
    ) as ac:
        response = await ac.get("/api/v1/admin/dashboard")
        assert response.status_code == 403
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_unauthorized_access_requires_authentication(client: AsyncClient) -> None:
    response = await client.get("/api/v1/student/dashboard")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_student_idor_rejects_other_student_profile_result_and_notifications() -> None:
    db = AsyncMock()

    user_service = AsyncMock()
    user_service.get_by_id.side_effect = lambda user_id: _user(user_id, RoleName.CANDIDATE)
    service = StudentService(db)
    service._user_service = user_service
    profile = await service.get_profile(STUDENT_A_ID)
    assert profile.id == STUDENT_A_ID
    user_service.get_by_id.assert_awaited_once_with(STUDENT_A_ID)

    db.execute.return_value = MagicMock(one_or_none=MagicMock(return_value=None))
    with pytest.raises(NotFoundError):
        await service.get_result(STUDENT_A_ID, RESULT_B_ID)

    notification_repo = AsyncMock()
    notification_repo.mark_read.return_value = False
    notification_service = NotificationService(db)
    notification_service._repo = notification_repo
    with pytest.raises(NotFoundError):
        await notification_service.mark_read(NOTIFICATION_B_ID, STUDENT_A_ID)


@pytest.mark.asyncio
async def test_interviewer_idor_rejects_other_interviewer_exam_candidates_reports() -> None:
    db = AsyncMock()
    db.get.return_value = SimpleNamespace(id=EXAM_B_ID, created_by=INTERVIEWER_B_ID)

    with pytest.raises(AuthorizationError):
        await InterviewerService(db).verify_exam_owner(EXAM_B_ID, INTERVIEWER_A_ID)

    with pytest.raises(AuthorizationError):
        await InterviewerService(db).list_my_candidates(
            INTERVIEWER_A_ID, exam_id=EXAM_B_ID
        )

    with pytest.raises(AuthorizationError):
        await ReportService(db).generate_exam_report(
            EXAM_B_ID, requesting_user_id=INTERVIEWER_A_ID, is_admin=False
        )


@pytest.mark.asyncio
async def test_ownership_checks_reject_other_student_attempt_and_interviewer_attempt() -> None:
    candidate_db = AsyncMock()
    candidate_db.get.return_value = SimpleNamespace(
        id=ATTEMPT_B_ID,
        candidate_id=STUDENT_B_ID,
        status="IN_PROGRESS",
    )
    with pytest.raises(NotFoundError):
        await ProctoringService(candidate_db).log_warning(
            ATTEMPT_B_ID,
            STUDENT_A_ID,
            WarningCreate(violation_type="TAB_SWITCH"),
        )

    interviewer_db = AsyncMock()
    interviewer_db.get.side_effect = [
        SimpleNamespace(id=ATTEMPT_B_ID, exam_id=EXAM_B_ID),
        SimpleNamespace(id=EXAM_B_ID, created_by=INTERVIEWER_B_ID),
    ]
    with pytest.raises(AuthorizationError):
        await InterviewerService(interviewer_db).verify_attempt_owner(
            ATTEMPT_B_ID, INTERVIEWER_A_ID
        )


def test_phase4_request_schemas_reject_mass_assignment() -> None:
    invalid_payloads = (
        (AdminUserUpdate, {"is_active": True, "role": "ADMIN"}),
        (AdminRoleChangeRequest, {"role": "ADMIN", "is_active": True}),
        (SystemSettingUpdate, {"value": "enabled", "updated_by": str(ADMIN_ID)}),
        (WarningCreate, {"violation_type": "TAB_SWITCH", "candidate_id": str(STUDENT_B_ID)}),
    )

    for schema, payload in invalid_payloads:
        with pytest.raises(PydanticValidationError):
            schema(**payload)


def _platform_stats() -> dict:
    return {
        "total_users": 3,
        "total_admins": 1,
        "total_interviewers": 1,
        "total_candidates": 1,
        "active_users": 3,
        "inactive_users": 0,
        "total_exams": 1,
        "draft_exams": 0,
        "published_exams": 1,
        "completed_exams": 0,
        "total_attempts": 1,
        "submitted_attempts": 0,
        "in_progress_attempts": 1,
        "total_results": 1,
        "evaluated_results": 1,
        "pending_evaluation_results": 0,
        "total_proctoring_warnings": 1,
    }


def _page() -> dict:
    return {"items": [], "total": 0, "page": 1, "page_size": 20, "total_pages": 0}


def _admin_list() -> dict:
    return {
        **_page(),
        "items": [
            {
                "id": STUDENT_A_ID,
                "email": "student@example.test",
                "role": "CANDIDATE",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "last_login_at": None,
            }
        ],
    }


def _student_exam_list() -> dict:
    return {
        **_page(),
        "items": [
            {
                "exam_id": EXAM_A_ID,
                "title": "Phase 4 Exam",
                "description": None,
                "duration_minutes": 30,
                "status": "PUBLISHED",
                "scheduled_at": None,
                "assigned_at": datetime.now(timezone.utc),
                "attempt_id": ATTEMPT_A_ID,
                "attempt_status": "IN_PROGRESS",
                "started_at": datetime.now(timezone.utc),
                "submitted_at": None,
            }
        ],
        "total": 1,
        "total_pages": 1,
    }


def _student_result_list() -> dict:
    return {
        **_page(),
        "items": [
            {
                "result_id": RESULT_B_ID,
                "exam_id": EXAM_A_ID,
                "exam_title": "Phase 4 Exam",
                "attempt_id": ATTEMPT_A_ID,
                "score": 8.0,
                "total_marks": 10.0,
                "percentage": 80.0,
                "total_questions": 5,
                "attempted_count": 5,
                "correct_count": 4,
                "status": "EVALUATED",
                "submitted_at": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
            }
        ],
        "total": 1,
        "total_pages": 1,
    }


def _profile(user_id: uuid.UUID, role: RoleName) -> dict:
    return {
        "id": user_id,
        "email": f"{role.value.lower()}@example.test",
        "role": role.value,
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "last_login_at": None,
    }


def _notification_list() -> dict:
    return {
        **_page(),
        "items": [
            {
                "id": NOTIFICATION_B_ID,
                "user_id": STUDENT_A_ID,
                "notification_type": "EXAM_ASSIGNED",
                "title": "Assigned",
                "message": "Exam assigned",
                "reference_id": EXAM_A_ID,
                "reference_type": "exam",
                "is_read": False,
                "created_at": datetime.now(timezone.utc),
            }
        ],
        "total": 1,
        "unread_count": 1,
        "total_pages": 1,
    }


def _candidate_analytics() -> dict:
    return {
        "candidate_id": STUDENT_A_ID,
        "email": "student@example.test",
        "total_exams_assigned": 1,
        "total_exams_attempted": 1,
        "total_exams_submitted": 1,
        "average_score": 8.0,
        "average_percentage": 80.0,
        "highest_percentage": 80.0,
        "total_proctoring_warnings": 1,
        "high_severity_warnings": 0,
    }


def _interviewer_exam_list() -> dict:
    return {
        **_page(),
        "items": [
            {
                "id": EXAM_A_ID,
                "title": "Phase 4 Exam",
                "description": None,
                "status": "PUBLISHED",
                "duration_minutes": 30,
                "scheduled_at": None,
                "created_at": datetime.now(timezone.utc),
                "total_questions": 5,
                "total_candidates": 1,
                "total_submissions": 1,
            }
        ],
        "total": 1,
        "total_pages": 1,
    }


def _candidate_list() -> dict:
    return {
        **_page(),
        "items": [
            {
                "candidate_id": STUDENT_A_ID,
                "email": "student@example.test",
                "exam_id": EXAM_A_ID,
                "exam_title": "Phase 4 Exam",
                "assigned_at": datetime.now(timezone.utc),
                "attempt_status": "SUBMITTED",
                "submitted_at": datetime.now(timezone.utc),
                "score": 8.0,
                "percentage": 80.0,
                "result_status": "EVALUATED",
            }
        ],
        "total": 1,
        "total_pages": 1,
    }


def _warning_list() -> dict:
    return {
        **_page(),
        "items": [
            {
                "id": uuid.uuid4(),
                "attempt_id": ATTEMPT_A_ID,
                "candidate_id": STUDENT_A_ID,
                "violation_type": "TAB_SWITCH",
                "severity": "LOW",
                "description": None,
                "created_at": datetime.now(timezone.utc),
            }
        ],
        "total": 1,
        "page_size": 50,
        "total_pages": 1,
    }


def _exam_analytics() -> dict:
    return {
        "exam_id": EXAM_A_ID,
        "exam_title": "Phase 4 Exam",
        "exam_status": "PUBLISHED",
        "total_candidates": 1,
        "started_attempts": 1,
        "submitted_attempts": 1,
        "abandoned_attempts": 0,
        "completion_rate": 100.0,
        "average_score": 8.0,
        "highest_score": 8.0,
        "lowest_score": 8.0,
        "average_percentage": 80.0,
        "evaluated_results": 1,
        "pending_evaluation_results": 0,
        "total_proctoring_warnings": 1,
    }


def _exam_report() -> dict:
    return {
        "exam_id": EXAM_A_ID,
        "exam_title": "Phase 4 Exam",
        "exam_status": "PUBLISHED",
        "duration_minutes": 30,
        "scheduled_at": None,
        "created_at": datetime.now(timezone.utc),
        "total_candidates": 1,
        "submitted_count": 1,
        "average_percentage": 80.0,
        "pass_count": 1,
        "fail_count": 0,
        "entries": [],
        "generated_at": datetime.now(timezone.utc),
    }


def _candidate_report() -> dict:
    return {
        "candidate_id": STUDENT_A_ID,
        "email": "student@example.test",
        "total_exams_assigned": 1,
        "total_exams_submitted": 1,
        "average_percentage": 80.0,
        "entries": [],
        "generated_at": datetime.now(timezone.utc),
    }


def _warning_summary() -> dict:
    return {
        "attempt_id": ATTEMPT_A_ID,
        "total_warnings": 1,
        "low_count": 1,
        "medium_count": 0,
        "high_count": 0,
        "critical_count": 0,
    }
