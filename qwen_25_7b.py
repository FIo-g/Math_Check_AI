import requests
import json
import time

# ==========================================
# ⚙️ 설정 (본인 환경에 맞게 수정하세요)
# ==========================================
INPUT_FILE = "파일명.md"  # 읽어들일 원본 파일명
OUTPUT_FILE = "verified_solution.md" # 검산 결과가 저장될 파일명
MODEL_NAME = "qwen2.5-math:7b"       # 사용할 수학 특화 모델
CHUNK_SIZE = 5                       # 한 번에 AI에게 던질 문제 수
PROBLEM_DELIMITER = "##"       # MD 파일에서 문제를 구분하는 기호

# 5단계 깐깐한 검산 프롬프트
SYSTEM_PROMPT = """
당신은 엄격한 수학 교수입니다. 제공된 마크다운 수학 풀이에 대해 다음 5단계를 거쳐 완벽하게 검산하고 마크다운 포맷으로 리포트를 작성하세요.
1. 풀이 검증 (계산 실수 및 수학적 오류 확인)
2. 교재 방법론 일치 여부 확인 (표준적인 풀이 방식인가?)
3. 논리적 완결성 점검 (비약이 없는지)
4. 대체 풀이법 제시 (더 효율적인 방법이 있다면)
5. 최종 정확도 확인 (정답 도출 과정 요약)
"""

# ==========================================
# 🛠️ 메인 로직 함수
# ==========================================
def verify_math_chunk(chunk_text, batch_num):
    url = "http://localhost:11434/api/generate"
    
    # Ollama API에 보낼 데이터 
    payload = {
        "model": MODEL_NAME,
        "prompt": f"{SYSTEM_PROMPT}\n\n[학생의 풀이]\n{chunk_text}",
        "stream": False,
        "options": {
            "num_ctx": 32768 
        }
    }
    
    print(f"⏳ [Batch {batch_num}] AI가 검산을 시작했습니다... (시간이 조금 걸릴 수 있습니다)")
    start_time = time.time()
    
    try:
        # AI 연산이 오래 걸릴 수 있으므로 timeout은 넉넉히 주거나 아예 없앱니다.
        response = requests.post(url, json=payload, timeout=None)
        response.raise_for_status()
        
        elapsed = round(time.time() - start_time, 1)
        print(f"✅ [Batch {batch_num}] 검산 완료! ({elapsed}초 소요)\n")
        return response.json()['response']
        
    except Exception as e:
        print(f"❌ [Batch {batch_num}] 오류 발생: {e}")
        return f"\n\n> [시스템 에러] Batch {batch_num} 검산 중 오류가 발생했습니다.\n\n"


# ==========================================
# 🚀 실행부
# ==========================================
if __name__ == "__main__":
    print("🚀 수학 과제 자동 검산 파이프라인을 가동합니다...\n")
    
    # 1. 원본 파일 읽기
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print(f"🚨 {INPUT_FILE} 파일을 찾을 수 없습니다! 파이썬 파일과 같은 폴더에 넣어주세요.")
        exit()

    # 2. 문제 단위로 쪼개기
    # 구분자를 기준으로 텍스트를 나눕니다. (빈 텍스트 방지를 위해 필터링)
    raw_problems = content.split(PROBLEM_DELIMITER)
    problems = [f"{PROBLEM_DELIMITER}{p}" for p in raw_problems if p.strip()]
    
    total_problems = len(problems)
    print(f"📚 총 {total_problems}개의 문제를 성공적으로 인식했습니다.")
    
    # 3. CHUNK_SIZE(5개) 단위로 묶기
    batches = []
    for i in range(0, total_problems, CHUNK_SIZE):
        batch = "".join(problems[i:i+CHUNK_SIZE])
        batches.append(batch)
        
    total_batches = len(batches)
    print(f"📦 총 {total_batches}번의 AI 검산 요청을 진행합니다 (배치당 {CHUNK_SIZE}문제).\n" + "="*40 + "\n")

    # 4. 출력 파일 초기화 및 AI 검산 시작
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out_f:
        out_f.write("# 📝 수학 과제 자동 검산 결과 리포트\n\n")

    for idx, batch_text in enumerate(batches, 1):
        # AI에게 검산 요청
        verification_result = verify_math_chunk(batch_text, idx)
        
        # 결과 파일에 바로바로 이어쓰기 (중간에 꺼져도 데이터 보존)
        with open(OUTPUT_FILE, "a", encoding="utf-8") as out_f:
            out_f.write(f"## 📌 Batch {idx} 검산 결과\n\n")
            out_f.write(verification_result)
            out_f.write("\n\n---\n\n")

    print(f"🎉 모든 검산이 완료되었습니다! [{OUTPUT_FILE}] 파일을 확인해주세요.")
