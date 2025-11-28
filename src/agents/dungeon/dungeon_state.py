from typing import TypedDict, Annotated, Dict, List, Any
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


# ===== Event Agent용 State =====
class DungeonEventState(TypedDict):
    """Event Agent 내부에서 사용하는 State"""

    messages: Annotated[list, add_messages]
    heroine_data: dict
    heroine_memories: list
    event_room: int
    next_floor: int
    used_events: list  # 이전 층에서 사용한 event_template_id 리스트 (중복 방지용)

    selected_main_event: str
    sub_event: str
    final_answer: str


class DungeonEventParser(BaseModel):
    """Event Agent의 LLM 응답 파서"""

    sibal: str = Field(description="asd")




class SuperDungeonState(TypedDict):
    # ===== Input Data =====
    # 언리얼에서 받아온 초기 던전 데이터
    dungeon_base_data: Dict[str, Any]  # 던전 기본 맵 구조 (rooms, floor 등)
    # 히로인 관련 데이터
    heroine_data: Dict[str, Any]  # 히로인 정보 (heroine_id, memory_progress, event_room 포함)
    heroine_stats: List[Any]  # 히로인 스탯 (몬스터 밸런싱용)
    heroine_memories: List[Any]  # 히로인 해금 정보
    # DB 및 설정
    monster_db: Dict[int, Any]  # 몬스터 DB (몬스터 에이전트에서 사용)
    # 이벤트 중복 방지용 (세션 전체에서 사용된 이벤트 추적)
    used_events: List[Dict[str, Any]]  # [{"event_template_id": 13, "room_id": 5, "floor": 1, "choice_id": "..."}]
    # ===== Agent 결과물 =====
    # Event Agent 결과
    main_event_result: str  # 이벤트 생성 결과
    sub_event_result: str
    # Monster Agent 결과
    monster_result: Dict[str, Any]  # 몬스터 배치 결과
    difficulty_log: Dict[str, Any]  # 난이도 로그
    # ===== Final Output =====
    # 최종 병합된 JSON
    final_dungeon_json: Dict[str, Any]
