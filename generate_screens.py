"""Build firmware fallback images using the same portrait design as live data."""
from pathlib import Path
from display_ui import render_status
from bridge import pack
root=Path(__file__).resolve().parent
for name,state in [('waiting',{'connected':False,'screen':'boot','tasks':[]}),('offline',{'connected':False,'tasks':[]})]:
    image=render_status(state);image.save(root/(name+'-preview.png'))
    raw=pack(image)
    (root/'firmware'/'src'/(name+'.h')).write_text('#pragma once\n#include <Arduino.h>\nstatic const uint8_t '+name+'Frame[] PROGMEM = {'+','.join(str(v) for v in raw)+'};\n')
