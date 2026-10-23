import io
import wave

def make_clip(raw, suffix, start):
    """Decode and physically trim audio. Never expose the full song to the player."""
    from pydub import AudioSegment
    import imageio_ffmpeg
    AudioSegment.converter = imageio_ffmpeg.get_ffmpeg_exe()
    if suffix.lower() == "wav":
        audio = AudioSegment.from_file(io.BytesIO(raw), format="wav")
    else:
        # Give ffmpeg an explicit decoder format; ffprobe is not required.
        formats = {"mp3": "mp3", "m4a": "mp4", "mp4": "mp4", "ogg": "ogg", "flac": "flac"}
        audio = AudioSegment.from_file(io.BytesIO(raw), format=formats.get(suffix.lower(), suffix.lower()))
    begin = round(float(start) * 1000)
    if begin < 0 or begin + 10000 > len(audio):
        raise ValueError(f"시작 지점 뒤에 10초가 필요합니다. 음원 길이: {len(audio)/1000:.1f}초")
    audio = audio[begin:begin+10000].set_frame_rate(22050).set_channels(1).set_sample_width(2)
    output = io.BytesIO()
    audio.export(output, format="wav")
    result = output.getvalue()
    with wave.open(io.BytesIO(result)) as check:
        if check.getnframes() != 220500:
            raise ValueError("10초 음원 변환에 실패했습니다.")
    return result
