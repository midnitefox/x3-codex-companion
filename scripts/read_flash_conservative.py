import sys,struct,hashlib
import esptool
from esptool.loader import ESPLoader
original=ESPLoader.read_flash
def conservative_read(self,offset,length,progress_fn=None):
 if not self.IS_STUB:return original(self,offset,length,progress_fn)
 self.check_command('read flash',self.ESP_CMDS['READ_FLASH'],struct.pack('<IIII',offset,length,1024,1))
 data=bytearray();self._port.timeout=5
 while len(data)<length:
  part=self.read();data.extend(part);self.write(struct.pack('<I',len(data)))
  if progress_fn and len(data)%65536==0:progress_fn(len(data),length,offset)
 if len(data)!=length:raise RuntimeError('Wrong read size')
 digest=self.read()
 if digest!=hashlib.md5(data).digest():raise RuntimeError('Flash digest mismatch')
 return bytes(data)
ESPLoader.read_flash=conservative_read
esptool.main()
