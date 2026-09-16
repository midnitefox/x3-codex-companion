'use strict';
// Read only the local rollout identified by Codex IPC. Never retain question text.
const fs=require('node:fs'), path=require('node:path'), os=require('node:os');
const {StringDecoder}=require('node:string_decoder');
class QuestionState {
  constructor(file) { this.file=file;this.offset=0;this.tail='';this.decoder=new StringDecoder('utf8');this.pending=new Set();this.calls=new Map(); }
  consume(e) {
    if(e.type!=='response_item')return;
    const p=e.payload||{};
    if(p.type==='function_call' && /(^|\.)request_user_input_async$/.test(p.name||'')) {
      try {
        const q=JSON.parse(p.arguments).questions;
        if(Array.isArray(q))this.calls.set(p.call_id,q.map((_,i)=>JSON.stringify(['request_user_input_async',p.call_id,i])));
      } catch {}
    } else if(p.type==='function_call_output' && this.calls.has(p.call_id)) {
      try {
        const result=JSON.parse(p.output);
        if(result.accepted===true)for(const id of this.calls.get(p.call_id))this.pending.add(id);
      } catch {}
      this.calls.delete(p.call_id);
    } else if(p.type==='message' && p.role==='user') {
      for(const c of p.content||[]) {
        const t=c.text||'', start='<send_user_message_question_reply>',end='</send_user_message_question_reply>';
        if(!t.startsWith(start)||!t.trimEnd().endsWith(end))continue;
        try {for(const r of JSON.parse(t.slice(start.length,t.lastIndexOf(end))))this.pending.delete(r.questionItemId);}catch {}
      }
    }
  }
  poll() {
    let fd;
    try {
      const root=path.resolve(process.env.CODEX_HOME||path.join(os.homedir(),'.codex'),'sessions');
      const relative=path.relative(root,path.resolve(this.file));
      if(relative.startsWith('..')||path.isAbsolute(relative)||!this.file.endsWith('.jsonl'))return null;
      fd=fs.openSync(this.file,'r');const size=fs.fstatSync(fd).size;
      if(size<this.offset){this.offset=0;this.tail='';this.decoder=new StringDecoder('utf8');this.pending.clear();this.calls.clear();}
      const buf=Buffer.alloc(1024*1024);
      while(this.offset<size) {
        const n=fs.readSync(fd,buf,0,Math.min(buf.length,size-this.offset),this.offset);if(!n)break;
        this.offset+=n;this.tail+=this.decoder.write(buf.subarray(0,n));
        let at;
        while((at=this.tail.indexOf('\n'))>=0) {
          const line=this.tail.slice(0,at);this.tail=this.tail.slice(at+1);
          // Other log records are discarded without parsing their contents.
          if(!line.includes('request_user_input_async')&&!line.includes('function_call_output')&&!line.includes('send_user_message_question_reply'))continue;
          try{this.consume(JSON.parse(line));}catch{}
        }
        if(this.tail.length>32*1024*1024)throw Error('Oversized log record');
      }
      return this.pending.size;
    } catch {return null;} finally {if(fd!==undefined)fs.closeSync(fd);}
  }
}
module.exports={QuestionState};
