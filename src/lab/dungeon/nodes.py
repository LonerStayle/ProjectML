"""
LangGraph Nodes 정의
각 Agent를 호출하여 State를 업데이트하는 노드 함수들
통신 프로토콜 스프레드시트 구조를 기반으로 작성
"""
from typing import Dict, Any, List
from .state import DungeonState, DifficultyContext
from .models import RoomData, DungeonData, RewardTable
from .monster_agent import MonsterCompositionAgent
from .event_agent import EventPlanningAgent


def monster_balancing_node(state: DungeonState) -> Dict[str, Any]:
    """
    Monster Agent를 호출하여 몬스터 배치 계획 생성
    
    통신 프로토콜:
    - 입력: player_ids, heroine_ids, hero_stats, monster_db, floor, room_count
    - 출력: rooms, difficulty_context
    
    Args:
        state: 현재 던전 상태
    
    Returns:
        업데이트할 State 딕셔너리
    """
    hero_stats = state["hero_stats"]
    monster_db = state["monster_db"]
    floor = state["floor"]
    room_count = state["room_count"]
    
    # Monster Agent 생성 및 실행
    agent = MonsterCompositionAgent(hero_stats, monster_db)
    rooms, difficulty_context = agent.generate_rooms(floor, room_count)
    
    return {
        "rooms": rooms,
        "difficulty_context": difficulty_context
    }


def event_planning_node(state: DungeonState) -> Dict[str, Any]:
    """
    Event Agent를 호출하여 이벤트 계획 생성
    
    통신 프로토콜:
    - 입력: hero_stats, rooms, difficulty_context (Monster Agent 출력)
    - 출력: event_rooms
    
    Args:
        state: 현재 던전 상태 (rooms, difficulty_context 포함)
    
    Returns:
        업데이트할 State 딕셔너리
    """
    hero_stats = state["hero_stats"]
    rooms: List[RoomData] = state.get("rooms", [])
    difficulty_context: DifficultyContext = state.get("difficulty_context", {})
    
    # Event Agent 생성 및 실행
    agent = EventPlanningAgent(hero_stats)
    event_rooms: List[RoomData] = agent.update_rooms_with_events(rooms, difficulty_context)
    
    return {
        "event_rooms": event_rooms
    }


def item_planning_node(state: DungeonState) -> Dict[str, Any]:
    """
    Item Agent를 호출하여 아이템 계획 생성 및 최종 던전 데이터 생성
    
    통신 프로토콜:
    - 입력: player_ids, heroine_ids, event_rooms, difficulty_context
    - 출력: dungeon_data (보상 포함)
    
    Args:
        state: 현재 던전 상태
    
    Returns:
        업데이트할 State 딕셔너리
    """
    player_ids = state["player_ids"]
    heroine_ids = state["heroine_ids"]
    event_rooms = state.get("event_rooms", state.get("rooms", []))
    
    # TODO: Item Agent 구현 - 보상 테이블 생성
    # 현재는 빈 보상 테이블로 생성
    rewards: List[RewardTable] = []
    
    # 최종 던전 데이터 생성
    dungeon_data = DungeonData(
        player_ids=player_ids,
        heroine_ids=heroine_ids,
        rooms=event_rooms,
        rewards=rewards
    )
    
    return {
        "dungeon_data": dungeon_data
    }

