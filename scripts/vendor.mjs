import {cp,mkdir} from 'node:fs/promises';
await mkdir('live/vendor/mediapipe',{recursive:true});
for(const file of ['vision_bundle.mjs','wasm'])await cp(`node_modules/@mediapipe/tasks-vision/${file}`,`live/vendor/mediapipe/${file}`,{recursive:true});
console.log('Pinned MediaPipe browser assets copied.');
