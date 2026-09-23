from __future__ import annotations

from dataclasses import asdict, dataclass
import uuid

from .experimenter import ExperimentPlan


@dataclass
class StepState:
    index: int
    text: str
    done: bool


@dataclass
class ExperimentGuideState:
    sessionId: str
    title: str
    status: str
    currentStepIndex: int
    steps: list[StepState]
    resultInputRequired: bool


class ExperimentStepGuideService:
    def __init__(self) -> None:
        self._sessions: dict[str, ExperimentGuideState] = {}

    def start(self, plan: ExperimentPlan) -> ExperimentGuideState:
        session_id = str(uuid.uuid4())
        steps = [StepState(index=i + 1, text=step, done=False) for i, step in enumerate(plan.steps)]
        state = ExperimentGuideState(
            sessionId=session_id,
            title=plan.title,
            status="in_progress",
            currentStepIndex=1 if steps else 0,
            steps=steps,
            resultInputRequired=False,
        )
        self._sessions[session_id] = state
        return state

    def get(self, session_id: str) -> ExperimentGuideState:
        if session_id not in self._sessions:
            raise ValueError("존재하지 않는 실험 세션입니다.")
        return self._sessions[session_id]

    def complete_current_step(self, session_id: str) -> ExperimentGuideState:
        state = self.get(session_id)
        if state.status == "completed":
            return state

        current = self._find_current_step(state)
        if current is None:
            state.status = "completed"
            state.currentStepIndex = 0
            state.resultInputRequired = True
            return state

        current.done = True

        next_step = self._find_next_step(state)
        if next_step is None:
            state.currentStepIndex = 0
            state.status = "awaiting_result"
            state.resultInputRequired = True
        else:
            state.currentStepIndex = next_step.index

        return state

    def submit_result(self, session_id: str) -> ExperimentGuideState:
        state = self.get(session_id)
        state.status = "completed"
        state.currentStepIndex = 0
        state.resultInputRequired = False
        return state

    def list_sessions(self) -> list[ExperimentGuideState]:
        return list(self._sessions.values())

    def _find_current_step(self, state: ExperimentGuideState) -> StepState | None:
        for step in state.steps:
            if step.index == state.currentStepIndex:
                return step
        return None

    def _find_next_step(self, state: ExperimentGuideState) -> StepState | None:
        for step in state.steps:
            if not step.done:
                return step
        return None


def as_dict(state: ExperimentGuideState) -> dict:
    return {
        "sessionId": state.sessionId,
        "title": state.title,
        "status": state.status,
        "currentStepIndex": state.currentStepIndex,
        "steps": [asdict(step) for step in state.steps],
        "resultInputRequired": state.resultInputRequired,
    }
