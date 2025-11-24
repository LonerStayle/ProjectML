"""
Monster Composition Agent
예산 내에서 몬스터를 조합하여 방을 구성하는 Agent
엑셀 데이터 스프레드시트 구조를 기반으로 작성
"""
import random
from typing import List, Dict, Any, Tuple
from .models import MonsterMetadata, StatData, RoomData, MonsterSpawnData
from .state import DifficultyContext


class MonsterCompositionAgent:
    """몬스터 조합 Agent"""
    
    def __init__(self, hero_stats: List[StatData], monster_db: Dict[int, MonsterMetadata]):
        self.hero_stats = hero_stats
        self.monster_db = monster_db
    
    def calculate_room_budget(self, tier: int, hero_combat_score: float) -> float:
        """
        난이도 티어에 따라 방 예산 계산
        
        Args:
            tier: 난이도 티어 (1=쉬움, 2=보통, 3=어려움)
            hero_combat_score: 히로인 전투력 점수
        
        Returns:
            예산 포인트 (float)
        """
        base_budget = hero_combat_score * 0.1  # 기본 예산은 전투력의 10%
        
        tier_multipliers = {
            1: 0.5,   # 쉬움: 50%
            2: 1.0,   # 보통: 100%
            3: 1.5    # 어려움: 150%
        }
        
        return base_budget * tier_multipliers.get(tier, 1.0)
    
    def generate_spawn_plan(self, budget: float, room_size: int) -> List[MonsterSpawnData]:
        """
        예산 내에서 몬스터를 랜덤 쇼핑하여 스폰 계획 생성
        
        Args:
            budget: 사용 가능한 예산
            room_size: 방 크기 (2~4)
        
        Returns:
            몬스터 스폰 데이터 리스트
        """
        spawn_plan: List[MonsterSpawnData] = []
        remaining_budget = budget
        
        # 몬스터 리스트를 비용 순으로 정렬 (저렴한 것부터)
        available_monsters = list(self.monster_db.values())
        available_monsters.sort(key=lambda m: m.cost_point)
        
        # Knapsack 유사 알고리즘: 예산 내에서 랜덤하게 선택
        max_attempts = 100
        attempts = 0
        
        while remaining_budget > 0 and attempts < max_attempts:
            attempts += 1
            
            # 예산에 맞는 몬스터 필터링
            affordable = [m for m in available_monsters if m.cost_point <= remaining_budget]
            
            if not affordable:
                break
            
            # 랜덤 선택 (비용이 낮은 몬스터가 더 자주 선택되도록 가중치 부여)
            weights = [1.0 / (m.cost_point + 1) for m in affordable]
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]
            
            selected = random.choices(affordable, weights=weights, k=1)[0]
            
            # 위치 계산 (0~1 범위의 정규화된 좌표)
            pos_x, pos_y = self._calculate_position(selected, len(spawn_plan), room_size)
            
            spawn_plan.append(MonsterSpawnData(
                monster_id=selected.monster_id,
                pos_x=pos_x,
                pos_y=pos_y
            ))
            
            remaining_budget -= selected.cost_point
        
        return spawn_plan
    
    def _calculate_position(self, monster: MonsterMetadata, spawn_index: int, room_size: int) -> Tuple[float, float]:
        """
        몬스터 위치 계산 (0~1 범위의 정규화된 좌표)
        - 원거리: 벽 쪽 (0.0~0.2 또는 0.8~1.0)
        - 근거리: 중앙 쪽 (0.3~0.7)
        
        Args:
            monster: 몬스터 메타데이터
            spawn_index: 스폰 순서
            room_size: 방 크기
        
        Returns:
            (posX, posY) 튜플 (0~1 범위)
        """
        if monster.is_ranged:
            # 원거리: 벽 쪽에 배치
            wall_positions = [
                (0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9),
                (0.1, 0.5), (0.9, 0.5), (0.5, 0.1), (0.5, 0.9),
                (0.2, 0.2), (0.2, 0.8), (0.8, 0.2), (0.8, 0.8)
            ]
            pos = wall_positions[spawn_index % len(wall_positions)]
        else:
            # 근거리: 중앙 쪽에 배치
            center_positions = [
                (0.5, 0.5), (0.4, 0.5), (0.6, 0.5), (0.5, 0.4), (0.5, 0.6),
                (0.3, 0.5), (0.7, 0.5), (0.5, 0.3), (0.5, 0.7),
                (0.4, 0.4), (0.6, 0.6), (0.4, 0.6), (0.6, 0.4)
            ]
            pos = center_positions[spawn_index % len(center_positions)]
        
        return pos
    
    def generate_rooms(self, floor: int, room_count: int) -> Tuple[List[RoomData], DifficultyContext]:
        """
        전체 층의 방 계획 생성
        
        Args:
            floor: 층 수
            room_count: 방 개수
        
        Returns:
            (rooms, difficulty_context) 튜플
        """
        rooms: List[RoomData] = []
        total_budget_used = 0.0
        total_budget_allocated = 0.0
        
        # 평균 히로인 전투력 계산
        avg_combat_score = sum(stat.combat_score for stat in self.hero_stats) / len(self.hero_stats) if self.hero_stats else 0.0
        hero_combat_scores = [stat.combat_score for stat in self.hero_stats]
        
        # 각 방의 티어 결정 (층이 깊을수록 어려워짐)
        for room_idx in range(room_count):
            # 층에 따라 기본 티어 결정
            base_tier = min(3, max(1, (floor - 1) // 3 + 1))
            
            # 방 타입 결정
            if room_idx == room_count - 1:
                # 마지막 방은 보물방
                room_type = 3  # 보물
                tier = 3
            elif room_idx == room_count - 2:
                # 마지막에서 두 번째 방은 전투방 (보스전)
                room_type = 1  # 전투
                tier = 3
            else:
                # 일반 방은 랜덤하게 타입과 티어 결정
                room_type = random.choice([0, 1, 2])  # 빈방, 전투, 이벤트
                tier = random.choice([base_tier - 1, base_tier, base_tier + 1])
                tier = max(1, min(3, tier))  # 1~3 범위로 제한
            
            # 방 크기 결정
            room_size = random.randint(2, 4)
            
            # 전투방인 경우에만 몬스터 배치
            monsters = None
            if room_type == 1:  # 전투방
                budget = self.calculate_room_budget(tier, avg_combat_score)
                total_budget_allocated += budget
                
                spawn_plan = self.generate_spawn_plan(budget, room_size)
                actual_cost = sum(self.monster_db[m.monster_id].cost_point for m in spawn_plan)
                total_budget_used += actual_cost
                
                monsters = spawn_plan
            
            # 이웃 방 연결 (간단한 선형 연결)
            neighbors = []
            if room_idx > 0:
                neighbors.append(room_idx - 1)
            if room_idx < room_count - 1:
                neighbors.append(room_idx + 1)
            
            room = RoomData(
                room_id=room_idx,
                room_type=room_type,
                size=room_size,
                neighbors=neighbors,
                monsters=monsters,
                event_type=random.randint(0, 3) if room_type == 2 else None  # 이벤트 방인 경우
            )
            rooms.append(room)
        
        # 난이도 컨텍스트 생성
        difficulty_context: DifficultyContext = {
            "total_budget_allocated": total_budget_allocated,
            "total_budget_used": total_budget_used,
            "budget_utilization": total_budget_used / total_budget_allocated if total_budget_allocated > 0 else 0.0,
            "floor": floor,
            "room_count": room_count,
            "hero_combat_scores": hero_combat_scores
        }
        
        return rooms, difficulty_context

