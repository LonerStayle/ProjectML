from typing import Dict, Any
from langgraph.graph import START, END, StateGraph
from agents.dungeon.dungeon_state import SuperDungeonState, DungeonEventState



# ===== Node 1: Event Processing =====
def event_node(state: SuperDungeonState) -> SuperDungeonState:
    """
    Event Agent를 실행하는 노드
    - 히로인 정보와 던전 정보를 기반으로 이벤트 생성
    """
    print("\n[Event Node] 이벤트 생성 시작...")

    # TODO: 실제 Event Agent 호출 (현재는 임시 구현)
    # from agents.dungeon.event.dungeon_event_agent import graph_builder as event_graph

    event_result = {
        "main_event": "임시_메인_이벤트",
        "sub_event": "임시_서브_이벤트",
        "event_room": state.get("heroine_data", {}).get("event_room", 3),
        "description": "이벤트 생성 완료",
    }

    print(f"[Event Node] 완료: {event_result.get('main_event', 'N/A')}")

    return {"event_result": event_result}


# ===== Node 2: Monster Balancing =====
def monster_node(state: SuperDungeonState) -> Dict[str, Any]:
    """
    Monster Agent를 실행하는 노드
    - 던전 맵에 몬스터를 배치하고 밸런싱
    """
    print("\n[Monster Node] 몬스터 밸런싱 시작...")

    # TODO: 실제 Monster Agent 호출
    # from agents.dungeon.monster.nodes import monster_balancing_node

    monster_result = {"monsters": [], "total_difficulty": 0, "rooms_filled": 0}

    difficulty_log = {
        "ai_multiplier": 1.0,
        "target_score": 0,
        "ai_reasoning": "임시 로그",
    }

    print(f"[Monster Node] 완료: {len(monster_result.get('monsters', []))}마리 배치")

    return {"monster_result": monster_result, "difficulty_log": difficulty_log}


# ===== Node 3: Merge Results (Algorithm Only) =====
def merge_results_node(state: SuperDungeonState) -> Dict[str, Any]:
    """
    Event와 Monster 결과를 알고리즘적으로 병합
    LLM 사용 없이 순수 로직으로 구현
    """
    print("\n[Merge Node] 결과 병합 시작 (알고리즘)...")

    # 1. 기본 던전 데이터 가져오기
    base_data = state.get("dungeon_base_data", {})
    event_result = state.get("event_result", {})
    monster_result = state.get("monster_result", {})
    difficulty_log = state.get("difficulty_log", {})

    # 2. 최종 JSON 구조 생성
    final_json = {
        # 기본 던전 구조 유지
        "dungeon_id": base_data.get("dungeon_id", "unknown"),
        "floor": base_data.get("floor", 1),
        "rooms": base_data.get("rooms", []),
        # Event 정보 병합
        "events": {
            "main_event": event_result.get("main_event", ""),
            "sub_event": event_result.get("sub_event", ""),
            "event_room_index": event_result.get("event_room", -1),
            "description": event_result.get("description", ""),
        },
        # Monster 정보 병합
        "monsters": {
            "spawn_list": monster_result.get("monsters", []),
            "total_count": len(monster_result.get("monsters", [])),
            "total_difficulty": monster_result.get("total_difficulty", 0),
            "rooms_filled": monster_result.get("rooms_filled", 0),
        },
        # 메타 정보
        "meta": {
            "difficulty_multiplier": difficulty_log.get("ai_multiplier", 1.0),
            "ai_reasoning": difficulty_log.get("ai_reasoning", ""),
            "target_score": difficulty_log.get("target_score", 0),
            "generated_at": "2025-11-28",  # 실제로는 datetime 사용
        },
    }

    print(f"[Merge Node] 병합 완료:")
    print(f"  - Events: {final_json['events']['main_event']}")
    print(f"  - Monsters: {final_json['monsters']['total_count']}마리")
    print(f"  - Difficulty: x{final_json['meta']['difficulty_multiplier']}")

    return {"final_dungeon_json": final_json}


# ===== Graph Construction =====
def create_super_dungeon_graph():
    """
    Super Dungeon Agent의 LangGraph 생성
    Event와 Monster를 병렬 실행하고 결과를 병합
    """
    graph_builder = StateGraph(SuperDungeonState)

    # 노드 추가
    graph_builder.add_node("event_node", event_node)
    graph_builder.add_node("monster_node", monster_node)
    graph_builder.add_node("merge_results_node", merge_results_node)

    # Edge 연결 (병렬 실행)
    graph_builder.add_edge(START, "event_node")
    graph_builder.add_edge(START, "monster_node")

    # 두 노드가 완료되면 merge로 이동
    graph_builder.add_edge("event_node", "merge_results_node")
    graph_builder.add_edge("monster_node", "merge_results_node")

    # 최종 종료
    graph_builder.add_edge("merge_results_node", END)

    return graph_builder.compile()


# ===== Main Execution (for testing) =====
if __name__ == "__main__":
    print("=" * 60)
    print("Super Dungeon Agent - Base Code Test")
    print("=" * 60)

    # 테스트용 초기 State
    initial_state: SuperDungeonState = {
        "dungeon_base_data": {
            "dungeon_id": "test_dungeon_001",
            "floor": 1,
            "rooms": [
                {"room_id": 0, "type": "start"},
                {"room_id": 1, "type": "normal"},
                {"room_id": 2, "type": "normal"},
                {"room_id": 3, "type": "event"},
                {"room_id": 4, "type": "boss"},
            ],
        },
        "heroine_data": {
            "heroine_id": "hero_001",
            "name": "테스트 히로인",
            "event_room": 3,
            "memory_progress": 0,
        },
        "heroine_stats": [],
        "heroine_memories": [],
        "monster_db": {},
        "used_events": [],  # 이벤트 중복 방지용
        "event_result": {},
        "monster_result": {},
        "difficulty_log": {},
        "final_dungeon_json": {},
    }

    # Graph 생성 및 실행
    graph = create_super_dungeon_graph()
    result = graph.invoke(initial_state)

    print("\n" + "=" * 60)
    print("Final Result:")
    print("=" * 60)
    import json

    print(
        json.dumps(result.get("final_dungeon_json", {}), indent=2, ensure_ascii=False)
    )
