

🚀 Git 협업 전략
## 1. Commit Message Convention

feat: 기능 추가   
fix: 버그 수정   
refactor: 코드 개선  
etc: 기타 변경   

## 2. Branch Structure

작은 팀(3인)의 프로젝트 특성에 맞춰
가볍고 단순한 브랜치 전략을 사용했습니다.

main   
feature/*   
fix/*  


1) main — 최종 배포용 브랜치   
항상 정상 동작하는 최신 버전을 유지합니다.  
PR 검토 후에만 병합하도록 운영했습니다.   
main



2. feature/ — 기능 추가용 브랜치*   
기능 단위로 분리하여 개발 후 main에 병합했습니다.   
feature/login   
feature/chat-engine   
feature/rag-core  


3) fix/ — 버그 픽스용 단기 브랜치*   
예상치 못한 오류나 긴급 수정이 필요할 때 사용했습니다.   
fix/login-error   
fix/inventory-null   
fix/rag-timeout

