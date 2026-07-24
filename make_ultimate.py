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
    g_xml = ''
    if glow:
        g_xml = (f'<a:effectLst><a:glow rad="{glow}">'
                 f'<a:srgbClr val="{color}"><a:alpha val="{glow_a}"/></a:srgbClr>'
                 f'</a:glow></a:effectLst>')
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="d{id}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm{rs}>'
            f'<a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/>'
            f'</a:xfrm><a:prstGeom prst="{preset}"><a:avLst/></a:prstGeom>'
            f'{f_xml}{l_xml}{g_xml}</p:spPr></p:sp>')

def dot(id, x, y, size, color, alpha):
    return sp(id,'ellipse', x-size//2, y-size//2, size, size, color, alpha)

def ring(id, x, y, size, color, alpha, lw=30000, glow_rad=150000):
    return sp(id,'ellipse', x-size//2, y-size//2, size, size, color, alpha,
              outline=True, lw=lw, glow=glow_rad, glow_a=min(80000,alpha+30000))

def hex_ring(id, x, y, size, color, alpha, glow_rad=200000):
    return sp(id,'hexagon', x-size//2, y-size//2, size, size, color, alpha,
              outline=True, lw=25400, glow=glow_rad, glow_a=min(80000,alpha+20000))

def orb(id, x, y, size, color, alpha):
    return sp(id,'ellipse', x-size//2, y-size//2, size, size, color, alpha)

def slash(id, cx, cy, length, color, alpha, angle_deg=15):
    rot = angle_deg * 60000
    thick = 18000  # ~0.02 inch thin line
    return sp(id,'rect', cx-length//2, cy-thick//2, length, thick, color, alpha, rot=rot)

def star(id, x, y, size, color, alpha, pts=4):
    preset = f'star{pts}'
    return sp(id, preset, x-size//2, y-size//2, size, size, color, alpha,
              glow=size//3, glow_a=min(80000,alpha+20000))

def half_frame(id, x, y, size, color, alpha, rot=0):
    return sp(id,'halfFrame', x, y, size, size, color, alpha, rot=rot,
              outline=True, lw=38100)

# ── PER-SLIDE DECORATIONS ────────────────────────────────────────────────────
# ID strategy: decorative shapes use 500+ to never conflict with existing shapes

def slide1_decor():
    """Title slide: glow orbs, neon ring, speed slashes, sparkles"""
    s=[]; n=500
    # Atmosphere orbs
    s+=[ orb(n,   W-I,    I,    3*I, '2196F3', 6000), # blue top-right
         orb(n+1, 0,      H,    4*I, 'FF6D00', 5000), # orange bottom-left
         orb(n+2, CX,     CY,   5*I, '00BCD4', 3000), # cyan center
         orb(n+3, W//4,   I,    2*I, '9C27B0', 5000)] # purple top-left
    n+=4
    # Large neon ring behind title
    s+=[ ring(n,   CX, CY-I//2, 7*I, 'FF6D00', 12000, lw=20000, glow_rad=300000),
         ring(n+1, CX, CY-I//2, 5*I, '00BCD4', 8000,  lw=15000, glow_rad=200000)]
    n+=2
    # Hexagon grid
    s+=[ hex_ring(n,   I,      I//2,    2*I,   '2196F3', 10000),
         hex_ring(n+1, W-I,    H-I,     2*I,   'FF6D00', 10000),
         hex_ring(n+2, W//4,   H*3//4,  I,     '00BCD4', 8000),
         hex_ring(n+3, W*3//4, I//2,    I,     'FF6D00', 8000)]
    n+=4
    # Speed slash lines across slide
    for i,(cy2,angle,color,a) in enumerate([
        (I,      12, 'FFFFFF', 8000),
        (I*3//2, 12, '00BCD4', 10000),
        (H-I,   -12, 'FF6D00', 8000),
        (H*3//4,-12, 'FFFFFF', 6000),
    ]):
        s.append(slash(n+i, CX, cy2, 8*I, color, a, angle))
    n+=4
    # Star sparkles
    for i,(x2,y2,sz,c) in enumerate([
        (I//2, H//2, I//2, 'FF6D00'),
        (W-I//2, H//3, I//3, '00BCD4'),
        (W//4, H*3//4, I//3, 'FFFFFF'),
        (W*3//4, H//4, I//2, 'FF6D00'),
    ]):
        s.append(star(n+i, x2, y2, sz, c, 20000, pts=4))
    n+=4
    # Particles
    pts=[(I//2,I//2,'FF6D00',80000),(2*I,I//3,'00BCD4',70000),
         (4*I,I//4,'FFFFFF',50000),(7*I,I//2,'2196F3',80000),
         (I//4,2*I,'00BCD4',60000),(8*I,2*I,'FF6D00',70000),
         (I//2,4*I,'FFFFFF',50000),(5*I,H-I//4,'2196F3',70000),
         (W-I//4,H//2,'00BCD4',60000),(3*I,H-I//3,'FF6D00',60000)]
    for i,(x2,y2,c,a) in enumerate(pts):
        s.append(dot(n+i, x2, y2, 60000+i*6000, c, a))
    return ''.join(s)

def slide2_decor():
    """Ranks: rank-tier colored orbs, hexagons"""
    s=[]; n=520
    # Rank color aura orbs (bronze to SSL)
    rank_colors = ['CD7F32','C0C0C0','FFD700','00BFFF','9C27B0','FF6D00']
    for i,c in enumerate(rank_colors):
        y2 = I//2 + i*(H//6)
        s.append(orb(n+i, I, y2, I, c, 8000))
    n+=6
    # Background atmosphere
    s+=[ orb(n,   W-2*I, I,   3*I, 'FFD700', 5000),
         orb(n+1, W//2,  H,   4*I, '9C27B0', 4000),
         orb(n+2, 0,     H//2, 3*I,'2196F3', 4000)]
    n+=3
    # Hex rings
    s+=[ hex_ring(n,   W*3//4, H//4, 2*I, 'FFD700', 10000),
         hex_ring(n+1, W//4,  H*3//4,2*I, '2196F3', 8000),
         hex_ring(n+2, CX, CY, 4*I, 'FF6D00', 6000)]
    n+=3
    # Stars at top/bottom
    s+=[ star(n,   W-I//2, I//2,  I//2, 'FFD700', 25000, 5),
         star(n+1, W-I,    H-I//2,I//3, 'FFD700', 20000, 6),
         star(n+2, I//2,   H-I//2,I//3, '9C27B0', 15000, 4)]
    n+=3
    # Slash lines
    s+=[ slash(n,   CX, I,   7*I, '00BCD4', 6000, 10),
         slash(n+1, CX, H-I, 7*I, 'FF6D00', 6000,-10)]
    n+=2
    # Particles
    pts=[(2*I,I//3,'FFD700',80000),(5*I,I//4,'C0C0C0',70000),
         (8*I,I//2,'FF6D00',80000),(I//4,H//2,'2196F3',60000),
         (W-I//4,H*3//4,'9C27B0',70000),(4*I,H-I//4,'FFD700',60000)]
    for i,(x2,y2,c,a) in enumerate(pts):
        s.append(dot(n+i, x2, y2, 70000, c, a))
    return ''.join(s)

def slide3_decor():
    """Text/analysis slide: corner brackets, circuit vibes"""
    s=[]; n=540
    # Corner halfFrames
    for i,(x2,y2,rot) in enumerate([
        (0,         0,         0),
        (W-I,       0,         5400000),  # 90°
        (0,         H-I,       16200000), # 270°
        (W-I,       H-I,       10800000), # 180°
    ]):
        s.append(half_frame(n+i, x2, y2, I, '00BCD4', 15000, rot))
    n+=4
    # Atmosphere
    s+=[ orb(n,   CX, CY, 6*I, '2196F3', 4000),
         orb(n+1, W-I, 0,  3*I, 'FF6D00', 5000),
         orb(n+2, 0,   H,  3*I, '00BCD4', 4000)]
    n+=3
    # Hexagons
    s+=[ hex_ring(n,   I,       I,       2*I, '2196F3', 8000),
         hex_ring(n+1, W-I,     H-I,     2*I, 'FF6D00', 8000),
         hex_ring(n+2, CX+2*I,  CY-I,    I,   '00BCD4', 10000)]
    n+=3
    # Cross accent shapes
    s+=[ sp(n,   'cross', CX-I//4, H*3//4-I//4, I//2, I//2, 'FF6D00', 8000),
         sp(n+1, 'cross', W*3//4, I//4, I//3, I//3, '00BCD4', 8000)]
    n+=2
    # Particles
    pts=[(I//2,I//3,'2196F3',70000),(3*I,I//4,'00BCD4',60000),
         (6*I,I//2,'FFFFFF',50000),(8*I,I//3,'FF6D00',60000),
         (I//3,3*I,'00BCD4',60000),(W-I//3,2*I,'2196F3',60000),
         (4*I,H-I//3,'FF6D00',70000),(7*I,H-I//2,'FFFFFF',50000)]
    for i,(x2,y2,c,a) in enumerate(pts):
        s.append(dot(n+i, x2, y2, 60000+i*5000, c, a))
    return ''.join(s)

def slide4_decor():
    """Stats: HUD frames, diamond accents, orange power"""
    s=[]; n=560
    # HUD corner frames
    for i,(x2,y2,rot) in enumerate([
        (0,       0,       0),
        (W-2*I,   0,       5400000),
        (0,       H-2*I,   16200000),
        (W-2*I,   H-2*I,   10800000),
    ]):
        s.append(half_frame(n+i, x2, y2, 2*I, 'FF6D00', 18000, rot))
    n+=4
    # Diamond accents
    for i,(x2,y2,c) in enumerate([
        (I//2,   CY, 'FF6D00'), (W-I//2, CY, 'FF6D00'),
        (CX,     I//2,'00BCD4'),(CX,     H-I//2,'00BCD4'),
    ]):
        s.append(sp(n+i,'diamond',x2-I//4,y2-I//4,I//2,I//2,c,15000))
    n+=4
    # Atmosphere
    s+=[ orb(n,   0,   0,   4*I, 'FF6D00', 6000),
         orb(n+1, W,   H,   4*I, 'FF6D00', 5000),
         orb(n+2, CX,  CY,  3*I, '2196F3', 3000)]
    n+=3
    # Hex grid
    s+=[ hex_ring(n,   I,      I,      2*I, 'FF6D00', 12000),
         hex_ring(n+1, W-I,    H-I,    2*I, 'FF6D00', 12000),
         hex_ring(n+2, CX,     CY,     5*I, 'FF6D00', 5000)]
    n+=3
    # Speed lines
    s+=[ slash(n,   CX, I,   8*I, 'FF6D00', 8000, 8),
         slash(n+1, CX, H-I, 8*I, 'FF6D00', 8000,-8)]
    n+=2
    # Stars
    for i,(x2,y2,sz) in enumerate([
        (I//3,H//3,I//3),(W-I//3,H*2//3,I//3),(W//3,H-I//4,I//4)]):
        s.append(star(n+i, x2, y2, sz, 'FF6D00', 20000, 4))
    n+=3
    # Particles
    pts=[(I//2,I//4,'FF6D00',90000),(3*I,I//3,'FFFFFF',60000),
         (6*I,I//4,'FF6D00',80000),(I//3,2*I,'00BCD4',60000),
         (W-I//3,3*I,'FF6D00',70000),(5*I,H-I//4,'2196F3',60000),
         (8*I,H-I//3,'FF6D00',80000)]
    for i,(x2,y2,c,a) in enumerate(pts):
        s.append(dot(n+i, x2, y2, 65000+i*5000, c, a))
    return ''.join(s)

def slide5_decor():
    """Quick Chat: speech bubble vibes, two-column flair"""
    s=[]; n=580
    # Large speech bubble circles (background)
    s+=[ ring(n,   W//4,   CY, 3*I, '00BCD4', 7000, lw=20000, glow_rad=200000),
         ring(n+1, W*3//4, CY, 3*I, 'FF6D00', 7000, lw=20000, glow_rad=200000)]
    n+=2
    # Large quote mark shapes (low opacity)
    s+=[ sp(n,   'leftBrace', I//4, I//2, I, I*3//2, 'FFFFFF', 8000),
         sp(n+1, 'rightBrace',W-I-I//4, I//2, I, I*3//2, 'FF6D00', 8000)]
    n+=2
    # Atmosphere
    s+=[ orb(n,   0,  CY, 4*I, '00BCD4', 5000),
         orb(n+1, W,  CY, 4*I, 'FF6D00', 5000),
         orb(n+2, CX, 0,  3*I, '9C27B0', 4000)]
    n+=3
    # Hex rings
    s+=[ hex_ring(n,   W//4,  CY,   4*I, '00BCD4', 7000),
         hex_ring(n+1, W*3//4,CY,   4*I, 'FF6D00', 7000),
         hex_ring(n+2, CX,    CY,   6*I, 'FFFFFF', 3000)]
    n+=3
    # Vertical center divider dots
    for i in range(6):
        y2 = I//2 + i*(H//6)
        s.append(dot(n+i, CX, y2, 40000, 'FFFFFF', 10000))
    n+=6
    # Stars
    s+=[ star(n,   I//2,     I//2,  I//3,'00BCD4', 20000,5),
         star(n+1, W-I//2,   H-I//2,I//3,'FF6D00', 20000,5),
         star(n+2, CX,       I//4,  I//4,'FFFFFF', 15000,4)]
    n+=3
    # Particles
    pts=[(I//3,I//3,'00BCD4',80000),(W//4-I//2,I//4,'FFFFFF',60000),
         (W*3//4+I//2,I//4,'FF6D00',70000),(W-I//3,I//3,'FF6D00',80000),
         (I//4,H//2,'2196F3',60000),(W-I//4,H//3,'00BCD4',70000),
         (W//4,H-I//3,'00BCD4',70000),(W*3//4,H-I//3,'FF6D00',70000)]
    for i,(x2,y2,c,a) in enumerate(pts):
        s.append(dot(n+i, x2, y2, 60000, c, a))
    return ''.join(s)

def slide6_decor():
    """5 Stages: stage-number glows, progression arc"""
    s=[]; n=600
    # 5 large stage glow circles — one for each stage area
    stage_colors=['2196F3','00BCD4','FF6D00','FF1744','00E676']
    for i,c in enumerate(stage_colors):
        x2 = I//2 + i*(W//5)
        s.append(orb(n+i, x2, CY, 2*I, c, 6000))
    n+=5
    # Big rings over stage areas
    for i,c in enumerate(['2196F3','00BCD4','FF6D00','FF1744','00E676']):
        x2 = I//2 + i*(W//5)
        s.append(ring(n+i, x2, CY, I, c, 15000, lw=25400, glow_rad=150000))
    n+=5
    # Atmosphere
    s+=[ orb(n,   0,  0,  4*I, '2196F3', 5000),
         orb(n+1, W,  H,  4*I, '00E676', 5000),
         orb(n+2, CX, CY, 6*I, 'FF6D00', 3000)]
    n+=3
    # Hex rings
    s+=[ hex_ring(n,   I,     H//4,  2*I, '2196F3', 10000),
         hex_ring(n+1, W-I,   H*3//4,2*I, '00E676', 10000),
         hex_ring(n+2, CX,    I,     3*I, 'FF6D00', 7000)]
    n+=3
    # Stars
    for i,(x2,y2,c) in enumerate([(I//3,I//3,'00E676'),(W-I//3,I//3,'2196F3'),
                                   (CX,H-I//3,'FF6D00')]):
        s.append(star(n+i, x2, y2, I//3, c, 20000, 5))
    n+=3
    # Slash lines
    s+=[ slash(n,   CX, I//2, 8*I, '00BCD4', 6000, 5),
         slash(n+1, CX, H-I//2,8*I,'FF6D00', 6000,-5)]
    n+=2
    # Particles
    pts=[(I//3,I//4,'2196F3',80000),(W//3,I//4,'00BCD4',70000),
         (W*2//3,I//4,'FF6D00',80000),(W-I//3,I//4,'00E676',70000),
         (I//4,H//2,'2196F3',60000),(W-I//4,H//2,'FF1744',60000),
         (W//3,H-I//3,'00BCD4',70000),(W*2//3,H-I//3,'FF6D00',70000)]
    for i,(x2,y2,c,a) in enumerate(pts):
        s.append(dot(n+i, x2, y2, 70000, c, a))
    return ''.join(s)

def slide7_decor():
    """Gameplay: speed lines everywhere, ball trajectory dots"""
    s=[]; n=620
    # Heavy speed lines
    for i,(cy2,angle,c,a) in enumerate([
        (I,      18, 'FF6D00', 12000),
        (I*3//2, 18, '00BCD4', 10000),
        (I*5//2, 15, 'FFFFFF', 8000),
        (H-I,   -18, 'FF6D00', 12000),
        (H-I*2, -15, '00BCD4', 8000),
        (CY,     20, '2196F3', 6000),
    ]):
        s.append(slash(n+i, CX, cy2, 9*I, c, a, angle))
    n+=6
    # Ball trajectory dots (arc-like)
    for i in range(8):
        t = i/7
        x2 = int(I + t*(W-2*I))
        y2 = int(CY - I*math.sin(math.pi*t)*2)
        s.append(dot(n+i, x2, y2, 80000+i*10000, 'FF6D00', 15000+i*2000))
    n+=8
    # Atmosphere
    s+=[ orb(n,   0,  CY, 5*I, 'FF6D00', 7000),
         orb(n+1, W,  CY, 5*I, '2196F3', 6000),
         orb(n+2, CX, CY, 4*I, 'FFFFFF', 2000)]
    n+=3
    # Hex rings
    s+=[ hex_ring(n,   I,   I,   2*I, 'FF6D00', 12000),
         hex_ring(n+1, W-I, H-I, 2*I, '2196F3', 12000),
         hex_ring(n+2, CX,  CY,  6*I, 'FF6D00', 5000)]
    n+=3
    # Arrows
    s+=[ sp(n,   'rightArrow', I,      CY-I//4, 3*I, I//2, 'FF6D00', 12000),
         sp(n+1, 'leftArrow',  W-3*I,  CY-I//4, 3*I, I//2, '2196F3', 12000)]
    n+=2
    # Stars
    for i,(x2,y2,sz,c) in enumerate([(I//3,I//3,I//2,'FF6D00'),
                                      (W-I//3,I//3,I//3,'00BCD4'),
                                      (W-I//3,H-I//3,I//2,'FF6D00')]):
        s.append(star(n+i,x2,y2,sz,c,25000,4))
    n+=3
    # Extra particles
    pts=[(I//2,I//4,'FF6D00',90000),(3*I,I//3,'FFFFFF',70000),
         (7*I,I//3,'2196F3',80000),(I//3,H//3,'00BCD4',70000),
         (W-I//3,H*2//3,'FF6D00',80000),(5*I,H-I//4,'2196F3',70000)]
    for i,(x2,y2,c,a) in enumerate(pts):
        s.append(dot(n+i,x2,y2,70000,c,a))
    return ''.join(s)

def slide8_decor():
    """Scouting Report: radar rings, HUD frames, tech grid"""
    s=[]; n=640
    # Radar concentric rings
    for i,sz in enumerate([6*I, 4*I, 2*I, I]):
        a = 6000 + i*3000
        s.append(ring(n+i, CX+2*I, CY, sz, 'FF6D00', a, lw=15000, glow_rad=100000))
    n+=4
    # Target crosshair lines (thin long rectangles)
    s+=[ sp(n,   'rect', I,    CY-8000, W-2*I, 16000, 'FF6D00', 8000),  # horizontal
         sp(n+1, 'rect', CX+2*I-8000, I, 16000, H-2*I,'FF6D00', 8000)]  # vertical
    n+=2
    # HUD corner frames
    for i,(x2,y2,rot) in enumerate([
        (0, 0, 0),(W-2*I, 0, 5400000),
        (0, H-2*I, 16200000),(W-2*I, H-2*I, 10800000)]):
        s.append(half_frame(n+i, x2, y2, 2*I, '00BCD4', 15000, rot))
    n+=4
    # Atmosphere
    s+=[ orb(n,   CX+2*I,  CY,  5*I, 'FF6D00', 5000),
         orb(n+1, 0,        0,   4*I, '2196F3', 5000),
         orb(n+2, W,        H,   4*I, 'FF6D00', 4000)]
    n+=3
    # Hex rings
    s+=[ hex_ring(n,   I,     I,     2*I, '00BCD4', 10000),
         hex_ring(n+1, W-I,   H-I,   2*I, 'FF6D00', 10000)]
    n+=2
    # Diamond accents on stat labels side
    for i in range(4):
        y2 = I + i*(H//4)
        s.append(sp(n+i,'diamond', I//4, y2, I//4, I//4, 'FF6D00', 12000))
    n+=4
    # Stars
    for i,(x2,y2,c) in enumerate([(I//3,H-I//3,'FF6D00'),(W*3//4,I//3,'00BCD4')]):
        s.append(star(n+i,x2,y2,I//3,c,20000,5))
    n+=2
    # Particles
    pts=[(I//3,I//4,'00BCD4',80000),(3*I,I//3,'FF6D00',70000),
         (8*I,I//3,'FFFFFF',60000),(I//3,3*I,'2196F3',70000),
         (W-I//3,2*I,'FF6D00',80000),(5*I,H-I//4,'00BCD4',70000),
         (7*I,H-I//3,'FF6D00',80000)]
    for i,(x2,y2,c,a) in enumerate(pts):
        s.append(dot(n+i,x2,y2,65000,c,a))
    return ''.join(s)

def slide9_decor():
    """Congrats: MAXIMUM celebration — confetti, burst, stars"""
    s=[]; n=660
    # Burst rays from center-ish
    burst_cx, burst_cy = CX, CY-I//2
    for i in range(12):
        angle = i * 30
        rad = angle * 60000
        s.append(sp(n+i,'rect', burst_cx-I*3//2, burst_cy-10000,
                    3*I, 20000, 'FF6D00', 12000+i*1500, rot=rad))
    n+=12
    # More burst rays in cyan
    for i in range(8):
        angle = i*45 + 22
        rad = angle * 60000
        s.append(sp(n+i,'rect', burst_cx-I, burst_cy-8000,
                    2*I, 16000, '00BCD4', 10000+i*1500, rot=rad))
    n+=8
    # Confetti scatter — many tiny colored rectangles
    confetti=[
        (I,    I//2,   'FF6D00',800000), (2*I, I//3,  '00BCD4',900000),
        (3*I,  I//4,   'FFD700',800000), (4*I, I//2,  'FF1744',900000),
        (5*I,  I//3,   '00E676',800000), (6*I, I//4,  '9C27B0',900000),
        (7*I,  I//2,   'FF6D00',800000), (8*I, I//3,  '00BCD4',900000),
        (I//2, H//3,   'FFD700',800000), (I//4, 2*I,  'FF1744',900000),
        (W-I//2,H//3,  '00E676',800000), (W-I//4,2*I,'9C27B0',900000),
        (2*I,  H*3//4, 'FF6D00',800000), (4*I, H*3//4,'FFD700',900000),
        (6*I,  H*3//4, '00BCD4',800000), (8*I, H*3//4,'FF1744',900000),
        (I//2, H-I//3, '00E676',800000), (W-I//2,H-I//3,'9C27B0',900000),
        (3*I,  H-I//4, 'FF6D00',800000), (7*I, H-I//4,'00BCD4',900000),
    ]
    for i,(x2,y2,c,a) in enumerate(confetti):
        rot = (i*37*60000) % 21600000
        s.append(sp(n+i,'rect', x2, y2, 80000+i*5000, 40000, c, 70000, rot=rot))
    n+=len(confetti)
    # Celebration stars
    for i,(x2,y2,sz,c,pts) in enumerate([
        (I//2,    I//2,    I//2, 'FFD700', 5),
        (W-I//2,  I//2,    I//2, 'FFD700', 5),
        (I//2,    H-I//2,  I//2, 'FF6D00', 4),
        (W-I//2,  H-I//2,  I//2, 'FF6D00', 4),
        (CX,      I//3,    I,    'FFD700', 6),
        (W//4,    H//4,    I//2, '00BCD4', 5),
        (W*3//4,  H//4,    I//2, '00E676', 5),
        (W//4,    H*3//4,  I//3, 'FF1744', 4),
        (W*3//4,  H*3//4,  I//3, '9C27B0', 4),
    ]):
        s.append(star(n+i, x2, y2, sz, c, 35000, pts))
    n+=9
    # Atmosphere orbs
    s+=[ orb(n,   CX,     CY,   6*I, 'FFD700', 5000),
         orb(n+1, I//2,   I//2, 3*I, 'FF6D00', 6000),
         orb(n+2, W-I//2, I//2, 3*I, '00BCD4', 6000),
         orb(n+3, CX,     H,    4*I, '9C27B0', 5000)]
    n+=4
    # Hex rings
    s+=[ hex_ring(n,   CX-I, CY,  4*I, 'FFD700', 12000, glow_rad=300000),
         hex_ring(n+1, I,    I,   2*I, 'FF6D00', 10000),
         hex_ring(n+2, W-I,  H-I, 2*I, '00BCD4', 10000)]
    n+=3
    # Slash lines
    s+=[ slash(n,   CX, I,   8*I, 'FFD700', 10000, 15),
         slash(n+1, CX, H-I, 8*I, 'FFD700', 10000,-15)]
    n+=2
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
    3: ('<p:strips dir="lu"/>',                  'med'),
    4: ('<p:wheel spokes="8"/>',                 'fast'),
    5: ('<p:split dir="vert" orient="out"/>',    'med'),
    6: ('<p:checker dir="horz"/>',               'fast'),
    7: ('<p:newsflash/>',                        'fast'),
    8: ('<p:diamond/>',                          'med'),
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

    # 2. On slide 1: inject hidden audio shape + audio relationship
    if n == 1:
        xml = xml.replace('</p:spTree>', f'{audio_pic_xml}</p:spTree>', 1)
        rels_path = WORK / 'ppt/slides/_rels/slide1.xml.rels'
        rels = rels_path.read_text(encoding='utf-8')
        AUDIO_TYPE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/audio'
        if AUDIO_RID not in rels:
            rels = rels.replace('</Relationships>',
                f'<Relationship Id="{AUDIO_RID}" Type="{AUDIO_TYPE}" Target="../media/audio1.wav"/></Relationships>')
            rels_path.write_text(rels, encoding='utf-8')

    # 3. Transitions
    t_xml, t_spd = TRANSITIONS[n]
    trans = f'<p:transition spd="{t_spd}">{t_xml}</p:transition>'

    # 4. Animations
    shape_ids = get_shape_ids(xml)
    f1, f2, dstep, sdelay, adur = ANIM_CFG[n]
    audio_snip = audio_timing_xml if n == 1 else None
    timing = make_timing(shape_ids, f1, f2, dstep, sdelay, adur, audio_snip)

    xml = xml.replace('</p:sld>', f'{trans}{timing}</p:sld>')
    sp_path.write_text(xml, encoding='utf-8')

    shape_count = len(get_shape_ids(xml))
    print(f'Slide {n}: {shape_count} total shapes | {t_xml[:22]} | {f1}')

# ── REPACK ────────────────────────────────────────────────────────────────────
OUT.unlink(missing_ok=True)
res = subprocess.run(['zip','-Xr',str(OUT.resolve()),'.'], cwd=str(WORK),
                     capture_output=True, text=True)
print(f'\nRepack: {res.returncode}')
print(f'Output: {OUT}  ({OUT.stat().st_size//1024} KB)')
