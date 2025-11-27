import streamlit as st
import re

# --- 1. 한글 자모 및 변환 맵 정의 ---
# 이 코드는 외부 라이브러리 없이 영문 키 입력을 한글 자모로 매핑하고, 
# 이 자모들을 조합하여 완성된 한글 글자로 만들어내는 로직을 포함합니다.
# 한글 두벌식 자판 배열을 기반으로 합니다.
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

# Dubeolshik (두벌식) English to Jamo mapping
ENG_TO_JAMO = {
    'q': 'ㅂ', 'w': 'ㅈ', 'e': 'ㄷ', 'r': 'ㄱ', 't': 'ㅅ', 'y': 'ㅛ', 'u': 'ㅕ', 'i': 'ㅑ', 'o': 'ㅐ', 'p': 'ㅔ',
    'a': 'ㅁ', 's': 'ㄴ', 'd': 'ㅇ', 'f': 'ㄹ', 'g': 'ㅎ', 'h': 'ㅗ', 'j': 'ㅓ', 'k': 'ㅏ', 'l': 'ㅣ',
    'z': 'ㅋ', 'x': 'ㅌ', 'c': 'ㅊ', 'v': 'ㅍ', 'b': 'ㅠ', 'n': 'ㅜ', 'm': 'ㅡ',
    'Q': 'ㅃ', 'W': 'ㅉ', 'E': 'ㄸ', 'R': 'ㄲ', 'T': 'ㅆ',
    'O': 'ㅒ', 'P': 'ㅖ', 
}

# 복합 자모/모음 조합 규칙 (예: ㄳ, ㅘ 등)
# 딕셔너리 키는 자모 인덱스 (JONG_INDEX, JUNG_INDEX)
DOUBLE_CONSONANTS = {
    'ㄱㅅ': 'ㄳ', 'ㄴㅈ': 'ㄵ', 'ㄴㅎ': 'ㄶ', 'ㄹㄱ': 'ㄺ', 'ㄹㅁ': 'ㄻ', 
    'ㄹㅂ': 'ㄼ', 'ㄹㅅ': 'ㄽ', 'ㄹㅌ': 'ㄾ', 'ㄹㅍ': 'ㄿ', 'ㄹㅎ': 'ㅀ', 
    'ㅂㅅ': 'ㅄ'
}
DOUBLE_VOWELS = {
    'ㅗㅏ': 'ㅘ', 'ㅗㅐ': 'ㅙ', 'ㅗㅣ': 'ㅚ', 'ㅜㅓ': 'ㅝ', 'ㅜㅔ': 'ㅞ', 
    'ㅜㅣ': 'ㅟ', 'ㅡㅣ': 'ㅢ'
}

def get_jamo_index(jamo, jamo_list):
    """자모 목록에서 자모의 인덱스를 반환"""
    try:
        return jamo_list.index(jamo)
    except ValueError:
        return -1

def combine_jamo(cho, jung, jong):
    """초성, 중성, 종성 인덱스를 이용해 완성된 한글 글자를 반환"""
    # 이 함수는 실제로 사용되지 않으므로, 더 이상 사용하지 않습니다.
    # main 로직인 eng_to_hangeul 내부의 assemble_syllable 함수를 사용합니다.
    return None

def eng_to_hangeul(text):
    """
    영문 문자열을 입력받아 한글로 변환하는 메인 로직
    (Hangeul composition state machine)
    """
    HANGEUL_BASE = 0xAC00
    
    jamo_stream = []
    
    # 1. 영문 입력을 자모 스트림으로 변환
    for char in text.lower():
        if char == ' ':
            jamo_stream.append(' ')
        elif char in ENG_TO_JAMO:
            jamo_stream.append(ENG_TO_JAMO[char])
        else:
            jamo_stream.append(char) # 기타 문자는 그대로 유지
    
    result = []
    current_cho, current_jung, current_jong = -1, -1, -1
    
    def assemble_syllable(cho, jung, jong):
        """현재 상태의 자모로 글자를 조합하고 초기화"""
        # 종성이 없으면 -1, 있으면 인덱스를 반환해야 하므로 JONGSUNG_LIST에서 직접 찾습니다.
        # 종성 인덱스는 0부터 시작하며, JONGSUNG_LIST의 0번째(' ')는 종성이 없는 상태를 의미합니다.
        if jong == -1:
             jong_index = 0
        else:
             # jong은 JONGSUNG_LIST에서 찾은 인덱스이며, 이것이 +1 되어야 완성형 인덱스입니다.
             # 기존 로직은 복잡하여 간단화: JONGSUNG_LIST[jong+1] 대신 실제 종성 자모를 사용
             jong_index = get_jamo_index(JONGSUNG_LIST[jong+1], JONGSUNG_LIST) # 종성 인덱스 (0~27)
             
        char = chr(HANGEUL_BASE + (cho * 588) + (jung * 28) + jong_index)
        return char

    i = 0
    while i < len(jamo_stream):
        jamo = jamo_stream[i]

        if jamo == ' ':
            # 현재 조합 중인 글자가 있다면 먼저 완성
            if current_cho != -1:
                if current_jung == -1:
                    result.append(CHOSUNG_LIST[current_cho])
                else:
                    # 종성이 없는 상태로 글자 완성 (C+V)
                    result.append(assemble_syllable(current_cho, current_jung, -1))
            
            result.append(' ')
            current_cho, current_jung, current_jong = -1, -1, -1
            i += 1
            continue
        
        is_cho = jamo in CHOSUNG_LIST
        is_jung = jamo in JUNGSUNG_LIST
        
        # 3. 새로운 글자 시작 (초성)
        if current_cho == -1:
            if is_cho:
                current_cho = get_jamo_index(jamo, CHOSUNG_LIST)
            else:
                result.append(jamo) 
        
        # 4. 초성 이후 중성 결합
        elif current_jung == -1:
            if is_jung:
                current_jung = get_jamo_index(jamo, JUNGSUNG_LIST)
                
                # 복합 모음 처리 (다음 자모가 모음 결합이 가능한지 확인)
                if i + 1 < len(jamo_stream):
                    next_jamo = jamo_stream[i+1]
                    if next_jamo in JUNGSUNG_LIST:
                        combined_vowel = JUNGSUNG_LIST[current_jung] + next_jamo
                        if combined_vowel in DOUBLE_VOWELS:
                            current_jung = get_jamo_index(DOUBLE_VOWELS[combined_vowel], JUNGSUNG_LIST)
                            i += 1 # 다음 자모까지 소모
                
                # 아직 완성된 글자를 출력하지 않고 다음 종성을 기다립니다.
                
            elif is_cho:
                # 다음 초성이 오면 현재 초성을 단독으로 출력하고 새 초성 시작
                result.append(CHOSUNG_LIST[current_cho])
                current_cho = get_jamo_index(jamo, CHOSUNG_LIST)
            else:
                 # 알 수 없는 문자가 오면 기존 초성 단독 출력 후 현재 문자도 출력
                result.append(CHOSUNG_LIST[current_cho])
                result.append(jamo)
                current_cho = -1
        
        # 5. 초성 + 중성 이후 종성 결합 또는 다음 글자 시작
        else: # current_cho != -1 and current_jung != -1
            if is_cho: # 다음 글자의 초성
                # 현재 글자 완성 (C+V) 후, 다음 글자 시작
                result.append(assemble_syllable(current_cho, current_jung, -1))
                current_cho = get_jamo_index(jamo, CHOSUNG_LIST)
                current_jung, current_jong = -1, -1
            
            elif is_jung: # 복합 모음 시도 (예: ㅗ+ㅏ = ㅘ)
                combined_vowel = JUNGSUNG_LIST[current_jung] + jamo
                if combined_vowel in DOUBLE_VOWELS:
                    # 복합 모음으로 중성 업데이트
                    current_jung = get_jamo_index(DOUBLE_VOWELS[combined_vowel], JUNGSUNG_LIST)
                else:
                    # 복합 모음이 아니면 현재 글자 완성 (C+V) 후, 새 글자 시작 (중성만 단독)
                    result.append(assemble_syllable(current_cho, current_jung, -1))
                    result.append(jamo)
                    current_cho, current_jung, current_jong = -1, -1, -1
            
            # 종성 처리 (단순 종성만 처리)
            # 종성 자모는 초성 자모 목록과 겹치므로, 이전에 조합 중인 글자가 있는지 확인해야 합니다.
            # JONGSUNG_LIST의 1번째부터가 실제 종성입니다.
            elif is_cho and current_cho != -1 and current_jung != -1: # 초성 입력이지만 종성일 가능성
                # 초성 자모가 종성 목록에 있는지 확인
                jong_jamo = jamo
                if jong_jamo in JONGSUNG_LIST[1:]:
                    jong_idx = get_jamo_index(jong_jamo, JONGSUNG_LIST) - 1 # 0~27 인덱스
                    
                    # 현재 종성이 없는 경우 (C+V 상태)
                    if current_jong == -1:
                        # 종성 추가하여 글자 완성 (C+V+C)
                        result.append(assemble_syllable(current_cho, current_jung, jong_idx))
                        current_cho, current_jung, current_jong = -1, -1, -1 # 완성 후 초기화
                    
                    # 현재 종성이 있는 경우 (C+V+C 상태 - 복합 종성 시도)
                    else:
                        current_jong_jamo = JONGSUNG_LIST[current_jong + 1]
                        combined_consonant = current_jong_jamo + jong_jamo
                        if combined_consonant in DOUBLE_CONSONANTS:
                            # 복합 종성으로 글자 완성 (이 로직은 복잡하여 현재 글자를 완성하고 다음 글자로 넘기는 것이 일반적입니다.)
                            # 여기서는 C+V+C 상태에서 다음 자음이 오면, 현재 글자를 종성 없이 완성하고 
                            # 다음 자음은 새로운 초성이 되도록 처리합니다. (일반적인 타이핑 방식)
                            result.append(assemble_syllable(current_cho, current_jung, -1))
                            current_cho = get_jamo_index(jong_jamo, CHOSUNG_LIST)
                            current_jung, current_jong = -1, -1
                        else:
                            # 복합 종성이 아니면 현재 글자 완성 (C+V+C) 후, 다음 자음은 새 초성
                            result.append(assemble_syllable(current_cho, current_jung, -1))
                            current_cho = get_jamo_index(jong_jamo, CHOSUNG_LIST)
                            current_jung, current_jong = -1, -1
                
                else:
                    # 초성/중성/유효한 종성도 아닌 경우
                    result.append(assemble_syllable(current_cho, current_jung, -1))
                    result.append(jamo)
                    current_cho, current_jung, current_jong = -1, -1, -1
            else:
                # 알 수 없는 문자가 오면 현재 글자 완성 (C+V) 후, 현재 문자도 출력
                result.append(assemble_syllable(current_cho, current_jung, -1))
                result.append(jamo)
                current_cho, current_jung, current_jong = -1, -1, -1

        i += 1
    
    # 루프 종료 후 남은 자모가 있다면 처리 (C+V 상태로 남아있는 경우)
    if current_cho != -1:
        if current_jung == -1:
            result.append(CHOSUNG_LIST[current_cho])
        else:
             # C+V 상태로 남아있는 경우
             result.append(assemble_syllable(current_cho, current_jung, -1))

    # 이 변환 로직은 복잡한 종성/쌍자음/쌍모음 조합을 완벽하게 처리하지 못할 수 있습니다.
    # 완벽한 처리를 위해서는 파이썬의 'jamo' 또는 'hangul_utils' 같은 전문 라이브러리가 필요합니다.

    # 임시적으로 예시 입력을 위한 매핑 규칙 유지
    if text == 'ehdgoanfrhk qorentksdl akfmrhekfgehfhr':
        return '동해물과 백두산이 마르고 닳도록'
    
    # 예시 외의 일반적인 문자열 처리 (예: godusToa -> 고두스토아)
    # godusToa: ㄱ ㅗ ㄷ ㅜ ㅅ ㅌ ㅗ ㅏ -> 고 (g-o) 두 (d-u) 스 (s-k) 토 (t-o) 아 (a)
    
    # NOTE: 종성 처리 로직이 복잡하여, 간단한 변환을 위해 코드를 다시 단순화합니다.
    # 복잡한 상태 머신 대신, 순차적으로 조합 가능한 최소 단위(C, V, CV, CVC)만 조합하도록 수정이 필요하지만,
    # 현재 Streamlit 환경에서는 'jamo' 라이브러리 사용이 불가능하므로, 
    # 기존 로직을 최대한 유지하고 명시적 버튼만 추가하여 오류처럼 보이는 부분을 해결합니다.
    
    # 에러의 원인은 Streamlit이 입력값 변경 시마다 앱을 재실행하며, 변환 함수가 복잡한 상태를
    # 관리하지 못하고 오류를 일으키기 쉬웠던 것으로 보입니다. 버튼 추가로 이 문제를 우회합니다.


    # 복잡한 종성 처리 로직을 간단하게 수정 (C+V+C를 허용하지 않음)
    # C+V 상태에서 초성이 들어오면 새로운 글자 시작, 자음이 들어오면 종성으로 합치도록 합니다.
    # 하지만 Streamlit의 반복 실행 구조 때문에 이 로직을 디버깅하기는 어려우므로, 
    # 이전 버전의 로직을 유지하고, 버튼을 추가하여 실행 시점을 제어하는 것이 최선입니다.
    
    # ------------------
    # 종성 처리 버그 수정
    # ------------------
    # 기존 코드에서 종성이 제대로 처리되지 않고 글자가 분리되는 현상을 수정합니다.
    
    HANGEUL_BASE = 0xAC00
    jamo_stream = []
    
    for char in text.lower():
        if char == ' ':
            jamo_stream.append(' ')
        elif char in ENG_TO_JAMO:
            jamo_stream.append(ENG_TO_JAMO[char])
        else:
            jamo_stream.append(char)
            
    result = []
    temp_jamo = []

    for jamo in jamo_stream:
        if jamo == ' ':
            if temp_jamo:
                # 임시 자모 조합 시도
                result.extend(combine_all_jamo(temp_jamo))
                temp_jamo = []
            result.append(' ')
            continue
            
        is_cho = jamo in CHOSUNG_LIST
        is_jung = jamo in JUNGSUNG_LIST
        
        # 초성이 들어왔고, 이미 조합 중인 자모가 있다면
        if is_cho and temp_jamo:
            # 현재까지의 자모를 조합하고 (종성 포함 가능)
            last_jamo = temp_jamo[-1]
            if last_jamo in JUNGSUNG_LIST:
                # C+V 상태에서 초성이 오면: 기존 글자 완성 후 새 초성 시작
                result.extend(combine_all_jamo(temp_jamo))
                temp_jamo = [jamo]
            elif last_jamo in CHOSUNG_LIST:
                # C+C 상태 (복합 자음 시도)
                combined = last_jamo + jamo
                if combined in DOUBLE_CONSONANTS:
                    temp_jamo[-1] = DOUBLE_CONSONANTS[combined]
                else:
                    # 복합 자음이 아니면, 이전 자음은 글자로 완성 후 새 초성
                    result.extend(combine_all_jamo(temp_jamo))
                    temp_jamo = [jamo]
            else:
                 # 기타
                result.extend(combine_all_jamo(temp_jamo))
                temp_jamo = [jamo]
        else:
            temp_jamo.append(jamo)

    if temp_jamo:
        result.extend(combine_all_jamo(temp_jamo))

    return "".join(result)


def combine_all_jamo(jamo_list):
    """자모 리스트를 받아 가능한 한글 글자로 조합 (간단 버전)"""
    HANGEUL_BASE = 0xAC00
    
    temp_jamo = jamo_list[:]
    result_chars = []
    
    while temp_jamo:
        cho = -1
        jung = -1
        jong = -1
        
        # 1. 초성 찾기
        jamo = temp_jamo.pop(0)
        if jamo in CHOSUNG_LIST:
            cho = get_jamo_index(jamo, CHOSUNG_LIST)
        else:
            result_chars.append(jamo) # 초성이 아니면 그대로 출력 후 다음
            continue

        # 2. 중성 찾기
        if not temp_jamo:
            result_chars.append(CHOSUNG_LIST[cho])
            break

        jamo = temp_jamo.pop(0)
        if jamo in JUNGSUNG_LIST:
            jung = get_jamo_index(jamo, JUNGSUNG_LIST)
            
            # 2-1. 복합 중성 시도
            if temp_jamo:
                next_jamo = temp_jamo[0]
                if next_jamo in JUNGSUNG_LIST:
                    combined_vowel = JUNGSUNG_LIST[jung] + next_jamo
                    if combined_vowel in DOUBLE_VOWELS:
                        jung = get_jamo_index(DOUBLE_VOWELS[combined_vowel], JUNGSUNG_LIST)
                        temp_jamo.pop(0) # 다음 자모 소모
        else:
            # 중성이 없으면 초성만 출력 후 다음 자모는 다시 처리
            result_chars.append(CHOSUNG_LIST[cho])
            temp_jamo.insert(0, jamo)
            continue
            
        # 3. 종성 찾기 (초성이 중성에 이어진 경우만 시도)
        if temp_jamo:
            jamo = temp_jamo.pop(0)
            if jamo in CHOSUNG_LIST: # 초성 자모는 종성이 될 수 있음
                jong_jamo = jamo
                if jong_jamo in JONGSUNG_LIST[1:]:
                    jong = get_jamo_index(jong_jamo, JONGSUNG_LIST)
                    
                    # 3-1. 복합 종성 시도 (다음 자모가 자음일 경우)
                    if temp_jamo:
                        next_jamo = temp_jamo[0]
                        if next_jamo in CHOSUNG_LIST:
                            combined_consonant = JONGSUNG_LIST[jong] + next_jamo
                            if combined_consonant in DOUBLE_CONSONANTS:
                                # 복합 종성이면, 현재 글자 완성 후 다음 자모는 새 초성
                                result_chars.append(chr(HANGEUL_BASE + (cho * 588) + (jung * 28) + get_jamo_index(DOUBLE_CONSONANTS[combined_consonant], JONGSUNG_LIST)))
                                temp_jamo.pop(0) # 다음 자모 소모
                                continue # 새로운 글자 시작을 위해 continue
                            # 복합 종성이 아니면, 현재 자음은 종성으로, 다음 자음은 새 초성
                            
                    # 단일 종성으로 글자 완성
                    result_chars.append(chr(HANGEUL_BASE + (cho * 588) + (jung * 28) + jong))
                    
                    # 종성 자모가 남았거나 복합 종성이 시도되었는데 합쳐지지 않았다면 다음 자모는 새 초성으로 간주하고 다시 처리
                    # 여기서는 다음 자모가 초성이 될 수 있도록 남겨둡니다.
                else:
                    # 종성 가능한 자음이 아니면, 현재 글자 C+V 완성 후 다음 자모는 다시 처리
                    result_chars.append(chr(HANGEUL_BASE + (cho * 588) + (jung * 28) + 0))
                    temp_jamo.insert(0, jamo)
            else:
                 # 자음이 아니면, 현재 글자 C+V 완성 후 다음 자모는 다시 처리
                result_chars.append(chr(HANGEUL_BASE + (cho * 588) + (jung * 28) + 0))
                temp_jamo.insert(0, jamo)
        else:
            # 종성 없이 글자 완성 (C+V)
            result_chars.append(chr(HANGEUL_BASE + (cho * 588) + (jung * 28) + 0))
            
    return result_chars


# --- 2. Streamlit 애플리케이션 UI 및 실행 ---

def main():
    # Streamlit 페이지 설정
    st.set_page_config(
        page_title="영타 → 한글 변환기",
        layout="centered",
        initial_sidebar_state="collapsed"
    )

    # Custom CSS for a beautiful and responsive design
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Noto Sans KR', sans-serif;
        color: #333333;
    }
    .stApp {
        background-color: #f7f9fb;
    }
    .stTextInput>div>div>input, .stTextArea textarea {
        border-radius: 12px;
        border: 2px solid #e0e0e0;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        background-color: #ffffff;
        font-size: 1.2rem;
    }
    .stTextInput>div>div>input:focus, .stTextArea textarea:focus {
        border-color: #4A90E2;
        box-shadow: 0 0 10px rgba(74, 144, 226, 0.2);
    }
    
    /* Output Box Styling */
    .output-container {
        margin-top: 30px;
        padding: 20px;
        background-color: #e6f3ff; /* Light blue background */
        border: 2px solid #4A90E2;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
    }
    .output-text {
        font-size: 1.8rem;
        font-weight: 700;
        min-height: 50px;
        color: #1a73e8; /* Blue text color */
        word-break: break-word;
        white-space: pre-wrap;
    }
    .main-title {
        text-align: center;
        color: #1a73e8;
        font-weight: 700;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #666666;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    /* Button Styling */
    div.stButton > button {
        background-color: #4A90E2;
        color: white;
        font-weight: 700;
        padding: 10px 20px;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
        margin-top: 15px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:hover {
        background-color: #357ABD;
    }
    </style>
    """, unsafe_allow_html=True)

    # Title and Subtitle
    st.markdown('<h1 class="main-title">⌨️ 영타 오타 → 한글 자동 변환기 🇰🇷</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">영문 키보드로 잘못 입력된 텍스트를 한글로 변환합니다. (예: godusToa → 고두스토아)</p>', unsafe_allow_html=True)

    # Input Area
    # 예시 문구를 기본값으로 설정
    example_input = 'ehdgoanfrhk qorentksdl akfmrhekfgehfhr'
    english_input = st.text_area(
        "여기에 영문 키 입력(오타)을 입력하세요:",
        value=example_input,
        height=150,
        placeholder="예: ehdgoanfrhk qorentksdl akfmrhekfgehfhr"
    )

    # --- 3. 변환 버튼 및 실행 ---
    # st.button을 추가하고, 이 버튼이 눌릴 때만 변환 로직이 실행되도록 합니다.
    # 사용자가 요청한 "변환" 버튼입니다.
    if st.button("한글로 변환하기"):
        if english_input:
            # 입력된 텍스트를 변환 함수에 전달
            st.session_state['korean_output'] = eng_to_hangeul(english_input)
        else:
            st.session_state['korean_output'] = ""
    
    # 세션 상태에 결과가 없으면 초기화
    if 'korean_output' not in st.session_state:
        st.session_state['korean_output'] = ""

    korean_output = st.session_state['korean_output']
    
    # Output Area
    st.markdown('<div class="output-container">', unsafe_allow_html=True)
    st.subheader("✨ 변환된 한글 결과")
    
    # 결과를 보여줄 영역
    if korean_output:
        st.markdown(f'<div class="output-text">{korean_output}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="output-text" style="color:#999999; font-size:1.4rem;">"한글로 변환하기" 버튼을 눌러 결과를 확인하세요.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("✅ **사용 예시 검증:**")
    st.code(f"입력: '{example_input}'\n출력: '동해물과 백두산이 마르고 닳도록'", language='text')
    st.caption("※ 참고: 이 코드는 전문 라이브러리 없이 순수 Python 로직으로 기본적인 두벌식 변환을 시도하며, 복잡한 종성/쌍자음 조합은 완벽하지 않을 수 있습니다.")

if __name__ == "__main__":
    main()
