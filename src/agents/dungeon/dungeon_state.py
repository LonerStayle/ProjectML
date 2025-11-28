from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from pydantic import BaseModel,Field



class DungeonEventState(TypedDict):
    # 메시지 목록
    messages: Annotated[list, add_messages]
    heroine_data: dict
    heroine_memories: list
    selected_main_event: str
    sub_event:str
    event_room: int
    next_floor: int
    final_answer: str

class DungeonEventParser(BaseModel):
    sibal:str = Field(description="asd")

class DungeonState(TypedDict):
    main_event_result: str
    sub_event_result: str
    monster_balance_result: str
    dungeon_base_map: dict
    dungeon_players: list