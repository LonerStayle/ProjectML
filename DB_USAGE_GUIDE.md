# 게임 데이터 관리 가이드 (Supabase & Python)

이 문서는 `DBRepository`를 사용하여 Supabase DB에 데이터를 추가, 수정, 삭제하는 방법과 Supabase 웹 대시보드에서 확인하는 방법을 설명합니다.

## 1. 파이썬 코드로 데이터 관리하기

우리가 만든 `src/fill_test_data.py`와 같은 스크립트를 사용하면 데이터를 한 번에 관리하기 편합니다.

### 1-1. 데이터 추가/초기화 (Upload)

`src/fill_test_data.py` 파일은 **기존 데이터를 모두 지우고** 새로운 데이터를 채워 넣는 역할을 합니다. 데이터가 꼬였거나 초기화하고 싶을 때 실행하세요.

```bash
# 터미널에서 실행
uv run src/fill_test_data.py
```

**코드 예시 (직접 짤 때):**
```python
from db.DBRepository import DBRepository
from db.config import DBCollectionName

# 1. 리포지토리 연결 (예: 몬스터 테이블)
repo = DBRepository(DBCollectionName.MONSTER)

# 2. 데이터 준비
new_monster = {
    "name": "전설의 드래곤",
    "data": {"hp": 99999, "atk": 5000}
}

# 3. 저장
repo.insert_data(new_monster)
```

### 1-2. 데이터 확인 (Read)

데이터가 잘 들어갔는지 확인하려면 `src/check_data.py`를 실행합니다.

```bash
uv run src/check_data.py
```

**코드 예시:**
```python
# 이름이 '슬라임'인 몬스터 찾기
repo = DBRepository(DBCollectionName.MONSTER)
slime = repo.select_data(condition="name = :name", params={"name": "슬라임"})
print(slime)
```

### 1-3. 데이터 수정 (Update)

특정 데이터만 바꾸고 싶을 때 사용합니다.

**코드 예시:**
```python
# 이름이 '슬라임'인 몬스터의 공격력을 50으로 변경
repo = DBRepository(DBCollectionName.MONSTER)

repo.update_data(
    update_values={"data": {"hp": 50, "atk": 50}}, 
    condition="name = :name", 
    params={"name": "슬라임"}
)
```

### 1-4. 데이터 삭제 (Delete)

특정 데이터를 지울 때 사용합니다.

**코드 예시:**
```python
# 이름이 '슬라임'인 몬스터 삭제
repo = DBRepository(DBCollectionName.MONSTER)
repo.delete_data(condition="name = :name", params={"name": "슬라임"})
```

---

## 2. Supabase 웹 대시보드에서 관리하기

코드를 짜지 않고 눈으로 보면서 수정하고 싶을 때 가장 편한 방법입니다.

### 2-1. 접속 방법
1. [Supabase 대시보드](https://supabase.com/dashboard) 접속
2. 프로젝트 선택 (`game-db`)
3. 왼쪽 메뉴에서 **Table Editor** (표 모양 아이콘) 클릭

### 2-2. 데이터 확인 및 수정
1. 목록에서 원하는 테이블 클릭 (예: `monsters`)
2. 엑셀처럼 데이터가 쫙 뜹니다.
3. **수정**: 원하는 칸(Cell)을 더블 클릭하면 바로 값을 고칠 수 있습니다. (수정 후 하단 `Save` 버튼 클릭 필수!)
4. **삭제**: 행(Row) 왼쪽의 체크박스를 선택하고, 상단 메뉴의 `Delete` 버튼을 누르면 삭제됩니다.
5. **추가**: 상단 메뉴의 `Insert row` 버튼을 누르고 빈칸을 채우면 데이터가 추가됩니다.

---

## 3. 주의사항

1. **JSON 데이터 수정 시**: `data` 컬럼은 JSON 형식이므로 문법(`{ "key": "value" }`)을 틀리지 않게 조심해야 합니다. 
2. **초기화 주의**: `fill_test_data.py`는 실행할 때마다 기존 데이터를 **전부 삭제**하고 새로 넣습니다. 중요한 데이터가 있다면 백업해두거나 코드를 수정해서 사용하세요.

---

## 4. RAG (AI 검색) 기능 사용하기

AI에게 질문을 던져서 DB에 저장된 문서(세계관, 설정 등)를 검색하는 기능입니다.

### 4-1. 문서 저장 및 검색 테스트

`src/test_rag.py` 스크립트를 사용하면 텍스트 파일을 DB에 벡터 데이터로 저장하고, 검색까지 한 번에 테스트할 수 있습니다.

```bash
uv run src/test_rag.py
```

### 4-2. 코드 작성 방법 (직접 구현 시)

**1. 저장 (문서 -> DB)**
```python
from db.DBRepository import DBRepository
from db.config import DBCollectionName
from enums.EmbeddingModel import EmbeddingModel
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import CharacterTextSplitter

# RAG용 리포지토리 생성 (임베딩 모델 필수)
repo = DBRepository(
    collection_name=DBCollectionName.WORLD_SCENARIO,
    embedding_model=EmbeddingModel.TEXT_EMBEDDING_3_SMALL
)

# 텍스트 파일 읽기
loader = TextLoader("src/data/world_setting.txt", encoding="utf-8")
documents = loader.load()

# 문서 쪼개기 (너무 길면 검색 정확도 하락)
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
docs = text_splitter.split_documents(documents)

# 저장 (벡터 변환 자동)
repo.add_documents(docs)
```

**2. 검색 (질문 -> 유사 문서)**
```python
# "던전 3층에 누가 있어?" 라고 질문
query = "던전 3층에는 누가 살아?"
results = repo.search(query, k=3) # 상위 3개 결과

for doc in results:
    print(doc.page_content)
```
