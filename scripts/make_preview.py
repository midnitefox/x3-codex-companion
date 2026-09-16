"""Synthetic renderer comparison sheet; never reads real Codex task data."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from display_ui import render_status
from PIL import Image
sheet=Image.new('1',(4*552+24,2*816+24),1)
for i,status in enumerate(['Working','Needs input','Ready','Idle','Failed','Waiting','Offline','Unavailable']):
    data={'connected':True,'tasks':[{'title':'Build my companion','status':status,'fresh':True}]}
    if status=='Waiting':data['tasks']=[]
    if status=='Offline':data['connected']=False
    sheet.paste(render_status(data),(24+(i%4)*552,24+(i//4)*816))
sheet.save(ROOT/'docs'/'status-preview.png')
print('Created docs/status-preview.png with synthetic data')
