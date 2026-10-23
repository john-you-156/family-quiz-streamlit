import base64
import html

def player_html(clip, artist, title):
    source = base64.b64encode(clip).decode("ascii")
    answer = html.escape(f"{artist} · {title}")
    return '''<!doctype html><html lang="ko"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
*{box-sizing:border-box}body{margin:0;background:#101b2d;color:white;font-family:system-ui,'Malgun Gothic',sans-serif;text-align:center}
button{border:0;border-radius:20px;padding:23px 18px;min-height:80px;font-weight:800;font-size:clamp(22px,4vw,34px);cursor:pointer;background:#f6c85f;color:#101b2d;width:min(96%,650px)}
button:disabled{opacity:.6}#answer{font-size:clamp(30px,6vw,60px);font-weight:900;margin:24px 0;line-height:1.4;word-break:keep-all}
#status{color:#c3d3e9;font-size:18px;margin:16px}#again{background:#2c425f;color:white;font-size:20px;min-height:52px;padding:12px;margin-top:12px}
</style><audio id="audio" preload="auto" src="data:audio/wav;base64,''' + source + '''"></audio>
<button id="main" onclick="advance()">▶ 노래 듣기 · 10초</button>
<div id="status" role="status">처음 누르면 재생 · 한 번 더 누르면 정답</div>
<div id="answer" hidden>''' + answer + '''</div>
<button id="again" hidden onclick="replay()">↻ 10초 다시 듣기</button>
<script>
const audio=document.getElementById('audio'),main=document.getElementById('main'),
status=document.getElementById('status'),answer=document.getElementById('answer'),again=document.getElementById('again');
let played=false, revealed=false;
async function play(){audio.pause();audio.currentTime=0;try{await audio.play();return true}catch(e){status.textContent='재생되지 않았습니다. 기기 음량을 확인한 뒤 다시 눌러 주세요.';return false}}
async function advance(){
if(!played){main.disabled=true;const ok=await play();main.disabled=false;if(ok){played=true;main.textContent='정답 확인';again.hidden=false;status.textContent='10초 재생 중… 정답은 버튼을 한 번 더 누르세요.'}}
else{audio.pause();revealed=true;answer.hidden=false;main.hidden=true;status.textContent='정답입니다! 가수와 제목을 함께 확인하세요.'}}
async function replay(){if(await play())status.textContent='10초 다시 재생 중…'}
audio.addEventListener('ended',()=>{status.textContent=revealed?'정답입니다!':'재생 끝! 정답 확인 버튼을 눌러 주세요.'});
audio.addEventListener('timeupdate',()=>{if(audio.currentTime>=10)audio.pause()});
window.addEventListener('pagehide',()=>audio.pause());
</script></html>'''
