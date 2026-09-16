'use strict';
const fields=new Set(['title','threadRuntimeStatus','hasUnreadTurn','requests','error']);
function applyPatch(state,p) {
  if(!Array.isArray(p.path))throw Error('Unknown patch format');
  if(!fields.has(p.path[0]))return;
  if(p.path.some(k=>['__proto__','prototype','constructor'].includes(k)))throw Error('Invalid path');
  let parent=state;
  for(const key of p.path.slice(0,-1)) {
    if(parent[key]==null)throw Error('Missing patch parent');
    parent=parent[key];
  }
  const key=p.path.at(-1);
  if(p.op==='remove') {if(Array.isArray(parent))parent.splice(key,1);else delete parent[key];}
  else if(p.op==='replace'||p.op==='add')parent[key]=p.value;
  else throw Error('Unknown patch operation');
}
function nonempty(v) {
  if(v==null)return false;
  if(typeof v==='object')return Object.values(v).some(nonempty);
  return Boolean(v);
}
function project(s) {
  const r=s.threadRuntimeStatus, flags=r?.activeFlags||[];
  let status='Unavailable';
  if(nonempty(s.requests)||flags.includes('waitingOnApproval')||flags.includes('waitingOnUserInput'))status='Needs input';
  else if(r?.type==='systemError'||nonempty(s.error))status='Failed';
  else if(r?.type==='active')status='Working';
  else if(s.hasUnreadTurn)status='Ready';
  else if(r?.type==='idle')status='Idle';
  return {title:typeof s.title==='string'?s.title.slice(0,160):'Untitled task',status};
}
module.exports={applyPatch,project};
