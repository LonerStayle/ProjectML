from langgraph.graph import StateGraph, END
from state import DungeonState
from nodes import monster_balancing_node



def build_dungeon_graph():
    workflow = StateGraph(DungeonState)
    
    # 노드 추가
    workflow.add_node("monster_balancing", monster_balancing_node)

    # 엣지 추가
    workflow.set_entry_point("monster_balancing")
    workflow.add_edge("monster_balancing", END)

    # 그래프 컴파일
    app = workflow.compile()
    return app
