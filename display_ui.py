"""Approved 528x792 Codex-outline status design with live titles and counts."""
from pathlib import Path
import os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parent
RANK={'Needs input':0,'Failed':1,'Working':2,'Ready':3,'Idle':4,'Unavailable':5}
KEYS={'Needs input':'input','Failed':'failed','Working':'working','Ready':'ready','Idle':'idle','Unavailable':'unknown'}
@lru_cache(maxsize=8)
def template(key):
    return Image.open(ROOT/'assets'/(key+'.png')).convert('1',dither=Image.Dither.NONE)
@lru_cache(maxsize=8)
def face(size):
    return ImageFont.truetype(str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/'ariblk.ttf'),size)
def title_lines(title):
    # Fixed large type; truncate with ellipsis instead of shrinking long task names.
    title=' '.join(str(title).upper().split()) or 'UNTITLED TASK'
    draw=ImageDraw.Draw(Image.new('1',(528,792)))
    lines=[];line=''
    for word in title.split():
        candidate=(line+' '+word).strip()
        if draw.textlength(candidate,font=face(34))<=410:
            line=candidate;continue
        if line:lines.append(line);line=''
        for ch in word:
            if draw.textlength(line+ch,font=face(34))>410:
                lines.append(line);line=''
            line+=ch
    if line:lines.append(line)
    if len(lines)>2:
        lines=lines[:2]
        while draw.textlength(lines[-1]+'...',font=face(34))>410:lines[-1]=lines[-1][:-1]
        lines[-1]+='...'
    return lines

def select_view(data):
    tasks=data.get('tasks',[])
    live=sorted((t for t in tasks if t.get('fresh')),key=lambda t:RANK.get(t.get('status'),9)) if data.get('connected') else []
    if data.get('screen')=='boot':return 'waiting','CONNECT THE USB BRIDGE',None
    if not data.get('connected'):return 'offline','STATUS FEED DISCONNECTED',None
    if not live:return 'waiting','AWAITING TASK STATUS',None
    task=live[0];key=KEYS.get(task.get('status'),'unknown')
    # Missing/stale tasks make aggregate counts incomplete; never present partial totals as complete.
    counts=None if len(live)!=len(tasks) or any(t.get('status') not in KEYS or t.get('status')=='Unavailable' for t in live) else [sum(t['status']==status for t in live) for status in ['Working','Needs input','Ready']]
    return key,task.get('title','Untitled task'),counts

def render_status(data):
    key,title,counts=select_view(data)
    im=template(key).copy();draw=ImageDraw.Draw(im)
    lines=title_lines(title)
    top=522 if len(lines)>1 else 542
    for i,line in enumerate(lines):draw.text((264,top+i*40),line,font=face(34),fill=1,anchor='mt')
    active={'working':0,'input':1,'ready':2}.get(key,-1)
    for i in range(3):
        value='--' if counts is None else str(counts[i]).zfill(2)
        draw.text((112+i*152,680),value,font=face(43),fill=1 if i==active else 0,anchor='mt')
    return im
