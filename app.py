from html import escape
import streamlit as st
from questions import CHOSEONG, SONGS, initials

st.set_page_config(page_title="세대공감 퀴즈", page_icon="🎉", layout="wide", initial_sidebar_state="collapsed")
st.markdown('''<style>
.stApp{background:#101b2d;color:#fff}.block-container{max-width:1250px;padding-top:1.3rem;padding-bottom:1rem}
header{background:transparent!important}.quiz-card{position:relative;background:#1b2b42;border:1px solid #38516d;border-radius:26px;padding:65px 24px 42px;text-align:center;min-height:300px;display:flex;align-items:center;justify-content:center}
.badge{position:absolute;right:22px;top:18px;color:#bacde4;font-size:17px}
.initials{font-size:clamp(58px,10vw,146px);font-weight:900;line-height:1.5;letter-spacing:.07em;word-break:keep-all;overflow-wrap:anywhere}
.answer{font-size:clamp(32px,6vw,65px);font-weight:900;color:#f6c85f;text-align:center;line-height:1.5;margin:18px 0}
.music-title{text-align:center;font-size:clamp(36px,7vw,70px);font-weight:900;padding:20px 0}
div.stButton>button{min-height:64px;font-size:23px;font-weight:750;border-radius:15px}
.st-key-music_stage button{width:100%;min-height:330px;border-radius:26px;background:#1b2b42;border:2px solid #38516d;color:#fff;padding:38px 24px}
.st-key-music_stage button p{font-size:clamp(38px,7vw,90px)!important;font-weight:900;line-height:1.6;word-break:keep-all}
.st-key-music_stage button:hover,.st-key-music_stage button:focus{background:#233954;border-color:#f6c85f;color:#f6c85f}
[data-testid="stSidebar"]{background:#17263b}
@media(max-width:600px){.block-container{padding-left:12px;padding-right:12px}.quiz-card{padding-left:10px;padding-right:10px}.initials{font-size:clamp(42px,11vw,70px)}.st-key-music_stage button{min-height:280px}.st-key-music_stage button p{font-size:clamp(30px,8vw,48px)!important}}
</style>''', unsafe_allow_html=True)

st.markdown('''
<style>
.block-container,[data-testid="stMainBlockContainer"]{max-width:none!important;width:100%;padding:3.5rem clamp(12px,2vw,40px) 20px!important}
[data-testid="stVerticalBlock"]{gap:.65rem}
.quiz-card{container-type:inline-size;min-height:clamp(250px,53svh,680px);padding:56px 20px 28px;border:2px solid #6f86a2;border-radius:24px}
.initials{font-size:clamp(56px,min(13cqw,24svh),250px);line-height:1.35;letter-spacing:.035em;color:#fff;font-weight:900}
.quiz-answer{font-size:clamp(44px,min(10cqw,19svh),200px);line-height:1.35;color:#ffe08a;font-weight:900;word-break:keep-all}
.badge{font-size:clamp(20px,2vw,30px);color:#e1eaf5;top:14px;right:20px}
.question-counter{font-size:clamp(22px,2.5vw,36px);font-weight:800;color:#e1eaf5}
div.stButton>button{min-height:76px;border:2px solid #6f86a2}
div.stButton>button p{font-size:clamp(22px,2.6vw,36px)!important;font-weight:800!important}
.st-key-music_stage{container-type:inline-size}
.st-key-music_stage button{min-height:clamp(260px,57svh,720px);padding:24px;background:#1b2b42;border:2px solid #6f86a2}
.st-key-music_stage button p{font-size:clamp(48px,min(11cqw,21svh),220px)!important;line-height:1.35;white-space:normal;overflow-wrap:anywhere}
[data-testid="stSidebarCollapsedControl"] button,[data-testid="stSidebarCollapseButton"] button{min-width:58px;min-height:52px;background:#f6c85f;color:#101b2d;border-radius:12px;border:2px solid #fff}
[data-testid="stSidebarCollapsedControl"] svg,[data-testid="stSidebarCollapseButton"] svg{width:32px;height:32px}
[data-testid="stSidebar"] label p,[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p{font-size:20px!important;color:#e1eaf5}
button:focus-visible{outline:4px solid #fff!important;outline-offset:3px}
@media(max-height:600px) and (min-width:700px){.block-container{padding-top:2.7rem!important}.quiz-card{min-height:43svh;padding-top:42px}.st-key-music_stage button{min-height:48svh}div.stButton>button{min-height:60px}}
@media(max-width:600px){.quiz-card{padding-left:10px;padding-right:10px}.st-key-music_stage button{min-height:48svh}}
</style>''',unsafe_allow_html=True)

def large_text(text):
    words=text.split()
    if len(text.replace(' ',''))<=8 or len(words)<2:
        return escape(text)
    split=min(range(1,len(words)),key=lambda i:abs(len(' '.join(words[:i]))-len(' '.join(words[i:]))))
    return escape(' '.join(words[:split]))+'<br>'+escape(' '.join(words[split:]))

if st.session_state.get("quiz_version") != 2:
    st.session_state.update(quiz_version=2,game="초성퀴즈",q=0,m=0,reveal=False,hint=False,finished=False)
    st.session_state.pop("clips",None)
    st.session_state.pop("clip_meta",None)
s=st.session_state

def move(key,delta,total):
    s[key]=max(0,min(total-1,s[key]+delta))
    s.reveal=False;s.hint=False;s.finished=False

def reveal_answer():
    s.reveal=True

with st.sidebar:
    st.title("🎉 세대공감 퀴즈")
    game=st.radio("게임 선택",["초성퀴즈","음악퀴즈"],index=["초성퀴즈","음악퀴즈"].index(s.game))
    if game!=s.game:
        s.game=game;s.reveal=False;s.hint=False;s.finished=False;st.rerun()
    st.caption("초성: 영화·드라마 5문제 + 속담 5문제")
    st.caption("음악은 별도 휴대폰에서 재생하세요. 문제 화면을 터치하면 정답이 나옵니다.")
    st.caption("왼쪽 위 노란 화살표로 메뉴를 닫거나 다시 열 수 있습니다.")
    if st.button("이 게임 처음부터",use_container_width=True):
        s.q=0;s.m=0;s.reveal=False;s.hint=False;s.finished=False;st.rerun()

def navigation(key,total):
    a,b=st.columns(2)
    a.button("← 이전 문제",disabled=s[key]==0,on_click=move,args=(key,-1,total),use_container_width=True)
    if s[key]<total-1:
        b.button("다음 문제 →",on_click=move,args=(key,1,total),use_container_width=True,type="primary")
    elif b.button("게임 마치기 🎉",use_container_width=True,type="primary"):
        s.finished=True;st.rerun()

if s.finished:
    st.markdown('<div class="music-title">🎉 모두 수고하셨습니다!</div>',unsafe_allow_html=True)
    st.balloons()
    st.write("서로에게 큰 박수를 보내 주세요. 왼쪽 메뉴에서 다른 게임을 선택할 수 있습니다.")
elif s.game=="초성퀴즈":
    q=CHOSEONG[s.q]
    st.markdown(f'<div class="question-counter">초성퀴즈 · {s.q+1} / {len(CHOSEONG)}</div>',unsafe_allow_html=True)
    st.progress((s.q+1)/len(CHOSEONG))
    text=q['title'] if s.reveal else initials(q['title'])
    text_class='quiz-answer' if s.reveal else 'initials'
    st.markdown(f'<div class="quiz-card"><span class="badge">{q["category"]}</span><div class="{text_class}">{large_text(text)}</div></div>',unsafe_allow_html=True)
    if s.reveal:
        if q['year']:st.caption(q['year'])
    elif s.hint:st.info(q['hint'])
    a,b=st.columns(2)
    if a.button("💡 힌트",use_container_width=True):s.hint=True;st.rerun()
    b.button("정답 확인",on_click=reveal_answer,use_container_width=True)
    navigation("q",len(CHOSEONG))
else:
    i=s.m;song=SONGS[i]
    st.markdown(f'<div class="question-counter">음악퀴즈 · {i+1} / {len(SONGS)}</div>',unsafe_allow_html=True)
    st.progress((i+1)/len(SONGS))
    with st.container(key="music_stage"):
        label=f"{song['artist']} · {song['title']}" if s.reveal else f"🎵 문제 {i+1}"
        st.button(label,key=f"music_answer_{i}",on_click=reveal_answer,use_container_width=True)
    st.caption("정답입니다! 다음 문제로 넘어가세요." if s.reveal else "다른 휴대폰에서 노래를 들려준 뒤, 위의 큰 화면을 터치해 정답을 확인하세요.")
    navigation("m",len(SONGS))
