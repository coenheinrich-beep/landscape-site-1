#!/usr/bin/env python3
"""
Built on the EXACT code that opened on iOS (test_anims.py):
- same sp() function, same make_timing(), same injection point
- same safe transitions + fade animations
- enhanced decor_per_slide() with per-slide themes but proven-safe patterns
"""
import zipfile, shutil, re, os
from pathlib import Path

SRC  = Path('/home/user/landscape-site-1/rl_bachelor.pptx')
OUT  = Path('/home/user/landscape-site-1/rl_bachelor_extra.pptx')
WORK = Path('/tmp/pptx_final')
shutil.rmtree(WORK, ignore_errors=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)

W=9144000; H=5143500; CX=W//2; CY=H//2

# EXACT sp() from test_anims.py (the version confirmed to open on iOS)
def sp(id, preset, x, y, cx, cy, color, alpha, rot=0, outline=False, lw=25400):
    rs = f' rot="{rot}"' if rot else ''
    if outline:
        f_xml = '<a:noFill/>'
        l_xml = f'<a:ln w="{lw}"><a:solidFill><a:srgbClr val="{color}"><a:alpha val="{alpha}"/></a:srgbClr></a:solidFill></a:ln>'
    else:
        f_xml = f'<a:solidFill><a:srgbClr val="{color}"><a:alpha val="{alpha}"/></a:srgbClr></a:solidFill>'
        l_xml = '<a:ln><a:noFill/></a:ln>'
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{id}" name="d{id}"/>'
            f'<p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm{rs}><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/>'
            f'</a:xfrm><a:prstGeom prst="{preset}"><a:avLst/></a:prstGeom>'
            f'{f_xml}{l_xml}</p:spPr></p:sp>')

# Per-slide decorations — every shape uses sp() directly with literal coords (no helpers)
# All coords manually verified >= 0, all IDs sequential from 500
def decor(slide, c1, c2, c3):
    s = []; n = 500
    if slide == 1:  # Title — large rings + corner dots + bars
        s.append(sp(n,'ellipse',CX-600000,CY-600000,1200000,1200000,c1,6000,outline=True,lw=38100)); n+=1
        s.append(sp(n,'ellipse',CX-1200000,CY-1200000,2400000,2400000,c2,4000,outline=True,lw=25400)); n+=1
        s.append(sp(n,'ellipse',CX-2000000,CY-2000000,4000000,4000000,c3,2000,outline=True,lw=15000)); n+=1
        s.append(sp(n,'rect',0,0,W,H//8,c1,5000)); n+=1
        s.append(sp(n,'rect',0,H-H//8,W,H//8,c2,5000)); n+=1
        for i in range(6):
            s.append(sp(n,'ellipse',int(W*i/6),int(H*0.08),180000,180000,c3,10000)); n+=1
        for i in range(6):
            s.append(sp(n,'ellipse',int(W*i/6+W//12),int(H*0.87),140000,140000,c1,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,10000,600000,300000,c3,12000)); n+=1
        s.append(sp(n,'diamond',CX-300000,H-310000,600000,300000,c2,12000)); n+=1
    elif slide == 2:  # Ranks — rings + accent bars + diamonds
        s.append(sp(n,'ellipse',CX-500000,CY-500000,1000000,1000000,c1,8000,outline=True,lw=38100)); n+=1
        s.append(sp(n,'ellipse',CX-1000000,CY-1000000,2000000,2000000,'FFD700',5000,outline=True,lw=25400)); n+=1
        s.append(sp(n,'rect',0,0,W,H//10,'FFD700',8000)); n+=1
        s.append(sp(n,'rect',0,H-H//10,W,H//10,c2,8000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5),int(H*0.1),200000,200000,'FFD700',10000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5+W//10),int(H*0.85),160000,160000,c3,10000)); n+=1
        s.append(sp(n,'diamond',CX-350000,15000,700000,350000,'FFD700',15000)); n+=1
        s.append(sp(n,'diamond',CX-350000,H-365000,700000,350000,c1,15000)); n+=1
    elif slide == 3:  # Stats — corner brackets + central ring
        s.append(sp(n,'ellipse',CX-700000,CY-700000,1400000,1400000,c1,6000,outline=True,lw=38100)); n+=1
        s.append(sp(n,'ellipse',CX-1300000,CY-1300000,2600000,2600000,c2,3000,outline=True,lw=20000)); n+=1
        s.append(sp(n,'rect',0,0,W,H//8,c1,5000)); n+=1
        s.append(sp(n,'rect',0,H-H//8,W,H//8,c3,5000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5),int(H*0.1),200000,200000,c2,8000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5+W//10),int(H*0.85),150000,150000,c1,8000)); n+=1
        s.append(sp(n,'diamond',CX-300000,10000,600000,300000,c3,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,H-310000,600000,300000,c2,10000)); n+=1
    elif slide == 4:  # Quick Chat — wider rings + colored dots
        s.append(sp(n,'ellipse',CX-600000,CY-600000,1200000,1200000,'FF6D00',7000,outline=True,lw=40000)); n+=1
        s.append(sp(n,'ellipse',CX-1100000,CY-1100000,2200000,2200000,c2,4000,outline=True,lw=25400)); n+=1
        s.append(sp(n,'rect',0,0,W,H//8,'FF6D00',6000)); n+=1
        s.append(sp(n,'rect',0,H-H//8,W,H//8,c3,6000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5),int(H*0.1),200000,200000,'FF6D00',10000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5+W//10),int(H*0.85),150000,150000,c1,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,10000,600000,300000,c3,12000)); n+=1
        s.append(sp(n,'diamond',CX-300000,H-310000,600000,300000,'FF6D00',12000)); n+=1
    elif slide == 5:  # Gameplay — speed bar rings + cyan dots
        s.append(sp(n,'ellipse',CX-600000,CY-600000,1200000,1200000,'00BCD4',7000,outline=True,lw=38100)); n+=1
        s.append(sp(n,'ellipse',CX-1200000,CY-1200000,2400000,2400000,c2,4000,outline=True,lw=25400)); n+=1
        s.append(sp(n,'rect',0,0,W,H//8,'00BCD4',5000)); n+=1
        s.append(sp(n,'rect',0,H-H//8,W,H//8,c3,5000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5),int(H*0.1),200000,200000,'00BCD4',10000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5+W//10),int(H*0.85),150000,150000,c1,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,10000,600000,300000,c3,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,H-310000,600000,300000,'00BCD4',10000)); n+=1
    elif slide == 6:  # Stages — purple + blue theme
        s.append(sp(n,'ellipse',CX-600000,CY-600000,1200000,1200000,'9C27B0',6000,outline=True,lw=38100)); n+=1
        s.append(sp(n,'ellipse',CX-1100000,CY-1100000,2200000,2200000,c2,3000,outline=True,lw=20000)); n+=1
        s.append(sp(n,'rect',0,0,W,H//8,'9C27B0',5000)); n+=1
        s.append(sp(n,'rect',0,H-H//8,W,H//8,c3,5000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5),int(H*0.1),200000,200000,'9C27B0',10000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5+W//10),int(H*0.85),150000,150000,c1,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,10000,600000,300000,c3,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,H-310000,600000,300000,'9C27B0',10000)); n+=1
    elif slide == 7:  # Scouting — green accent rings
        s.append(sp(n,'ellipse',CX-600000,CY-600000,1200000,1200000,'00E676',7000,outline=True,lw=38100)); n+=1
        s.append(sp(n,'ellipse',CX-1200000,CY-1200000,2400000,2400000,c2,4000,outline=True,lw=25400)); n+=1
        s.append(sp(n,'rect',0,0,W,H//8,'00E676',5000)); n+=1
        s.append(sp(n,'rect',0,H-H//8,W,H//8,c3,5000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5),int(H*0.1),200000,200000,'00E676',10000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5+W//10),int(H*0.85),150000,150000,c1,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,10000,600000,300000,c3,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,H-310000,600000,300000,'00E676',10000)); n+=1
    elif slide == 8:  # Roast/Fails — red accent rings
        s.append(sp(n,'ellipse',CX-600000,CY-600000,1200000,1200000,'FF1744',7000,outline=True,lw=38100)); n+=1
        s.append(sp(n,'ellipse',CX-1200000,CY-1200000,2400000,2400000,c2,4000,outline=True,lw=25400)); n+=1
        s.append(sp(n,'rect',0,0,W,H//8,'FF1744',5000)); n+=1
        s.append(sp(n,'rect',0,H-H//8,W,H//8,c3,5000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5),int(H*0.1),200000,200000,'FF1744',10000)); n+=1
        for i in range(5):
            s.append(sp(n,'ellipse',int(W*i/5+W//10),int(H*0.85),150000,150000,c1,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,10000,600000,300000,c3,10000)); n+=1
        s.append(sp(n,'diamond',CX-300000,H-310000,600000,300000,'FF1744',10000)); n+=1
    else:  # slide 9 — gold celebration rings + diamonds
        s.append(sp(n,'ellipse',CX-600000,CY-600000,1200000,1200000,'FFD700',8000,outline=True,lw=40000)); n+=1
        s.append(sp(n,'ellipse',CX-1200000,CY-1200000,2400000,2400000,'FFD700',5000,outline=True,lw=28000)); n+=1
        s.append(sp(n,'ellipse',CX-1800000,CY-1800000,3600000,3600000,'FFD700',3000,outline=True,lw=18000)); n+=1
        s.append(sp(n,'rect',0,0,W,H//8,'FFD700',8000)); n+=1
        s.append(sp(n,'rect',0,H-H//8,W,H//8,'FF6D00',8000)); n+=1
        for i in range(6):
            s.append(sp(n,'ellipse',int(W*i/6),int(H*0.08),200000,200000,'FFD700',12000)); n+=1
        for i in range(6):
            s.append(sp(n,'ellipse',int(W*i/6+W//12),int(H*0.87),160000,160000,'FF6D00',12000)); n+=1
        s.append(sp(n,'diamond',CX-350000,10000,700000,350000,'FFD700',18000)); n+=1
        s.append(sp(n,'diamond',CX-350000,H-360000,700000,350000,'FFD700',18000)); n+=1
    return ''.join(s)

SLIDE_COLORS = {
    1:('FF6D00','2196F3','00BCD4'), 2:('FFD700','2196F3','9C27B0'),
    3:('FF6D00','2196F3','00BCD4'), 4:('00BCD4','FF6D00','9C27B0'),
    5:('2196F3','FF6D00','00BCD4'), 6:('2196F3','FF6D00','00E676'),
    7:('FF6D00','2196F3','00BCD4'), 8:('FF6D00','00BCD4','2196F3'),
    9:('FFD700','FF6D00','00BCD4'),
}
# EXACT same safe transitions from test_anims.py
TRANSITIONS = {
    1:('<p:zoom dir="in"/>','med'),   2:('<p:push dir="u"/>','fast'),
    3:('<p:wipe dir="l"/>','med'),    4:('<p:wheel spokes="4"/>','fast'),
    5:('<p:split dir="horz" orient="out"/>','med'), 6:('<p:blinds dir="vert"/>','fast'),
    7:('<p:newsflash/>','fast'),      8:('<p:circle/>','med'),
    9:('<p:zoom dir="out"/>','slow'),
}
# EXACT same anim config from test_anims.py
ANIM_CFG = {
    1:('fade','fade',100,300,600),   2:('fade','fade',100,200,500),
    3:('fade','fade', 80,200,400),   4:('fade','fade',100,300,600),
    5:('fade','fade', 70,200,350),   6:('fade','fade',110,300,600),
    7:('fade','fade',120,250,600),   8:('fade','fade', 70,200,350),
    9:('fade','fade',150,500,800),
}

def get_shape_ids(xml):
    return [int(m) for m in re.findall(r'<p:cNvPr id="(\d+)"', xml) if m != '1']

# EXACT make_timing from test_anims.py
def make_timing(shape_ids, f1, f2, delay_step, start_delay, anim_dur):
    if not shape_ids:
        return '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot"/></p:par></p:tnLst><p:bldLst/></p:timing>'
    nid = [3]
    def nxt(): v = nid[0]; nid[0] += 1; return v
    shapes_xml = []; builds_xml = []
    for i, spid in enumerate(shape_ids):
        filt = f1 if i % 2 == 0 else f2
        rel_dly = i * delay_step
        ctn_id = nxt(); set_id = nxt(); anim_id = nxt()
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
    p = WORK / f'ppt/slides/slide{n}.xml'
    xml = p.read_text(encoding='utf-8')
    c1, c2, c3 = SLIDE_COLORS[n]
    xml = xml.replace('</p:grpSpPr>', f'</p:grpSpPr>{decor(n, c1, c2, c3)}', 1)
    shape_ids = get_shape_ids(xml)
    t_inner, spd = TRANSITIONS[n]
    f1, f2, dstep, sdelay, adur = ANIM_CFG[n]
    timing = make_timing(shape_ids, f1, f2, dstep, sdelay, adur)
    xml = xml.replace('</p:sld>', f'<p:transition spd="{spd}">{t_inner}</p:transition>{timing}</p:sld>')
    p.write_text(xml, encoding='utf-8')
    print(f'slide{n}: {len(shape_ids)} shapes')

OUT.unlink(missing_ok=True)
all_files = []
for root, dirs, files in os.walk(WORK):
    dirs.sort()
    for f in sorted(files):
        full = Path(root) / f
        arc = full.relative_to(WORK).as_posix()
        all_files.append((arc, full))
def key(p): return (0,p[0]) if p[0]=='[Content_Types].xml' else (1,p[0]) if p[0]=='_rels/.rels' else (2,p[0])
all_files.sort(key=key)
with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as zout:
    for arc, full in all_files:
        zout.write(full, arc)
print('Done:', OUT.stat().st_size // 1024, 'KB')
