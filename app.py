import io
import json
import zipfile
from pathlib import Path
from html import escape
import streamlit as st
import streamlit.components.v1 as components
from questions import CHOSEONG, SONGS, initials
from audio_utils import make_clip
from player import player_html

st.set_page_config(page_title="세대공감 퀴즈", page_icon="🎉", layout="wide")
st.markdown('''<style>
.stApp{background:#101b2d;color:#fff}.block-container{max-width:1250px;padding-top:1.3rem;padding-bottom:1rem}
header{background:transparent!important} .quiz-card{position:relative;background:#1b2b42;border:1px solid #38516d;border-radius:26px;padding:65px 24px 42px;text-align:center;min-height:300px;display:flex;align-items:center;justify-content:center}
.badge{position:absolute;right:22px;top:18px;color:#bacde4;font-size:17px}
.initials{font-size:clamp(58px,10vw,146px);font-weight:900;line-height:1.5;letter-spacing:.07em;word-break:keep-all;overflow-wrap:anywhere}
.answer{font-size:clamp(32px,6vw,65px);font-weight:900;color:#f6c85f;text-align:center;line-height:1.5;margin:18px 0}
.music-title{text-align:center;font-size:clamp(36px,7vw,70px);font-weight:900;padding:20px 0}
div.stButton>button{min-height:64px;font-size:23px;font-weight:750;border-radius:15px}
[data-testid="stSidebar"]{background:#17263b} @media(max-width:600px){.block-container{padding-left:12px;padding-right:12px}.quiz-card{padding-left:10px;padding-right:10px}.initials{font-size:clamp(42px,11vw,70px)}}
</style>''', unsafe_allow_html=True)

for key, value in {"game":"초성퀴즈","q":0,"m":0,"reveal":False,"hint":False,"clips":{},"clip_meta":{},"finished":False}.items():
    if key not in st.session_state: st.session_state[key]=value
s=st.session_state

def move(key, delta, total):
    s[key]=max(0,min(total-1,s[key]+delta));s.reveal=False;s.hint=False;s.finished=False

with st.sidebar:
    st.title("🎉 세대공감 퀴즈")
    game=st.radio("게임 선택", ["초성퀴즈","음악퀴즈","진행자 준비"], index=["초성퀴즈","음악퀴즈","진행자 준비"].index(s.game))
    if game!=s.game:
        s.game=game;s.reveal=False;s.hint=False;s.finished=False;st.rerun()
    st.caption("태블릿은 가로 화면을 권장합니다. 준비를 마치면 왼쪽 메뉴를 닫아 주세요.")
    if st.button("이 게임 처음부터", use_container_width=True):
        s.q=0;s.m=0;s.reveal=False;s.hint=False;s.finished=False;st.rerun()
    st.caption("음원은 현재 브라우저 세션에만 보관됩니다. 준비 후 10초 음원 ZIP을 내려받아 두세요.")

def navigation(key,total):
    a,b=st.columns(2)
    a.button("← 이전 문제",disabled=s[key]==0,on_click=move,args=(key,-1,total),use_container_width=True)
    if s[key]<total-1:
        b.button("다음 문제 →",on_click=move,args=(key,1,total),use_container_width=True,type="primary")
    elif b.button("게임 마치기 🎉",use_container_width=True,type="primary"):
        s.finished=True;st.rerun()

if s.game=="진행자 준비":
    st.title("진행자 준비")
    st.info("음원을 올리고 시작 지점을 지정한 뒤 ‘10초 만들기’를 누르세요. 각 녹음의 길이가 달라 하이라이트 시각은 직접 들어 보고 정합니다. 상용 음원은 포함되어 있지 않습니다.")
    st.caption("음원 이용 권한을 확인해 주세요. 곡마다 원곡 가수를 기본 정답으로 넣었습니다. 다른 가수의 녹음이라면 정답 가수도 바꿀 수 있습니다.")
    bundle=st.file_uploader("이전에 저장한 10초 음원 ZIP 복원",type=["zip"])
    if bundle and st.button("ZIP 복원하기"):
        try:
            with zipfile.ZipFile(bundle) as z:
                if sum(x.file_size for x in z.infolist())>50_000_000: raise ValueError("압축 해제 용량이 너무 큽니다.")
                meta=json.loads(z.read("manifest.json"))
                import wave
                recovered={}; recovered_meta={}
                for i in range(len(SONGS)):
                    name=f"{i+1:02d}.wav"
                    if name in z.namelist():
                        raw=z.read(name)
                        with wave.open(io.BytesIO(raw)) as w:
                            if abs(w.getnframes()/w.getframerate()-10)>.01: raise ValueError("10초가 아닌 파일이 있습니다.")
                        recovered[i]=raw;recovered_meta[i]=meta.get(str(i),{})
                s.clips.update(recovered);s.clip_meta.update(recovered_meta)
                st.success(f"{len(recovered)}곡 복원 완료")
        except Exception as e: st.error(f"복원 실패: {e}")
    st.subheader(f"음원 준비 {len(s.clips)} / 10")
    for i,song in enumerate(SONGS):
        with st.expander(f"{'✅' if i in s.clips else '⬜'} {i+1}. {song['artist']} · {song['title']}"):
            st.write(song['why']);st.caption("추천 구간: "+song['cue'])
            artist=st.text_input("정답으로 보여 줄 가수",value=s.clip_meta.get(i,{}).get("artist",song['artist']),key=f"artist_{i}")
            uploaded=st.file_uploader("사용 가능한 음원",type=["mp3","wav","m4a","ogg","flac"],key=f"file_{i}")
            start=st.number_input("하이라이트 시작 시각 (초) · 예: 1분 5초 → 65",min_value=0.0,value=float(s.clip_meta.get(i,{}).get("start",0)),step=1.0,key=f"start_{i}")
            if st.button("10초 만들기 / 적용",key=f"cut_{i}"):
                if uploaded is None: st.warning("먼저 음원 파일을 선택해 주세요.")
                else:
                    try:
                        with st.spinner("10초 음원을 만드는 중…"):
                            s.clips[i]=make_clip(uploaded.getvalue(),uploaded.name.rsplit('.',1)[-1],start)
                            s.clip_meta[i]={"artist":artist.strip() or song['artist'],"start":start,"title":song['title']}
                        st.success("완료! 아래에서 들어 보고 하이라이트를 확인해 주세요.")
                    except Exception as e: st.error(f"음원 변환 실패: {e}")
            if i in s.clips:
                st.audio(s.clips[i],format="audio/wav")
                st.download_button("이 곡 10초 WAV 저장",s.clips[i],file_name=f"quiz_{i+1:02d}.wav",mime="audio/wav",key=f"download_{i}")
    if s.clips:
        output=io.BytesIO()
        with zipfile.ZipFile(output,"w",zipfile.ZIP_DEFLATED) as z:
            z.writestr("manifest.json",json.dumps(s.clip_meta,ensure_ascii=False))
            for i,raw in s.clips.items(): z.writestr(f"{i+1:02d}.wav",raw)
        st.download_button("준비한 10초 음원 ZIP 저장",output.getvalue(),"quiz_audio.zip","application/zip")
    with st.expander("초성 정답표 · 진행자만 보기"):
        st.table([{"번호":i+1,"초성":initials(q['title']),"정답":q['title'],"범주":q['category'],"연도":q['year']} for i,q in enumerate(CHOSEONG)])
elif s.finished:
    st.markdown('<div class="music-title">🎉 모두 수고하셨습니다!</div>',unsafe_allow_html=True)
    st.balloons()
    st.write("서로에게 큰 박수를 보내 주세요. 왼쪽 메뉴에서 다른 게임을 선택할 수 있습니다.")
elif s.game=="초성퀴즈":
    q=CHOSEONG[s.q]
    st.caption(f"초성퀴즈 · {s.q+1} / {len(CHOSEONG)}")
    st.progress((s.q+1)/len(CHOSEONG))
    st.markdown(f'<div class="quiz-card"><span class="badge">{q["category"]}</span><div class="initials">{escape(initials(q["title"]))}</div></div>',unsafe_allow_html=True)
    if s.reveal:
        st.markdown(f'<div class="answer">{escape(q["title"])}</div>',unsafe_allow_html=True)
        st.caption(q['year'])
    elif s.hint: st.info(q['hint'])
    a,b=st.columns(2)
    if a.button("💡 힌트",use_container_width=True):s.hint=True;st.rerun()
    if b.button("정답 확인",use_container_width=True):s.reveal=True;st.rerun()
    navigation("q",len(CHOSEONG))
else:
    i=s.m;song=SONGS[i]
    st.caption(f"음악퀴즈 · {i+1} / {len(SONGS)}")
    st.progress((i+1)/len(SONGS))
    st.markdown('<div class="music-title">🎵 이 노래는 무엇일까요?</div>',unsafe_allow_html=True)
    if i in s.clips:
        components.html(player_html(s.clips[i],s.clip_meta.get(i,{}).get('artist',song['artist']),song['title']),height=400,scrolling=True)
    else:
        st.warning("이 문제의 10초 음원이 아직 준비되지 않았습니다. 왼쪽 메뉴의 ‘진행자 준비’에서 음원을 넣어 주세요.")
    navigation("m",len(SONGS))
