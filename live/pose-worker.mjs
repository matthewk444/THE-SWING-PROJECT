import {FilesetResolver,PoseLandmarker} from './vendor/mediapipe/vision_bundle.mjs';
let pose;
self.onmessage=async({data})=>{
 try{
 if(data.type==='init'){
 const files=await FilesetResolver.forVisionTasks(new URL('./vendor/mediapipe/wasm',self.location.href).href,true);
 const options={baseOptions:{modelAssetPath:'/model.task',delegate:'GPU'},runningMode:'VIDEO',numPoses:2,outputSegmentationMasks:false};
 let delegate='GPU';try{pose=await PoseLandmarker.createFromOptions(files,options);}catch{options.baseOptions.delegate='CPU';delegate='CPU';pose=await PoseLandmarker.createFromOptions(files,options);}
 self.postMessage({id:data.id,ready:true,delegate});
 }else if(data.type==='frame'){
 const t=performance.now();try{const r=pose.detectForVideo(data.bitmap,data.timestamp);self.postMessage({id:data.id,poses:r.landmarks,ms:performance.now()-t});}finally{data.bitmap.close();}
 }
 }catch(e){self.postMessage({id:data.id,error:String(e.message||e)});}
};
