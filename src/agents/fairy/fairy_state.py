from pydantic import BaseModel,Field    
from enum import StrEnum

class FairyRouteType(StrEnum):
    MONSTER_GUIDE = "MONSTER_GUIDE"
    EVENT_GUIDE = "EVENT_GUIDE"
    DUNGEON_NAVIGATOR = "DUNGEON_NAVIGATOR"
    INTERACTION_HANDLER = "INTERACTION_HANDLER"
    MULTI_ACTION_PLANNER = "MULTI_ACTION_PLANNER"
    SMALLTALK = "SMALLTALK"
    UNKNOWN_INTENT = "UNKNOWN_INTENT"
    
class FairyRouteOutput(BaseModel):
    route: FairyRouteType = Field(description="선택된 라우터 타입")
    
from langgraph.graph import MessagesState
from pydantic import BaseModel,Field

class FairyState(MessagesState):
    question: str


class FairyOutput(BaseModel):
    response:str = Field(description="응답한 메시지")
    
