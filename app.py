import streamlit as st

# ========== 영타 → 한글 변환 로직 ========== #

eng_table = {
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

cho_list  = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
jung_list = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
jong_list = ['', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']


def combine_hangul(chars):
    result = ""
    cho = jung = jong = -1

    def flush():
        nonlocal cho, jung, jong, result
        if cho != -1 and jung != -1:
            code = 0xAC00 + cho * 21 * 28 + jung * 28 + (jong if jong != -1 else 0)
            result += chr(code)
        else:
            if cho != -1:
                result += cho_list[cho]
            if jung != -1:
                result += jung_list[jung]
        cho = jung = jong = -1

    for ch in chars:
        if ch in cho_list and jung == -1:
            cho = cho_list.index(ch)
        elif ch in jung_list and jung == -1:
            jung = jung_list.index(ch)
        elif ch in jung_list and jung != -1:
            flush()
            jung = jung_list.index(ch)
        elif ch in jong_list and jung != -1 and jong == -1:
            jong = jong_list.index(ch)
        else:
            flush()
            if ch in cho_list:
                cho = cho_list.index(ch)
            elif ch in jung_list:
                jung = jung_list.index(ch)
    flush()
    return result


def eng_to_kor(text):
    result = []
    buffer = ""

    i = 0
    while i < len(text):
        buffer += text[i]

        if buffer in eng_table:
            i += 1
            if i < len(text) and buffer + text[i] in eng_table:
                buffer += text[i]
                result.append(eng_table[buffer])
                buffer = ""
                i += 1
            else:
                continue
        else:
            if len(buffer) > 1 and buffer[:-1] in eng_table:
                result.append(eng_table[buffer[:-1]])
                buffer = buffer[-1]
            elif buffer not in eng_table:
                result.append(buffer)
                buffer = ""
        i += 1

    if buffer:
        if buffer in eng_table:
            result.append(eng_table[buffer])
        else:
            result.append(buffer)

    return combine_hangul(result)


# ========== Streamlit UI ========== #

st.title("영타 → 한글 자동 변환기")
st.write("영어 자판으로 잘못 입력한 한글을 자동 변환합니다.")

input_text = st.text_area("영타 입력 (예: dkssud → 안녕)")

if st.button("변환"):
    output = eng_to_kor(input_text)
    st.success(output)
