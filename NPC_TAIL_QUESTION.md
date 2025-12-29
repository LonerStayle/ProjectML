코드를 분석해봤습니다. 현재 구조와 문제점을 정리해드리겠습니다.

---

## 📊 현재 코드 분석

### 현재 의도 분류 흐름

```
┌─────────────────────────────────────────────────────────────┐
│                    _classify_intent()                       │
├─────────────────────────────────────────────────────────────┤
│  Input:                                                     │
│  - user_message (현재 메시지만)                               │
│  - short_term_summary (요약본)  ← 실제 대화 아님!             │
│                                                             │
│  Output: general | memory_recall | scenario_inquiry | ...   │
└─────────────────────────────────────────────────────────────┘
```

### 🔴 핵심 문제점

**1. 의도 분류에서 실제 대화 맥락을 안 봄**

```python
async def _classify_intent(self, state: HeroineState) -> str:
    user_message = state["messages"][-1].content
    conversation_context = state.get("short_term_summary", "")  # ⚠️ 요약만 사용!
    
    prompt = f"""...
<recent_conversation_context>
{conversation_context}  # ← 이건 요약이지, 실제 대화가 아님
</recent_conversation_context>
..."""
```

**2. `newly_unlocked_scenario`가 현재 턴에서만 유효**

```python
# _keyword_analyze_node에서 설정됨
if unlocked_threshold is not None:
    scenario = heroine_scenario_service.get_scenario_by_exact_progress(...)
    newly_unlocked_scenario = scenario.get("content", "")
    # ⚠️ 이건 현재 턴에서 호감도 변화로 해금된 것만!
    # 이전 턴에서 해금된 기억은 추적 안됨
```

**3. 꼬리질문 시나리오 재현**

```
[턴 1] 플레이어: "검 훈련 좋아해?" (호감도 +10 → memoryProgress 50 달성)
       NPC: "숲에 간 기억이 돌아왔어..." (newly_unlocked_scenario 사용됨 ✅)
       
[턴 2] 플레이어: "그때 숲에 왜 갔어?"
       → newly_unlocked_scenario = None (이미 소멸됨)
       → short_term_summary = "..." (요약이라 구체적 맥락 없음)
       → 의도 분류: "그때"가 뭔지 모름 → general로 분류될 가능성 높음 ❌
```

---

## ✅ 현재 코드에서 이미 있는 것들

| 기능 | 상태 | 위치 |
|------|------|------|
| 기억 해금 감지 | ✅ 있음 | `detect_memory_unlock()` |
| 시나리오 검색 | ✅ 있음 | `_retrieve_scenario()` |
| 최근 기억 질문 감지 | ⚠️ 부분적 | `_is_recent_memory_question()` |
| 대화 버퍼 | ✅ 있음 | `conversation_buffer` |
| 의도별 라우팅 | ✅ 있음 | LangGraph 조건부 엣지 |

---

## 🛠️ 최소 수정으로 해결하는 방법

HWAIN님 제안대로 **최근 3턴을 의도 분류에 직접 주입**하면 됩니다.

### 수정 1: `_classify_intent` 개선

```python
async def _classify_intent(self, state: HeroineState) -> str:
    """의도 분류 (최근 3턴 맥락 포함)"""
    user_message = state["messages"][-1].content
    
    # 🔥 변경: 요약 대신 실제 최근 대화 3턴 사용
    conversation_buffer = state.get("conversation_buffer", [])
    recent_turns = conversation_buffer[-6:]  # 3턴 = 6개 메시지 (user + assistant)
    
    recent_dialogue = self._format_recent_turns(recent_turns)
    
    # 🔥 추가: 최근 해금된 기억 정보
    recently_unlocked = state.get("recently_unlocked_memory")
    unlocked_context = ""
    if recently_unlocked:
        unlocked_context = f"""
[최근 해금된 기억]
- memory_progress: {recently_unlocked.get('memory_progress')}
- 내용 요약: {recently_unlocked.get('summary', '')}
- 키워드: {recently_unlocked.get('keywords', [])}
"""

    prompt = f"""다음 플레이어 메시지의 의도를 분류하세요.

<recent_dialogue>
{recent_dialogue}
</recent_dialogue>
{unlocked_context}
<player_message>
{user_message}
</player_message>

<classification_rules>
- general: 일상 대화, 감정 표현, 질문 없는 대화
- memory_recall: 플레이어와 히로인이 함께 나눈 과거 대화/경험
- scenario_inquiry: 히로인 본인의 신상정보, 과거, 기억 상실 전 이야기
  ⚠️ 중요: "그때", "그거", "방금 말한 거" 같은 지시어가 최근 NPC 발화의 
     기억/과거 이야기를 가리키면 → scenario_inquiry
- heroine_recall: 다른 히로인과 나눈 대화 내용 질문
</classification_rules>

<output>
반드시 general, memory_recall, scenario_inquiry, heroine_recall 중 하나만 출력하세요.
</output>
"""
    # ... 나머지 동일

def _format_recent_turns(self, conversation_buffer: list) -> str:
    """최근 대화를 포맷팅"""
    if not conversation_buffer:
        return "없음"
    
    lines = []
    for item in conversation_buffer:
        role = "플레이어" if item.get("role") == "user" else "히로인"
        content = item.get("content", "")
        lines.append(f"{role}: {content}")
    
    return "\n".join(lines)
```

### 수정 2: State에 `recently_unlocked_memory` 추가 및 유지

```python
# npc_state.py에 추가
class RecentlyUnlockedMemory(TypedDict):
    memory_progress: int
    summary: str
    keywords: list
    unlocked_at: str  # ISO timestamp
    ttl_turns: int  # 남은 턴 수 (예: 5턴 후 만료)

class HeroineState(TypedDict):
    # ... 기존 필드들
    recently_unlocked_memory: Optional[RecentlyUnlockedMemory]
```

```python
# heroine_agent.py - _keyword_analyze_node 수정
async def _keyword_analyze_node(self, state: HeroineState) -> dict:
    # ... 기존 코드 ...
    
    if unlocked_threshold is not None:
        scenario = heroine_scenario_service.get_scenario_by_exact_progress(
            heroine_id=npc_id, memory_progress=unlocked_threshold
        )
        if scenario:
            newly_unlocked_scenario = scenario.get("content", "")
            
            # 🔥 추가: recently_unlocked_memory 설정
            recently_unlocked_memory = {
                "memory_progress": unlocked_threshold,
                "summary": scenario.get("title", ""),  # 또는 내용 요약
                "keywords": self._extract_keywords_from_scenario(scenario),
                "unlocked_at": datetime.now().isoformat(),
                "ttl_turns": 5,  # 5턴 동안 유지
            }
            return {
                "affection_delta": affection_delta,
                "used_liked_keyword": used_keyword,
                "newly_unlocked_scenario": newly_unlocked_scenario,
                "recently_unlocked_memory": recently_unlocked_memory,  # 🔥 추가
            }
    
    # 🔥 추가: 기존 recently_unlocked_memory TTL 감소
    existing_memory = state.get("recently_unlocked_memory")
    if existing_memory:
        ttl = existing_memory.get("ttl_turns", 0) - 1
        if ttl > 0:
            existing_memory["ttl_turns"] = ttl
            return {
                "affection_delta": affection_delta,
                "used_liked_keyword": used_keyword,
                "newly_unlocked_scenario": None,
                "recently_unlocked_memory": existing_memory,  # TTL 감소해서 유지
            }
    
    return {
        "affection_delta": affection_delta,
        "used_liked_keyword": used_keyword,
        "newly_unlocked_scenario": None,
        "recently_unlocked_memory": None,  # 만료됨
    }


```

### 수정 3: `_is_recent_memory_question` 확장


---

## 📊 수정 전후 비교

### Before (현재)

```
[턴 2] "그때 숲에 왜 갔어?"
       ↓
       _classify_intent()
       - short_term_summary만 참조 (구체적 맥락 없음)
       - "그때"가 뭔지 모름
       ↓
       → general로 분류 ❌
```

### After (수정 후)

```
[턴 2] "그때 숲에 왜 갔어?"
       ↓
       _classify_intent()
       - recent_dialogue: "히로인: 숲에 간 기억이 돌아왔어..."
       - recently_unlocked_memory: {progress: 50, keywords: ["숲"]}
       - "그때" + "숲" + 최근 기억 해금 → scenario_inquiry
       ↓
       _retrieve_scenario()
       - memory_progress=50 시나리오 검색
       ↓
       → 정확한 응답 ✅
```

---

## 🎯 최종 권장안

| 우선순위 | 수정 항목 | 난이도 | 효과 |
|---------|----------|--------|------|
| **1** | `_classify_intent`에 최근 3턴 추가 | 낮음 | 높음 |
| **2** | `recently_unlocked_memory` State 추가 | 중간 | 높음 |
| **3** | `_is_recent_memory_question` 확장 | 낮음 | 중간 |
| 선택 | Redis 세션에도 `recently_unlocked_memory` 저장 | 중간 | 영속성 |

**1번만 수정해도 상당 부분 해결**됩니다. Query Rewriting 없이 LLM 1회 호출로 맥락 파악 + 의도 분류가 가능합니다.