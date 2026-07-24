#!/usr/bin/env python3
"""
Final version — built on exactly what opened on iOS:
- same shape types as rl_test_anims (ellipse, rect, diamond only)
- same animation structure (no pulse, fade/slide/wipe filters)
- same safe transitions
- 9 unique visual themes per slide
"""
import zipfile, shutil, re, os
from pathlib import Path

SRC  = Path('rl_bachelor.pptx')
OUT  = Path('rl_bachelor_extra.pptx')
WORK = Path('/tmp/pptx_final')
shutil.rmtree(WORK, ignore_errors=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)

W=9144000; H=5143500; CX=W//2; CY=H//2

def sp(id, preset, x, y, cx, cy, color, alpha, outline=False, lw=25400):
    if outline:
        f_xml='<a:noFill/>'
        l_xml=f'<a:ln w="{lw}"><a:solidFill><a:srgbClr val="{color}"><a:alpha val="{alpha}"/></a:srgbClr></a:solidFill></a:ln>'
    else:
        f_xml=f'<a:solidFill><a:srgbClr val="{color}"><a:alpha val="{alpha}"/></a:srgbClr></a:solidFill>'
        l_xml='<a:ln><a:noFill/></a:ln>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="d{id}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/>'
            f'</a:xfrm><a:prstGeom prst="{preset}"><a:avLst/></a:prstGeom>'
            f'{f_xml}{l_xml}</p:spPr></p:sp>')

def orb(id, x, y, sz, c, a):  return sp(id,'ellipse',max(0,x-sz//2),max(0,y-sz//2),sz,sz,c,a)
def ring(id, x, y, sz, c, a, lw=25400): return sp(id,'ellipse',max(0,x-sz//2),max(0,y-sz//2),sz,sz,c,a,outline=True,lw=lw)
def bar(id, x, y, w2, h2, c, a): return sp(id,'rect',x,y,w2,h2,c,a)
def dmd(id, x, y, sz, c, a):  return sp(id,'diamond',max(0,x-sz//2),max(0,y-sz//2),sz,sz,c,a)
def dot(id, x, y, sz, c, a):  return sp(id,'ellipse',max(0,x-sz//2),max(0,y-sz//2),sz,sz,c,a)

# Each slide gets ~14 unique decorative shapes (matching rl_test_anims shape count)
def make_decor(slide, c1, c2, c3):
    s=[]; n=500
    if slide == 1:  # Title — big center rings, corner orbs, speed bars
        s += [ring(n,CX,CY,7000000,c1,5000,lw=40000), ring(n+1,CX,CY,5000000,c2,4000,lw=30000), ring(n+2,CX,CY,3000000,c3,3000,lw=20000)]; n+=3
        s += [orb(n,0,0,3000000,c1,5000), orb(n+1,W,0,3000000,c2,4000), orb(n+2,0,H,3000000,c3,4000), orb(n+3,W,H,3000000,c1,4000)]; n+=4
        s += [bar(n,0,0,W,60000,c1,20000), bar(n+1,0,H-60000,W,60000,c2,20000)]; n+=2
        s += [dmd(n,CX-400000,50000,500000,c3,15000), dmd(n+1,CX-400000,H-550000,500000,c1,15000)]; n+=2
        s += [dot(n,500000,CY,200000,c2,30000), dot(n+1,W-500000,CY,200000,c2,30000), dot(n+2,CX,300000,150000,c3,25000)]; n+=3
    elif slide == 2:  # Ranks — vertical rank orbs, gold accents
        for i,c in enumerate(['CD7F32','C0C0C0','FFD700','00BFFF','9C27B0','FF6D00']):
            s.append(orb(n,700000,500000+i*750000,600000,c,8000)); n+=1
        s += [ring(n,W*3//4,CY,3000000,'FFD700',6000,lw=35000), orb(n+1,W-500000,0,2500000,'FFD700',4000)]; n+=2
        s += [bar(n,0,0,W,50000,'FFD700',12000), bar(n+1,0,H-50000,W,50000,'FFD700',12000)]; n+=2
        s += [dmd(n,W-600000,H//2,400000,'FFD700',20000), dmd(n+1,W-600000,H//4,300000,c2,15000), dmd(n+2,W-600000,H*3//4,300000,c3,15000)]; n+=3
        s += [dot(n,CX,100000,150000,'FFD700',20000)]; n+=1
    elif slide == 3:  # Text — corner brackets, blue circuit
        for x2,y2 in [(0,0),(W-900000,0),(0,H-90000),(W-900000,H-90000)]:
            s.append(bar(n,x2,y2,900000,90000,c1,18000)); n+=1
        for x2,y2 in [(0,0),(W-90000,0),(0,H-900000),(W-90000,H-900000)]:
            s.append(bar(n,x2,y2,90000,900000,c1,18000)); n+=1
        s += [orb(n,CX,CY,6000000,c2,3000), ring(n+1,CX,CY,4000000,c1,4000,lw=20000)]; n+=2
        s += [bar(n,0,CY-30000,W,60000,c3,5000)]; n+=1
        s += [dmd(n,300000,300000,300000,c1,15000), dmd(n+1,W-300000,H-300000,300000,c2,15000)]; n+=2
    elif slide == 4:  # Stats — orange power grid, HUD corners
        for x2,y2 in [(0,0),(W-800000,0),(0,H-80000),(W-800000,H-80000)]:
            s.append(bar(n,x2,y2,800000,80000,c1,20000)); n+=1
        for x2,y2 in [(0,0),(W-80000,0),(0,H-800000),(W-80000,H-800000)]:
            s.append(bar(n,x2,y2,80000,800000,c1,20000)); n+=1
        s += [orb(n,CX,CY,5000000,c1,4000), ring(n+1,CX,CY,7000000,c1,3000,lw=15000)]; n+=2
        s += [bar(n,0,CY-25000,W,50000,c1,6000)]; n+=1
        s += [dmd(n,300000,CY,400000,c1,18000), dmd(n+1,W-300000,CY,400000,c1,18000), dmd(n+2,CX,200000,350000,c3,15000)]; n+=3
    elif slide == 5:  # Quick Chat — dual rings, center divider
        s += [ring(n,W//4,CY,3500000,c1,7000,lw=35000), ring(n+1,W*3//4,CY,3500000,c2,7000,lw=35000)]; n+=2
        s += [ring(n,W//4,CY,5000000,c1,3000,lw=15000), ring(n+1,W*3//4,CY,5000000,c2,3000,lw=15000)]; n+=2
        s += [orb(n,0,CY,4000000,c1,4000), orb(n+1,W,CY,4000000,c2,4000)]; n+=2
        for i in range(5):
            s.append(dot(n,CX,500000+i*1000000,80000,'FFFFFF',8000)); n+=1
        s += [bar(n,0,0,W,50000,c3,10000), bar(n+1,0,H-50000,W,50000,c3,10000)]; n+=2
        s += [dmd(n,300000,300000,300000,c1,20000), dmd(n+1,W-300000,H-300000,300000,c2,20000)]; n+=2
    elif slide == 6:  # 5 Stages — 5 column rings
        stage_colors=['2196F3','00BCD4','FF6D00','FF1744','00E676']
        for i,sc in enumerate(stage_colors):
            x2=700000+i*(W//5)
            s.append(orb(n,x2,CY,1800000,sc,6000)); n+=1
            s.append(ring(n,x2,CY,2500000,sc,4000,lw=20000)); n+=1
        s += [bar(n,0,0,W,50000,c1,12000), bar(n+1,0,H-50000,W,50000,c3,12000)]; n+=2
        s += [orb(n,0,0,3000000,c1,4000), orb(n+1,W,H,3000000,c3,4000)]; n+=2
    elif slide == 7:  # Gameplay — speed lines, trajectory dots
        for i,y2 in enumerate([300000,600000,H-600000,H-300000]):
            s.append(bar(n,0,y2,W,30000,'FF6D00' if i<2 else '00BCD4',8000)); n+=1
        for i in range(7):
            t=i/6; x2=int(700000+t*(W-1400000)); y2=int(CY-1500000*(4*t*(1-t)))
            s.append(dot(n,x2,y2,120000+i*20000,'FF6D00',15000+i*3000)); n+=1
        s += [orb(n,0,CY,4000000,c1,5000), orb(n+1,W,CY,4000000,c2,5000)]; n+=2
        s += [ring(n,CX,CY,6000000,c1,3000,lw=15000)]; n+=1
        s += [dmd(n,300000,300000,400000,c1,20000), dmd(n+1,W-300000,H-300000,400000,c2,20000)]; n+=2
    elif slide == 8:  # Scouting — radar rings + crosshair
        for i,sz in enumerate([6000000,4500000,3000000,1500000]):
            s.append(ring(n,W*3//5,CY,sz,c1,5000+i*2000,lw=15000+i*5000)); n+=1
        s += [bar(n,500000,CY-25000,W-1000000,50000,c1,8000), bar(n+1,W*3//5-25000,300000,50000,H-600000,c1,8000)]; n+=2
        for x2,y2 in [(0,0),(W-800000,0),(0,H-80000),(W-800000,H-80000)]:
            s.append(bar(n,x2,y2,800000,80000,c3,15000)); n+=1
        for x2,y2 in [(0,0),(W-80000,0),(0,H-800000),(W-80000,H-800000)]:
            s.append(bar(n,x2,y2,80000,800000,c3,15000)); n+=1
        s += [orb(n,0,0,3000000,c2,4000), orb(n+1,W*3//5,CY,4000000,c1,3000)]; n+=2
    else:  # slide 9 — confetti, diamonds, celebration rings
        confetti=[('FF6D00',700000,300000),('00BCD4',1600000,200000),('FFD700',2500000,150000),('FF1744',3400000,300000),('00E676',4300000,200000),('9C27B0',5200000,150000),('FF6D00',6100000,300000),('00BCD4',7000000,200000),('FFD700',700000,H-400000),('FF1744',2500000,H-350000),('00E676',4300000,H-400000),('9C27B0',6500000,H-350000)]
        for c,x2,y2 in confetti:
            s.append(bar(n,x2,y2,350000,120000,c,70000)); n+=1
        for i,sz in enumerate([7000000,5000000,3000000]):
            s.append(ring(n,CX,CY-500000,sz,'FFD700',4000+i*3000,lw=20000+i*8000)); n+=1
        s += [dmd(n,300000,300000,500000,'FFD700',30000), dmd(n+1,W-300000,300000,500000,'FFD700',30000), dmd(n+2,300000,H-300000,500000,'FF6D00',30000), dmd(n+3,W-300000,H-300000,500000,'FF6D00',30000), dmd(n+4,CX,150000,700000,'FFD700',25000)]; n+=5
        s += [bar(n,0,0,W,60000,'FFD700',20000), bar(n+1,0,H-60000,W,60000,'FFD700',20000)]; n+=2
    return ''.join(s)

SLIDE_COLORS = {
    1:('FF6D00','2196F3','00BCD4'), 2:('FFD700','2196F3','9C27B0'),
    3:('2196F3','00BCD4','FF6D00'), 4:('FF6D00','00BCD4','FFFFFF'),
    5:('00BCD4','FF6D00','9C27B0'), 6:('2196F3','FF6D00','00E676'),
    7:('FF6D00','2196F3','00BCD4'), 8:('FF6D00','00BCD4','2196F3'),
    9:('FFD700','FF6D00','00BCD4'),
}
TRANSITIONS = {
    1:('<p:zoom dir="in"/>','med'),   2:('<p:push dir="u"/>','fast'),
    3:('<p:wipe dir="l"/>','med'),    4:('<p:wheel spokes="4"/>','fast'),
    5:('<p:split dir="horz" orient="out"/>','med'), 6:('<p:blinds dir="vert"/>','fast'),
    7:('<p:newsflash/>','fast'),      8:('<p:circle/>','med'),
    9:('<p:zoom dir="out"/>','slow'),
}
# Animation filters — only those confirmed working in rl_test_anims
ANIM_CFG = {
    1:('fade','fade',110,300,600),   2:('fade','fade',100,200,500),
    3:('fade','fade', 80,200,400),   4:('fade','fade',100,300,600),
    5:('fade','fade', 70,200,350),   6:('fade','fade',110,300,600),
    7:('fade','fade',110,250,600),   8:('fade','fade', 70,200,350),
    9:('fade','fade',130,400,700),
}

def get_shape_ids(xml):
    return [int(m) for m in re.findall(r'<p:cNvPr id="(\d+)"', xml) if m != '1']

# Exact same make_timing as rl_test_anims.py — the version that opened on iOS
def make_timing(shape_ids, f1, f2, delay_step, start_delay, anim_dur):
    if not shape_ids:
        return '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot"/></p:par></p:tnLst><p:bldLst/></p:timing>'
    nid=[3]
    def nxt(): v=nid[0]; nid[0]+=1; return v
    shapes_xml=[]; builds_xml=[]
    for i,spid in enumerate(shape_ids):
        filt=f1 if i%2==0 else f2
        rel_dly=i*delay_step
        ctn_id=nxt(); set_id=nxt(); anim_id=nxt()
        shapes_xml.append(
            f'<p:par><p:cTn id="{ctn_id}" presetID="10" presetClass="entr" presetSubtype="0"'
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
    return (
        f'<p:timing><p:tnLst><p:par>'
        f'<p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot">'
        f'<p:childTnLst>'
        f'<p:par><p:cTn id="2" fill="hold">'
        f'<p:stCondLst><p:cond delay="{start_delay}"/></p:stCondLst>'
        f'<p:childTnLst>{"".join(shapes_xml)}</p:childTnLst>'
        f'</p:cTn></p:par>'
        f'</p:childTnLst></p:cTn>'
        f'</p:par></p:tnLst>'
        f'<p:bldLst>{"".join(builds_xml)}</p:bldLst>'
        f'</p:timing>'
    )

for n in range(1, 10):
    p = WORK/f'ppt/slides/slide{n}.xml'
    xml = p.read_text(encoding='utf-8')
    c1,c2,c3 = SLIDE_COLORS[n]
    decor = make_decor(n, c1, c2, c3)
    xml = xml.replace('</p:grpSpPr>', f'</p:grpSpPr>{decor}', 1)
    shape_ids = get_shape_ids(xml)
    t_inner,spd = TRANSITIONS[n]
    f1,f2,dstep,sdelay,adur = ANIM_CFG[n]
    timing = make_timing(shape_ids, f1, f2, dstep, sdelay, adur)
    xml = xml.replace('</p:sld>', f'<p:transition spd="{spd}">{t_inner}</p:transition>{timing}</p:sld>')
    p.write_text(xml, encoding='utf-8')
    print(f'slide{n}: {len(shape_ids)} shapes')

OUT.unlink(missing_ok=True)
all_files=[]
for root,dirs,files in os.walk(WORK):
    dirs.sort()
    for f in sorted(files):
        full=Path(root)/f; arc=full.relative_to(WORK).as_posix()
        all_files.append((arc,full))
def key(p): return (0,p[0]) if p[0]=='[Content_Types].xml' else (1,p[0]) if p[0]=='_rels/.rels' else (2,p[0])
all_files.sort(key=key)
with zipfile.ZipFile(OUT,'w',zipfile.ZIP_DEFLATED) as zout:
    for arc,full in all_files: zout.write(full,arc)
print('Done:', OUT.stat().st_size//1024, 'KB')
