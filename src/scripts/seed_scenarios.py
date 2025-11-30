"""
시나리오 데이터 임베딩 및 DB 삽입 스크립트

사용법:
    python src/scripts/seed_scenarios.py
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

from db.config import CONNECTION_URL


# 히로인 시나리오 데이터 (heroine_scenario_database.md 기반)
HEROINE_SCENARIOS = [
    # 레티아 (heroine_id=1)
    {
        "heroine_id": 1,
        "memory_progress": 10,
        "title": "레티아 기본 기억",
        "content": """레티아는 기억을 잃기 전 세일럼 제국의 귀족 가문 '루크 가문'의 일원이었다. 
그녀는 쌍검을 다루는 실력 있는 검사였으며, 가문을 위해 일했다. 
현재는 기억을 잃고 셀레파이스 길드에서 모험가로 활동 중이다."""
    },
    {
        "heroine_id": 1,
        "memory_progress": 50,
        "title": "레티아의 과거 - 망각자 소녀",
        "content": """레티아는 어린 시절 '망각자 소녀'로 불리며 학대받았다.
루크 가문에서 그녀를 발견하고 거두어 키웠다.
검술을 배우며 가문의 일원으로 성장했다."""
    },
    {
        "heroine_id": 1,
        "memory_progress": 70,
        "title": "레티아의 트라우마 - 리라",
        "content": """레티아에게는 '리라'라는 친구가 있었다.
리라는 레티아를 진심으로 대해준 유일한 사람이었다.
하지만 어떤 사건으로 인해 리라를 잃게 되었다."""
    },
    
    # 루파메스 (heroine_id=2)
    {
        "heroine_id": 2,
        "memory_progress": 10,
        "title": "루파메스 기본 기억",
        "content": """루파메스는 비스트 종족 중 늑대족 출신이다.
대검을 다루는 강력한 전사이며, 본능적인 전투 감각을 가지고 있다.
현재 기억을 잃고 셀레파이스 길드에서 활동 중이다."""
    },
    {
        "heroine_id": 2,
        "memory_progress": 50,
        "title": "루파메스의 과거 - 굶주림",
        "content": """루파메스는 어린 시절 극심한 굶주림을 겪었다.
늑대족 부족이 전쟁으로 멸망하면서 혼자 살아남았다.
배고픔에 대한 트라우마가 있어 음식을 매우 중요하게 여긴다."""
    },
    {
        "heroine_id": 2,
        "memory_progress": 70,
        "title": "루파메스의 트라우마 - 동족",
        "content": """루파메스는 극심한 굶주림 속에서 끔찍한 선택을 해야 했다.
거울을 보는 것을 두려워하며, 자신의 과거를 부정하려 한다.
포크와 나이프 사용법을 배운 것은 과거를 극복하려는 노력이다."""
    },
    
    # 로코 (heroine_id=3)
    {
        "heroine_id": 3,
        "memory_progress": 10,
        "title": "로코 기본 기억",
        "content": """로코는 하프 드워프로, 작은 체격에 망치를 무기로 사용한다.
소심하고 겁이 많지만 동료를 지키려는 마음이 강하다.
현재 기억을 잃고 셀레파이스 길드에서 탱커 역할을 맡고 있다."""
    },
    {
        "heroine_id": 3,
        "memory_progress": 50,
        "title": "로코의 과거 - 대장간",
        "content": """로코는 드워프 대장장이 가문 출신이다.
아버지에게 금속 다루는 법과 망치 사용법을 배웠다.
따뜻한 가정에서 자랐으며 정직함을 중요하게 여긴다."""
    },
    {
        "heroine_id": 3,
        "memory_progress": 70,
        "title": "로코의 트라우마 - 부모님",
        "content": """로코는 거대한 골렘의 습격으로 부모님을 잃었다.
그 순간 무언가를 놓쳐버렸다는 죄책감에 시달린다.
거대한 것에 대한 공포가 있지만 동료를 지키기 위해 극복하려 한다."""
    }
]


# 대현자 시나리오 데이터 (sage_scenarios_detailed_v1.md 기반)
SAGE_SCENARIOS = [
    {
        "scenario_level": 1,
        "title": "레테 행성 기본",
        "content": """레테(Lethe)는 기억과 망각이 섞인 중세 판타지 행성이다.
암네시아라는 현상으로 인해 많은 사람들이 기억을 잃는다.
기억을 잃은 자들을 '망각자'라고 부른다.
셀레파이스 길드는 망각자들이 모여 활동하는 곳이다."""
    },
    {
        "scenario_level": 2,
        "title": "나르가 연합",
        "content": """나르가 연합은 6개 종족(휴먼, 엘프, 비스트, 드워프, 페어리, 매지션)이 모인 국가다.
각 종족은 고유한 특성과 문화를 가지고 있다.
연합 외에도 세일럼 제국, 인스머스 수도회 등 다른 세력이 존재한다."""
    },
    {
        "scenario_level": 3,
        "title": "카다스 던전",
        "content": """카다스는 망각자들이 탐험하는 던전이다.
던전에서 '기억의 파편'을 얻을 수 있으며, 이를 통해 기억을 되찾을 수 있다.
던전 진입에는 특정 조건이 필요하다."""
    },
    {
        "scenario_level": 4,
        "title": "디멘시움",
        "content": """디멘시움은 던전에서 얻을 수 있는 귀중한 자원이다.
나르가 연합에서 디멘시움을 독점하기 위해 망각자들을 이용한다.
위치즈 부대는 망각자 관리를 담당하는 조직이다."""
    },
    {
        "scenario_level": 5,
        "title": "암네시아의 진실",
        "content": """암네시아는 사실 '축복'이다.
기억의 죽음으로부터 보호받기 위한 현상이다.
주인공(멘토)은 특별한 능력을 가지고 있어 히로인들의 기억을 되찾아줄 수 있다."""
    },
    {
        "scenario_level": 6,
        "title": "암네시아 대란",
        "content": """과거에 '암네시아 대란'이라는 대규모 사건이 있었다.
'기억의 영웅'이 세계를 구했다고 전해진다.
디멘시아 사건과 관련이 있으며, 내부에 배신자가 있었다."""
    },
    {
        "scenario_level": 7,
        "title": "고대의 존재",
        "content": """세계에는 고대의 존재들이 있다.
다곤, 메모리아 등 강력한 존재들이 세계에 영향을 미친다.
메모리아는 '거짓 신'으로 불린다."""
    },
    {
        "scenario_level": 8,
        "title": "사트라의 정체",
        "content": """사트라는 지식의 존재 '사틀라'의 아바타이다.
소토스라는 고대 존재와 연관이 있다.
멘토를 돕는 이유는 순수한 호기심과 호의이다."""
    },
    {
        "scenario_level": 9,
        "title": "주인공의 과거",
        "content": """주인공(멘토)은 과거 '기억의 영웅' 케네스와 관련이 있다.
암네시아 대란 당시 중요한 역할을 했다.
기억을 되찾으면 모든 진실이 밝혀진다."""
    },
    {
        "scenario_level": 10,
        "title": "나선의 의미",
        "content": """모든 것은 나선으로 연결되어 있다.
멘토의 선택이 세계의 운명을 결정한다.
엔딩은 멘토의 결정에 따라 달라진다."""
    }
]


def seed_heroine_scenarios():
    """히로인 시나리오 삽입"""
    engine = create_engine(CONNECTION_URL)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    print("히로인 시나리오 삽입 시작...")
    
    for scenario in HEROINE_SCENARIOS:
        # 임베딩 생성
        embedding = embeddings.embed_query(scenario["content"])
        
        sql = text("""
            INSERT INTO heroine_scenarios (heroine_id, memory_progress, title, content, content_embedding)
            VALUES (:heroine_id, :memory_progress, :title, :content, :embedding)
            ON CONFLICT DO NOTHING
        """)
        
        with engine.connect() as conn:
            conn.execute(sql, {
                "heroine_id": scenario["heroine_id"],
                "memory_progress": scenario["memory_progress"],
                "title": scenario["title"],
                "content": scenario["content"],
                "embedding": str(embedding)
            })
            conn.commit()
        
        print(f"  - {scenario['title']} 완료")
    
    print("히로인 시나리오 삽입 완료!")


def seed_sage_scenarios():
    """대현자 시나리오 삽입"""
    engine = create_engine(CONNECTION_URL)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    print("대현자 시나리오 삽입 시작...")
    
    for scenario in SAGE_SCENARIOS:
        # 임베딩 생성
        embedding = embeddings.embed_query(scenario["content"])
        
        sql = text("""
            INSERT INTO sage_scenarios (scenario_level, title, content, content_embedding)
            VALUES (:scenario_level, :title, :content, :embedding)
            ON CONFLICT DO NOTHING
        """)
        
        with engine.connect() as conn:
            conn.execute(sql, {
                "scenario_level": scenario["scenario_level"],
                "title": scenario["title"],
                "content": scenario["content"],
                "embedding": str(embedding)
            })
            conn.commit()
        
        print(f"  - {scenario['title']} 완료")
    
    print("대현자 시나리오 삽입 완료!")


if __name__ == "__main__":
    print("=" * 50)
    print("시나리오 데이터 시딩 시작")
    print("=" * 50)
    
    seed_heroine_scenarios()
    print()
    seed_sage_scenarios()
    
    print()
    print("=" * 50)
    print("시딩 완료!")
    print("=" * 50)

