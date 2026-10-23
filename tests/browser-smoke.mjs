// Isolated headless software test. No OS camera, personal profile or athlete footage.
import {chromium} from 'playwright';
import assert from 'node:assert/strict';
const browser=await chromium.launch({executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1100}});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
try{
await page.goto('http://127.0.0.1:8502');
await page.screenshot({path:'live-preview.png',fullPage:true});
const result=await page.evaluate(async()=>{
 const worker=new Worker('/pose-worker.mjs',{type:'module'});
 const ask=(data,transfer=[])=>new Promise((resolve,reject)=>{const timeout=setTimeout(()=>reject(Error('worker timeout')),45000);worker.onmessage=({data:r})=>{clearTimeout(timeout);r.error?reject(Error(r.error)):resolve(r);};worker.onerror=e=>reject(Error(e.message));worker.postMessage(data,transfer);});
 try{const ready=await ask({id:1,type:'init'});const canvas=new OffscreenCanvas(320,240);const ctx=canvas.getContext('2d');ctx.fillStyle='black';ctx.fillRect(0,0,320,240);const bitmap=canvas.transferToImageBitmap();const inference=await ask({id:2,type:'frame',bitmap,timestamp:100},[bitmap]);return {ready,poses:inference.poses.length,ms:inference.ms};}finally{worker.terminate();}
});
assert.equal(result.ready.ready,true);assert.equal(result.poses,0);console.log('Browser worker inference:',JSON.stringify(result));
// Deliberate synthetic stream; never requests physical camera permission.
await page.evaluate(()=>{const canvas=document.createElement('canvas');canvas.width=640;canvas.height=360;const c=canvas.getContext('2d');c.fillStyle='black';c.fillRect(0,0,640,360);window.fixtureTimer=setInterval(()=>{c.fillRect(0,0,640,360);},33);navigator.mediaDevices.getUserMedia=async()=>canvas.captureStream(30);});
await page.getByRole('button',{name:'Enable camera',exact:true}).click();
await page.waitForFunction(()=>document.querySelector('#state').textContent==='LIVE',null,{timeout:45000});
await page.waitForFunction(()=>document.querySelector('#telemetry').textContent.includes('Inference:'),null,{timeout:45000});
await page.getByRole('button',{name:'Capture swing',exact:true}).click();
await page.waitForFunction(()=>document.querySelector('#reviewBody').hidden===false,null,{timeout:20000});
assert.match(await page.locator('#repBadge').textContent(),/NEEDS CLEARER/);
await page.getByRole('button',{name:'Stop session',exact:true}).click();
assert.equal(await page.locator('#state').textContent(),'CAMERA OFF');
assert.equal(await page.evaluate(()=>document.querySelector('#camera').srcObject),null);
assert.deepEqual(errors,[]);console.log('Synthetic capture, no-person abstention, and stop cleanup: passed');
// Generate a real video container from a canvas; exercise the file decoding path.
const webm=await page.evaluate(async()=>{const c=document.createElement('canvas');c.width=320;c.height=240;const ctx=c.getContext('2d');const stream=c.captureStream(20);const chunks=[];const recorder=new MediaRecorder(stream,{mimeType:'video/webm'});const done=new Promise(resolve=>recorder.onstop=resolve);recorder.ondataavailable=e=>chunks.push(e.data);recorder.start();const timer=setInterval(()=>{ctx.fillStyle='black';ctx.fillRect(0,0,320,240);},50);await new Promise(r=>setTimeout(r,1300));recorder.stop();await done;clearInterval(timer);stream.getTracks().forEach(t=>t.stop());return Array.from(new Uint8Array(await new Blob(chunks).arrayBuffer()));});
await page.locator('#videoFile').setInputFiles({name:'synthetic-blank.webm',mimeType:'video/webm',buffer:Buffer.from(webm)});
await page.waitForFunction(()=>!document.querySelector('#analyzeFile').disabled);
await page.locator('summary').click();
await page.locator('#clipEnd').fill('0.8');
await page.getByRole('button',{name:'Analyze selected window',exact:true}).click();
await page.waitForFunction(()=>document.querySelector('#fileStatus').textContent.startsWith('Window analyzed'),null,{timeout:60000});
assert.match(await page.locator('#repBadge').textContent(),/NEEDS CLEARER/);
const metadata={hand:'Right',direction:'Left',view:'Open side',drill:'Tee'};
const library=[0,1].map(n=>({version:1,name:`Synthetic test reference ${n}`,source:'Test-only mathematical fixture; not an athlete',meta:metadata,frames:Array.from({length:25},(_,i)=>({t:i*50,valid:true,vector:[.5+i/100,.7,.6,.8,1,i/24+n,-.5]}))}));
await page.locator('#importRef').setInputFiles({name:'test-refs.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(library))});
await page.waitForFunction(()=>document.querySelector('#libraryCount').textContent==='2 REFERENCES');
await page.reload();assert.equal(await page.locator('#libraryCount').textContent(),'2 REFERENCES');
await page.getByRole('button',{name:'Remove',exact:true}).first().click();
assert.equal(await page.locator('#libraryCount').textContent(),'1 REFERENCES');
assert.deepEqual(errors,[]);console.log('Video import/decoding, reference import, persistence, removal: passed');

await page.setViewportSize({width:390,height:844});await page.screenshot({path:'live-preview-mobile.png',fullPage:true});
assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
console.log('Mobile overflow check: passed');
}finally{await browser.close();}
