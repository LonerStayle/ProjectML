# 장기 기억 메모리 Mem0 대체 방식

```
점수 = 최신도 + 중요도 + 관련도 + 키워드
```

### 장기 메모리 검색시 고려요소
- 현재 NPC-NPC간 대화 retriever 검색시 최신도 / 중요도 / 관련도(dense retriever) 만 고려함 여기에 keyword(PGroonga) retriever 도 포함하여 user-npc 장기 메모리를 구성
가중치 설정이 자유로워야 함
- 각 히로인 마다 세션이 달라야 하고 다른 히로인의 기억을 검색하지 않도록 해야함
### 장기 메모리 저장시 고려요소
- 중복/ 충돌 처리
	- 대화내용에서 중복이 있는지 비교해서 중복을 방지하고 / 변화된 사실이 있으면 기존의 db를 명시적으로 삭제하는 대신 가장 중요한 사실과 선호도만 선택적으로 저장해서 망각
	- 누구에 대한 사실인지가 명시되어야 함 user 에 대한 사실인지 히로인에 대한 사실인지, 이것을 content 컬럼에 추출한 fact와 같이 저장하거나 따로 컬럼을 만들어서 누구에 대한 사실인지와 발화자가 누구인지에 대한 정보가 있어야 함(그 정보가 없으면 이게 누구에 대한 fact 인지 판단인지 불명확해진다.)
	- "speaker(user, heroin)"=발화자가 누구인가, "subject(user, heroin, world)"=무엇에 대한 사실인가, subject_id(만약 heroin에 대한 사실 이면 'letia'등,user면 'user' 등)=subject가 히로인이나 user 일경우 그 이름 

### 추출 예시

|대화|speaker|subject|subject_id|content|
|---|---|---|---|---|
|플레이어: "나는 고양이 좋아해"|user|user|user|고양이를 좋아함|
|레티아: "저도 고양이 좋아해요"|heroine|heroine|letia|고양이를 좋아함|
|레티아: "오빠는 따뜻한 사람이에요"|heroine|user|user|따뜻한 사람임|
|플레이어: "이 마을은 평화롭네"|user|world|world|마을이 평화로움|

---

### 쿼리 예시

```python
# 레티아가 알고 있는 플레이어 정보
SELECT * FROM user_memories 
WHERE user_id = $1 
  AND subject = 'user' 
  AND subject_id = 'user'
  AND (speaker = 'user' OR heroine_id = 'letia')
  AND invalid_at IS NULL;

# 플레이어가 아는 레티아 정보
SELECT * FROM user_memories 
WHERE user_id = $1 
  AND subject = 'heroine' 
  AND subject_id = 'letia'
  AND invalid_at IS NULL;

# 레티아가 플레이어에 대해 내린 평가
SELECT * FROM user_memories 
WHERE user_id = $1 
  AND speaker = 'heroine' 
  AND subject = 'user'
  AND content_type = 'opinion'
  AND invalid_at IS NULL;
```


### 가중치 계산 예시
Score = (w_recency × Recency) + (w_importance × Importance) + (w_relevance × Relevance) + (w_keyword × Keyword)
### 검색시 가중치 계산 4가지 요소

| 요소                   | 의미                   | 범위        | 계산 방식                        | 예시                                      |
| -------------------- | -------------------- | --------- | ---------------------------- | --------------------------------------- |
| **Recency (최신도)**    | 얼마나 최근 기억인가?         | 0.0 ~ 1.0 | 지수 감쇠: `exp(-days / 30)`     | 2시간 전 = 0.98, 7일 전 = 0.79, 30일 전 = 0.37 |
| **Importance (중요도)** | 얼마나 중요한 기억인가?        | 0.0 ~ 1.0 | 정규화: `importance / 10`       | 7/10 = 0.70, 3/10 = 0.30                |
| **Relevance (관련도)**  | 검색어와 의미적으로 얼마나 유사한가? | 0.0 ~ 1.0 | Cosine Similarity (pgvector) | "음식" 검색 → 음식 대화 = 0.85                  |
| **Keyword (키워드 일치)** | 검색어가 직접 포함되어 있는가?    | 0.0 ~ 1.0 | BM25 정규화 (PGroonga)          | "라면" 검색 → "라면 좋아함" = 0.92               |
### 메모리 저장 참고 코드
```python
from langchain_postgres import PGVector
from langchain.embeddings import OpenAIEmbeddings
import asyncpg

class CustomMemoryStore:
    def __init__(self, connection_string: str):
        # Direct connection 또는 Session mode pooler 사용
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.vector_store = PGVector(
            embeddings=self.embeddings,
            collection_name="user_memories",
            connection=connection_string,
            use_jsonb=True,
        )
    
    async def add_memory(self, user_id: str, content: str, 
                         heroine_id: str = None, memory_type: str = "fact"):
        """LLM으로 fact 추출 후 저장"""
        # 1. 기존 유사 메모리 검색
        existing = await self.search_memory(user_id, content, heroine_id)
        
        # 2. 중복/충돌 처리 (Mem0의 핵심 로직)
        if existing and existing[0].score > 0.9:
            # 업데이트: 기존 메모리 invalidate
            await self._invalidate_memory(existing[0].id)
        
        # 3. 새 메모리 추가
        embedding = self.embeddings.embed_query(content)
        # ... INSERT 로직
    
    async def search_memory(self, user_id: str, query: str, 
                           heroine_id: str = None, limit: int = 5):
        """Semantic search with metadata filtering"""
        filter_dict = {"user_id": user_id}
        if heroine_id:
            filter_dict["heroine_id"] = heroine_id
        
        return self.vector_store.similarity_search_with_score(
            query=query,
            k=limit,
            filter=filter_dict
        )
```

### 정리된 스키마
```sql
CREATE TABLE user_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id TEXT NOT NULL,
    heroine_id TEXT,  -- 게임용: 히로인별 메모리 분리
    
    -- Fact 메타데이터
    speaker TEXT NOT NULL, -- 'user' | 'heroine' -- 누가 말했는가?
    subject TEXT NOT NULL, -- 'user' | 'letia' | 'lupames' | 'roco' | 'world'
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'fact',  -- 'fact' | 'preference' | 'event' | 'opinion' | 'personal'
    
    -- 검색용
    embedding vector(1536),
    importance INT DEFAULT 5 CHECK (importance BETWEEN 1 AND 10),
    
    -- 시간
    valid_at TIMESTAMPTZ DEFAULT NOW(),
    invalid_at TIMESTAMPTZ,  
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 핵심 인덱스
CREATE INDEX idx_memory_session ON user_memories (user_id, heroine_id, invalid_at);
CREATE INDEX idx_memory_vector ON user_memories USING hnsw (embedding vector_cosine_ops);
CREATE INDEX idx_memory_pgroonga ON user_memories USING pgroonga (content);
```

### Pydantic 스키마
```python
from enum import Enum
from pydantic import BaseModel, Field

class Speaker(str, Enum):
    USER = "user"
    LETIA = "letia"
    LUPAMES = "lupames"
    ROCO = "roco"

class Subject(str, Enum):
    USER = "user"
    LETIA = "letia"
    LUPAMES = "lupames"
    ROCO = "roco"
    WORLD = "world"

class ContentType(str, Enum):
    PREFERENCE = "preference"
    TRAIT = "trait"
    EVENT = "event"
    OPINION = "opinion"
    PERSONAL = "personal"

class ExtractedFact(BaseModel):
    speaker: Speaker              # 누가 말했나
    subject: Subject              # 무엇에 대한 사실인가              
    content_type: ContentType
    content: str
    importance: int = Field(default=5, ge=1, le=10)
```

### **Bi-temporal Modeling** 패턴으로, Zep/Graphiti가 사용하는 핵심 개념 추가
- 각 컬럼의 역할

|컬럼|의미|용도|
|---|---|---|
|`created_at`|DB에 레코드가 생성된 시점|시스템 감사(audit)|
|`updated_at`|DB에서 레코드가 수정된 시점|시스템 감사|
|`valid_at`|**사실이 현실에서 유효해진 시점**|비즈니스 로직|
|`invalid_at`|**사실이 현실에서 무효화된 시점**|비즈니스 로직|
- 예시
```
[Day 1] 플레이어: "나는 고양이를 좋아해"
→ 저장: {content: "고양이를 좋아함", valid_at: Day1, invalid_at: NULL}

[Day 30] 플레이어: "요즘은 강아지가 더 좋아"
→ 기존 레코드 업데이트: {invalid_at: Day30}  
→ 새 레코드 추가: {content: "강아지를 좋아함", valid_at: Day30, invalid_at: NULL}
```

- 시간기반 질의 가능
```sql
-- 현재 유효한 사실만
SELECT * FROM user_memories 
WHERE invalid_at IS NULL;

-- Day 15 시점에 유효했던 사실
SELECT * FROM user_memories 
WHERE valid_at <= 'Day15' AND (invalid_at IS NULL OR invalid_at > 'Day15');

-- 플레이어 취향 변화 이력
SELECT * FROM user_memories 
WHERE content LIKE '%좋아함%' 
ORDER BY valid_at;

-- 최근 N일 동안 생성된 기억
SELECT * FROM user_memories 
WHERE user_id = $1
  AND heroine_id = $2
  AND created_at >= NOW() - INTERVAL '1 day' * $3
  AND invalid_at IS NULL
ORDER BY created_at DESC;

-- N일 전에 했던 이야기 조회
SELECT * FROM user_memories 
WHERE user_id = $1
  AND heroine_id = $2
  AND created_at >= NOW() - INTERVAL '${N} days'
  AND created_at < NOW() - INTERVAL '${N-1} days'
ORDER BY created_at;
```

### updated_at이 필요한 경우
하지만 실제로는 다음 상황에서 업데이트가 발생할 수 있음:

|상황|업데이트 대상|
|---|---|
|중요도 재평가|`importance`|
|메모리 티어 변경|`memory_tier`|
|임베딩 재생성|`embedding`|
|오타/내용 수정|`content`|
|디버깅/감사 추적|전반적|

### LLM 기반 Fact 추출 예시
```python
from pydantic import BaseModel
from typing import List

class ExtractedFact(BaseModel):
    content: str
    memory_type: str  # preference, personal, event, relationship
    importance: float

FACT_EXTRACTION_PROMPT = """
대화에서 장기 기억으로 저장할 만한 중요한 사실을 추출하세요.
게임 컨텍스트: 로맨스 시뮬레이션 게임의 NPC가 플레이어에 대해 기억해야 할 정보

추출 기준:
- 플레이어의 선호도 (좋아하는 것, 싫어하는 것)
- 개인 정보 (이름, 직업 등)
- 히로인과의 관계 이벤트
- 플레이어의 감정 상태

대화:
{conversation}

JSON 형식으로 응답:
"""

async def extract_facts(llm, conversation: str) -> List[ExtractedFact]:
    response = await llm.ainvoke(
        FACT_EXTRACTION_PROMPT.format(conversation=conversation)
    )
    return parse_json_response(response)
```

### Hybrid Search 스코어링 구조 예시
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class SearchWeights:
    """가중치 설정 (합이 1.0일 필요 없음, 실험으로 튜닝)"""
    recency: float = 0.15
    importance: float = 0.15
    relevance: float = 0.50      # dense retriever (cosine similarity)
    keyword: float = 0.20        # sparse retriever (PGroonga BM25)

@dataclass
class MemorySearchResult:
    memory_id: str
    content: str
    
    # 개별 점수 (디버깅용)
    recency_score: float        # 0~1
    importance_score: float     # 0~1 (원본 1~10을 정규화)
    relevance_score: float      # 0~1 (cosine similarity)
    keyword_score: float        # 0~1 (BM25 정규화)
    
    # 최종 점수
    final_score: float

class HybridMemorySearcher:
    def __init__(self, weights: SearchWeights = None):
        self.weights = weights or SearchWeights()
    
    def calculate_recency_score(self, created_at: datetime) -> float:
        """최신도: 최근일수록 높은 점수"""
        days_old = (datetime.now() - created_at).days
        # 지수 감쇠: 30일 기준
        return max(0.0, math.exp(-days_old / 30.0))
    
    def calculate_importance_score(self, importance: int) -> float:
        """중요도: 1~10 → 0~1 정규화"""
        return importance / 10.0
    
    def calculate_final_score(
        self,
        recency: float,
        importance: float,
        relevance: float,
        keyword: float
    ) -> float:
        """최종 스코어 계산"""
        return (
            self.weights.recency * recency +
            self.weights.importance * importance +
            self.weights.relevance * relevance +
            self.weights.keyword * keyword
        )
```
### SQL 기반 Hybrid Search 쿼리 예시
```sql
-- 히로인별 세션 분리 + Hybrid Search
WITH relevance_search AS (
    -- Dense Retriever (pgvector cosine similarity)
    SELECT 
        id,
        content,
        importance,
        created_at,
        1 - (embedding <=> $1) AS relevance_score  -- cosine similarity
    FROM user_memories
    WHERE user_id = $2
      AND heroine_id = $3          -- 히로인별 세션 분리
      AND invalid_at IS NULL
    ORDER BY embedding <=> $1
    LIMIT 20
),
keyword_search AS (
    -- Sparse Retriever (PGroonga BM25)
    SELECT 
        id,
        pgroonga_score(tableoid, ctid) AS keyword_score
    FROM user_memories
    WHERE user_id = $2
      AND heroine_id = $3
      AND invalid_at IS NULL
      AND content &@~ $4           -- PGroonga 전문검색
    LIMIT 20
)
SELECT 
    r.id,
    r.content,
    -- 개별 점수
    EXP(-EXTRACT(EPOCH FROM (NOW() - r.created_at)) / (30 * 86400)) AS recency_score,
    r.importance / 10.0 AS importance_score,
    r.relevance_score,
    COALESCE(k.keyword_score / MAX(k.keyword_score) OVER (), 0) AS keyword_score,
    -- 최종 점수
    (
        $5 * EXP(-EXTRACT(EPOCH FROM (NOW() - r.created_at)) / (30 * 86400)) +  -- w_recency
        $6 * (r.importance / 10.0) +                                             -- w_importance
        $7 * r.relevance_score +                                                 -- w_relevance
        $8 * COALESCE(k.keyword_score / MAX(k.keyword_score) OVER (), 0)        -- w_keyword
    ) AS final_score
FROM relevance_search r
LEFT JOIN keyword_search k ON r.id = k.id
ORDER BY final_score DESC
LIMIT $9;
```

### 히로인별 세션분리 예시
```python
class MemoryRepository:
    
    async def search_memories(
        self,
        user_id: str,
        heroine_id: str,           # 필수: 히로인별 분리
        query_text: str,
        query_embedding: list[float],
        weights: SearchWeights,
        limit: int = 10
    ) -> list[MemorySearchResult]:
        """
        핵심: heroine_id로 필터링하여 다른 히로인 기억 접근 차단
        """
        
        # 1. Dense search (pgvector)
        dense_results = await self._dense_search(
            user_id, heroine_id, query_embedding, limit=20
        )
        
        # 2. Sparse search (PGroonga)
        sparse_results = await self._sparse_search(
            user_id, heroine_id, query_text, limit=20
        )
        
        # 3. 병합 및 스코어 계산
        return self._merge_and_score(
            dense_results, sparse_results, weights, limit
        )
    
    async def _dense_search(
        self, user_id: str, heroine_id: str, 
        embedding: list[float], limit: int
    ):
        stmt = (
            select(
                UserMemory.id,
                UserMemory.content,
                UserMemory.importance,
                UserMemory.created_at,
                (1 - UserMemory.embedding.cosine_distance(embedding)).label('relevance')
            )
            .where(
                UserMemory.user_id == user_id,
                UserMemory.heroine_id == heroine_id,  # 세션 분리
                UserMemory.invalid_at.is_(None)
            )
            .order_by(UserMemory.embedding.cosine_distance(embedding))
            .limit(limit)
        )
        return await self.session.execute(stmt)
```