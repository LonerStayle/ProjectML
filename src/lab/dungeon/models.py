"""
던전 밸런싱 시스템의 데이터 모델 정의
엑셀 데이터 스프레드시트 구조를 기반으로 작성
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List


@dataclass
class MonsterMetadata:
    """
    몬스터 메타데이터 - 엑셀 데이터 스프레드시트 구조 (monsterData Schema)
    
    엑셀 구조:
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
    attack_range: float  # 사정거리
    weaknesses: Optional[List[int]] = None  # 약점 속성 ID 리스트
    strengths: Optional[List[int]] = None  # 강점 속성 ID 리스트
    name: Optional[str] = None  # 이름 (옵션, DB에서 사용)
    
    @property
    def cost_point(self) -> float:
        """
        비용 포인트 계산: hp * attack * speed * attackSpeed
        (공격속도도 고려하여 계산)
        """
        return self.hp * self.attack * self.speed * self.attack_speed
    
    @property
    def is_ranged(self) -> bool:
        """원거리 몬스터 여부 (attackRange > 0)"""
        return self.attack_range > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (DB 저장 형식)"""
        return {
            "name": self.name or f"Monster_{self.monster_id}",
            "data": {
                "monsterId": self.monster_id,
                "hp": self.hp,
                "speed": self.speed,
                "attack": self.attack,
                "attackSpeed": self.attack_speed,
                "attackRange": self.attack_range,
                "weaknesses": self.weaknesses or [],
                "strengths": self.strengths or [],
                "cost_point": self.cost_point,
                "is_ranged": self.is_ranged
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonsterMetadata":
        """
        딕셔너리에서 생성 (DB 로드 형식 또는 엑셀 데이터 형식)
        
        Args:
            data: DB 형식 {"name": "...", "data": {...}} 또는 
                  엑셀 형식 {"monsterId": ..., "hp": ..., ...}
        """
        # DB 형식인지 확인
        if "data" in data:
            monster_data = data["data"]
            name = data.get("name")
        else:
            # 엑셀 형식
            monster_data = data
            name = None
        
        return cls(
            monster_id=monster_data.get("monsterId", monster_data.get("monster_id", 0)),
            hp=monster_data.get("hp", 0),
            speed=monster_data.get("speed", 0),
            attack=monster_data.get("attack", 0),
            attack_speed=monster_data.get("attackSpeed", monster_data.get("attack_speed", 1.0)),
            attack_range=monster_data.get("attackRange", monster_data.get("attack_range", 0.0)),
            weaknesses=monster_data.get("weaknesses"),
            strengths=monster_data.get("strengths"),
            name=name
        )


@dataclass
class MonsterSpawnData:
    """
    몬스터 스폰 데이터 - 엑셀 데이터 스프레드시트 구조 (monsterSpawnData Schema)
    
    엑셀 구조:
    - monsterId: int (몬스터 타입 ID)
    - posX: float (X 좌표, 0~1)
    - posY: float (Y 좌표, 0~1)
    """
    monster_id: int
    pos_x: float  # X 좌표 (0~1)
    pos_y: float  # Y 좌표 (0~1)
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "monsterId": self.monster_id,
            "posX": self.pos_x,
            "posY": self.pos_y
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MonsterSpawnData":
        """딕셔너리에서 생성"""
        return cls(
            monster_id=data.get("monsterId", data.get("monster_id", 0)),
            pos_x=data.get("posX", data.get("pos_x", 0.0)),
            pos_y=data.get("posY", data.get("pos_y", 0.0))
        )


@dataclass
class RoomData:
    """
    방 데이터 - 엑셀 데이터 스프레드시트 구조 (roomData Schema)
    
    엑셀 구조:
    - roomId: int (방 고유 ID)
    - type: int (0:빈방, 1:전투, 2:이벤트, 3:보물)
    - size: int (방 크기, 2~4)
    - neighbors: int[] (연결된 방 ID 리스트)
    - monsters: monsterSpawnData (전투방에서만)
    - eventType: int/null (이벤트 방에서만)
    """
    room_id: int
    room_type: int  # 0:빈방, 1:전투, 2:이벤트, 3:보물
    size: int  # 방 크기 (2~4)
    neighbors: List[int] = field(default_factory=list)  # 연결된 방 ID 리스트
    monsters: Optional[List[MonsterSpawnData]] = None  # 전투방에서만
    event_type: Optional[int] = None  # 이벤트 방에서만
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        result = {
            "roomId": self.room_id,
            "type": self.room_type,
            "size": self.size,
            "neighbors": self.neighbors
        }
        
        if self.monsters is not None:
            result["monsters"] = [m.to_dict() for m in self.monsters]
        
        if self.event_type is not None:
            result["eventType"] = self.event_type
        
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RoomData":
        """딕셔너리에서 생성"""
        monsters = None
        if "monsters" in data and data["monsters"]:
            monsters = [MonsterSpawnData.from_dict(m) for m in data["monsters"]]
        
        return cls(
            room_id=data.get("roomId", data.get("room_id", 0)),
            room_type=data.get("type", 0),
            size=data.get("size", 2),
            neighbors=data.get("neighbors", []),
            monsters=monsters,
            event_type=data.get("eventType", data.get("event_type"))
        )


@dataclass
class RewardTable:
    """
    보상 테이블 - 엑셀 데이터 스프레드시트 구조 (rewardTable Schema)
    
    엑셀 구조:
    - rarity: int (0~3: 커먼, 언커먼, 레어, 레전드)
    - itemTable: int[] (아이템 ID 리스트)
    """
    rarity: int  # 0~3 (커먼, 언커먼, 레어, 레전드)
    item_table: List[int]  # 아이템 ID 리스트
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "rarity": self.rarity,
            "itemTable": self.item_table
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RewardTable":
        """딕셔너리에서 생성"""
        return cls(
            rarity=data.get("rarity", 0),
            item_table=data.get("itemTable", data.get("item_table", []))
        )


@dataclass
class DungeonData:
    """
    던전 데이터 - 엑셀 데이터 스프레드시트 구조 (dungeonData Schema)
    
    엑셀 구조:
    - playerIds: int[] (참여 플레이어 ID 리스트)
    - heroIneId: int[] (각 플레이어가 선택한 히로인 ID 리스트)
    - rooms: roomData[] (방 정보 리스트)
    - rewards: rewardTable[] (보상 테이블 리스트)
    """
    player_ids: List[int]  # 참여 플레이어 ID 리스트
    heroine_ids: List[int]  # 각 플레이어가 선택한 히로인 ID 리스트
    rooms: List[RoomData]  # 방 정보 리스트
    rewards: List[RewardTable]  # 보상 테이블 리스트
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "playerIds": self.player_ids,
            "heroIneId": self.heroine_ids,
            "rooms": [room.to_dict() for room in self.rooms],
            "rewards": [reward.to_dict() for reward in self.rewards]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DungeonData":
        """딕셔너리에서 생성"""
        return cls(
            player_ids=data.get("playerIds", data.get("player_ids", [])),
            heroine_ids=data.get("heroIneId", data.get("heroine_ids", [])),
            rooms=[RoomData.from_dict(r) for r in data.get("rooms", [])],
            rewards=[RewardTable.from_dict(r) for r in data.get("rewards", [])]
        )


@dataclass
class StatData:
    """
    스탯 데이터 - 엑셀 데이터 스프레드시트 구조 (statData Schema)
    
    엑셀 구조:
    - hp: int (기본 HP)
    - moveSpeed: float (이동속도, 500 × value로 계산)
    - cooldownReduction: float (쿨다운 감소량, 1.0 × value로 계산)
    - strength: int (힘)
    - dexterity: int (민첩)
    - critChance: float (치명타 확률, 가산 계산)
    - skillDamageMultiplier: float (스킬 데미지 증가, 곱셈 계산)
    - autoAttackMultiplier: float (자동 공격 데미지 증가, 곱셈 계산)
    - attackSpeed: float (공격속도, 곱셈 계산)
    """
    hp: int
    move_speed: float  # 이동속도
    cooldown_reduction: float  # 쿨다운 감소량
    strength: int  # 힘
    dexterity: int  # 민첩
    crit_chance: float = 0.0  # 치명타 확률
    skill_damage_multiplier: float = 1.0  # 스킬 데미지 증가
    auto_attack_multiplier: float = 1.0  # 자동 공격 데미지 증가
    attack_speed: float = 1.0  # 공격속도
    
    @property
    def combat_score(self) -> float:
        """전투력 점수 계산"""
        # HP와 공격 관련 스탯을 기반으로 계산
        base_damage = (self.strength + self.dexterity) * self.auto_attack_multiplier
        return self.hp * base_damage * self.attack_speed
    
    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            "hp": self.hp,
            "moveSpeed": self.move_speed,
            "cooldownReduction": self.cooldown_reduction,
            "strength": self.strength,
            "dexterity": self.dexterity,
            "critChance": self.crit_chance,
            "skillDamageMultiplier": self.skill_damage_multiplier,
            "autoAttackMultiplier": self.auto_attack_multiplier,
            "attackSpeed": self.attack_speed,
            "combat_score": self.combat_score
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StatData":
        """딕셔너리에서 생성"""
        return cls(
            hp=data.get("hp", 250),
            move_speed=data.get("moveSpeed", data.get("move_speed", 1.0)),
            cooldown_reduction=data.get("cooldownReduction", data.get("cooldown_reduction", 1.0)),
            strength=data.get("strength", 0),
            dexterity=data.get("dexterity", 0),
            crit_chance=data.get("critChance", data.get("crit_chance", 0.0)),
            skill_damage_multiplier=data.get("skillDamageMultiplier", data.get("skill_damage_multiplier", 1.0)),
            auto_attack_multiplier=data.get("autoAttackMultiplier", data.get("auto_attack_multiplier", 1.0)),
            attack_speed=data.get("attackSpeed", data.get("attack_speed", 1.0))
        )

