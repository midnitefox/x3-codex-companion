#include <Arduino.h>
#include <BoardConfig.h>
#include <EInkDisplay.h>
#include <XteinkDetect.h>
#include "waiting.h"
#include "offline.h"

// A second static 52 KB buffer prevents partial/corrupt USB frames reaching glass.
// No filesystem writes, networking, or automatic sleep in this docked prototype.
static constexpr size_t FrameBytes = 792 * 528 / 8;
static uint8_t incoming[FrameBytes];
static uint8_t header[16];
static size_t headerCount=0, payloadCount=0;
static uint32_t wanted=0, sequence=0, checksum=0, lastByte=0, lastPacket=0;
static uint32_t refreshCount=0;
static bool online=false, safePanel=false;
static EInkDisplay display(8,10,21,4,5,6);
static uint32_t number(const uint8_t* p) {
  return uint32_t(p[0]) | uint32_t(p[1])<<8 | uint32_t(p[2])<<16 | uint32_t(p[3])<<24;
}
static uint32_t crc32(const uint8_t* data,size_t size) {
  uint32_t c=0xFFFFFFFF;
  for(size_t i=0;i<size;++i) {c^=data[i];for(int b=0;b<8;++b)c=(c>>1)^(0xEDB88320 & (0u-(c&1u)));}
  return ~c;
}
static void resetPacket() {headerCount=0;payloadCount=0;wanted=0;}
static void paint(const uint8_t* frame,bool clean) {
  display.setFramebuffer(frame);
  display.displayBuffer(clean?EInkDisplay::FULL_REFRESH:EInkDisplay::FAST_REFRESH,true);
}
static void finishPacket() {
  if(crc32(incoming,wanted)!=checksum) {Serial.println("ERROR CRC");resetPacket();return;}
  if(!wanted&&!online) {Serial.println("ERROR NEED_FRAME");resetPacket();return;}
  if(wanted)paint(incoming,(refreshCount++%12)==0);
  lastPacket=millis();online=true;
  Serial.printf("ACK %lu\n",static_cast<unsigned long>(sequence));
  resetPacket();
}
static void receive(uint8_t b) {
  static constexpr uint8_t magic[4]={'X','3','S','T'};
  lastByte=millis();
  if(headerCount<4) {if(b==magic[headerCount])header[headerCount++]=b;else headerCount=(b=='X'?1:0);return;}
  if(headerCount<16) {
    header[headerCount++]=b;
    if(headerCount==16) {
      sequence=number(header+4);wanted=number(header+8);checksum=number(header+12);
      if(wanted!=0&&wanted!=FrameBytes) {Serial.println("ERROR LENGTH");resetPacket();}
      else if(wanted==0)finishPacket();
    }
    return;
  }
  incoming[payloadCount++]=b;
  if(payloadCount==wanted)finishPacket();
}
void setup() {
  // Absorb USB packet bursts while the loop consumes the bounded frame parser.
  Serial.setRxBufferSize(4096);
  Serial.begin(115200);
  freeink::selectXteinkDevice();
  display.setDisplayX3();
  BoardConfig::holdPowerRails();
  BoardConfig::releaseSdRail();
  freeink::applyXteinkDisplayController();
  display.begin();
  safePanel=display.getDisplayWidth()==792&&display.getDisplayHeight()==528;
  if(safePanel)paint(waitingFrame,true);
}
void loop() {
  static uint32_t lastHello=0;
  if(!safePanel) {delay(100);return;}
  if(headerCount&&millis()-lastByte>3000)resetPacket();
  if(headerCount==0&&Serial&&millis()-lastHello>2000) {
    Serial.println("X3STATUS 1 792 528");lastHello=millis();
  }
  while(Serial.available())receive(static_cast<uint8_t>(Serial.read()));
  if(online&&millis()-lastPacket>15000) {online=false;paint(offlineFrame,true);}
  delay(1);
}
