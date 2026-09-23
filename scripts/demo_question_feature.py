from __future__ import annotations

from pathlib import Path
import json

from src.world_explorer_vision.questioning import QuestionService, as_dict, follow_up_as_dict
from src.world_explorer_vision.recognizer import RecognitionService


def main() -> None:
    recognizer = RecognitionService(feedback_file=Path("data/recognition_feedback.jsonl"))
    service = QuestionService(recognizer=recognizer)

    samples = [
        service.ask_text("왜 비가 오면 흙 냄새가 나", level="very_easy"),
        service.ask_voice("왜 달은 내가 움직이면 따라오는 것처럼 보여", level="easy"),
        service.ask_photo("ice_in_cup.jpg", "여기 있는 얼음은 왜 떠 있어", level="detailed"),
        service.ask_photo("tree_leaf.png", image_hint="tree", level="professional"),
    ]

    for idx, item in enumerate(samples, start=1):
        print(f"\n=== SAMPLE {idx} ===")
        print(json.dumps(as_dict(item), ensure_ascii=False, indent=2))

    followup_1 = service.start_follow_up("왜 얼음은 물에 떠?", level="easy")
    followup_2 = service.ask_follow_up(followup_1.threadId, "왜 밀도가 낮아?", level="detailed")
    followup_3 = service.ask_follow_up(followup_1.threadId, "그럼 모든 물질도 얼면 가벼워져?", level="professional")

    print("\n=== FOLLOW-UP SAMPLE 1 ===")
    print(json.dumps(follow_up_as_dict(followup_1), ensure_ascii=False, indent=2))

    print("\n=== FOLLOW-UP SAMPLE 2 ===")
    print(json.dumps(follow_up_as_dict(followup_2), ensure_ascii=False, indent=2))

    print("\n=== FOLLOW-UP SAMPLE 3 ===")
    print(json.dumps(follow_up_as_dict(followup_3), ensure_ascii=False, indent=2))

    print("\n=== FOLLOW-UP HISTORY ===")
    print(json.dumps(service.get_follow_up_history(followup_1.threadId), ensure_ascii=False, indent=2))

    observation_plan = service.create_observation_plan("그림자는 왜 생겨?")
    print("\n=== OBSERVATION PLAN SAMPLE ===")
    print(json.dumps(observation_plan, ensure_ascii=False, indent=2))

    experiment_suggestions = service.create_experiment_suggestions(
        "집에서 얼음으로 확인할 수 있는 실험이 뭐야?",
        available_items=["컵", "물", "얼음", "종이", "동전"],
    )
    print("\n=== EXPERIMENT SUGGESTION SAMPLE ===")
    print(json.dumps(experiment_suggestions, ensure_ascii=False, indent=2))

    step_guide_start = service.start_experiment_guide(
        "집에서 얼음으로 확인할 수 있는 실험이 뭐야?",
        available_items=["컵", "물", "얼음", "종이", "동전"],
        selected_index=0,
    )
    session_id = step_guide_start["guide"]["sessionId"]

    print("\n=== STEP GUIDE START ===")
    print(json.dumps(step_guide_start, ensure_ascii=False, indent=2))

    step_1_done = service.complete_experiment_step(session_id)
    step_2_done = service.complete_experiment_step(session_id)
    step_3_done = service.complete_experiment_step(session_id)

    print("\n=== STEP GUIDE AFTER STEP 1 ===")
    print(json.dumps(step_1_done, ensure_ascii=False, indent=2))

    print("\n=== STEP GUIDE AFTER STEP 2 ===")
    print(json.dumps(step_2_done, ensure_ascii=False, indent=2))

    print("\n=== STEP GUIDE AFTER STEP 3 ===")
    print(json.dumps(step_3_done, ensure_ascii=False, indent=2))

    result_submitted = service.submit_experiment_result(session_id)
    print("\n=== STEP GUIDE COMPLETED ===")
    print(json.dumps(result_submitted, ensure_ascii=False, indent=2))

    service.add_experiment_photo(session_id, "start", "photo_start_001.jpg")
    service.add_experiment_photo(session_id, "middle", "photo_middle_001.jpg")
    service.add_experiment_photo(session_id, "end", "photo_end_001.jpg")
    service.add_experiment_observation(session_id, "햇빛 쪽 얼음이 먼저 작아졌어요.")
    service.add_experiment_measurement(session_id, "5분 후 얼음 지름", 2.4, "cm")
    service.set_experiment_expected_result(session_id, "햇빛 쪽 얼음이 더 빨리 녹을 것이다.")
    service.set_experiment_actual_result(session_id, "햇빛 쪽 얼음이 더 빨리 녹았다.")

    record_snapshot = service.get_experiment_record(session_id)
    print("\n=== EXPERIMENT RECORD SAMPLE ===")
    print(json.dumps(record_snapshot, ensure_ascii=False, indent=2))

    analysis_snapshot = service.analyze_experiment_result(session_id)
    print("\n=== EXPERIMENT ANALYSIS SAMPLE ===")
    print(json.dumps(analysis_snapshot, ensure_ascii=False, indent=2))

    related_snapshot = service.recommend_related_questions("왜 하늘은 파란색일까?")
    print("\n=== RELATED QUESTION SAMPLE ===")
    print(json.dumps(related_snapshot, ensure_ascii=False, indent=2))

    vault_all = service.get_curiosity_vault()
    print("\n=== CURIOSITY VAULT ALL ===")
    print(json.dumps(vault_all, ensure_ascii=False, indent=2))

    if vault_all["entries"]:
        first_entry_id = vault_all["entries"][0]["entryId"]
        changed = service.update_curiosity_category(first_entry_id, "자연")
        print("\n=== CURIOSITY CATEGORY UPDATED ===")
        print(json.dumps(changed, ensure_ascii=False, indent=2))

    vault_search = service.search_curiosity_vault("얼음")
    print("\n=== CURIOSITY VAULT SEARCH (얼음) ===")
    print(json.dumps(vault_search, ensure_ascii=False, indent=2))

    catalog_all = service.get_science_catalog()
    print("\n=== SCIENCE CATALOG ALL ===")
    print(json.dumps(catalog_all, ensure_ascii=False, indent=2))

    catalog_physics = service.get_science_catalog("물리")
    print("\n=== SCIENCE CATALOG PHYSICS ===")
    print(json.dumps(catalog_physics, ensure_ascii=False, indent=2))

    catalog_search = service.search_science_catalog("열")
    print("\n=== SCIENCE CATALOG SEARCH (열) ===")
    print(json.dumps(catalog_search, ensure_ascii=False, indent=2))

    today_pick = service.get_today_curiosity(limit=1)
    print("\n=== TODAY CURIOSITY ===")
    print(json.dumps(today_pick, ensure_ascii=False, indent=2))

    if today_pick["items"]:
        question = today_pick["items"][0]["question"]
        action_explain = service.choose_today_curiosity_action(question, "알아보기", level="easy")
        print("\n=== TODAY ACTION: 알아보기 ===")
        print(json.dumps(action_explain, ensure_ascii=False, indent=2))

        action_observe = service.choose_today_curiosity_action(question, "직접 확인하기", level="easy")
        print("\n=== TODAY ACTION: 직접 확인하기 ===")
        print(json.dumps(action_observe, ensure_ascii=False, indent=2))

    exploration_record = service.get_exploration_record()
    print("\n=== EXPLORATION RECORD ===")
    print(json.dumps(exploration_record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
