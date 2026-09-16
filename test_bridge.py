import struct, unittest, zlib
import bridge
class ProtocolTests(unittest.TestCase):
    def test_frame_roundtrip_and_integrity(self):
        image=bridge.render({'connected':True,'tasks':[{'title':'Test','status':'Working','fresh':True}]})
        payload=bridge.pack(image);packet=bridge.packet(37,payload)
        self.assertEqual(len(payload),52272)
        self.assertEqual(packet[:4],b'X3ST')
        seq,size,crc=struct.unpack('<III',packet[4:16])
        self.assertEqual((seq,size),(37,52272));self.assertEqual(crc,zlib.crc32(packet[16:]))
        damaged=bytearray(packet[16:]);damaged[15]^=1
        self.assertNotEqual(crc,zlib.crc32(damaged))
    def test_heartbeat(self):
        self.assertEqual(bridge.packet(1),b'X3ST'+struct.pack('<III',1,0,0))
    def test_stale_state_not_live(self):
        stale=bridge.render({'connected':True,'tasks':[{'title':'Task','status':'Working','fresh':False}]})
        live=bridge.render({'connected':True,'tasks':[{'title':'Task','status':'Working','fresh':True}]})
        self.assertNotEqual(stale.tobytes(),live.tobytes())
if __name__=='__main__':unittest.main()
