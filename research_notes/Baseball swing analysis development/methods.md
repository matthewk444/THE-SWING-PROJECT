# Practical video methods and open source options

## What can we build tonight?

### Takeaway
Recommendation: use pretrained MediaPipe Tasks with OpenCV in a local Python pipeline, then expose measured camera-plane features and quality flags through a simple UI. This is an engineering recommendation, not a validated swing coaching model.

### Cited Findings
- The Tasks Python API supports decoded video frames: construct `PoseLandmarkerOptions(base_options=BaseOptions(model_asset_path=...), running_mode=RunningMode.VIDEO)`, call `PoseLandmarker.create_from_options`, then `detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=rgb_array), timestamp_ms)`. Video mode blocks and uses tracking; livestream can discard input while busy. Results include normalized landmarks and world landmarks, plus visibility. — [Python guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python)
- Google lists Mac, Windows and Linux, Python 3.9+, pip 20.3+. — [Setup](https://developers.google.com/edge/mediapipe/solutions/setup_python)
- Current PyPI release checked October 22, 2026 is 1.1.1; its available Mac wheel is macOS 11+ ARM64. Python classifiers list 3.9–3.14. Input processing is on device, but the current privacy notice says Tasks sends performance and utilization metrics to Google. — [PyPI](https://pypi.org/project/mediapipe/)
- Official model bundles include lite, full and heavy, and output 33 body landmarks. The model is optimized for real-time fitness applications. Full bundle: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task`. — [Overview and model downloads](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker)

### Inferences
- Start with Python 3.11 if already available; test installed package imports and one inference before selecting the final dependency pins. On Apple Silicon the current wheel is a plausible direct install. Do not assume an Intel wheel exists for the latest version.
- Convert OpenCV BGR frames to RGB. Use increasing millisecond timestamps, preserve source timing, and separate playback FPS from capture FPS for slow motion. Use VIDEO mode to process all frames sequentially.
- MVP outputs: annotated frames/video, per-frame landmark CSV, JSON metric summary, provenance, quality status, and coach review prompts. Keep the LLM out of measurement; later it may translate verified measurements into explanations.
- Initial features: visible-side knee/elbow camera-plane angles, torso inclination in the image, head/hip displacement relative to a fixed camera reference and initial body-size scale. Convert normalized x/y to pixel coordinates before angles, because width and height differ. Never re-center every frame around the hip when measuring hip drift.
- Manual stride/contact frame labels are preferable to pretending wrist acceleration identifies true contact. Refuse metrics if required joints are missing, cropped, low confidence, or viewing angle is unsuitable.

### Gaps
- No execution or dependency installation occurred in this research task. Binary model URL returned an unsupported binary-content response to web fetch, so the implementation must verify an actual download and task load.
- No baseball-specific accuracy guarantee, universal ideal joint angle, or validated coaching thresholds were found for this generic model.

## What are the measurement limits?

### Takeaway
Single-camera pose is useful for review and repeatability, but estimated coordinates must not become unsupported bat-speed, true 3D biomechanics, or scouting grades.

### Cited Findings
- The linked BlazePose GHUM model card declares Apache 2.0, excludes metric-accurate depth applications, and warns of degradation/jitter with lighting, motion and occlusion. Its depth is inferred using synthetic GHUM fitting, and it cautions against distant subjects or hidden heads. — [Model card](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20BlazePose%20GHUM%203D.pdf)
- Current Tasks documentation describes world-coordinate outputs in meters; this is an output convention, not a stated baseball measurement accuracy. The older linked model card discusses scale ambiguity, so these documents should not be collapsed into a claim of calibrated motion capture. — [Python output guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker/python); [Model card](https://storage.googleapis.com/mediapipe-assets/Model%20Card%20BlazePose%20GHUM%203D.pdf)
- OpenCap offers multi-camera capture with 2+ iPhones, calibration and cloud computation; it also now offers a monocular beta. — [OpenCap](https://www.opencap.ai/); [Multi-camera setup](https://www.opencap.ai/get-started)

### Inferences
- A projected shoulder/hip line angle is not true transverse-plane hip–shoulder separation. Wrist speed is not bat speed. Generic body keypoints do not track the bat, ball, impact, exit velocity, or launch angle.
- Capture guidance for prototype: fixed tripod, full body and bat visible, well-lit scene, one hitter, known camera viewpoint, original high-frame-rate video when available, no edited slow motion. Record handedness explicitly and handle lead/trail mapping.
- Long-term measurement work needs synchronized calibrated views or paired reference instrumentation, then baseball-specific validation. Separate observation, possible explanation, and coach-approved experiment; do not claim corrective causality from one clip.
- Evaluate angle/frame agreement against manual labels and reference instrumentation on held-out hitters. Split datasets by athlete/session, not neighboring frames. Test left/right hitters, camera types, clothes, lighting, body sizes and skill levels.

### Gaps
- This investigation did not establish OpenCap baseball swing validity, commercial terms, or which monocular features transfer to fast batting. It should be evaluated as a later research option, not assumed solved.

## Which GitHub projects are useful?

### Takeaway
MediaPipe is the lowest-friction baseline; MMPose is a serious alternative for custom pose training. Existing baseball demos provide architectural ideas but not evidence that coaching works.

### Cited Findings
- MediaPipe repository has Apache 2.0 licensing. — [License](https://github.com/google-ai-edge/mediapipe/blob/master/LICENSE)
- MMPose is a PyTorch toolbox with 2D/3D tasks, whole-body models, RTMPose families, dataset customization, training, evaluation and deployment documentation. Repository license is Apache 2.0. — [README](https://github.com/open-mmlab/mmpose/blob/main/README.md); [Repository](https://github.com/open-mmlab/mmpose)
- Ultralytics repository uses AGPL-3.0. This differs from Apache-licensed candidates and must be considered before choosing it for distribution. — [License](https://github.com/ultralytics/ultralytics/blob/main/LICENSE)
- `andrew9990828/baseball-swing-analysis-capstone` describes a side-view pipeline with pose extraction, rough swing events, metrics and small professional baselines. Its README explicitly identifies contact as a proxy, no bat/ball tracking, slow-motion timing problems, angle wrapping, and invalid hip drift from hip-centered normalization. GitHub metadata returned no license (`license: null`) during this review. — [Project](https://github.com/andrew9990828/baseball-swing-analysis-capstone)
- OpenCap's current core repository is under `opencap-org`, rather than the older Stanford organization path. — [OpenCap core](https://github.com/opencap-org/opencap-core)

### Inferences
- Build original application code around official MediaPipe APIs; do not copy the unlicensed baseball demo. Its documented failure modes are useful design-review checks.
- MMPose/RTMPose is a later benchmark candidate if MediaPipe struggles on occluded swing poses, with increased dependency and training complexity.
- Bat detection needs dedicated bat endpoints/shaft labels and temporal tracking. Generic object bounding boxes alone will not provide precise bat angles or calibrated speeds.

### Gaps
- No alternative was benchmarked on the user's video. Repository claims are authors' descriptions, not independently reproduced results. No public project found here supplies a validated end-to-end professional scouting system.
