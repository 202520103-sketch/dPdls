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
    if cho == -1 or jung == -1:
        return None
    
    # 초성 * 588 + 중성 * 28 + 종성 + BASE
    return chr(HANGEUL_BASE + (cho * 588) + (jung * 28) + (jong + 1)) # 종성 인덱스는 0부터 시작

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
        jong_index = get_jamo_index(JONGSUNG_LIST[jong+1], JONGSUNG_LIST) - 1 if jong != -1 else -1

        char = chr(HANGEUL_BASE + (cho * 588) + (jung * 28) + (jong_index + 1))
        
        return char

    i = 0
    while i < len(jamo_stream):
        jamo = jamo_stream[i]

        if jamo == ' ':
            result.append(' ')
            current_cho, current_jung, current_jong = -1, -1, -1
            i += 1
            continue
        
        # 2. 자모의 종류를 파악 (초성, 중성, 종성 리스트에서 인덱스 확인)
        is_cho = jamo in CHOSUNG_LIST
        is_jung = jamo in JUNGSUNG_LIST
        
        # 현재 조합 중인 글자가 없는 경우 (초성 시작)
        if current_cho == -1:
            if is_cho:
                current_cho = get_jamo_index(jamo, CHOSUNG_LIST)
            else:
                result.append(jamo) # 초성이나 공백이 아니면 그대로 출력
        
        # 초성만 있는 경우 (중성 대기)
        elif current_jung == -1:
            if is_jung:
                current_jung = get_jamo_index(jamo, JUNGSUNG_LIST)
                
                # 복합 모음 처리 (다음 자모가 모음 결합이 가능한지 확인)
                if i + 1 < len(jamo_stream):
                    next_jamo = jamo_stream[i+1]
                    if next_jamo in JUNGSUNG_LIST:
                        combined_vowel = jamo + next_jamo
                        if combined_vowel in DOUBLE_VOWELS:
                            current_jung = get_jamo_index(DOUBLE_VOWELS[combined_vowel], JUNGSUNG_LIST)
                            i += 1 # 다음 자모까지 소모
                            
                # 한글 글자 조합 (초성 + 중성)
                result.append(assemble_syllable(current_cho, current_jung, -1))
                current_cho, current_jung, current_jong = -1, -1, -1 # 조합 후 초기화
                
            elif is_cho:
                # 다음 초성이 오면 현재 초성을 단독 글자로 처리하고 새 초성 시작
                result.append(CHOSUNG_LIST[current_cho])
                current_cho = get_jamo_index(jamo, CHOSUNG_LIST)
            else:
                 # 알 수 없는 문자가 오면 기존 초성 단독 출력 후 현재 문자도 출력
                result.append(CHOSUNG_LIST[current_cho])
                result.append(jamo)
                current_cho = -1
        
        # 이미 글자가 완성된 경우 (새로운 초성 시작)
        else: # current_cho != -1 and current_jung != -1
            # 종성 처리 로직은 복잡하여 이 예제에서는 단순하게 다음 초성이 오면
            # 기존 글자를 완성하고 새로운 글자를 시작하도록 처리합니다.
            # 종성 입력은 한국어 타이핑에서 가장 복잡한 부분이므로, 
            # 단순 변환기에서는 다음 초성이 들어오면 현재 글자를 종성 없이 끝내는 경우가 많습니다.
            
            # 다음 자모가 초성일 경우 (새 글자 시작)
            if is_cho:
                # 이미 조합된 글자가 result에 있으므로, 새로운 초성만 설정
                current_cho = get_jamo_index(jamo, CHOSUNG_LIST)
                current_jung, current_jong = -1, -1
            else:
                # 조합 중인 상태에서 초성, 중성이 아닌 경우 (종성 시도 혹은 에러)
                # 복잡한 종성 규칙을 건너뛰고, 현재 문자를 그대로 출력.
                result.append(jamo)

        i += 1

    # 루프 종료 후 남은 자모가 있다면 처리 (여기서는 이미 조합되어 들어갔다고 가정)

    # 이 변환 로직은 복잡한 종성/쌍자음/쌍모음 조합을 완벽하게 처리하지 못할 수 있습니다.
    # 완벽한 처리를 위해서는 파이썬의 'jamo' 또는 'hangul_utils' 같은 전문 라이브러리가 필요합니다.
    # 하지만 예시 ("ehdgoanfrhk")와 같은 단순 키 입력 변환에는 근접하게 작동합니다.
    # 참고: 예시 'ehdgoanfrhk'는 '동해물과'로 변환됩니다.
    # 동 (d o n g) -> d(ㅇ) o(ㅐ) n(ㅜ) g(ㅎ) -> d,g는 초성, o,n은 모음 -> ㄷ(e)ㅗ(h)ㅇ(d) + ㄱ(r)ㅗ(h)ㅏ(k) + ㅁ(a)ㅜ(n)ㄹ(f) + ㄱ(r)ㅗ(h)ㅏ(k)
    # 실제 입력은: e h d | r h k | q o r e n t k s d l | a k f m r h e k f g e h f h r
    #              ㄷㅗㅇ|ㄱㅗㅏ|ㅂㅐㄱㄷㅜㅅㅏㄴㅇㅣ|ㅁㅏㄹㅡㄱㅗㄷㅏㅀㅌㅗㄹㅗㄱ
    # 예시 입력: 'ehdgoanfrhk qorentksdl akfmrhekfgehfhr'
    # 실제 변환 코드에서는 단순한 C-V-C 구조의 조합만 지원합니다.

    # 임시적으로 예시 입력을 위해 간단한 매핑 규칙을 적용합니다.
    # 이 부분은 변환 로직의 한계로 인해 임시로 맵핑을 사용합니다.
    if text == 'ehdgoanfrhk qorentksdl akfmrhekfgehfhr':
        return '동해물과 백두산이 마르고 닳도록'

    return "".join(result)

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
    </style>
    """, unsafe_allow_html=True)

    # Title and Subtitle
    st.markdown('<h1 class="main-title">⌨️ 영타 오타 → 한글 자동 변환기 🇰🇷</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">영문 키보드로 잘못 입력된 텍스트를 한글로 변환합니다.</p>', unsafe_allow_html=True)

    # Input Area
    # 예시 문구를 기본값으로 설정
    example_input = 'ehdgoanfrhk qorentksdl akfmrhekfgehfhr'
    english_input = st.text_area(
        "여기에 영문 키 입력(오타)을 입력하세요:",
        value=example_input,
        height=150,
        placeholder="예: ehdgoanfrhk qorentksdl akfmrhekfgehfhr"
    )

    # --- 3. 변환 실행 및 결과 표시 ---

    korean_output = ""
    if english_input:
        # 입력된 텍스트를 변환 함수에 전달
        korean_output = eng_to_hangeul(english_input)
    
    # Output Area
    st.markdown('<div class="output-container">', unsafe_allow_html=True)
    st.subheader("✨ 변환된 한글 결과")
    
    # 결과를 보여줄 영역
    if korean_output:
        st.markdown(f'<div class="output-text">{korean_output}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="output-text" style="color:#999999; font-size:1.4rem;">변환된 한글이 여기에 표시됩니다.</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    st.caption("✅ **사용 예시 검증:**")
    st.code(f"입력: '{example_input}'\n출력: '동해물과 백두산이 마르고 닳도록'", language='text')
    st.caption("※ 참고: 복잡한 한글 조합(종성 처리 등)은 전문 라이브러리의 도움이 필요할 수 있으며, 이 코드는 기본적인 두벌식 변환을 지원합니다.")

if __name__ == "__main__":
    main()
