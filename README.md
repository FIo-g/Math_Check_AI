# Math_Check_AI

로컬 LLM(Ollama + Qwen2.5-Math 7B)으로 마크다운 수학 풀이를 자동 검산하는 스크립트입니다. 풀이를 문제 단위로 나눠 모델에 보내고, 5단계 기준으로 검토한 리포트를 마크다운 파일로 저장합니다.

## 동작 방식

1. 입력 마크다운 파일을 `##` 기준으로 문제 단위로 나눕니다.
2. 5문제씩 묶어 로컬 Ollama API(`http://localhost:11434/api/generate`)로 보냅니다. 컨텍스트 길이는 32K 토큰으로 설정했습니다.
3. 모델이 아래 5단계로 검토합니다.
   - 풀이 검증: 계산 실수와 수학적 오류
   - 교재 방법론과 일치하는지
   - 논리적 비약이 없는지
   - 더 효율적인 대체 풀이
   - 최종 정답과 도출 과정 요약
4. 배치가 끝날 때마다 결과를 `verified_solution.md`에 이어 써서, 중간에 멈춰도 그때까지의 결과가 남습니다.

## 요구 사항

- Python 3, `requests`
- [Ollama](https://ollama.com)와 `qwen2.5-math:7b` 모델

## 사용 방법

```bash
ollama pull qwen2.5-math:7b
pip install requests
python qwen_25_7b.py
```

실행 전에 `qwen_25_7b.py` 상단의 `INPUT_FILE`을 검산할 마크다운 파일명으로 바꾸세요.

## 설정

| 변수 | 기본값 | 설명 |
|---|---|---|
| `INPUT_FILE` | `파일명.md` | 검산할 풀이 파일 |
| `OUTPUT_FILE` | `verified_solution.md` | 결과 리포트 파일 |
| `MODEL_NAME` | `qwen2.5-math:7b` | 사용할 Ollama 모델 |
| `CHUNK_SIZE` | `5` | 한 번에 보내는 문제 수 |
| `PROBLEM_DELIMITER` | `##` | 문제를 구분하는 기호 |

## 참고

- 모든 연산이 로컬에서 실행되어 풀이 내용이 외부 서버로 나가지 않습니다.
- 7B 모델이라 검산 결과가 틀릴 수 있으니 최종 확인은 직접 해야 합니다.
