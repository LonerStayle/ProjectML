import random
import json
import os
from typing import List, Dict, Any, Tuple
from enums.LLM import LLM
from models import MonsterMetadata, StatData, RoomData, MonsterSpawnData
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


class MonsterCompositionAgent:
    """알고리즘 로직 구현 기반 몬스터 배치 Agent"""
    
    def __init__(self, hero_stats: List[StatData], monster_db: Dict[int, MonsterMetadata]):
        self.hero_stats = hero_stats
        self.monster_db = monster_db
        self.llm = LLM()
    
    def _calculate_party_score(self) -> float:
        """
        히로인 평균 전투력 계산 (힘, 기량, HP 기반)
        """

        if not self.hero_stats: return 0.0
        return sum(h.combat_score for h in self.hero_stats) / len(self.hero_stats)
    
    def _select_monsters(self, target_score: float) -> List[MonsterSpawnData]:
        """
        타겟 점수와 Cost가 비슷한 몬스터 후보군 선정
        """

        candidates = []
        for m in self.monster_db.values():
            # 오차범위 +-30%
            if target_score * 0.7 <= m.cost_point <= target_score * 1.3:
                candidates.append(m)

        # 조건에 맞는 몬스터가 없으면 Cost가 가장 낮은 3마리 반환 (안전장치)
        if not candidates:
            candidates = sorted(self.monster_db.values(), key=lambda x: x.cost_point)[:3]
        return candidates
        
    
    def _generate_coordinate(self) -> Tuple[float, float]:
        """
        [좌표생성] 0.1 ~ 0.9 사이 랜덤 좌표
        """
        x = random.uniform(0.1, 0.9)
        y = random.uniform(0.1, 0.9)
        return (round(x, 2), round(y, 2))

    def process_dungeon(self, dungeon_json: Dict[str, Any]) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """메인 처리 함수"""
        # 1. 히로인 점수 계산 및 타겟 설정(1.2배 난이도)
        party_score = self._calculate_party_score()
        target_score = party_score * 1.2

        updated_rooms = []
        raw_rooms = dungeon_json.get("rooms", [])

        # 2. 몬스터 후보군 선정
        candidates = self._select_monsters(target_score)

        for room_dict in raw_rooms:
            room = RoomData.from_dict(room_dict)

            # 전투방(type 1)이고 비어있으면 채우기
            if room.room_type == 1 and not room.monsters:
                spawn_list = []
                # 방 크기에 비례해 마릿수 결정 (Size = 3 -> 3~4 마리)
                count = random.randint(room.size, room.size + 1)

                for _ in range(count):
                    if candidates:
                        mob = random.choice(candidates)
                        gx, gy = self._generate_coordinate()

                        spawn_list.append(MonsterSpawnData(
                            monster_id=mob.monster_id,
                            pos_x = gx,
                            pos_y = gy
                        ))
                room.monsters = spawn_list
            updated_rooms.append(room.to_dict())

        dungeon_json["rooms"] = updated_rooms

        log = {
            "hero_power" : party_score,
            "target_score" : target_score,
            "candidate_monsters" : [m.name for m in candidates]
        }

        return dungeon_json, log

