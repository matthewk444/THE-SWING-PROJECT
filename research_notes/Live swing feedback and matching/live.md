# Live browser swing feedback

## What implementation fits the current local prototype?

### Takeaway
Recommendation: add a standalone localhost browser live page linked from the Python/Streamlit app. Run MediaPipe Tasks Vision in the browser and preferably a worker, with local package/WASM/model assets; keep Python for saved-session analysis.

### Cited Findings
- Official web API is `@mediapipe/tasks-vision`; its VIDEO mode handles camera streams. `detectForVideo` is synchronous and blocks the calling thread; Google explicitly recommends workers to avoid main-thread blocking. Model assets may be stored inside the project. — [Web guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/web_js)
- `FilesetResolver.forVisionTasks(basePath)` accepts the WASM asset directory. — [FilesetResolver](https://developers.google.com/edge/api/mediapipe/js/tasks-vision.filesetresolver)
- `detectForVideo(videoFrame,timestamp,callback)` takes milliseconds, returns synchronously, and only guarantees masks during the callback; the return-result overload copies masks. `POSE_CONNECTIONS` provides drawing edges. — [PoseLandmarker API](https://developers.google.com/edge/api/mediapipe/js/tasks-vision.poselandmarker)
- `ImageBitmap` is transferable and available in workers; `close()` releases graphics resources. — [ImageBitmap](https://developer.mozilla.org/en-US/docs/Web/API/ImageBitmap)

### Inferences
- Pin a tested package version. Copy its `vision_bundle.mjs` and entire `wasm/` directory under a public vendor path; serve the full/lite `.task` model locally. Use matching package and WASM versions, preserve filenames, verify HTTP 200 and correct JavaScript/WASM content types. CDN is optional, not necessary once assets are installed.
- Suggested initialization (engineering sketch, not tested here):

```javascript
import {FilesetResolver, PoseLandmarker} from '/vendor/mediapipe/vision_bundle.mjs';
const files = await FilesetResolver.forVisionTasks('/vendor/mediapipe/wasm');
const pose = await PoseLandmarker.createFromOptions(files, {
  baseOptions: {modelAssetPath: '/models/pose_landmarker_full.task', delegate: 'GPU'},
  runningMode: 'VIDEO', numPoses: 1, outputSegmentationMasks: false,
  minPoseDetectionConfidence: .5, minPosePresenceConfidence: .5,
  minTrackingConfidence: .5
});
```

- Prefer a worker containing that model instance. Main thread calls `createImageBitmap(video)`, transfers it with `worker.postMessage({bitmap,timestampMs,sessionId},[bitmap])`, worker calls `detectForVideo`, posts plain landmarks, and closes bitmap in `finally`. Keep at most one frame in flight; skip new frames when busy to prevent unbounded latency. GPU/OffscreenCanvas support must be tested in target browser; retry CPU with a clearly shown status if necessary.
- Set busy BEFORE awaiting bitmap creation. Stop/restart must invalidate session IDs so late promises/results cannot revive an old session. Never send raw frames to Python merely for pose inference.
- Initial feedback should prioritize framing/pose visibility and explainable camera-plane metrics. Display a buffered post-swing summary, not a rapid stream of distracting corrections. Record/save only on an explicit action, and offer JSON/session export.

### Gaps
- No browser model or worker was executed during this research-only task. Package runtime may have worker-loading constraints; validate the chosen version and use a throttled main-thread fallback if needed.
- No evidence that live single-camera landmarks produce validated bat speed or universally correct coaching advice.

## What permissions and camera setup are needed?

### Takeaway
Use an explicit Start camera button in a top-level localhost page. Request video only and give useful errors; local HTTP on another device's LAN IP is not equivalent to localhost.

### Cited Findings
- `getUserMedia` needs a secure context and user permission; localhost qualifies. An iframe needs top-level permission delegation. Errors include `NotAllowedError`, `NotFoundError`, `NotReadableError`, and `OverconstrainedError`. A user can ignore the permission prompt indefinitely. — [MDN getUserMedia](https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia)
- `MediaStreamTrack.getSettings()` returns the current constrainable track properties. — [getSettings](https://developer.mozilla.org/en-US/docs/Web/API/MediaStreamTrack/getSettings)

### Inferences
- Start with `navigator.mediaDevices.getUserMedia({audio:false,video:{width:{ideal:1280},height:{ideal:720},frameRate:{ideal:60},facingMode:'user'}})`. Ideal constraints tolerate unsupported requests. Allow selecting rear camera for phone use, but do not promise 60/120fps from a request alone.
- Assign stream to a muted, autoplay, playsInline video element; await ready video dimensions before inference. Match canvas pixel size to source dimensions, scale display separately, and mirror both video and overlay consistently. Keep measurement coordinates unmirrored and handedness explicit.
- Stop by canceling callbacks, stopping all stream tracks, clearing srcObject, and disposing model/worker. Also clean up pagehide and unmount. Distinguish permission denied from camera busy or missing hardware.
- Linking to a top-level page avoids Streamlit component sandbox/Permissions Policy issues. Phone access requires HTTPS or a supported trusted development origin and camera permission on that phone.

### Gaps
- Target browser and actual camera capabilities are unknown until runtime. No actual user camera was opened by this research task.

## How should FPS and latency be measured honestly?

### Takeaway
Report camera settings, observed video callback rate, analyzed-frame rate, and processing latency separately. A smooth preview does not establish adequate sampling of a fast swing.

### Cited Findings
- `requestVideoFrameCallback` supplies `mediaTime`, `presentedFrames`, display timing, and sometimes capture timing. It runs at the lower of video frame rate and browser paint rate: a 120fps video on a 60Hz browser gets 60 callbacks. Callbacks can arrive one display interval late and provide no strict synchronization guarantee. — [MDN video frame callbacks](https://developer.mozilla.org/en-US/docs/Web/API/HTMLVideoElement/requestVideoFrameCallback)

### Inferences
- Prefer requestVideoFrameCallback over requestAnimationFrame. If falling back, skip duplicate `video.currentTime` frames. Use strictly increasing timestamps within a model session; camera restart or uploaded-video seek should create/reset the model. Keep media timestamp separately from processing timestamp.
- Track source configured FPS with getSettings(), observed callback count per wall-time window, completed inference count per window, skipped busy frames, and worker inference duration via performance.now() difference. Label round-trip worker delay separately; it includes transport/queue/copy cost, not camera-to-screen latency. Claim capture latency only when capture timestamps are actually available and comparable.
- Use an empty initial rate display rather than guessed FPS, and show rolling estimates after sufficient observations. Do not use 1000/inference_ms as actual analyzed FPS.
- Live feedback is best for positioning and repeated-motion review. Preserve original high-speed recordings for offline processing when users need precise sequencing, and suppress timing claims when capture/source cadence is unknown or sampling sparse.

### Gaps
- No device latency benchmark was performed; an advertised real-time FPS number would be unsupported. High-speed camera capture availability varies by hardware/browser.
