#!/usr/bin/env python3
"""
Built on the EXACT code that opened on iOS (test_anims.py):
- same sp() function, same make_timing(), same injection point
- same safe transitions + fade animations
- enhanced decor_per_slide() with per-slide themes but proven-safe patterns
- color patches: rank colors, invisible text fixes, scouting bar colors
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

# EXACT decor_simple() from test_anims.py (the confirmed-working full-deck test).
# Every slide gets the IDENTICAL 18-shape structure — only fill colors vary,
# which is exactly what the confirmed-working file did.
def decor(slide, c1, c2, c3):
    s = []; n = 500
    s.append(sp(n,'ellipse',CX-600000,CY-600000,1200000,1200000,c1,6000,outline=True,lw=38100)); n+=1
    s.append(sp(n,'ellipse',CX-900000,CY-900000,1800000,1800000,c2,4000,outline=True,lw=25400)); n+=1
    s.append(sp(n,'rect',0,0,W,H//8,c1,5000)); n+=1
    s.append(sp(n,'rect',0,H-H//8,W,H//8,c2,5000)); n+=1
    for i in range(5):
        s.append(sp(n,'ellipse',int(W*i/5),int(H*0.1),200000,200000,c3,8000)); n+=1
    for i in range(5):
        s.append(sp(n,'ellipse',int(W*i/5+W//10),int(H*0.85),150000,150000,c1,8000)); n+=1
    s.append(sp(n,'diamond',CX-300000,10000,600000,300000,c3,10000)); n+=1
    s.append(sp(n,'diamond',CX-300000,H-310000,600000,300000,c2,10000)); n+=1
    return ''.join(s)

# EXACT SLIDE_COLORS rotation from test_anims.py (confirmed working)
SLIDE_COLORS = {
    1:('FF6D00','2196F3','00BCD4'), 2:('2196F3','00BCD4','FF6D00'),
    3:('00BCD4','FF6D00','2196F3'), 4:('FF6D00','00BCD4','2196F3'),
    5:('2196F3','FF6D00','00BCD4'), 6:('00BCD4','2196F3','FF6D00'),
    7:('FF6D00','2196F3','00BCD4'), 8:('2196F3','00BCD4','FF6D00'),
    9:('00BCD4','FF6D00','2196F3'),
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

def recolor_shape(xml, shape_id, new_color):
    """Replace all srgbClr values within a specific shape (targeted by cNvPr id)."""
    idx = xml.find(f'cNvPr id="{shape_id}"')
    if idx < 0:
        return xml
    start = xml.rfind('<p:sp>', 0, idx)
    end = xml.find('</p:sp>', idx) + 7
    shape = xml[start:end]
    shape_new = re.sub(r'<a:srgbClr val="[0-9A-Fa-f]{6}"',
                       f'<a:srgbClr val="{new_color}"', shape)
    return xml[:start] + shape_new + xml[end:]

def patch_slide_colors(slide_num, xml):
    """Apply targeted color improvements — fixes invisible text + color-codes content."""
    if slide_num == 2:
        # Color-code Rocket League ranks (slide 2 = rank explanation slide)
        xml = recolor_shape(xml, 5,  'FFD700')  # SSL/GC → gold
        xml = recolor_shape(xml, 7,  '4FC3F7')  # Champion → sky blue
        xml = recolor_shape(xml, 9,  '00E5FF')  # Diamond → bright cyan
        xml = recolor_shape(xml, 11, 'CE93D8')  # Platinum → lavender
        xml = recolor_shape(xml, 13, 'FFC107')  # Gold → amber
        xml = recolor_shape(xml, 15, '90A4AE')  # Silver → silver-gray
        xml = recolor_shape(xml, 17, 'FF3D00')  # Bronze/BRYTON → red-orange (WAS INVISIBLE 0D1117)

    elif slide_num == 5:
        # Fix invisible "WHAT HE MEANS" column header (was 0D1117 = invisible on dark bg)
        xml = recolor_shape(xml, 5, '00BCD4')   # WHAT HE TYPES → cyan
        xml = recolor_shape(xml, 7, 'FF6D00')   # WHAT HE MEANS → orange (WAS INVISIBLE)

    elif slide_num == 8:
        # Color scouting report bars: red = embarrassingly bad, gold = ironically great
        xml = recolor_shape(xml, 9,  'FF1744')  # Accuracy 8% bar → red
        xml = recolor_shape(xml, 13, 'FF1744')  # Ball Chasing 99% bar → red
        xml = recolor_shape(xml, 17, 'FF1744')  # Rotation 5% bar → red
        xml = recolor_shape(xml, 21, 'FF1744')  # Toxicity 92% bar → red
        xml = recolor_shape(xml, 25, 'FF1744')  # Blaming Teammates 97% bar → red
        xml = recolor_shape(xml, 29, 'FF1744')  # Actual Skill 3% bar → red
        xml = recolor_shape(xml, 33, 'FFD700')  # Heart & Passion 100% bar → gold

    return xml

for n in range(1, 10):
    p = WORK / f'ppt/slides/slide{n}.xml'
    xml = p.read_text(encoding='utf-8')

    # Apply color patches before adding decorations
    xml = patch_slide_colors(n, xml)

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
