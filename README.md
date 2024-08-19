# myAgent
rag chatbot

주간 개발PC 고장으로 인하여 미완성 , chat 미구현으로 test 불가 프로젝트

고도화 과제
- 멀티턴 에이전트
  : agent를 통한 사용자 발화 history 분석 기반 검색 유무 노드 분기처리와 발화 재구성 노드 처리 필요

- 멀티모달 지원
  : GPT4o 사용시 활용 가능하도록 기반은 구축하였으나 노드 미존재

- 동시성 해결
  : async API , 내부 모델의 경우 serving 구축간 GPU별 모델 가동 및 로드밸런싱 / GPU slicing등 고안 필요

- 모델 토큰 제한 해결
  : input token
    - max token 초과시 request context를 분할하여 refine chain을 통해 순회 답변 생성으로 대응 가능
    - 하지만 최종 생성까지 시간이 많이 소요되며 답변의 품질이 저하됨 (할루시네이션 , 요구하지 않은 정보도 출력하는 현상 증가) , Model Tokenizer 개선등으로 max token을 늘리는것이 더욱 효과적
  : output token
    - refine chain 기반 답변 추가생성을 통해 해결 가능 , 품질 저하 최소화과 관건
 
- 멀티 에이전트 / 파이프라인 노드화
  : crew ai , LangGraph등을 기반으로 구축 가능
    특성화된 도메인 chatbot 구축 후 멀티 에이전트를 통해 그룹화 하여 서비스 가능할 것으로 기대
