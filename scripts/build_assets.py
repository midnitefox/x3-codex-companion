from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
import html
OUT=Path(__file__).resolve().parents[1]/'assets'
OUT.mkdir(exist_ok=True)
import os
font=TTFont(str(Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts'/'ariblk.ttf')); gs=font.getGlyphSet(); cmap=font.getBestCmap(); upem=font['head'].unitsPerEm

def lettering(value,cx,top,size,maxw,fill='black'):
    widths=[gs[cmap[ord(c)]].width for c in value]; scale=min(size/upem,maxw/sum(widths))
    ascent=0;descent=0
    for c in value:
        p=BoundsPen(gs);gs[cmap[ord(c)]].draw(p)
        if p.bounds:ascent=max(ascent,p.bounds[3]);descent=min(descent,p.bounds[1])
    x=cx-sum(widths)*scale/2; baseline=top+ascent*scale
    out=[]
    for c,w in zip(value,widths):
        p=SVGPathPen(gs);gs[cmap[ord(c)]].draw(p)
        out.append(f'<path d="{p.getCommands()}" transform="translate({x:.3f} {baseline:.3f}) scale({scale:.6f} {-scale:.6f})" fill="{fill}"/>');x+=w*scale
    return ''.join(out)

def diamond(x,y,r=7):return f'<path d="M{x} {y-r}l{r} {r} -{r} {r} -{r} -{r}Z"/>'

# Original supplied perimeter preserved exactly; only the terminal glyph is replaced.
OUTLINE = 'M7.34,1.34c-.36,0-.7.06-1.04.17s-.65.28-.93.5c-.28.22-.52.47-.72.77s-.34.62-.44.96c-.07.25-.23.41-.48.48-.27.07-.53.18-.78.32-.25.14-.47.31-.67.51-.2.2-.37.42-.51.67s-.25.51-.32.78-.11.55-.11.84.04.56.11.84c.07.27.18.53.32.78.14.25.31.47.51.67.18.18.24.4.17.65-.07.27-.11.55-.11.84,0,.25.03.49.08.73.06.24.14.47.25.7.11.22.24.43.4.62s.33.36.53.51.41.28.63.38c.23.1.46.18.7.23.24.05.49.07.74.06.25,0,.49-.04.73-.11l.09-.02c.22-.03.4.04.56.19.2.2.42.37.67.51s.51.25.78.32.55.11.84.11.56-.04.84-.11.53-.18.78-.32c.25-.14.47-.31.67-.51s.37-.42.51-.67.25-.51.32-.78l.03-.08c.08-.2.23-.33.45-.39.34-.09.66-.24.96-.44s.55-.44.77-.72c.22-.28.38-.59.5-.93s.17-.68.17-1.04c0-.89-.36-1.7-.95-2.29-.18-.18-.24-.4-.17-.65.07-.27.11-.55.11-.84,0-.25-.03-.49-.08-.73-.06-.24-.14-.47-.25-.7-.11-.22-.24-.43-.4-.62-.16-.19-.33-.36-.53-.51-.2-.15-.41-.28-.63-.38-.23-.1-.46-.18-.7-.23s-.49-.07-.74-.06c-.25,0-.49.04-.73.11-.25.07-.47,0-.65-.17-.59-.59-1.29-.9-2.12-.94h-.17,0ZM7.34,0C8.47,0,9.5.41,10.3,1.09c.26-.05.54-.07.82-.07.33,0,.67.04.99.11.33.07.64.18.95.32.3.14.59.32.85.52.27.2.51.44.72.69.21.26.4.53.55.83.15.3.27.61.36.93.09.32.14.65.15.99.01.33,0,.67-.07,1,.24.28.44.59.61.92.16.33.29.68.37,1.04s.12.73.11,1.1c0,.37-.06.73-.15,1.09-.1.36-.23.7-.41,1.02s-.39.62-.64.89-.53.51-.84.72c-.31.2-.64.37-.98.49-.16.44-.38.85-.67,1.23-.29.38-.62.7-1.01.97-.39.27-.8.48-1.25.62s-.91.21-1.38.21c-1.12,0-2.11-.36-2.96-1.09-.26.05-.54.07-.82.07-.34,0-.67-.04-.99-.11-.33-.07-.64-.18-.95-.32-.3-.14-.59-.32-.85-.52s-.51-.44-.72-.69c-.21-.26-.4-.53-.55-.83s-.27-.61-.36-.93c-.09-.32-.14-.65-.15-.99s0-.67.07-1c-.68-.78-1.04-1.69-1.1-2.72v-.24c0-.47.06-.93.21-1.38.14-.45.35-.87.62-1.25.27-.39.59-.72.97-1.01.37-.29.78-.51,1.23-.67.16-.44.38-.85.67-1.23s.62-.7,1.01-.97.8-.48,1.25-.62C6.41.07,6.87,0,7.34,0'

def status_mark(kind):
    marks={
      'working':'<circle cx="5.6" cy="8.35" r=".73"/><circle cx="8.35" cy="8.35" r=".73"/><circle cx="11.1" cy="8.35" r=".73"/>',
      'input':'<path d="M6.6 6.55c0-2.05 3.65-2.12 3.65.03 0 1.45-1.9 1.45-1.9 2.85"/><circle cx="8.35" cy="11.25" r=".58" fill="black" stroke="none"/>',
      'ready':'<path d="M5.55 8.35l1.85 1.9 3.75-4.05"/>',
      'idle':'<path d="M6.85 5.9v4.9m3-4.9v4.9"/>',
      'failed':'<path d="M8.35 5.55v3.75"/><circle cx="8.35" cy="11.25" r=".58" fill="black" stroke="none"/>',
      'waiting':'<circle cx="8.35" cy="8.35" r="3.1"/><path d="M8.35 6.45v2.05l1.55.85"/>',
      'offline':'<path d="M8.7 6.15l.7-.7a1.65 1.65 0 0 1 2.33 2.33l-.7.7M8 10.55l-.7.7a1.65 1.65 0 0 1-2.33-2.33l.7-.7M5.8 5.8l5.1 5.1"/>',
      'unknown':'<path d="M5.95 8.35h4.8"/>'
    }
    treatment='fill="black"' if kind=='working' else 'fill="none" stroke="black" stroke-width="1.05" stroke-linecap="round" stroke-linejoin="round"'
    return '<path fill="black" fill-rule="evenodd" d="'+OUTLINE+'"/><g '+treatment+'>'+marks[kind]+'</g>'

def icon(kind):
    return '<g transform="translate(114.5 38) scale(17.9042)">'+status_mark(kind)+'</g>'

states=[('working','WORKING','TASK IN PROGRESS'),('input','NEEDS INPUT','QUESTION WAITING'),('ready','READY','RESPONSE READY'),('idle','IDLE','NO ACTIVE WORK'),('failed','FAILED','CHECK THE TASK'),('waiting','WAITING','AWAITING STATUS'),('offline','OFFLINE','FEED DISCONNECTED'),('unknown','UNKNOWN','STATUS UNAVAILABLE')]

def screen(key,label,sub):
    p=['<rect width="528" height="792" fill="white"/>','<path d="M40 16H488L512 40V752L488 776H40L16 752V40Z" fill="none" stroke="black" stroke-width="6"/>','<path d="M44 28H484L500 44V748L484 764H44L28 748V44Z" fill="none" stroke="black" stroke-width="2"/>']
    # Clip every stripe to a reserved rail; the emblem cannot touch it.
    for side,x in [('l',40),('r',458)]:
        uid=key+side
        p.append(f'<defs><clipPath id="{uid}"><rect x="{x}" y="65" width="30" height="410"/></clipPath></defs><g clip-path="url(#{uid})">')
        for y in range(20,640,64):p.append(f'<path d="M{x-20} {y+45}l70-70v30l-70 70Z"/>')
        p.append('</g>')
    p.append(icon(key))
    if key=='input':
        p.extend([lettering('NEEDS',264,355,72,376),lettering('INPUT',264,420,72,376)])
    else:p.append(lettering(label,264,390,78,376))
    # Task name replaces the redundant status-description banner.
    p.append('<path d="M58 502H470L488 520V594L470 612H58L40 594V520Z"/>')
    tasklines=[]
    for i,line in enumerate(tasklines):p.append(lettering(line,264,522+i*40,34,410,'white'))
    # Counts summarize all tracked tasks; dashes never imply zero on a lost feed.
    values=['03','01','02'] if key not in ('offline','waiting','unknown') else ['--','--','--']
    active={'working':0,'input':1,'ready':2}.get(key,-1)
    for i,(name,value) in enumerate(zip(['RUN','INPUT','READY'],values)):
        x=40+i*152
        fill='black' if i==active else 'white'; ink='white' if i==active else 'black'
        p.append(f'<rect x="{x}" y="632" width="144" height="92" fill="{fill}" stroke="black" stroke-width="2"/>')
        p.append(lettering(name,x+72,643,30,130,ink))

    for x in [48,80,112]:p.append(f'<path d="M{x} 738h18l15 15h-18Z"/>')
    for x in [218,250,282]:p.append(diamond(x,746,5))
    p.append('<g transform="translate(450 735) scale(.5)" fill="none" stroke="black" stroke-width="5"><path d="M12 39V4m0 23L0 18V10m12 23 14-10V12"/><path d="M7 8l5-7 5 7"/><circle cx="12" cy="41" r="4" fill="black"/><circle cx="0" cy="8" r="3" fill="black"/><rect x="23" y="7" width="6" height="6" fill="black"/></g>')
    if key=='offline':p.append('<path d="M447 734l22 23" stroke="white" stroke-width="6"/><path d="M447 734l22 23" stroke="black" stroke-width="3"/>')
    return ''.join(p)

for key,label,sub in states:
    body=screen(key,label,sub)
    (OUT/(key+'.svg')).write_text('<svg xmlns="http://www.w3.org/2000/svg" width="528" height="792" viewBox="0 0 528 792">'+body+'</svg>')
