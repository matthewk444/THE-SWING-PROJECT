export const EDGES=[[11,12],[11,13],[13,15],[12,14],[14,16],[11,23],[12,24],[23,24],[23,25],[25,27],[24,26],[26,28]];
export const FEATURE_NAMES=['Lead knee','Trail knee','Lead elbow','Trail elbow','Stance width','Hand position sideways','Hand height'];
const finite=Number.isFinite;
export function point(p,i,w,h){const a=p?.[i];return a&&[a.x,a.y,a.visibility,a.presence].every(finite)&&a.visibility>=.65&&a.presence>=.65&&a.x>=0&&a.x<=1&&a.y>=0&&a.y<=1?[a.x*w,a.y*h]:null;}
const dist=(a,b)=>Math.hypot(a[0]-b[0],a[1]-b[1]);
const mid=(a,b)=>[(a[0]+b[0])/2,(a[1]+b[1])/2];
function angle(a,b,c){const u=[a[0]-b[0],a[1]-b[1]],v=[c[0]-b[0],c[1]-b[1]],d=Math.hypot(...u)*Math.hypot(...v);return d<1e-6?null:Math.acos(Math.max(-1,Math.min(1,(u[0]*v[0]+u[1]*v[1])/d)))/Math.PI;}
export function describe(poses,w,h,meta){
 if(poses.length!==1)return {valid:false,cue:poses.length?'Keep only one hitter in view.':'Step into view with your whole body visible.'};
 const p=poses[0], ids=[0,11,12,13,14,15,16,23,24,25,26,27,28], q=Object.fromEntries(ids.map(i=>[i,point(p,i,w,h)]));
 if(ids.some(i=>!q[i]))return {valid:false,cue:'Move back or adjust the view so head, hands, hips and feet track clearly.'};
 const hip=mid(q[23],q[24]),shoulder=mid(q[11],q[12]),scale=dist(hip,shoulder);
 if(scale<30)return {valid:false,cue:'Move closer; your torso is too small in this view.'};
 const left=meta.hand==='Right',lead=left?[23,25,27,11,13,15]:[24,26,28,12,14,16],trail=left?[24,26,28,12,14,16]:[23,25,27,11,13,15];
 const hands=mid(q[15],q[16]),sign=meta.direction==='Left'?-1:1;
 const vector=[angle(...lead.slice(0,3).map(i=>q[i])),angle(...trail.slice(0,3).map(i=>q[i])),angle(...lead.slice(3).map(i=>q[i])),angle(...trail.slice(3).map(i=>q[i])),dist(q[27],q[28])/scale,(hands[0]-hip[0])*sign/scale,(hands[1]-hip[1])/scale];
 if(vector.some(v=>!finite(v)))return {valid:false,cue:'Tracking is uncertain; adjust the camera.'};
 return {valid:true,cue:'Full body tracked. Ready to capture.',vector,head:[q[0][0]/scale,q[0][1]/scale],scale,knee:vector[0]*180};
}
export function summarize(frames){
 const good=frames.filter(f=>f.valid),coverage=frames.length?good.length/frames.length:0;
 const span=frames.length>1?(frames.at(-1).t-frames[0].t)/1000:0;
 const gaps=frames.slice(1).map((f,i)=>f.t-frames[i].t),maxGap=gaps.length?Math.max(...gaps):0;
 const trackedGaps=good.slice(1).map((f,i)=>f.t-good[i].t);
 const maxTrackedGap=trackedGaps.length?Math.max(...trackedGaps):Infinity;
 const movement=good.length?Math.max(...Array.from({length:7},(_,k)=>Math.max(...good.map(f=>f.vector[k]))-Math.min(...good.map(f=>f.vector[k])))):0;
 const adequate=good.length>=12&&coverage>=.7&&span>=.5&&maxGap<=350&&maxTrackedGap<=350&&movement>=.08;
 return {coverage,good:good.length,total:frames.length,span,maxGap,maxTrackedGap,movement,adequate,kneeRange:good.length?[Math.min(...good.map(f=>f.vector[0]))*180,Math.max(...good.map(f=>f.vector[0]))*180]:null};
}
export function resample(frames,n=32){
 const good=frames.filter(f=>f.valid),start=good[0]?.t,end=good.at(-1)?.t;
 if(good.length<2||end<=start)throw Error('Not enough timed movement samples.');
 let j=0;return Array.from({length:n},(_,i)=>{const t=start+(end-start)*i/(n-1);while(j<good.length-2&&good[j+1].t<t)j++;const a=good[j],b=good[j+1],r=(t-a.t)/(b.t-a.t);return a.vector.map((v,k)=>v+(b.vector[k]-v)*r);});
}
export function dtw(a,b){
 const rows=Array.from({length:a.length+1},()=>Array(b.length+1).fill(Infinity));rows[0][0]=0;
 const lengths=Array.from({length:a.length+1},()=>Array(b.length+1).fill(0)),band=Math.max(8,Math.abs(a.length-b.length));
 for(let i=1;i<=a.length;i++)for(let j=Math.max(1,i-band);j<=Math.min(b.length,i+band);j++){
 const options=[[i-1,j],[i,j-1],[i-1,j-1]].sort((x,y)=>rows[x[0]][x[1]]-rows[y[0]][y[1]]),[u,v]=options[0];
 const cost=Math.sqrt(a[i-1].reduce((s,x,k)=>s+(x-b[j-1][k])**2,0)/a[i-1].length);
 rows[i][j]=cost+rows[u][v];lengths[i][j]=lengths[u][v]+1;
 }
 return rows[a.length][b.length]/lengths[a.length][b.length];
}
export function comparable(a,b){return ['hand','view','drill'].every(k=>a[k]===b[k]);}
export function rank(session,refs){
 if(!summarize(session.frames).adequate)throw Error('Insufficient tracking for a comparison.');
 const a=resample(session.frames);
 return refs.filter(r=>!(r.created&&session.created&&r.created===session.created)&&comparable(session.meta,r.meta)&&summarize(r.frames).adequate).map(r=>{
 const b=resample(r.frames),differences=FEATURE_NAMES.map((name,k)=>({name,distance:a.reduce((s,x,i)=>s+Math.abs(x[k]-b[i][k]),0)/a.length})).sort((x,y)=>y.distance-x.distance);
 return {reference:r,distance:dtw(a,b),differences};}).sort((x,y)=>x.distance-y.distance);
}
export function validateReference(r){
 if(!r||r.version!==1||typeof r.name!=='string'||!r.name.trim()||r.name.length>100||typeof r.source!=='string'||r.source.length>1000||!r.source.trim())throw Error('Reference requires a name and source.');
 if(!['Right','Left'].includes(r.meta?.hand)||!['Left','Right'].includes(r.meta?.direction)||!['Open side','Back side'].includes(r.meta?.view)||!['Tee','Front toss','Live pitch','Dry swing'].includes(r.meta?.drill))throw Error('Invalid reference capture metadata.');
 if(!Array.isArray(r.frames)||r.frames.length>500||!r.frames.length)throw Error('Invalid reference frame count.');
 let prev=-Infinity;
 for(const f of r.frames){if(!finite(f.t)||f.t<=prev||typeof f.valid!=='boolean')throw Error('Invalid reference timing.');prev=f.t;if(f.valid&&(!Array.isArray(f.vector)||f.vector.length!==7||f.vector.some(x=>!finite(x)||Math.abs(x)>20)))throw Error('Invalid motion features.');}
 if(!summarize(r.frames).adequate)throw Error('Reference does not pass tracking coverage / timing checks.');
 return r;
}
