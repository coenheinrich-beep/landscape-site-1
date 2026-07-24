#!/usr/bin/env python3
"""
Add slide transitions and staggered entrance animations to rl_bachelor.pptx.
No text or content is changed — only visual effects are added.
"""
import zipfile, shutil, re, subprocess
from pathlib import Path

SRC  = Path('/home/user/landscape-site-1/rl_bachelor.pptx')
OUT  = Path('/home/user/landscape-site-1/rl_bachelor_extra.pptx')
WORK = Path('/tmp/pptx_enhance')

shutil.rmtree(WORK, ignore_errors=True)
with zipfile.ZipFile(SRC) as z:
    z.extractall(WORK)

# Per-slide config:
#   transition_inner_xml, speed, filter1, filter2,
#   delay_step_ms (between shapes), start_delay_ms (after slide loads), anim_dur_ms
SLIDE_CONFIG = {
    1: ('<p:zoom dir="in"/>',                 'med',  'zoom(inCenter)',    'fade',             120, 400, 700),
    2: ('<p:push dir="u"/>',                  'fast', 'slide(fromLeft)',   'slide(fromRight)', 100, 300, 500),
    3: ('<p:wipe dir="l"/>',                  'med',  'wipe(left)',        'wipe(right)',       80, 200, 400),
    4: ('<p:wheel spokes="4"/>',              'fast', 'zoom(inCenter)',    'dissolve',         100, 300, 600),
    5: ('<p:split dir="horz" orient="out"/>', 'med',  'wipe(left)',        'wipe(right)',       70, 200, 350),
    6: ('<p:blinds dir="vert"/>',             'fast', 'slide(fromBottom)', 'slide(fromLeft)',  120, 400, 600),
    7: ('<p:newsflash/>',                     'fast', 'zoom(inCenter)',    'fade',             120, 250, 600),
    8: ('<p:circle/>',                        'med',  'wipe(left)',        'wipe(right)',       70, 200, 350),
    9: ('<p:zoom dir="out"/>',                'slow', 'zoom(inCenter)',    'dissolve',         200, 600, 900),
}

def get_shape_ids(xml):
    """All cNvPr IDs except 1 (group container)."""
    return [int(m) for m in re.findall(r'<p:cNvPr id="(\d+)"', xml) if m != '1']

def make_timing(shape_ids, f1, f2, delay_step, start_delay, anim_dur):
    """
    Build <p:timing> XML with staggered entrance animations.
    Animations auto-play start_delay ms after the slide loads,
    with each shape entering delay_step ms after the previous.
    """
    if not shape_ids:
        return '<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="whenNotActive" nodeType="tmRoot"/></p:par></p:tnLst><p:bldLst/></p:timing>'

    # IDs: 1=root, 2=outer-par cTn, then 3 per shape (cTn + set.cTn + anim.cTn)
    nid = [3]
    def nxt():
        v = nid[0]; nid[0] += 1; return v

    shapes_xml = []
    builds_xml = []

    for i, spid in enumerate(shape_ids):
        filt     = f1 if i % 2 == 0 else f2
        rel_dly  = i * delay_step
        ctn_id   = nxt()
        set_id   = nxt()
        anim_id  = nxt()

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
        builds_xml.append(
            f'<p:bldP spid="{spid}" grpId="{i}" uiExpand="1" build="p"/>'
        )

    return (
        f'<p:timing>'
        f'<p:tnLst><p:par>'
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

for slide_num in range(1, 10):
    slide_path = WORK / f'ppt/slides/slide{slide_num}.xml'
    xml = slide_path.read_text(encoding='utf-8')

    trans_inner, speed, f1, f2, delay_step, start_delay, anim_dur = SLIDE_CONFIG[slide_num]
    shape_ids = get_shape_ids(xml)

    trans_xml  = f'<p:transition spd="{speed}">{trans_inner}</p:transition>'
    timing_xml = make_timing(shape_ids, f1, f2, delay_step, start_delay, anim_dur)

    new_xml = xml.replace('</p:sld>', f'{trans_xml}{timing_xml}</p:sld>')
    slide_path.write_text(new_xml, encoding='utf-8')
    print(f'Slide {slide_num}: {len(shape_ids)} shapes animated | transition: {trans_inner[:30]} | filters: {f1} / {f2}')

# Repack
OUT.unlink(missing_ok=True)
res = subprocess.run(['zip', '-Xr', str(OUT.resolve()), '.'], cwd=str(WORK), capture_output=True, text=True)
print(f'\nRepack exit code: {res.returncode}')
if res.stderr: print(res.stderr)

size_kb = OUT.stat().st_size / 1024
print(f'Output: {OUT}  ({size_kb:.0f} KB)')
