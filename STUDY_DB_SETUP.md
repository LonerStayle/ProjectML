# 게임 데이터베이스 구축 과정 학습 노트

이 문서는 프로젝트의 데이터베이스(PostgreSQL + pgvector) 환경을 구축하고, Python으로 연동하며, 클라우드(Supabase)에 배포하기까지의 과정을 정리한 학습 자료입니다.

## 1. 목표 설정
- **데이터베이스**: PostgreSQL (게임 데이터 저장)
- **확장 기능**: pgvector (RAG AI 기능을 위한 벡터 검색 지원)
- **환경**: 로컬 개발(Docker) -> 클라우드 배포(Supabase)
- **언어**: Python 3.12 (SQLAlchemy, LangChain)

---

## 2. 로컬 개발 환경 구축 (Docker)

내 컴퓨터에 DB를 직접 설치하는 대신, `Docker`를 사용하여 깔끔하게 가상 서버를 띄웠습니다.

### 2-1. docker-compose.yml 작성
`pgvector/pgvector:pg16` 이미지를 사용하여 PostgreSQL 16버전과 벡터 확장이 포함된 컨테이너를 정의했습니다.

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    ports:
      - "5435:5432"  # 로컬 포트 5435를 컨테이너 포트 5432와 연결 (포트 충돌 방지)
    environment:
      POSTGRES_PASSWORD: password # 비밀번호 설정
    volumes:
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql # 초기화 스크립트 자동 실행
```

### 2-2. 초기화 스크립트 (init.sql)
DB가 켜질 때 자동으로 실행되는 SQL 파일입니다.
1. `CREATE EXTENSION vector;`: 벡터 검색 기능 활성화
2. `CREATE TABLE ...`: 몬스터, 아이템 등 필요한 테이블 생성

---

## 3. Python 코드 구현

### 3-1. 라이브러리 선택
- **psycopg (v3)**: 최신 PostgreSQL 드라이버
- **SQLAlchemy**: SQL을 직접 안 쓰고 파이썬 객체처럼 DB를 다루기 위한 ORM 도구
- **LangChain-Postgres**: 벡터 검색을 쉽게 하기 위한 도구

### 3-2. DBRepository 클래스 (핵심)
하나의 클래스로 일반적인 데이터 저장(CRUD)과 AI 검색(RAG)을 모두 처리하도록 설계했습니다.

```python
class DBRepository:
    def __init__(self):
        # DB 연결
        self.engine = create_engine(CONNECTION_URL)

    # 일반 데이터 저장
    def insert_data(self, data):
        # 딕셔너리 데이터를 받아서 SQL INSERT 실행
        ...

    # AI 벡터 검색
    def search(self, query):
        # 질문과 유사한 문서를 찾아서 반환
        ...
```

### 3-3. JSON 처리
PostgreSQL의 `JSONB` 타입을 활용하여 몬스터의 스탯이나 아이템 정보를 유연하게 저장했습니다.
- 파이썬 `dict` -> DB 저장 시 `json.dumps()`로 문자열 변환
- DB 조회 시 -> 파이썬에서 다시 `dict`로 사용

---

## 4. 클라우드 배포 (Supabase)

로컬에서 만든 환경을 그대로 인터넷 상의 서버(Supabase)로 옮겼습니다.

### 4-1. 설정
1. Supabase 프로젝트 생성
2. `init.sql` 내용을 복사해서 Supabase SQL Editor에서 실행 (테이블 생성)
3. `.env` 파일의 주소를 로컬 주소(`localhost`)에서 Supabase 주소로 변경

### 4-2. 연결 주소 형식 (중요)
Python 라이브러리와의 호환성을 위해 주소 형식을 맞춰주었습니다.
```ini
# 올바른 형식 (postgresql+psycopg://)
DATABASE_URL=postgresql+psycopg://user:password@host:port/db
```

---

## 5. 트러블슈팅 (오류 해결 기록)

개발 과정에서 발생했던 문제들과 해결 방법입니다.

### Q1. `ModuleNotFoundError: No module named 'enum.EmbeddingModel'`
- **원인**: 소스 폴더에 `enum`이라는 이름의 폴더를 만들었는데, 파이썬의 기본 라이브러리인 `enum`과 이름이 겹쳐서 충돌 발생.
- **해결**: 폴더 이름을 `src/enum` -> `src/enums`로 변경하여 충돌 방지.

### Q2. `ModuleNotFoundError: No module named 'psycopg2'`
- **원인**: 우리는 최신 버전인 `psycopg` (v3)를 쓰려고 했지만, 일부 라이브러리(SQLAlchemy 등)가 구버전인 `psycopg2`를 찾음.
- **해결 1**: 코드에서 `postgresql+psycopg://` 명시 (v3 사용 선언)
- **해결 2**: 호환성을 위해 `psycopg2-binary` 라이브러리 추가 설치 (`uv add psycopg2-binary`)

### Q3. `Port is already allocated` (Docker 포트 충돌)
- **원인**: 내 컴퓨터에 이미 PostgreSQL(5432 포트)이 설치되어 있거나 다른 프로그램이 쓰고 있어서 충돌.
- **해결**: `docker-compose.yml`에서 외부 포트를 `5435`로 변경하여 해결.

