from langchain.chat_models import init_chat_model
from enums.LLM import LLM
from agents.dungeon.dungeon_state import DungeonEventParser

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
    # 1. DB에서 main_event 목록을 가져와야댐
    # 2. DB에서 던전 정보를 꺼내야함
    # 3. 전층에서 중복 안되게끔만 난수로 메인 이벤트 생성
    return {"selected_main_event": "asd"}


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
