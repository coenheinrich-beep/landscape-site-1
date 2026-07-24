#!/usr/bin/env python3
"""
ULTIMATE Rocket League presentation — built from original pptx.
Adds: chiptune music, max transitions, cascade animations,
and heavy visual design (glow orbs, hexagons, particles,
speed lines, neon rings, themed per-slide elements).
"""
import zipfile, shutil, re, subprocess, struct, wave, math
from pathlib import Path

SRC  = Path('rl_bachelor.pptx')
OUT  = Path('rl_bachelor_extra.pptx')
WORK = Path('/tmp/pptx_ultimate')

shutil.rmtree(WORK, ignore_errors=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)

W = 9144000   # slide width  (10 in)
H = 5143500   # slide height (5.625 in)
I = 914400    # 1 inch in EMU
CX = W // 2  # 4572000
CY = H // 2  # 2571750

# ── AUDIO ────────────────────────────────────────────────────────────────────
SR = 22050
def sq(f, t): return 1.0 if math.sin(2*math.pi*f*t) >= 0 else -1.0
def note(f, beats, bpm=140):
    n = int(SR*(60/bpm)*beats)
    return [sq(f, i/SR)*0.35*min(1,(n-i)/(SR*0.04)) for i in range(n)]
def track(pat, dur):
    out=[]
    while len(out)/SR < dur:
        for f,b in pat: out.extend(note(f,b))
    return out[:int(SR*dur)]

MELO=[(784,.5),(880,.5),(1047,1),(784,.5),(659,.5),(784,1),
      (523,.5),(659,.5),(784,.5),(880,.5),(1047,1.5),(784,.5),
      (880,.5),(784,.5),(659,1),(523,.5),(392,.5),(523,2)]
BASS=[(130,.5),(130,.5),(146,1),(130,.5),(130,.5),(130,1),
      (174,.5),(174,.5),(174,.5),(146,.5),(130,2),
      (146,.5),(146,.5),(130,1),(98,.5),(98,.5),(130,2)]
m=track(MELO,30); b=track(BASS,30)
mix=[max(-0.95,min(0.95,x+y)) for x,y in zip(m,b)]
wav_path=WORK/'ppt/media/audio1.wav'
with wave.open(str(wav_path),'w') as wf:
    wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes(struct.pack(f'<{len(mix)}h',*[int(s*32767) for s in mix]))
print(f'Audio: {wav_path.stat().st_size//1024} KB')

# Register content type
ct=WORK/'[Content_Types].xml'; ctx=ct.read_text()
if 'wav' not in ctx:
    ct.write_text(ctx.replace('</Types>','<Default Extension="wav" ContentType="audio/wav"/></Types>'))

# ── SHAPE BUILDER ─────────────────────────────────────────────────────────────
def sp(id, preset, x, y, cx, cy, color, alpha, rot=0,
       outline=False, lw=25400, glow=0, glow_a=50000):
    rs = f' rot="{rot}"' if rot else ''
    if outline:
        f_xml = '<a:noFill/>'
        l_xml = (f'<a:ln w="{lw}"><a:solidFill>'
                 f'<a:srgbClr val="{color}"><a:alpha val="{alpha}"/></a:srgbClr>'
                 f'</a:solidFill></a:ln>')
    else:
        f_xml = (f'<a:solidFill><a:srgbClr val="{color}">'
                 f'<a:alpha val="{alpha}"/></a:srgbClr></a:solidFill>')
        l_xml = '<a:ln><a:noFill/></a:ln>'
    g_xml = ''  # glow effects removed — not supported on iOS PowerPoint
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="d{id}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm{rs}>'
            f'<a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/>'
            f'</a:xfrm><a:prstGeom prst="{preset}"><a:avLst/></a:prstGeom>'
            f'{f_xml}{l_xml}{g_xml}</p:spPr></p:sp>')

# Only ellipse, rect, diamond — confirmed safe on iOS PowerPoint
def orb(id, x, y, size, color, alpha):
    return sp(id,'ellipse', x-size//2, y-size//2, size, size, color, alpha)
def ring(id, x, y, size, color, alpha, lw=30000):
    return sp(id,'ellipse', x-size//2, y-size//2, size, size, color, alpha, outline=True, lw=lw)
def dot(id, x, y, size, color, alpha):
    return sp(id,'ellipse', x-size//2, y-size//2, size, size, color, alpha)
def bar(id, x, y, w2, h2, color, alpha):
    return sp(id,'rect', x, y, w2, h2, color, alpha)
def dmd(id, x, y, size, color, alpha):
    return sp(id,'diamond', x-size//2, y-size//2, size, size, color, alpha)

# ── PER-SLIDE DECORATIONS ────────────────────────────────────────────────────
def slide1_decor():
    s=[]; n=500
    # Big atmosphere orbs
    s+=[orb(n,W-I,0,4*I,'2196F3',5000),orb(n+1,0,H,4*I,'FF6D00',5000),
        orb(n+2,CX,CY,6*I,'00BCD4',3000),orb(n+3,W//4,0,2*I,'9C27B0',4000)]; n+=4
    # Concentric rings behind title
    for i,sz in enumerate([8*I,6*I,4*I]):
        s.append(ring(n+i,CX,CY-I//2,sz,'FF6D00',5000+i*2000,lw=15000+i*5000)); n+=1
    n+=2
    # Top/bottom accent bars
    s+=[bar(n,0,0,W,I//4,'FF6D00',15000),bar(n+1,0,H-I//4,W,I//4,'00BCD4',15000)]; n+=2
    # Left/right edge bars
    s+=[bar(n,0,0,I//4,H,'2196F3',8000),bar(n+1,W-I//4,0,I//4,H,'2196F3',8000)]; n+=2
    # Speed lines (thin horizontal bars)
    for i,y2 in enumerate([I,I*3//2,H-I,H*3//4]):
        s.append(bar(n+i,0,y2,W,12000,'FFFFFF',4000+i*1000)); n+=1
    n+=3
    # Diamond sparkles
    for i,(x2,y2,sz,c) in enumerate([(I//2,H//2,I//3,'FF6D00'),(W-I//2,H//3,I//4,'00BCD4'),(W//4,H*3//4,I//4,'FFFFFF'),(W*3//4,H//4,I//3,'FF6D00')]):
        s.append(dmd(n+i,x2,y2,sz,c,20000)); n+=1
    n+=3
    # Particles
    for i,(x2,y2,c,a) in enumerate([(I//2,I//2,'FF6D00',60000),(2*I,I//3,'00BCD4',50000),(4*I,I//4,'FFFFFF',40000),(7*I,I//2,'2196F3',60000),(I//4,2*I,'00BCD4',50000),(8*I,2*I,'FF6D00',55000),(5*I,H-I//4,'2196F3',50000),(W-I//4,H//2,'00BCD4',50000),(3*I,H-I//3,'FF6D00',55000)]):
        s.append(dot(n+i,x2,y2,55000+i*5000,c,a)); n+=1
    return ''.join(s)

def slide2_decor():
    s=[]; n=520
    rank_colors=['CD7F32','C0C0C0','FFD700','00BFFF','9C27B0','FF6D00']
    for i,c in enumerate(rank_colors):
        s.append(orb(n+i,I,I//2+i*(H//6),I,c,8000)); n+=1
    s+=[orb(n,W-2*I,0,3*I,'FFD700',5000),orb(n+1,W//2,H,4*I,'9C27B0',4000),orb(n+2,0,H//2,3*I,'2196F3',4000)]; n+=3
    for i,sz in enumerate([5*I,3*I,I]):
        s.append(ring(n+i,W*3//4,CY,sz,'FFD700',5000+i*3000,lw=20000)); n+=1
    n+=2
    s+=[bar(n,0,0,W,I//5,'FFD700',10000),bar(n+1,0,H-I//5,W,I//5,'FFD700',10000)]; n+=2
    for i,(x2,y2,c) in enumerate([(W-I//2,I//2,'FFD700'),(W-I,H-I//2,'FFD700'),(I//2,H-I//2,'9C27B0')]):
        s.append(dmd(n+i,x2,y2,I//2,c,20000)); n+=1
    n+=2
    for i,(x2,y2,c,a) in enumerate([(2*I,I//3,'FFD700',60000),(5*I,I//4,'C0C0C0',50000),(8*I,I//2,'FF6D00',60000),(I//4,H//2,'2196F3',50000),(W-I//4,H*3//4,'9C27B0',55000),(4*I,H-I//4,'FFD700',55000)]):
        s.append(dot(n+i,x2,y2,70000,c,a)); n+=1
    return ''.join(s)

def slide3_decor():
    s=[]; n=540
    # Corner L-brackets from rects
    for x2,y2 in [(0,0),(W-I,0),(0,H-I//4),(W-I,H-I//4)]:
        s.append(bar(n,x2,y2,I,I//4,'00BCD4',15000)); n+=1
    for x2,y2 in [(0,0),(W-I//4,0),(0,H-I),(W-I//4,H-I)]:
        s.append(bar(n,x2,y2,I//4,I,'00BCD4',15000)); n+=1
    s+=[orb(n,CX,CY,6*I,'2196F3',4000),orb(n+1,W-I,0,3*I,'FF6D00',5000),orb(n+2,0,H,3*I,'00BCD4',4000)]; n+=3
    for i,sz in enumerate([4*I,2*I]):
        s.append(ring(n+i,I,I,sz,'2196F3',6000+i*2000,lw=20000)); n+=1
        s.append(ring(n+i+2,W-I,H-I,sz,'FF6D00',6000+i*2000,lw=20000)); n+=1
    n+=2
    for i,(x2,y2,c,a) in enumerate([(I//2,I//3,'2196F3',60000),(3*I,I//4,'00BCD4',50000),(6*I,I//2,'FFFFFF',40000),(8*I,I//3,'FF6D00',50000),(I//3,3*I,'00BCD4',50000),(W-I//3,2*I,'2196F3',50000),(4*I,H-I//3,'FF6D00',55000),(7*I,H-I//2,'FFFFFF',40000)]):
        s.append(dot(n+i,x2,y2,55000+i*4000,c,a)); n+=1
    return ''.join(s)

def slide4_decor():
    s=[]; n=560
    # HUD corner accents from pairs of rects
    for x2,y2 in [(0,0),(W-2*I,0),(0,H-I//4),(W-2*I,H-I//4)]:
        s.append(bar(n,x2,y2,2*I,I//4,'FF6D00',18000)); n+=1
    for x2,y2 in [(0,0),(W-I//4,0),(0,H-2*I),(W-I//4,H-2*I)]:
        s.append(bar(n,x2,y2,I//4,2*I,'FF6D00',18000)); n+=1
    for i,(x2,y2,c) in enumerate([(I//2,CY,'FF6D00'),(W-I//2,CY,'FF6D00'),(CX,I//2,'00BCD4'),(CX,H-I//2,'00BCD4')]):
        s.append(dmd(n+i,x2,y2,I//2,c,15000)); n+=1
    s+=[orb(n,0,0,4*I,'FF6D00',6000),orb(n+1,W,H,4*I,'FF6D00',5000),orb(n+2,CX,CY,3*I,'2196F3',3000)]; n+=3
    for i,sz in enumerate([6*I,4*I,2*I]):
        s.append(ring(n+i,CX,CY,sz,'FF6D00',4000+i*2000,lw=15000)); n+=1
    n+=2
    s+=[bar(n,0,CY-8000,W,16000,'FF6D00',5000),bar(n+1,CX-8000,0,16000,H,'FF6D00',5000)]; n+=2
    for i,(x2,y2,c,a) in enumerate([(I//2,I//4,'FF6D00',70000),(3*I,I//3,'FFFFFF',50000),(6*I,I//4,'FF6D00',65000),(I//3,2*I,'00BCD4',50000),(W-I//3,3*I,'FF6D00',60000),(5*I,H-I//4,'2196F3',50000),(8*I,H-I//3,'FF6D00',65000)]):
        s.append(dot(n+i,x2,y2,60000+i*4000,c,a)); n+=1
    return ''.join(s)

def slide5_decor():
    s=[]; n=580
    s+=[ring(n,W//4,CY,3*I,'00BCD4',7000,lw=20000),ring(n+1,W*3//4,CY,3*I,'FF6D00',7000,lw=20000)]; n+=2
    s+=[orb(n,0,CY,4*I,'00BCD4',5000),orb(n+1,W,CY,4*I,'FF6D00',5000),orb(n+2,CX,0,3*I,'9C27B0',4000)]; n+=3
    for i,sz in enumerate([5*I,3*I]):
        s.append(ring(n+i,W//4,CY,sz,'00BCD4',3000+i*2000,lw=12000)); n+=1
        s.append(ring(n+i+2,W*3//4,CY,sz,'FF6D00',3000+i*2000,lw=12000)); n+=1
    n+=2
    for i in range(7):
        y2=I//2+i*(H//7)
        s.append(dot(n+i,CX,y2,35000,'FFFFFF',8000)); n+=1
    s+=[bar(n,0,0,W,I//5,'9C27B0',8000),bar(n+1,0,H-I//5,W,I//5,'9C27B0',8000)]; n+=2
    for i,(x2,y2,c) in enumerate([(I//2,I//2,'00BCD4'),(W-I//2,H-I//2,'FF6D00'),(CX,I//4,'FFFFFF')]):
        s.append(dmd(n+i,x2,y2,I//3,c,20000)); n+=1
    n+=2
    for i,(x2,y2,c,a) in enumerate([(I//3,I//3,'00BCD4',65000),(W-I//3,I//3,'FF6D00',65000),(I//4,H//2,'2196F3',50000),(W-I//4,H//3,'00BCD4',55000),(W//4,H-I//3,'00BCD4',55000),(W*3//4,H-I//3,'FF6D00',55000)]):
        s.append(dot(n+i,x2,y2,60000,c,a)); n+=1
    return ''.join(s)

def slide6_decor():
    s=[]; n=600
    stage_colors=['2196F3','00BCD4','FF6D00','FF1744','00E676']
    for i,c in enumerate(stage_colors):
        x2=I//2+i*(W//5)
        s.append(orb(n+i,x2,CY,2*I,c,6000)); n+=1
    for i,c in enumerate(stage_colors):
        x2=I//2+i*(W//5)
        s.append(ring(n+i,x2,CY,I,c,15000,lw=25000)); n+=1
    s+=[orb(n,0,0,4*I,'2196F3',5000),orb(n+1,W,H,4*I,'00E676',5000),orb(n+2,CX,CY,6*I,'FF6D00',3000)]; n+=3
    s+=[bar(n,0,0,W,I//5,'2196F3',8000),bar(n+1,0,H-I//5,W,I//5,'00E676',8000)]; n+=2
    for i,(x2,y2,c) in enumerate([(I//3,I//3,'00E676'),(W-I//3,I//3,'2196F3'),(CX,H-I//3,'FF6D00')]):
        s.append(dmd(n+i,x2,y2,I//3,c,20000)); n+=1
    n+=2
    for i,(x2,y2,c,a) in enumerate([(I//3,I//4,'2196F3',65000),(W//3,I//4,'00BCD4',60000),(W*2//3,I//4,'FF6D00',65000),(W-I//3,I//4,'00E676',60000),(I//4,H//2,'2196F3',50000),(W-I//4,H//2,'FF1744',50000),(W//3,H-I//3,'00BCD4',55000),(W*2//3,H-I//3,'FF6D00',55000)]):
        s.append(dot(n+i,x2,y2,65000,c,a)); n+=1
    return ''.join(s)

def slide7_decor():
    s=[]; n=620
    # Speed lines
    for i,y2 in enumerate([I,I*3//2,I*5//2,H-I,H-I*2,CY]):
        c='FF6D00' if i%2==0 else '00BCD4'
        s.append(bar(n+i,0,y2,W,14000,c,6000+i*1000)); n+=1
    # Ball arc dots
    for i in range(9):
        t=i/8
        x2=int(I+t*(W-2*I))
        y2=int(CY-I*(4*t*(1-t))*1.5)  # parabola
        s.append(dot(n+i,x2,y2,70000+i*8000,'FF6D00',12000+i*2000)); n+=1
    s+=[orb(n,0,CY,5*I,'FF6D00',7000),orb(n+1,W,CY,5*I,'2196F3',6000),orb(n+2,CX,CY,4*I,'FFFFFF',2000)]; n+=3
    for i,sz in enumerate([7*I,5*I,3*I]):
        s.append(ring(n+i,CX,CY,sz,'FF6D00',3000+i*2000,lw=12000)); n+=1
    n+=2
    for i,(x2,y2,c,a) in enumerate([(I//2,I//4,'FF6D00',70000),(3*I,I//3,'FFFFFF',55000),(7*I,I//3,'2196F3',65000),(I//3,H//3,'00BCD4',55000),(W-I//3,H*2//3,'FF6D00',65000),(5*I,H-I//4,'2196F3',55000)]):
        s.append(dot(n+i,x2,y2,65000,c,a)); n+=1
    return ''.join(s)

def slide8_decor():
    s=[]; n=640
    for i,sz in enumerate([6*I,4*I,2*I,I]):
        s.append(ring(n+i,CX+2*I,CY,sz,'FF6D00',5000+i*2500,lw=12000)); n+=1
    s+=[bar(n,I,CY-8000,W-2*I,16000,'FF6D00',8000),bar(n+1,CX+2*I-8000,I,16000,H-2*I,'FF6D00',8000)]; n+=2
    # Corner accents
    for x2,y2 in [(0,0),(W-2*I,0),(0,H-I//4),(W-2*I,H-I//4)]:
        s.append(bar(n,x2,y2,2*I,I//4,'00BCD4',15000)); n+=1
    for x2,y2 in [(0,0),(W-I//4,0),(0,H-2*I),(W-I//4,H-2*I)]:
        s.append(bar(n,x2,y2,I//4,2*I,'00BCD4',15000)); n+=1
    s+=[orb(n,CX+2*I,CY,5*I,'FF6D00',5000),orb(n+1,0,0,4*I,'2196F3',5000),orb(n+2,W,H,4*I,'FF6D00',4000)]; n+=3
    for i in range(4):
        s.append(dmd(n+i,I//4,I+i*(H//4),I//3,'FF6D00',12000)); n+=1
    for i,(x2,y2,c) in enumerate([(I//3,H-I//3,'FF6D00'),(W*3//4,I//3,'00BCD4')]):
        s.append(dmd(n+i,x2,y2,I//3,c,20000)); n+=1
    n+=1
    for i,(x2,y2,c,a) in enumerate([(I//3,I//4,'00BCD4',65000),(3*I,I//3,'FF6D00',55000),(8*I,I//3,'FFFFFF',50000),(I//3,3*I,'2196F3',55000),(W-I//3,2*I,'FF6D00',65000),(5*I,H-I//4,'00BCD4',55000),(7*I,H-I//3,'FF6D00',65000)]):
        s.append(dot(n+i,x2,y2,60000,c,a)); n+=1
    return ''.join(s)

def slide9_decor():
    s=[]; n=660
    # Confetti — plain colored rects, no rotation
    confetti_data=[('FF6D00',I,I//2),('00BCD4',2*I,I//3),('FFD700',3*I,I//4),('FF1744',4*I,I//2),('00E676',5*I,I//3),('9C27B0',6*I,I//4),('FF6D00',7*I,I//2),('00BCD4',8*I,I//3),('FFD700',I//2,H//3),('FF1744',I//4,2*I),('00E676',W-I//2,H//3),('9C27B0',W-I//4,2*I),('FF6D00',2*I,H*3//4),('FFD700',4*I,H*3//4),('00BCD4',6*I,H*3//4),('FF1744',8*I,H*3//4),('00E676',I//2,H-I//3),('9C27B0',W-I//2,H-I//3),('FF6D00',3*I,H-I//4),('00BCD4',7*I,H-I//4)]
    for i,(c,x2,y2) in enumerate(confetti_data):
        s.append(bar(n+i,x2,y2,90000+i*4000,45000,c,70000)); n+=1
    # Celebration diamonds
    for i,(x2,y2,sz,c) in enumerate([(I//2,I//2,I//2,'FFD700'),(W-I//2,I//2,I//2,'FFD700'),(I//2,H-I//2,I//2,'FF6D00'),(W-I//2,H-I//2,I//2,'FF6D00'),(CX,I//3,I,'FFD700'),(W//4,H//4,I//2,'00BCD4'),(W*3//4,H//4,I//2,'00E676'),(W//4,H*3//4,I//3,'FF1744'),(W*3//4,H*3//4,I//3,'9C27B0')]):
        s.append(dmd(n+i,x2,y2,sz,c,35000)); n+=1
    s+=[orb(n,CX,CY,6*I,'FFD700',5000),orb(n+1,I//2,I//2,3*I,'FF6D00',6000),orb(n+2,W-I//2,I//2,3*I,'00BCD4',6000),orb(n+3,CX,H,4*I,'9C27B0',5000)]; n+=4
    for i,sz in enumerate([7*I,5*I,3*I]):
        s.append(ring(n+i,CX,CY-I//2,sz,'FFD700',4000+i*3000,lw=18000)); n+=1
    n+=2
    s+=[bar(n,0,0,W,I//4,'FFD700',15000),bar(n+1,0,H-I//4,W,I//4,'FFD700',15000)]; n+=2
    return ''.join(s)

DECOR_FN = {
    1: slide1_decor, 2: slide2_decor, 3: slide3_decor,
    4: slide4_decor, 5: slide5_decor, 6: slide6_decor,
    7: slide7_decor, 8: slide8_decor, 9: slide9_decor,
}

# ── TRANSITIONS ───────────────────────────────────────────────────────────────
TRANSITIONS = {
    1: ('<p:zoom dir="in"/>',                    'med'),
    2: ('<p:push dir="u"/>',                     'fast'),
    3: ('<p:wipe dir="l"/>',                     'med'),
    4: ('<p:wheel spokes="8"/>',                 'fast'),
    5: ('<p:split dir="vert" orient="out"/>',    'med'),
    6: ('<p:blinds dir="vert"/>',                'fast'),
    7: ('<p:newsflash/>',                        'fast'),
    8: ('<p:circle/>',                           'med'),
    9: ('<p:zoom dir="out"/>',                   'slow'),
}

# ── ANIMATION BUILDER ─────────────────────────────────────────────────────────
ANIM_CFG = {
    1: ('zoom(inCenter)',    'fade',              120, 300, 700),
    2: ('slide(fromLeft)',   'slide(fromRight)',  100, 200, 500),
    3: ('randomBar(horz)',   'randomBar(vert)',    80, 200, 400),
    4: ('zoom(inCenter)',    'dissolve',          100, 300, 600),
    5: ('wipe(left)',        'wipe(right)',        70, 200, 350),
    6: ('slide(fromBottom)', 'slide(fromLeft)',   110, 300, 600),
    7: ('zoom(inCenter)',    'zoom(inCenter)',    120, 250, 600),
    8: ('wipe(left)',        'wipe(right)',        70, 200, 350),
    9: ('zoom(inCenter)',    'dissolve',          150, 500, 800),
}

def get_shape_ids(xml):
    return [int(m) for m in re.findall(r'<p:cNvPr id="(\d+)"', xml) if m != '1']

AUDIO_SID = 499
AUDIO_RID = 'rId99'

audio_pic_xml = (
    f'<p:sp><p:nvSpPr>'
    f'<p:cNvPr id="{AUDIO_SID}" name="bg_audio">'
    f'<a:hlinkClick r:id="{AUDIO_RID}" action="ppaction://media"/>'
    f'</p:cNvPr>'
    f'<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
    f'<p:nvPr><p:cNvMediaPr>'
    f'<a:audioFile r:link="{AUDIO_RID}"/>'
    f'</p:cNvMediaPr></p:nvPr>'
    f'</p:nvSpPr>'
    f'<p:spPr>'
    f'<a:xfrm><a:off x="-914400" y="-914400"/><a:ext cx="457200" cy="457200"/></a:xfrm>'
    f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
    f'<a:solidFill><a:srgbClr val="000000"><a:alpha val="0"/></a:srgbClr></a:solidFill>'
    f'<a:ln><a:noFill/></a:ln>'
    f'</p:spPr></p:sp>'
)

audio_timing_xml = (
    f'<p:par><p:cTn id="900" fill="hold" nodeType="withEffect">'
    f'<p:stCondLst><p:cond delay="0"/></p:stCondLst>'
    f'<p:childTnLst>'
    f'<p:audio isNarration="0">'
    f'<p:cMediaNode vol="80000" mute="0" numSld="9" showWhenStopped="0">'
    f'<p:cTn id="901" fill="hold" nodeType="withEffect"/>'
    f'<p:tgtEl><p:spTgt spid="{AUDIO_SID}"/></p:tgtEl>'
    f'</p:cMediaNode></p:audio>'
    f'</p:childTnLst></p:cTn></p:par>'
)

def make_timing(shape_ids, f1, f2, delay_step, start_delay, anim_dur,
                audio_snippet=None):
    nid=[10]
    def nxt(): v=nid[0]; nid[0]+=1; return v

    animated_ids = [s for s in shape_ids if s != AUDIO_SID]
    shapes_xml=[]; builds_xml=[]

    for i,spid in enumerate(animated_ids):
        filt = f1 if i%2==0 else f2
        rel_dly = i*delay_step
        c1=nxt(); c2=nxt(); c3=nxt()

        shapes_xml.append(
            f'<p:par>'
            f'<p:cTn id="{c1}" presetID="10" presetClass="entr" presetSubtype="0"'
            f' fill="hold" grpId="{i}" nodeType="withEffect">'
            f'<p:stCondLst><p:cond delay="{rel_dly}"/></p:stCondLst>'
            f'<p:childTnLst>'
            f'<p:set><p:cBhvr>'
            f'<p:cTn id="{c2}" dur="1" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'<p:attrNameLst><p:attrName>style.visibility</p:attrName></p:attrNameLst>'
            f'</p:cBhvr><p:to><p:strVal val="visible"/></p:to></p:set>'
            f'<p:animEffect transition="in" filter="{filt}">'
            f'<p:cBhvr><p:cTn id="{c3}" dur="{anim_dur}"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
            f'</p:cBhvr></p:animEffect>'
            f'</p:childTnLst></p:cTn></p:par>'
        )

        # Pulse emphasis on first few content shapes
        if i in (0, 1, 2):
            p1=nxt(); p2=nxt()
            pulse_dly = rel_dly + anim_dur + 80
            shapes_xml.append(
                f'<p:par><p:cTn id="{p1}" presetID="26" presetClass="emph"'
                f' presetSubtype="0" fill="hold" grpId="{i+200}" nodeType="afterEffect">'
                f'<p:stCondLst><p:cond delay="{pulse_dly}"/></p:stCondLst>'
                f'<p:childTnLst><p:animScale>'
                f'<p:by x="112000" y="112000"/>'
                f'<p:cBhvr autoRev="1">'
                f'<p:cTn id="{p2}" dur="200" autoRev="1"/>'
                f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl>'
                f'</p:cBhvr></p:animScale>'
                f'</p:childTnLst></p:cTn></p:par>'
            )

        builds_xml.append(f'<p:bldP spid="{spid}" grpId="{i}" uiExpand="1" build="p"/>')

    audio_part = f'<p:par><p:cTn id="5" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>{audio_snippet}</p:childTnLst></p:cTn></p:par>' if audio_snippet else ''

    return (
        f'<p:timing><p:tnLst><p:par>'
        f'<p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot">'
        f'<p:childTnLst>'
        f'{audio_part}'
        f'<p:par><p:cTn id="2" fill="hold">'
        f'<p:stCondLst><p:cond delay="{start_delay}"/></p:stCondLst>'
        f'<p:childTnLst>{"".join(shapes_xml)}</p:childTnLst>'
        f'</p:cTn></p:par>'
        f'</p:childTnLst></p:cTn>'
        f'</p:par></p:tnLst>'
        f'<p:bldLst>{"".join(builds_xml)}</p:bldLst>'
        f'</p:timing>'
    )

# ── PROCESS EACH SLIDE ────────────────────────────────────────────────────────
for n in range(1, 10):
    sp_path = WORK / f'ppt/slides/slide{n}.xml'
    xml = sp_path.read_text(encoding='utf-8')

    # 1. Inject background decorations right after </p:grpSpPr>
    decor = DECOR_FN[n]()
    xml = xml.replace('</p:grpSpPr>', f'</p:grpSpPr>{decor}', 1)

    # 2. Transitions
    t_xml, t_spd = TRANSITIONS[n]
    trans = f'<p:transition spd="{t_spd}">{t_xml}</p:transition>'

    # 3. Animations (no audio)
    shape_ids = get_shape_ids(xml)
    f1, f2, dstep, sdelay, adur = ANIM_CFG[n]
    timing = make_timing(shape_ids, f1, f2, dstep, sdelay, adur)

    xml = xml.replace('</p:sld>', f'{trans}{timing}</p:sld>')
    sp_path.write_text(xml, encoding='utf-8')

    shape_count = len(get_shape_ids(xml))
    print(f'Slide {n}: {shape_count} total shapes | {t_xml[:22]} | {f1}')

# ── REPACK ────────────────────────────────────────────────────────────────────
# OOXML requires [Content_Types].xml first, then _rels/.rels, then everything
# else. `zip -r` uses filesystem order which puts them in the middle — that
# breaks PowerPoint's package reader. Use Python zipfile for correct ordering.
OUT.unlink(missing_ok=True)
import os
all_files = []
for root, dirs, files in os.walk(WORK):
    dirs.sort()
    for fname in sorted(files):
        full = Path(root) / fname
        arc  = full.relative_to(WORK).as_posix()
        all_files.append((arc, full))

def _sort_key(pair):
    arc = pair[0]
    if arc == '[Content_Types].xml': return (0, arc)
    if arc == '_rels/.rels':         return (1, arc)
    return (2, arc)

all_files.sort(key=_sort_key)

with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zout:
    for arc, full in all_files:
        zout.write(full, arc)

print(f'\nRepack: OK')
print(f'Output: {OUT}  ({OUT.stat().st_size//1024} KB)')
