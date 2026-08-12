from types import SimpleNamespace

import pytest

from app.api.v1.router import api_v1_router
from app.core.constants import QuestionType
from app.core.exceptions import ValidationError
from app.schemas.question import QuestionCandidateResponse
from app.services.submission_service import SubmissionService


def test_phase3_routers_are_registered_once() -> None:
    route_names = []
    for included_router in api_v1_router.routes:
        router = getattr(included_router, "original_router", None)
        if router is None:
            continue
        route_names.extend(getattr(route, "name", "") for route in router.routes)

    expected_route_names = {
        "create_exam",
        "list_exams",
        "get_exam",
        "update_exam",
        "delete_exam",
        "publish_exam",
        "schedule_exam",
        "assign_candidates",
        "list_candidates",
        "remove_candidate",
        "create_question",
        "list_questions",
        "get_question",
        "update_question",
        "delete_question",
        "start_attempt",
        "get_attempt",
        "save_answer",
        "submit_exam",
        "get_attempt_result",
        "list_exam_results",
    }

    for route_name in expected_route_names:
        assert route_names.count(route_name) == 1


def test_candidate_question_response_strips_correct_index() -> None:
    question = SimpleNamespace(
        id="00000000-0000-0000-0000-000000000001",
        exam_id="00000000-0000-0000-0000-000000000002",
        question_type=QuestionType.MCQ,
        content="Pick the correct option",
        marks=2.0,
        order_number=1,
        options={"choices": ["A", "B"], "correct_index": 1},
    )

    response = QuestionCandidateResponse.from_question(question)

    assert response.options == {"choices": ["A", "B"]}


def test_mcq_evaluation_uses_server_correct_index() -> None:
    is_correct, score = SubmissionService._evaluate_mcq(
        {"selected_index": 1},
        {"choices": ["A", "B"], "correct_index": 1},
        5.0,
    )

    assert is_correct is True
    assert score == 5.0


@pytest.mark.parametrize(
    ("answer_data", "question_type"),
    [
        ({"selected_index": 0, "score_awarded": 10}, QuestionType.MCQ),
        ({"text": "answer", "is_correct": True}, QuestionType.SHORT_ANSWER),
        ({"code": "print(1)", "stdout": "1"}, QuestionType.CODING),
        ({"file_path": "answer.pdf", "score": 10}, QuestionType.FILE),
        ({"anything": "goes"}, "UNKNOWN"),
    ],
)
def test_answer_validation_rejects_untrusted_or_unknown_fields(
    answer_data: dict,
    question_type: str,
) -> None:
    with pytest.raises(ValidationError):
        SubmissionService._validate_answer_data(answer_data, question_type)


@pytest.mark.parametrize(
    ("answer_data", "question_type"),
    [
        ({"selected_index": 0}, QuestionType.MCQ),
        ({"text": "short answer"}, QuestionType.SHORT_ANSWER),
        ({"code": "print(1)", "language": "python"}, QuestionType.CODING),
        ({"file_path": "uploads/attempt/file.pdf"}, QuestionType.FILE),
    ],
)
def test_answer_validation_accepts_supported_payloads(
    answer_data: dict,
    question_type: str,
) -> None:
    SubmissionService._validate_answer_data(answer_data, question_type)
