from pydantic import BaseModel
from typing import List, Dict, Optional

class AccessoryItemData(BaseModel):
    
    accessoryId: Optional[int] = None

    # 악세사리 명
    accessoryName: Optional[str] = None

    description: Optional[str] = None


