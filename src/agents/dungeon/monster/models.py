"""
던전 밸런싱 시스템의 데이터 모델 정의
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List


@dataclass
class MonsterMetadata:
    """
    몬스터 메타데이터(monsterData Schema)

    - monsterId: int (Primary Key)
    - hp: int (체력)
    - speed: int (이동속도)
    - attack: int (공격력)
    - attackSpeed: float (공격속도)
    - attackRange: float (사정거리)
    - weaknesses: int[] (약점 속성 ID 리스트)
    - strengths: int[] (강점 속성 ID 리스트)
    """

    monster_id: int
    hp: int
    speed: int  # 이동속도
    attack: int  # 공격력
    attack_speed: float  # 공격속도
    name: Optional[str] = None  # 이름 (옵션, DB에서 사용)

    @property
    def cost_point(self) -> float:
        """
        [몬스터 cost 공식]
        (체력 * 공격력 * 공속 * (이동속도/100) / 10)
        """
        return (
            self.hp * self.attack * self.attack_speed * (self.speed / 100.0)
        ) / 100.0


@dataclass
class StatData:
    """
    히로인(플레이어) 스탯 데이터
    """

    hp: int = 250
    strength: int = 10
    dexterity: int = 10
    defense: int = 10
    luck: int = 10

    @property
    def combat_score(self) -> float:
        """
        전투력 점수 계산 (intelligence 제외)
        """
        offensive_score = (self.strength * 1.5) + (self.dexterity * 1.2)
        defensive_score = (self.hp * 0.1) + (self.defense * 1.0)
        luck_bonus = self.luck * 0.5
        return offensive_score + defensive_score + luck_bonus

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatData":
        return cls(
            hp=data.get("hp", 250),
            strength=data.get("strength", 10),
            dexterity=data.get("dexterity", 10),
            defense=data.get("defense", 10),
            luck=data.get("luck", 10),
        )


@dataclass
class MonsterSpawnData:
    """배치된 몬스터 정보"""

    monster_id: int
    pos_x: float
    pos_y: float

    def to_dict(self) -> Dict[str, Any]:
        return {"monsterId": self.monster_id, "posX": self.pos_x, "posY": self.pos_y}


@dataclass
class RoomData:
    """방 데이터"""

    room_id: int
    room_type: int
    size: int
    monsters: Optional[List[MonsterSpawnData]] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoomData":
        monsters_data = data.get("monsters") or []
        spawn_list = []
        for m in monsters_data:
            spawn_list.append(
                MonsterSpawnData(
                    monster_id=m["monsterId"], pos_x=m["posX"], pos_y=m["posY"]
                )
            )

        return cls(
            room_id=data.get("roomId", 0),
            room_type=data.get("type", 0),
            size=data.get("size", 1),
            monsters=spawn_list if spawn_list else None,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "roomId": self.room_id,
            "type": self.room_type,
            "size": self.size,
            "monsters": [m.to_dict() for m in self.monsters] if self.monsters else None,
        }


@dataclass
class DungeonData:
    """전체 던전 데이터"""

    player_ids: List[int]
    heroine_ids: List[int]
    floor: int
    rooms: List[RoomData]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DungeonData":
        return cls(
            player_ids=data.get("player_ids", []),
            heroine_ids=data.get("heroine_ids", []),
            floor=data.get("floor", 1),
            rooms=[RoomData.from_dict(r) for r in data.get("rooms", [])],
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "player_ids": self.player_ids,
            "heroine_ids": self.heroine_ids,
            "floor": self.floor,
            "rooms": [r.to_dict() for r in self.rooms],
        }
