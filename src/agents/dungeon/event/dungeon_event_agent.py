from langchain.chat_models import init_chat_model
from enums.LLM import LLM
from agents.dungeon.dungeon_state import DungeonEventParser
import random

llm = init_chat_model(model=LLM.GPT5_1, temperature=0.5)

from prompts.promptmanager import PromptManager
from prompts.prompt_type.dungeon.DungeonPromptType import DungeonPromptType
from agents.dungeon.dungeon_state import DungeonEventState
from db.RDBRepository import RDBRepository
from langchain_core.messages import HumanMessage


def heroine_memories_node(state: DungeonEventState) -> DungeonEventState:
    heroine_id = state["heroine_data"]["heroine_id"]
    memory_progress = state["heroine_data"]["memory_progress"]

    repo = RDBRepository()
    heroine_memories = repo.select_first_row(heroine_id, memory_progress)

    return {"heroine_memories": heroine_memories}


def selected_main_event_node(state: DungeonEventState) -> DungeonEventState:
    """
    메인 이벤트 선택 로직
    1. DB에서 event_templates 목록 조회 (keyword 기반)
    2. floor_range, heroine_requirement 필터링
    3. used_events 중복 제거
    4. 랜덤으로 최종 선택
    """

    # DB에서 이벤트 목록 가져오기
    repo = RDBRepository()

    # TODO: 실제 DB 쿼리로 교체 필요
    # event_templates = repo.get_event_templates(floor=state["next_floor"])

    # 임시: 하드코딩된 이벤트 목록
    available_events = [
        "검은 형상의 무언가",
        "쓰러져있는 사람",
        "제단속에 고여있는 물",
        "미치광이 상인",
        "미지의 기억",
        "조여오는 죄책감(개별 이벤트)",
        "8번 출구",
        "심연을 숭배하는 자",
        "xx 해야 탈출할 수 있는 방",
        "떨쳐내기 힘든 유혹(개별 이벤트)"
    ]

    # used_events = state.get("used_events", [])
    # available_events = [e for e in available_events if e not in used_events]

    # 랜덤 선택
    selected_event = random.choice(available_events)

    print(f"[selected_main_event_node] 선택된 이벤트: {selected_event}")

    return {"selected_main_event": selected_event}


def create_sub_event_node(state: DungeonEventState) -> DungeonEventState:
    prompts = PromptManager(DungeonPromptType.DUNGEON_SUB_EVENT).get_prompt(
        heroine_data=state["heroine_data"],
        heroine_memories=state["heroine_memories"],
        selected_main_event=state["selected_main_event"],
        event_room=state["event_room"],
        next_floor=state["next_floor"],
    )

    parser_llm = llm.with_structured_output(DungeonEventParser)
    response = parser_llm.invoke(prompts)
    final_answer = state["selected_main_event"] + "\n\n----------" + response.sibal
    print(response)
    return {
        "messages": [HumanMessage(response.sibal)],
        "sub_event": response.sibal,
        "final_answer": final_answer,
    }


from langgraph.graph import START, END, StateGraph


graph_builder = StateGraph(DungeonEventState)
graph_builder.add_node("heroine_memories_node", heroine_memories_node)
graph_builder.add_node("selected_main_event_node", selected_main_event_node)
graph_builder.add_node("create_sub_event_node", create_sub_event_node)

graph_builder.add_edge(START, "heroine_memories_node")
graph_builder.add_edge("heroine_memories_node", "selected_main_event_node")

graph_builder.add_edge("selected_main_event_node", "create_sub_event_node")
graph_builder.add_edge("create_sub_event_node", END)
graph_builder
