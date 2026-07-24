#!/usr/bin/env python3
"""
Max-extra enhancement for rl_bachelor.pptx:
  - Every available OOXML slide transition, one per slide
  - Staggered entrance animations with emphasis pulses on titles
  - Chiptune background music embedded and set to play across all slides
"""
import zipfile, shutil, re, subprocess, struct, wave, math
from pathlib import Path

SRC  = Path('/home/user/landscape-site-1/rl_bachelor.pptx')
OUT  = Path('/home/user/landscape-site-1/rl_bachelor_extra.pptx')
WORK = Path('/tmp/pptx_max')

shutil.rmtree(WORK, ignore_errors=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)

# ── 1. GENERATE CHIPTUNE BEAT (WAV → embedded) ───────────────────────────────
SAMPLE_RATE = 22050
DURATION    = 30  # seconds — loops in PowerPoint


def square(freq, t):
    return 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0


def note(freq, dur_beats, bpm=140):
    dur_s = (60 / bpm) * dur_beats
    n_samples = int(SAMPLE_RATE * dur_s)
    samples = []
    for i in range(n_samples):
        t = i / SAMPLE_RATE
        fade = min(1.0, (n_samples - i) / (SAMPLE_RATE * 0.05))  # tiny tail fade
        v = square(freq, t) * 0.4 * fade
        # add sub-octave for fullness
        v += square(freq / 2, t) * 0.15 * fade
        samples.append(v)
    return samples


# Rocket League vibe — simple repeated motif in C major pentatonic
# Freqs (Hz): C5=523 E5=659 G5=784 A5=880 C6=1047 G4=392
melody_pattern = [
    (784, 0.5), (880, 0.5), (1047, 1.0),
    (784, 0.5), (659, 0.5), (784, 1.0),
    (523, 0.5), (659, 0.5), (784, 0.5), (880, 0.5),
    (1047, 1.5), (784, 0.5),
    (880, 0.5), (784, 0.5), (659, 1.0),
    (523, 0.5), (392, 0.5), (523, 1.5), (523, 0.5),
]

bass_pattern = [
    (130, 0.5), (130, 0.5), (146, 1.0),
    (130, 0.5), (130, 0.5), (130, 1.0),
    (174, 0.5), (174, 0.5), (174, 0.5), (146, 0.5),
    (130, 2.0),
    (146, 0.5), (146, 0.5), (130, 1.0),
    (98,  0.5), (98,  0.5), (130, 2.0),
]


def build_track(pattern, repeat_to_duration):
    out = []
    while len(out) / SAMPLE_RATE < repeat_to_duration:
        for freq, beats in pattern:
            out.extend(note(freq, beats))
    return out[:int(SAMPLE_RATE * repeat_to_duration)]


melody = build_track(melody_pattern, DURATION)
bass   = build_track(bass_pattern,   DURATION)

# Mix
mixed = [max(-0.95, min(0.95, m + b)) for m, b in zip(melody, bass)]

# Write WAV
wav_path = WORK / 'ppt/media/audio1.wav'
with wave.open(str(wav_path), 'w') as wf:
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(SAMPLE_RATE)
    packed = struct.pack(f'<{len(mixed)}h', *[int(s * 32767) for s in mixed])
    wf.writeframes(packed)

print(f'Generated audio: {wav_path.stat().st_size // 1024} KB')

# ── 2. WIRE AUDIO INTO SLIDE 1 ────────────────────────────────────────────────
# Add relationship in slide1.xml.rels
rels1_path = WORK / 'ppt/slides/_rels/slide1.xml.rels'
rels1 = rels1_path.read_text(encoding='utf-8')

AUDIO_RID   = 'rId99'
AUDIO_TYPE  = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio'
AUDIO_TARGET = '../media/audio1.wav'

audio_rel = f'<Relationship Id="{AUDIO_RID}" Type="{AUDIO_TYPE}" Target="{AUDIO_TARGET}"/>'
rels1 = rels1.replace('</Relationships>', f'{audio_rel}</Relationships>')
rels1_path.write_text(rels1, encoding='utf-8')

# Register the WAV content type
ct_path = WORK / '[Content_Types].xml'
ct_xml  = ct_path.read_text(encoding='utf-8')
if 'wav' not in ct_xml:
    wav_ct = '<Default Extension="wav" ContentType="audio/wav"/>'
    ct_xml = ct_xml.replace('</Types>', f'{wav_ct}</Types>')
    ct_path.write_text(ct_xml, encoding='utf-8')

# Audio shape + timing on slide 1 — hidden icon, auto-play, loop, cross-slides
AUDIO_SHAPE_ID = 99

audio_pic_xml = (
    f'<p:pic>'
    f'<p:nvPicPr>'
    f'<p:cNvPr id="{AUDIO_SHAPE_ID}" name="background_audio">'
    f'<a:hlinkClick r:id="{AUDIO_RID}" action="ppaction://media"/>'
    f'</p:cNvPr>'
    f'<p:cNvPicPr><a:picLocks noRot="1" noChangeAspect="1" noMove="1" '
    f'noResize="1" noSelect="1" noCrop="1" noGrp="1"/></p:cNvPicPr>'
    f'<p:nvPr>'
    f'<p:cNvMediaPr><a:audioFile r:link="{AUDIO_RID}"/></p:cNvMediaPr>'
    f'</p:nvPr>'
    f'</p:nvPicPr>'
    f'<p:blipFill><a:blip r:embed="{AUDIO_RID}"/>'
    f'<a:stretch><a:fillRect/></a:stretch></p:blipFill>'
    f'<p:spPr>'
    f'<a:xfrm><a:off x="-914400" y="-914400"/><a:ext cx="457200" cy="457200"/></a:xfrm>'
    f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
    f'</p:spPr>'
    f'</p:pic>'
)

# Audio timing (play on slide load, loop, cross-slide = numSld covers all 9 slides)
audio_timing_xml = (
    f'<p:par>'
    f'<p:cTn id="900" fill="hold" nodeType="withEffect">'
    f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
    f'<p:childTnLst>'
    f'<p:audio isNarration="0">'
    f'<p:cMediaNode vol="80000" mute="0" numSld="9" showWhenStopped="0">'
    f'<p:cTn id="901" fill="hold" nodeType="withEffect"/>'
    f'<p:tgtEl><p:spTgt spid="{AUDIO_SHAPE_ID}"/></p:tgtEl>'
    f'</p:cMediaNode>'
    f'</p:audio>'
    f'</p:childTnLst>'
    f'</p:cTn>'
    f'</p:par>'
)

# ── 3. PER-SLIDE CONFIG ───────────────────────────────────────────────────────
# (transition_inner_xml, speed, filter1, filter2, delay_step, start_delay, anim_dur)
# Using EVERY available OOXML transition type across 9 slides
SLIDE_CONFIG = {
    1: ('<p:zoom dir="in"/>',                    'med',  'zoom(inCenter)',    'fade',              120, 300, 700),
    2: ('<p:push dir="u"/>',                     'fast', 'slide(fromLeft)',   'slide(fromRight)',  100, 200, 500),
    3: ('<p:strips dir="lu"/>',                  'med',  'randomBar(horz)',   'randomBar(vert)',    80, 200, 400),
    4: ('<p:wheel spokes="8"/>',                 'fast', 'wheel(4)',          'dissolve',          100, 300, 600),
    5: ('<p:split dir="vert" orient="out"/>',    'med',  'wipe(left)',        'wipe(right)',        70, 200, 350),
    6: ('<p:checker dir="horz"/>',               'fast', 'slide(fromBottom)', 'slide(fromLeft)',   110, 300, 600),
    7: ('<p:newsflash/>',                        'fast', 'zoom(inCenter)',    'zoom(inCenter)',    120, 250, 600),
    8: ('<p:diamond/>',                          'med',  'wipe(left)',        'wipe(right)',        70, 200, 350),
    9: ('<p:zoom dir="out"/>',                   'slow', 'zoom(inCenter)',    'dissolve',          200, 600, 900),
}

# ── 4. ANIMATION BUILDER ──────────────────────────────────────────────────────

def get_shape_ids(xml):
    return [int(m) for m in re.findall(r'<p:cNvPr id="(\d+)"', xml) if m != '1']

def make_timing(shape_ids, f1, f2, delay_step, start_delay, anim_dur,
                extra_audio_shape=None, audio_timing_snippet=None):
    """
    Staggered entrance animations + optional emphasis pulse on first 2 shapes.
    extra_audio_shape: if set, add audio timing snippet to this timing block.
    """
    base_id = [10]
    def nxt():
        v = base_id[0]; base_id[0] += 1; return v

    all_ids = list(shape_ids)
    if extra_audio_shape:
        all_ids = [s for s in all_ids if s != extra_audio_shape]

    shapes_xml = []
    builds_xml = []

    for i, spid in enumerate(all_ids):
        filt     = f1 if i % 2 == 0 else f2
        rel_dly  = i * delay_step
        ctn_id   = nxt(); set_id = nxt(); anim_id = nxt()

        shapes_xml.append(
            f'<p:par>'
            f'<p:cTn id="{ctn_id}" presetID="10" presetClass="entr" presetSubtype="0"'
            f' fill="hold" grpId="{i}" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{rel_dly}"/></p:stCondLst>'
            f'<p:childTnLst>'
            f'<p:set><p:cBhvr>'
            f'<p:cTn id="{set_id}" dur="1" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="{filt}">'
            f'<p:cBhvr><p:cTn id="{anim_id}" dur="{anim_dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'</p:cBhvr></p:animEffect>'
            f'</p:childTnLst></p:cTn></p:par>'
        )
        builds_xml.append(f'<p:bldP spid="{spid}" grpId="{i}" uiExpand="1" build="p"/>')

        # Add a scale-pulse emphasis on the first real text shape (i==0) and image (i==2)
        if i in (0, 2) and i < len(all_ids):
            pulse_after = rel_dly + anim_dur + 100
            p1 = nxt(); p2 = nxt(); p3 = nxt()
            shapes_xml.append(
                f'<p:par>'
                f'<p:cTn id="{p1}" presetID="26" presetClass="emph" presetSubtype="0"'
                f' fill="hold" grpId="{i+100}" nodeType="afterEffect">'
                f'<p:stCondLst><p:cond delay="{pulse_after}"/></p:stCondLst>'
                f'<p:childTnLst>'
                f'<p:animScale>'
                f'<p:by x="115000" y="115000"/>'
                f'<p:cBhvr autoRev="1">'
                f'<p:cTn id="{p2}" dur="200" autoRev="1"/>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
                f'</p:cBhvr>'
                f'</p:animScale>'
                f'</p:childTnLst></p:cTn></p:par>'
            )

    # Audio snippet goes into the same timing root (slide 1 only)
    audio_part = audio_timing_snippet if audio_timing_snippet else ''

    shapes_combined = ''.join(shapes_xml)
    builds_combined = ''.join(builds_xml)

    return (
        f'<p:timing>'
        f'<p:tnLst><p:par>'
        f'<p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot">'
        f'<p:childTnLst>'
        # Audio plays immediately at slide load (before anything else)
        + (f'<p:par><p:cTn id="5" fill="hold">'
           f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
           f'<p:childTnLst>{audio_part}</p:childTnLst>'
           f'</p:cTn></p:par>' if audio_part else '')
        +
        f'<p:par><p:cTn id="2" fill="hold">'
        f'<p:stCondLst><p:cond delay="{start_delay}"/></p:stCondLst>'
        f'<p:childTnLst>{shapes_combined}</p:childTnLst>'
        f'</p:cTn></p:par>'
        f'</p:childTnLst></p:cTn>'
        f'</p:par></p:tnLst>'
        f'<p:bldLst>{builds_combined}</p:bldLst>'
        f'</p:timing>'
    )

# ── 5. PROCESS EACH SLIDE ────────────────────────────────────────────────────
for slide_num in range(1, 10):
    slide_path = WORK / f'ppt/slides/slide{slide_num}.xml'
    xml = slide_path.read_text(encoding='utf-8')

    cfg = SLIDE_CONFIG[slide_num]
    trans_inner, speed, f1, f2, delay_step, start_delay, anim_dur = cfg
    shape_ids = get_shape_ids(xml)

    trans_xml = f'<p:transition spd="{speed}">{trans_inner}</p:transition>'

    if slide_num == 1:
        # Inject hidden audio shape into spTree before </p:spTree>
        xml = xml.replace('</p:spTree>', f'{audio_pic_xml}</p:spTree>')
        shape_ids = get_shape_ids(xml)
        timing_xml = make_timing(
            shape_ids, f1, f2, delay_step, start_delay, anim_dur,
            extra_audio_shape=AUDIO_SHAPE_ID,
            audio_timing_snippet=audio_timing_xml,
        )
    else:
        timing_xml = make_timing(shape_ids, f1, f2, delay_step, start_delay, anim_dur)

    new_xml = xml.replace('</p:sld>', f'{trans_xml}{timing_xml}</p:sld>')
    slide_path.write_text(new_xml, encoding='utf-8')
    print(f'Slide {slide_num}: {len([s for s in shape_ids if s != AUDIO_SHAPE_ID])} shapes '
          f'| {trans_inner[:25]} | {f1}')

# ── 6. REPACK ─────────────────────────────────────────────────────────────────
OUT.unlink(missing_ok=True)
res = subprocess.run(
    ['zip', '-Xr', str(OUT.resolve()), '.'],
    cwd=str(WORK), capture_output=True, text=True
)
print(f'\nRepack: {res.returncode}')
print(f'Output: {OUT}  ({OUT.stat().st_size // 1024} KB)')
