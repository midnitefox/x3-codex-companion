'use strict';
// Read-only adapter for Codex desktop 26.908.9136. Internal IPC may change.
const net = require('node:net');
const {applyPatch, project} = require('./status-model.cjs');
const {QuestionState} = require('./question-state.cjs');
const questions=new Map();
const initial = process.argv[2];
const entries = new Map();
let socket, clientId, buffer = Buffer.alloc(0), connected = false;
const watched = new Map(initial ? [[initial, 'local']] : []);
function send(value) {
  if (!socket?.writable) return;
  const data = Buffer.from(JSON.stringify(value)), header = Buffer.alloc(4);
  header.writeUInt32LE(data.length); socket.write(Buffer.concat([header, data]));
}
function follow(id, hostId) {
  if (!connected) return;
  send({type:'broadcast', method:'thread-stream-following-changed', version:1,
    sourceClientId:clientId, params:{conversationId:id, hostId, following:true}});
}
function emit() {
  const now = Date.now();
  const tasks = [...entries.entries()].map(([id,e]) => {
    const task=project(e.state), pending=questions.get(id)?.poll();
    if(pending>0)task.status='Needs input';
    return {...task,fresh:connected && now-e.received < 45000};
  });
  process.stdout.write(JSON.stringify({connected, tasks})+'\n');
}
function message(m) {
  if (m.type === 'client-discovery-request') {
    send({type:'client-discovery-response', requestId:m.requestId, response:{canHandle:false}}); return;
  }
  if (m.type === 'response' && m.requestId === 'x3-init' && m.resultType === 'success') {
    clientId=m.result.clientId; connected=true;
    for (const [id, host] of watched) follow(id, host);
    send({type:'broadcast',method:'thread-stream-following-status-requested',version:1,sourceClientId:clientId,params:{}});
    return;
  }
  const p=m.params;
  if (m.type !== 'broadcast' || !p) return;
  if (m.method === 'thread-stream-following-changed' && m.sourceClientId !== clientId &&
      p.following && typeof p.conversationId==='string' && !watched.has(p.conversationId) && watched.size<6) {
    watched.set(p.conversationId,p.hostId); follow(p.conversationId,p.hostId);
  }
  if (m.method !== 'thread-stream-state-changed' || !watched.has(p.conversationId)) return;
  if (m.version !== 11) { entries.delete(p.conversationId); emit(); return; }
  const c=p.change;
  if (c.type === 'snapshot') {
    // Retain only status/title fields, never conversation history or tool output.
    const raw=c.conversationState, state={};
    if(p.hostId==='local' && typeof raw.rolloutPath==='string' && questions.get(p.conversationId)?.file!==raw.rolloutPath)
      questions.set(p.conversationId,new QuestionState(raw.rolloutPath));
    for (const k of ['title','threadRuntimeStatus','hasUnreadTurn','requests','error']) state[k]=raw[k];
    entries.set(p.conversationId,{state, revision:c.revision, owner:m.sourceClientId, received:Date.now()});
  } else if (c.type === 'patches') {
    const e=entries.get(p.conversationId);
    if (!e || e.revision !== c.baseRevision || e.owner !== m.sourceClientId) {
      entries.delete(p.conversationId); follow(p.conversationId,p.hostId); emit(); return;
    }
    try { for (const patch of c.patches) applyPatch(e.state,patch); }
    catch { entries.delete(p.conversationId); follow(p.conversationId,p.hostId); emit(); return; }
    e.revision=c.revision; e.received=Date.now();
  }
  emit();
}
function connect() {
  socket=net.connect('\\\\.\\pipe\\codex-ipc'); buffer=Buffer.alloc(0);
  socket.on('connect',()=>send({type:'request',requestId:'x3-init',method:'initialize',params:{clientType:'x3-status-display'}}));
  socket.on('data',chunk=>{
    buffer=Buffer.concat([buffer,chunk]);
    while(buffer.length>=4) {
      const n=buffer.readUInt32LE(0);
      if(!n || n>64*1024*1024) {socket.destroy();return;}
      if(buffer.length<n+4)return;
      const frame=buffer.subarray(4,n+4);buffer=buffer.subarray(n+4);
      try {message(JSON.parse(frame));} catch {socket.destroy();return;}
    }
  });
  socket.on('error',()=>{});
  socket.on('close',()=>{connected=false;entries.clear();emit();setTimeout(connect,3000);});
}
setInterval(emit,2000);
setInterval(()=>{for(const [id,host] of watched)follow(id,host);},15000);
connect();
