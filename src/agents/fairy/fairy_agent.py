from langchain.chat_models import init_chat_model
from enums.LLM import LLM
from agents.fairy.fairy_state import FairyRouteOutput, FairyState, FairyRouteType
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.types import Command, interrupt
from agents.fairy.temp_string import reverse_questions
import random

llm = init_chat_model(model=LLM.GPT4_1_MINI,temperature=0.2)
router_llm = init_chat_model(model=LLM.GPT4_1_MINI,temperature=0)

def router_node(state: FairyState) -> Command:
    last = state["messages"][-1]
    if not isinstance(last, HumanMessage):
        raise Exception("state.messages의 마지막 메시지가 휴먼 메시지가 아닙니다.")
    last_message = last.content

    parser_route_llm = router_llm.with_structured_output(FairyRouteOutput)
    route: FairyRouteOutput = parser_route_llm.invoke(last_message)
    if len(route.routes) == 1 and route.routes[0] == FairyRouteType.UNKNOWN_INTENT:
        clarification = reverse_questions[random.randint(0, 49)]
        user_resp = interrupt(clarification)
        return Command(
            goto="router",
            update={
                "messages": [
                    AIMessage(content=clarification),
                    HumanMessage(content=user_resp),
                ],
                "route_types": route.routes,
            },
        )
    return Command(goto="executor", update={"route_types": route.routes})


def monster_rag():
    return "\nasd"


def get_event_info():
    return "\nasdasd"

def dungeon_navigator():
    return "\ndungeon_navi"


def create_interaction():
    return "\n뿌뿌뿌"


def executor(state: FairyState) -> Command:
    route_types = state.get("route_types")
    if route_types is None:
        raise Exception("executor 호출 전에 route_type이 설정되지 않았습니다.")

    for route in route_types:
        if route == FairyRouteType.MONSTER_GUIDE:
            prompt_info = f"""\n몬스터 공략:{monster_rag()}"""

        elif route == FairyRouteType.EVENT_GUIDE:
            prompt_info = f"""\n이벤트:{get_event_info()}"""

        elif route == FairyRouteType.DUNGEON_NAVIGATOR:
            prompt_info = f"""\n길안내:{dungeon_navigator()}"""

        elif route == FairyRouteType.INTERACTION_HANDLER:
            action_detail = create_interaction()

        else:
            info = "SMALLTALK"

    prompt = PromptManager(FairyPromptType.FAIRY_DUNGEON_SYSTEM).get_prompt(
        heroine_info = "테스트",
        use_power = [rt.value if hasattr(rt, "value") else rt for rt in route_types],
        info = state['messages'][-1]
    )
    ai_answer = router_llm.invoke(prompt)
    print(prompt)
    print("*"*100)
    print("\n"+ai_answer.content)
    return {"messages": [ai_answer]}


from langgraph.graph import START, END, StateGraph
graph_builder = StateGraph(FairyState)
graph_builder.add_node("router", router_node)
graph_builder.add_node("executor", executor)

graph_builder.add_edge(START,"router")
graph_builder.add_conditional_edges(
    "router",
    router_node,
    {
        "router": "router",
        "executor": "executor",
    }
)
graph_builder.add_edge("executor", END)
graph = graph_builder.compile()
