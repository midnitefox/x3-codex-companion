"""Local Codex IPC -> portrait raster -> USB. No network listener or API key."""
import argparse, json, pathlib, queue, struct, subprocess, threading, time, zlib
from PIL import Image
import serial
from serial.tools import list_ports

ROOT=pathlib.Path(__file__).resolve().parent
THREAD=''
FRAME_BYTES=792*528//8
PRIORITY={'Needs input':0,'Failed':1,'Working':2,'Ready':3,'Idle':4,'Unavailable':5}
def render(data):
    from display_ui import render_status
    return render_status(data)

def pack(image):
    raw=image.transpose(Image.Transpose.ROTATE_90).tobytes()
    assert len(raw)==FRAME_BYTES
    return raw
def packet(seq,payload=b''):
    return b'X3ST'+struct.pack('<III',seq,len(payload),zlib.crc32(payload))+payload
def reader(proc,q):
    for line in proc.stdout:
        try:v=json.loads(line)
        except (ValueError,TypeError):continue
        while not q.empty():
            try:q.get_nowait()
            except queue.Empty:break
        q.put((time.monotonic(),v))
def run(args):
    proc=subprocess.Popen(['node',str(ROOT/'status-source.cjs')]+([args.thread] if args.thread else []),stdout=subprocess.PIPE,text=True,
                          creationflags=subprocess.CREATE_NO_WINDOW)
    q=queue.Queue();threading.Thread(target=reader,args=(proc,q),daemon=True).start()
    state={'connected':False,'tasks':[]};received=0;device=None;last_frame=None;seq=0;last_send=0;verified=False
    end=time.monotonic()+args.seconds if args.seconds else float('inf')
    try:
        while time.monotonic()<end:
            try:received,state=q.get(timeout=.25)
            except queue.Empty:pass
            now=time.monotonic()
            if now-received>8:state={'connected':False,'tasks':[]}
            frame=pack(render(state))
            if frame!=last_frame:
                render(state).save(ROOT/'preview.png')
                if args.preview_only:
                    print(json.dumps({'connected':state['connected'],'statuses':[t['status'] for t in state['tasks']]}),flush=True)
                    last_frame=frame
            if args.preview_only:continue
            try:
                if device is None:
                    matches=[p for p in list_ports.comports() if p.vid==0x303a and p.pid==0x1001]
                    if len(matches)!=1:time.sleep(1);continue
                    device=serial.Serial(port=None,baudrate=115200,timeout=1,write_timeout=5)
                    device.dtr=False;device.rts=False;device.port=matches[0].device;device.open()
                    device.write(b'X3HELLO\n')
                    deadline=time.monotonic()+4;verified=False
                    while time.monotonic()<deadline:
                        if device.readline().strip()==b'X3STATUS 1 792 528':verified=True;break
                    if not verified:
                        device.close();device=None
                        raise RuntimeError('Connected firmware is not X3 Status v1; no frame data sent.')
                    print(json.dumps({'usb':'connected','port':matches[0].device,'protocol':1}),flush=True)
                    last_frame=None
                if now-last_send>=2:
                    seq+=1;changed=frame!=last_frame
                    wire=packet(seq,frame if changed else b'')
                    # Pace native CDC traffic so a frame cannot overrun the MCU RX queue.
                    for offset in range(0,len(wire),256):
                        device.write(wire[offset:offset+256])
                        time.sleep(.003)
                    deadline=time.monotonic()+8;ack=False
                    while time.monotonic()<deadline:
                        reply=device.readline().strip()
                        if reply==f'ACK {seq}'.encode():ack=True;break
                        if reply.startswith(b'ERROR '):
                            raise serial.SerialException(reply.decode('ascii',errors='replace'))
                    if not ack:raise serial.SerialException('No frame acknowledgement')
                    if changed:print(json.dumps({'usb':'frame_ack','sequence':seq,'bytes':len(frame),'statuses':[t['status'] for t in state['tasks']]}),flush=True)
                    last_frame=frame;last_send=time.monotonic()
            except serial.SerialException as error:
                print(json.dumps({'usb':'retry','reason':str(error)}),flush=True)
                if device:device.close()
                device=None;time.sleep(1)
    finally:
        if device:device.close()
        proc.terminate();proc.wait(timeout=5)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--preview-only',action='store_true');p.add_argument('--seconds',type=int,default=0);p.add_argument('--thread',default=THREAD)
    run(p.parse_args())
