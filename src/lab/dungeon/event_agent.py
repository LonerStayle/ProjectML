"""
Event Planning Agent
난이도 컨텍스트를 기반으로 이벤트를 계획하는 Agent
엑셀 데이터 스프레드시트 구조를 기반으로 작성
"""
from typing import List
from .models import RoomData, StatData
from .state import DifficultyContext


class EventPlanningAgent:
    """이벤트 계획 Agent"""
    
    # 이벤트 타입 정의 (엑셀 roomData 구조: 0:빈방, 1:전투, 2:이벤트, 3:보물)
    # eventType은 이벤트 방(type=2)에서만 사용됨
    EVENT_TYPES = {
        0: "빈 이벤트",
        1: "회복의 샘",
        2: "상인",
        3: "신비한 사건"
    }
    
    def __init__(self, hero_stats: List[StatData]):
        self.hero_stats = hero_stats
    
    def select_event_type(self, room: RoomData, difficulty_context: DifficultyContext) -> int:
        """
        방의 정보와 난이도 컨텍스트를 기반으로 이벤트 타입 선택
        
        Args:
            room: 방 데이터
            difficulty_context: 난이도 컨텍스트
        
        Returns:
            이벤트 타입 (0~3)
        """
        import random
        
        # 예산 사용률이 높으면 (어려운 던전) 회복 이벤트 확률 증가
        budget_utilization = difficulty_context.get("budget_utilization", 0.5)
        
        if budget_utilization > 0.8:
            # 어려운 던전: 회복 확률 높음
            weights = {
                0: 0.1,  # 빈 이벤트
                1: 0.5,  # 회복의 샘
                2: 0.2,  # 상인
                3: 0.2   # 신비한 사건
            }
        elif budget_utilization < 0.5:
            # 쉬운 던전: 상인/신비한 사건 확률 높음
            weights = {
                0: 0.2,  # 빈 이벤트
                1: 0.1,  # 회복의 샘
                2: 0.4,  # 상인
                3: 0.3   # 신비한 사건
            }
        else:
            # 보통 던전: 균형잡힌 분포
            weights = {
                0: 0.15,  # 빈 이벤트
                1: 0.3,   # 회복의 샘
                2: 0.3,   # 상인
                3: 0.25   # 신비한 사건
            }
        
        # 정규화
        total = sum(weights.values())
        weights = {k: v / total for k, v in weights.items()}
        
        # 가중치 기반 랜덤 선택
        event_types = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(event_types, weights=probabilities, k=1)[0]
    
    def update_rooms_with_events(
        self, 
        rooms: List[RoomData], 
        difficulty_context: DifficultyContext
    ) -> List[RoomData]:
        """
        방 데이터에 이벤트 타입 추가
        
        Args:
            rooms: 방 데이터 리스트
            difficulty_context: 난이도 컨텍스트
        
        Returns:
            이벤트가 추가된 방 데이터 리스트
        """
        updated_rooms = []
        
        for room in rooms:
            # 이벤트 방(type=2)인 경우에만 이벤트 타입 선택
            if room.room_type == 2 and room.event_type is None:
                event_type = self.select_event_type(room, difficulty_context)
                # 새로운 RoomData 생성 (event_type 업데이트)
                updated_room = RoomData(
                    room_id=room.room_id,
                    room_type=room.room_type,
                    size=room.size,
                    neighbors=room.neighbors,
                    monsters=room.monsters,
                    event_type=event_type
                )
                updated_rooms.append(updated_room)
            else:
                # 이벤트 방이 아니거나 이미 event_type이 설정된 경우 그대로 사용
                updated_rooms.append(room)
        
        return updated_rooms

