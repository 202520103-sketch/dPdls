import streamlit as st

# -----------------------------
# 두벌식 영타 → 자모 매핑
# -----------------------------
ENG_MAP = {
    'r':'ㄱ','R':'ㄲ','rt':'ㄳ',
    's':'ㄴ','sw':'ㄵ','sg':'ㄶ',
    'e':'ㄷ','E':'ㄸ',
    'f':'ㄹ','fr':'ㄺ','fa':'ㄻ','fq':'ㄼ','ft':'ㄽ','fx':'ㄾ','fv':'ㄿ','fg':'ㅀ',
    'a':'ㅁ',
    'q':'ㅂ','Q':'ㅃ','qt':'ㅄ',
    't':'ㅅ','T':'ㅆ',
    'd':'ㅇ',
    'w':'ㅈ','W':'ㅉ',
    'c':'ㅊ',
    'z':'ㅋ',
    'x':'ㅌ',
    'v':'ㅍ',
    'g':'ㅎ',

    'k':'ㅏ','o':'ㅐ','i':'ㅑ','O':'ㅒ',
    'j':'ㅓ','p':'ㅔ','u':'ㅕ','P':'ㅖ',
    'h':'ㅗ','hk':'ㅘ','ho':'ㅙ','hl':'ㅚ',
    'y':'ㅛ',
    'n':'ㅜ','nj':'ㅝ','np':'ㅞ','nl':'ㅟ',
    'b':'ㅠ',
    'm':'ㅡ','ml':'ㅢ',
    'l':'ㅣ'
}

# 초성/중성/종성 테이블
CHOS = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
JWUN = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
JONG = ["",'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ',
        'ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']


# --------------------------------------------------------
# 1) 영타 → 자모 (문자 단위로 자동 처리)
# --------------------------------------------------------
def eng_to_jamo(text):
    res = []
    i = 0
    while i < len(text):
        # 2글자 자판 우선
        if i+1 < len(text) and text[i:i+2] in ENG_MAP:
            res.append(ENG_MAP[text[i:i+2]])
            i += 2
        elif text[i] in ENG_MAP:
            res.append(ENG_MAP[text[i]])
            i += 1
        else:
            res.append(text[i])  # 띄어쓰기·문장부호 그대로
            i += 1
    return res


# --------------------------------------------------------
# 2) 자모 → 한글(실제 타자기 조합 규칙 적용)
# --------------------------------------------------------
def jamo_to_hangul(jamo_list):
    result = ""
    cho = jung = jong = None

    def flush():
        nonlocal cho, jung, jong, result
        if cho is not None and jung is not None:
            code = (
                0xAC00 +
                CHOS.index(cho) * 21 * 28 +
                JWUN.index(jung) * 28 +
                (JONG.index(jong) if jong else 0)
            )
            result += chr(code)
        else:
            if cho: result += cho
            if jung: result += jung
        cho = jung = jong = None

    for j in jamo_list:

        # 공백/문장부호 → 무조건 음절 flush
        if len(j) != 1 or not j.isalpha() and j not in CHOS+JWUN+JONG:
            flush()
            result += j
            continue

        if j in CHOS:
            if cho is None:
                cho = j
            else:
                flush()
                cho = j

        elif j in JWUN:
            if cho is not None and jung is None:
                jung = j
            else:
                flush()
                jung = j

        elif j in JONG:
            if cho is not None and jung is not None and jong is None:
                jong = j
            else:
                flush()
                cho = j if j in CHOS else None

    flush()
    return result


# --------------------------------------------------------
# 최종 변환
# --------------------------------------------------------
def convert(text):
    jamo = eng_to_jamo(text)
    return jamo_to_hangul(jamo)


# ================= Streamlit UI =================
st.title("영타 → 한글 자동 변환기")
st.write("영타를 한국어 타자기 입력처럼 정확하게 변환합니다.")

txt = st.text_area("영타 입력")

if st.button("변환"):
    st.success(convert(txt))
