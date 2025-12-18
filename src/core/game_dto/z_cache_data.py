

from core.game_dto.ItemData import ItemData
from core.game_dto.WeaponData import WeaponData
from core.game_dto.AccessoryItemData import AccessoryItemData

cache_items = [
    ItemData(itemId=0, itemName="일반 한손검", itemType=1, rarity=0,
        weapon=WeaponData(
            weaponId=0, weaponType=1, weaponName="일반 한손검",
            rarity=0, attackPower=10, staggerPower=2,
            modifier={"strength": 0.7, "dexterity": 0.3, "intelligence": 0}
        )
    ),

    ItemData(itemId=1, itemName="고급 한손검", itemType=1, rarity=1,
        weapon=WeaponData(
            weaponId=1, weaponType=1, weaponName="고급 한손검",
            rarity=1, attackPower=12, staggerPower=2,
            modifier={"strength": 0.7, "dexterity": 0.3, "intelligence": 0}
        )
    ),

    ItemData(itemId=2, itemName="레어 한손검", itemType=1, rarity=2,
        weapon=WeaponData(
            weaponId=2, weaponType=1, weaponName="레어 한손검",
            rarity=2, attackPower=15, staggerPower=2,
            modifier={"strength": 0.7, "dexterity": 0.3, "intelligence": 0}
        )
    ),

    ItemData(itemId=3, itemName="레전드 한손검", itemType=1, rarity=3,
        weapon=WeaponData(
            weaponId=3, weaponType=1, weaponName="레전드 한손검",
            rarity=3, attackPower=20, staggerPower=2,
            modifier={"strength": 0.7, "dexterity": 0.3, "intelligence": 0}
        )
    ),

    ItemData(itemId=4, itemName="보급형 검", itemType=1, rarity=0,
        weapon=WeaponData(
            weaponId=4, weaponType=1, weaponName="보급형 검",
            rarity=0, attackPower=13, staggerPower=2,
            modifier={"strength": 0.5, "dexterity": 0.5, "intelligence": 0}
        )
    ),

    ItemData(itemId=5, itemName="아끼는 검", itemType=1, rarity=1,
        weapon=WeaponData(
            weaponId=5, weaponType=1, weaponName="아끼는 검",
            rarity=1, attackPower=16, staggerPower=2,
            modifier={"strength": 0.5, "dexterity": 0.5, "intelligence": 0}
        )
    ),

    ItemData(itemId=6, itemName="컬렉션 검", itemType=1, rarity=2,
        weapon=WeaponData(
            weaponId=6, weaponType=1, weaponName="컬렉션 검",
            rarity=2, attackPower=18, staggerPower=2,
            modifier={"strength": 0.5, "dexterity": 0.5, "intelligence": 0}
        )
    ),

    ItemData(itemId=7, itemName="검", itemType=1, rarity=3,
        weapon=WeaponData(
            weaponId=7, weaponType=1, weaponName="검",
            rarity=3, attackPower=22, staggerPower=2,
            modifier={"strength": 0.5, "dexterity": 0.5, "intelligence": 0}
        )
    ),

    # -----------------------
    # 쌍검 (weaponType=2)
    # -----------------------
    ItemData(itemId=20, itemName="일반 쌍검", itemType=2, rarity=0,
        weapon=WeaponData(
            weaponId=20, weaponType=2, weaponName="일반 쌍검",
            rarity=0, attackPower=6, staggerPower=1,
            modifier={"strength": 0.1, "dexterity": 0.8, "intelligence": 0.1}
        )
    ),

    ItemData(itemId=21, itemName="고급 쌍검", itemType=2, rarity=1,
        weapon=WeaponData(
            weaponId=21, weaponType=2, weaponName="고급 쌍검",
            rarity=1, attackPower=9, staggerPower=1,
            modifier={"strength": 0.1, "dexterity": 0.8, "intelligence": 0.1}
        )
    ),

    ItemData(itemId=22, itemName="레어 쌍검", itemType=2, rarity=2,
        weapon=WeaponData(
            weaponId=22, weaponType=2, weaponName="레어 쌍검",
            rarity=2, attackPower=11, staggerPower=1,
            modifier={"strength": 0.1, "dexterity": 0.8, "intelligence": 0.1}
        )
    ),

    ItemData(itemId=23, itemName="레전드 쌍검", itemType=2, rarity=3,
        weapon=WeaponData(
            weaponId=23, weaponType=2, weaponName="레전드 쌍검",
            rarity=3, attackPower=14, staggerPower=1,
            modifier={"strength": 0.1, "dexterity": 0.8, "intelligence": 0.1}
        )
    ),

    # -----------------------
    # 대검 (weaponType=3)
    # -----------------------
    ItemData(itemId=40, itemName="일반 대검", itemType=3, rarity=0,
        weapon=WeaponData(
            weaponId=40, weaponType=3, weaponName="일반 대검",
            rarity=0, attackPower=15, staggerPower=5,
            modifier={"strength": 0.75, "dexterity": 0.2, "intelligence": 0.05}
        )
    ),

    ItemData(itemId=41, itemName="고급 대검", itemType=3, rarity=1,
        weapon=WeaponData(
            weaponId=41, weaponType=3, weaponName="고급 대검",
            rarity=1, attackPower=21, staggerPower=5,
            modifier={"strength": 0.75, "dexterity": 0.2, "intelligence": 0.05}
        )
    ),
    ItemData(itemId=42, itemName="레어 대검", itemType=3, rarity=2,
        weapon=WeaponData(
            weaponId=42, weaponType=3, weaponName="레어 대검",
            rarity=2, attackPower=25, staggerPower=5,
            modifier={"strength": 0.75, "dexterity": 0.2, "intelligence": 0.05}
        )
    ),

    ItemData(itemId=43, itemName="레전드 대검", itemType=3, rarity=3,
        weapon=WeaponData(
            weaponId=43, weaponType=3, weaponName="레전드 대검",
            rarity=3, attackPower=32, staggerPower=5,
            modifier={"strength": 0.75, "dexterity": 0.2, "intelligence": 0.05}
        )
    ),

    ItemData(itemId=44, itemName="보급형 대검", itemType=3, rarity=0,
        weapon=WeaponData(
            weaponId=44, weaponType=3, weaponName="보급형 대검",
            rarity=0, attackPower=12, staggerPower=5,
            modifier={"strength": 0.2, "dexterity": 0.8, "intelligence": 0}
        )
    ),

    ItemData(itemId=45, itemName="아끼는 대검", itemType=3, rarity=1,
        weapon=WeaponData(
            weaponId=45, weaponType=3, weaponName="아끼는 대검",
            rarity=1, attackPower=16, staggerPower=5,
            modifier={"strength": 0.2, "dexterity": 0.8, "intelligence": 0}
        )
    ),

    ItemData(itemId=46, itemName="컬렉션 대검", itemType=3, rarity=2,
        weapon=WeaponData(
            weaponId=46, weaponType=3, weaponName="컬렉션 대검",
            rarity=2, attackPower=21, staggerPower=5,
            modifier={"strength": 0.2, "dexterity": 0.8, "intelligence": 0}
        )
    ),

    ItemData(itemId=47, itemName="대검", itemType=3, rarity=3,
        weapon=WeaponData(
            weaponId=47, weaponType=3, weaponName="대검",
            rarity=3, attackPower=26, staggerPower=5,
            modifier={"strength": 0.2, "dexterity": 0.8, "intelligence": 0}
        )
    ),

    # -----------------------
    # 둔기 (weaponType=4)
    # -----------------------
    ItemData(itemId=60, itemName="일반 둔기", itemType=4, rarity=0,
        weapon=WeaponData(
            weaponId=60, weaponType=4, weaponName="일반 둔기",
            rarity=0, attackPower=22, staggerPower=6,
            modifier={"strength": 0.8, "dexterity": 0.2, "intelligence": 0}
        )
    ),

    ItemData(itemId=61, itemName="고급 둔기", itemType=4, rarity=1,
        weapon=WeaponData(
            weaponId=61, weaponType=4, weaponName="고급 둔기",
            rarity=1, attackPower=24, staggerPower=6,
            modifier={"strength": 0.8, "dexterity": 0.2, "intelligence": 0}
        )
    ),

    ItemData(itemId=62, itemName="레어 둔기", itemType=4, rarity=2,
        weapon=WeaponData(
            weaponId=62, weaponType=4, weaponName="레어 둔기",
            rarity=2, attackPower=27, staggerPower=6,
            modifier={"strength": 0.8, "dexterity": 0.2, "intelligence": 0}
        )
    ),

    ItemData(itemId=63, itemName="레전드 둔기", itemType=4, rarity=3,
        weapon=WeaponData(
            weaponId=63, weaponType=4, weaponName="레전드 둔기",
            rarity=3, attackPower=30, staggerPower=6,
            modifier={"strength": 0.8, "dexterity": 0.2, "intelligence": 0}
        )
    ),

    ItemData(itemId=64, itemName="뿅망치", itemType=4, rarity=0,
        weapon=WeaponData(
            weaponId=64, weaponType=4, weaponName="뿅망치",
            rarity=0, attackPower=20, staggerPower=6,
            modifier={"strength": 0.85, "dexterity": 0.15, "intelligence": 0}
        )
    ),

    ItemData(itemId=65, itemName="의사봉", itemType=4, rarity=1,
        weapon=WeaponData(
            weaponId=65, weaponType=4, weaponName="의사봉",
            rarity=1, attackPower=23, staggerPower=6,
            modifier={"strength": 0.85, "dexterity": 0.15, "intelligence": 0}
        )
    ),

    ItemData(itemId=66, itemName="슬레지 해머", itemType=4, rarity=2,
        weapon=WeaponData(
            weaponId=66, weaponType=4, weaponName="슬레지 해머",
            rarity=2, attackPower=25, staggerPower=6,
            modifier={"strength": 0.85, "dexterity": 0.15, "intelligence": 0}
        )
    ),

    ItemData(itemId=67, itemName="뚝딱망치", itemType=4, rarity=3,
        weapon=WeaponData(
            weaponId=67, weaponType=4, weaponName="뚝딱망치",
            rarity=3, attackPower=28, staggerPower=6,
            modifier={"strength": 0.85, "dexterity": 0.15, "intelligence": 0}
        )
    ), 
    ItemData(
        itemId=100, itemName="용표식 반지", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=100, accessoryName="용표식 반지",
            description="데미지 감소 -20%"
        )
    ),
    ItemData(
        itemId=101, itemName="투검의 반지", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=101, accessoryName="투검의 반지",
            description="체력 최대시 데미지 증가 +20%"
        )
    ),
    ItemData(
        itemId=102, itemName="회복의 반지", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=102, accessoryName="회복의 반지",
            description="5초마다 체력 +10"
        )
    ),
    ItemData(
        itemId=103, itemName="축복의 반지", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=103, accessoryName="축복의 반지",
            description="최대 체력 증가 50"
        )
    ),
    ItemData(
        itemId=104, itemName="증오의 반지", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=104, accessoryName="증오의 반지",
            description="받는 데미지 +20% 주는 데미지 +20%"
        )
    ),
    ItemData(
        itemId=105, itemName="라다곤의 반지", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=105, accessoryName="라다곤의 반지",
            description="힘,기량,지능 +8"
        )
    ),
    ItemData(
        itemId=106, itemName="윤여민의 스카락", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=106, accessoryName="윤여민의 스카락",
            description="상시 슈퍼아머, 주는 데미지 -50%"
        )
    ),
    ItemData(
        itemId=107, itemName="광전사의 반지", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=107, accessoryName="광전사의 반지",
            description="체력 30% 이하 일시 데미지 +20%"
        )
    ),
    ItemData(
        itemId=108, itemName="마누라니의 반지", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=108, accessoryName="마누라니의 반지",
            description="지능 +20"
        )
    ),
    ItemData(
        itemId=109, itemName="켈빈 클라인", itemType=1, rarity=None,
        accessory=AccessoryItemData(
            accessoryId=109, accessoryName="켈빈 클라인",
            description="공격 속도 +30%"
        )
    ),
]