from typing import TypedDict, List, Dict, Any, Optional
from agents.dungeon.monster.models import MonsterMetadata, StatData, RoomData, DungeonData


class DungeonState(TypedDict):
    # input data
    heroine_stats: List[StatData] # 히로인 스탯 리스트
    monster_db: Dict[int, MonsterMetadata] # 몬스터 DB

    # payload
    dungeon_data: Dict[str, Any] # 언리얼이 보내온 json 데이터

    # context
    difficulty_log: Dict[str, Any]

