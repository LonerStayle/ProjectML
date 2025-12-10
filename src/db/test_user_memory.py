"""
User Memory Manager 테스트
"""

import asyncio
from db.user_memory_manager import user_memory_manager
from db.user_memory_models import NPC_ID_TO_HEROINE


async def test_save_and_search():
    """저장 및 검색 테스트"""

    # 테스트 데이터
    user_id = "test_10001"
    heroine_id = "letia"

    print("=" * 50)
    print("1. 대화 저장 테스트")
    print("=" * 50)

    # 대화 저장 (fact 추출 + 저장)
    memory_ids = await user_memory_manager.save_conversation(
        user_id=user_id,
        heroine_id=heroine_id,
        user_message="나는 고양이를 정말 좋아해. 특히 러시안블루!",
        npc_response="저도 고양이 좋아해요. 러시안블루는 정말 귀엽죠.",
    )

    print(f"저장된 메모리 수: {len(memory_ids)}")
    for mid in memory_ids:
        print(f"  - {mid}")

    print()
    print("=" * 50)
    print("2. 검색 테스트 (4요소 하이브리드)")
    print("=" * 50)

    # 검색
    memories = await user_memory_manager.search_memories(
        user_id=user_id, heroine_id=heroine_id, query="고양이", limit=5
    )

    print(f"검색 결과: {len(memories)}개")
    for mem in memories:
        print(f"  - [{mem.speaker}] {mem.content}")
        print(
            f"    점수: {mem.final_score:.3f} (recency={mem.recency_score:.2f}, "
            f"importance={mem.importance_score:.2f}, relevance={mem.relevance_score:.2f}, "
            f"keyword={mem.keyword_score:.2f})"
        )

    print()
    print("=" * 50)
    print("3. 동기 검색 테스트 (Mem0 호환 인터페이스)")
    print("=" * 50)

    # 동기 검색 (기존 heroine_agent 호환)
    results = user_memory_manager.search_memory_sync(
        player_id=10001, npc_id=1, query="고양이", limit=3  # test_10001과 다름  # letia
    )

    print(f"동기 검색 결과: {len(results)}개")
    for r in results:
        print(f"  - {r['memory']}")

    print()
    print("테스트 완료!")


if __name__ == "__main__":
    asyncio.run(test_save_and_search())
