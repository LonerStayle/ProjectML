from state import DungeonState
from monster_agent_with_llm import MonsterCompositionAgent
from enums.LLM import LLM
# from .event_agent import EventPlanningAgent


def monster_balancing_node(state: DungeonState) -> DungeonState:
    """
    몬스터 밸런싱을 수행하는 LangGraph 노드
    """
    print("\n[System] 몬스터 밸런싱 노드 시작...")
    
    # Monster Agent 생성 및 실행

    selected_model = LLM.GPT4_1_MINI

    agent = MonsterCompositionAgent(hero_stats=state["hero_stats"], 
        monster_db=state["monster_db"], 
        model_name=selected_model)
    filled_json, log = agent.process_dungeon(state["dungeon_data"])

    print(f"[System] 밸런싱 완료 (Model: {log.get('model_used', 'Unknown')})")
    print(f"   - AI 분석: {log.get('ai_reasoning', 'N/A')}")
    print(f"   - 전략 배율: x{log.get('ai_multiplier', 1.0)}")
    print(f"   - 타겟 점수: {log.get('target_score', 0):.1f}")
    
    return {
        "dungeon_data": filled_json,
        "difficulty_log": log
    }
