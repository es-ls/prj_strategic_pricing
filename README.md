# prj_strategic_pricing

PDF `Strategic Project Pricing Full Guide v4 Premium`의 견적 산정 흐름을 Excel 자동화 계산기로 옮긴 Python 프로젝트입니다.

## 무엇을 계산하나

이 계산기는 다음 15개 작업을 한 번의 Excel 입력/출력 흐름으로 정리합니다.

1. 고객 요구사항과 Scope 확정
2. In-Scope / Out-of-Scope 정리
3. WBS로 과업 분해
4. 역할별 M/M 산정
5. GPU/API/DB/외부 라이선스/교육비 분리 산정
6. Price Cost 산정
7. 고객 절감/창출 가치로 Price Ceiling 산정
8. 경쟁사/유사 프로젝트로 Price Market 산정
9. 내부 연 매출 기준으로 Price Anchor 확인
10. 4개 가격 후보 비교
11. Core / Standard / Premium 옵션 설계
12. 할인 가능 범위와 Walk-away Price 설정
13. 결제조건과 Scope 조정 카드 설계
14. PM, 기술, 인프라, 재무, 영업, 법무 협의
15. 고객 제출용 견적서/세부내역서/추진일정 작성

## 설치

```bash
python3 -m pip install -e .
```

## 사용법

샘플 입력 파일을 먼저 만듭니다.

```bash
prj-strategic-pricing-template input.xlsx
```

계산 결과 파일을 생성합니다.

```bash
prj-strategic-pricing-calc input.xlsx output.xlsx
```

## 입력 Excel 시트

- `deal_brief`: 고객사, 딜 유형, 기간, 예산, 경쟁 구도
- `scope`: In-Scope, Out-of-Scope, Assumption
- `wbs`: Phase, Workstream, Task, Role, Grade, M/M
- `rates`: Grade별 Monthly Rate
- `non_labor_costs`: GPU, API, DB, OCR, 라이선스, 교육비 등
- `value_market_anchor`: 고객 절감/창출 가치, 경쟁사 가격, 기간 기준
- `strategy`: 리스크 버퍼, 최소 마진, 제안가, 할인 범위, 패키지 배율
- `approval`: PM, 기술, 인프라, 재무, 영업, 법무 협의 상태

## 핵심 산식

```text
Labor Cost = sum(WBS M/M x Grade Monthly Rate)
Non-Labor Cost = GPU + API + DB + OCR + License + Education + ...
Price Cost = Labor Cost + Non-Labor Cost + Risk Buffer + Minimum Margin
Price Ceiling = Customer Saving x 60%
Price Market = Competitor Price Avg x 80%
Price Anchor = 1,000,000,000 KRW x Project Months / 12
Walk-away Price = Price Cost x Walk-away Multiplier
```

## 결과 Excel 시트

- `customer_quotation`: 고객 제출용 견적 요약
- `cost_breakdown`: 인력/비공수/버퍼/마진 세부내역
- `schedule`: WBS와 역할별 M/M
- `package_options`: Core / Standard / Premium 옵션
- `pricing_memo`: Ceiling / Market / Anchor / Cost 비교
- `checklist`: 제출 전 점검표
- `assumptions_scope`: Scope, Assumption, Out-of-Scope
- `approval_status`: 사내 협의 상태

## 테스트

```bash
python3 -m unittest
```
