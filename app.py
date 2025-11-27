import streamlit as st

# 두벌식 자판 매핑
KEYMAP = {
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

    'k':'ㅏ','o':'ㅐ','i':'ㅑ','O':'ㅒ','j':'ㅓ','p':'ㅔ','u':'ㅕ','P':'ㅖ',
    'h':'ㅗ','hk':'ㅘ','ho':'ㅙ','hl':'ㅚ',
    'y':'ㅛ',
    'n':'ㅜ','nj':'ㅝ','np':'ㅞ','nl':'ㅟ',
    'b':'ㅠ',
    'm':'ㅡ','ml':'ㅢ',
    'l':'ㅣ'
}

CHOS = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
JWUN = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
JONG = ["",'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ',
        'ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']


def eng_to_jamo(word):
    """영타를 자모로 바꾸기 (단어 단위)"""
    res = []
    i = 0
    while i < len(word):
        # 2글자 모음/자음 우선
        if i+1 < len(word) and word[i:i+2] in KEYMAP:
            res.append(KEYMAP[word[i:i+2]])
            i += 2
        elif word[i] in KEYMAP:
            res.append(KEYMAP[word[i]])
            i += 1
        else:
            res.append(word[i])  # 알파벳·문장부호 그대로 유지
            i += 1
    return res


def jamo_to_hangul(jamo_list):
    """자모 → 완성형 한글"""
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
        if j in CHOS and jung is None:
            cho = j
        elif j in JWUN:
            if jung is None:
                jung = j
            else:
                flush()
                jung = j
        elif j in JONG and jung is not None:
            if jong is None:
                jong = j
            else:
                flush()
                cho = j if j in CHOS else None
        else:
            flush()
            result += j  # 문장부호나 영문 그대로
    flush()
    return result


def convert_text(text):
    final = ""
    tokens = text.split(" ")  # 단어 단위 처리

    for t in tokens:
        jamo = eng_to_jamo(t)
        hangul = jamo_to_hangul(jamo)
        final += hangul + " "

    return final.strip()


# ================= STREAMLIT =================

st.title("영타 → 한글 자동 변환기")
st.write("영타로 잘못 입력한 문장을 완전하게 변환합니다.")

txt = st.text_area("영타 입력", placeholder="예: dl tlaqkfdl dlf wpeofh dks go?")

if st.button("변환"):
    st.success(convert_text(txt))
