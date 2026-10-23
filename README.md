# THE SWING PROJECT

Local swing-video review prototype for hitter development and scouting research. It uses pretrained MediaPipe body tracking and explicit geometry; it is not a trained or validated baseball coaching model.

## Live Swing Lab

The browser lab adds live camera guidance, four-second pose capture after a three-second countdown, skeleton sample review, window trimming, video-window analysis, and experimental comparison against your own reference library. It does not automatically identify swings/contact or supply a bundled MLB reference bank.

With the pose model downloaded as described below, run:

```sh
cd '/Users/matthewkim/THE SWING PROJECT'
npm ci
npm run vendor
python3 serve_live.py --port 8502
```

Open `http://127.0.0.1:8502`. `npm ci` restores the pinned browser dependencies; `npm run vendor` copies the matching MediaPipe bundle/WASM assets into the served app. Once installed, only the server command is needed. Camera permission is requested when you choose **Enable camera**. The server is restricted to this computer; another phone cannot use this loopback URL. Phone camera support would require a separate HTTPS setup.

Use an unmirrored fixed side view, good lighting and a full-body frame with one hitter. Set the actual batting side, pitcher direction in the image, open/back camera view and practice type before capture. Stop the camera when finished; changing tabs also stops analysis. Camera settings, analyzed samples per second and worker inference time are different quantities. The browser skips frames and does not measure bat speed.

For reference matching, analyze a clip you have permission to use, trim the same movement window, supply a player/reference name and source URL plus permission/license note, then save it. The library requires the same batting side, declared view and drill. Names are supplied by you and are not verified identities. Matches include a projected-knee trace overlay across normalized time and feature differences. The displayed DTW shape distance is experimental: lower means closer among eligible library clips, not a calibrated probability, talent grade or recommendation to copy that hitter. No MLB signatures are fabricated. A single eligible reference does not establish the closest player in MLB.

The browser stores extracted reference features, timestamps, metadata and source notes in localStorage (maximum 12 references); it does not save or upload original video. Use Remove to delete a reference and export JSON for a backup. The captured rep and skeletons are held in memory until navigation/reload; explicit rep exports can include landmarks. Imported videos are read locally. The app does not intentionally send footage to a server or call an LLM. MediaPipe documentation includes performance/utilization telemetry language, so local processing is not a guarantee of zero network traffic. The library belongs to this browser and origin; `localhost` and `127.0.0.1` can have separate storage.

```sh
npm test
```

Nine JavaScript and seven Python tests passed. Isolated headless Chrome checks passed actual MediaPipe inference, synthetic-camera capture/countdown/abstention and track cleanup, generated WebM import and inference, reference import/persistence/removal, and mobile overflow. The module-WASM loader was corrected and verified. These checks used synthetic inputs, not the physical camera or a real hitter; they do not establish steady live latency, baseball measurement accuracy or coaching effectiveness. See [LIVE_LAB_REPORT.md](LIVE_LAB_REPORT.md) for sources, implementation limits and the reference-curation sprint.

## Original Streamlit review

Use Python 3.11. On this Mac, open the project in VS Code, then run these commands in its terminal:

```sh
cd '/Users/matthewkim/THE SWING PROJECT'
python3.11 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
mkdir -p models
curl --fail --location 'https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_full/float16/latest/pose_landmarker_full.task' --output models/pose_landmarker_full.task
.venv/bin/python -m streamlit run app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`. If the environment and model already exist, just run the final command. The model is Google's official [Pose Landmarker full bundle](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker). Review model and dependency terms before redistribution. The `latest` download URL can change; the downloaded asset's hash is recorded in `models/MODEL_MANIFEST.md`. Use `requirements-lock.txt` for the complete tested dependency set on this Mac.

## Review a swing

1. Record one hitter from a fixed side view with full body visible and good light. Use an unmirrored original video and consistent camera placement. Prefer high-frame-rate acquisition when available.
2. Upload an MP4, MOV or AVI that you have permission to analyze. Keep it within 100 MB, 20 playback seconds and 1,800 frames.
3. Select batting handedness and analyze. Inspect the overlay before trusting a measurement.
4. Use the frame slider to locate the review start, lead-foot plant and visible bat–ball contact. Enter their zero-based frame numbers and check the confirmation box after inspecting them. The current event workflow requires start ≤ plant < contact; uncertain or absent contact is not an established event.
5. Read the camera-plane observations and download the review/landmark JSON. Compare multiple similarly recorded swings with a coach.

The prototype measures projected lead-knee angle at two selected frames and horizontal nose range relative to the starting projected torso length. Nose position is a head-position proxy. Missing, cropped or low-score landmarks cause metrics to be withheld. Model scores are not calibrated error probabilities.

It does not measure bat speed, exit velocity, true 3D hip–shoulder separation, injury risk or scouting potential. It does not infer physical timing from slow-motion playback. No universal ideal angle or movement target is assumed. The feedback is a coach-review prompt and experiment suggestion, not proof of a flaw or a validated prescription.

## Tests

```sh
.venv/bin/python -m pytest -q
```

The tests cover geometry, handedness, aspect ratio, invalid events and missing/low-score landmark handling. Passing them does not establish baseball measurement accuracy or coaching effectiveness. See the research report for the separate real-video and reference-data validation plan.

## Files and privacy

`app.py` provides the review UI; `swing.py` contains inference, geometry and overlays; `tests/test_swing.py` checks deterministic behavior. `RESEARCH_REPORT.md` contains research sources, data/licensing considerations, phased roadmap and estimated effort. No sample athlete footage or baseball-trained model is supplied.

Uploaded video is processed through temporary local files that are removed after each operation. Results remain in Streamlit session memory until cleared. Downloaded results are files you control. The application does not intentionally upload footage or invoke an LLM. MediaPipe's current [package notice](https://pypi.org/project/mediapipe/) describes performance/utilization telemetry, so this is not a zero-network-traffic guarantee. Run as a local tool; public hosting would require a separate privacy, access-control and retention design.

Next development priorities are consented real-swing validation, a rights-cleared quality-reviewed reference bank, structured provenance, event-anchored comparison, coach annotations and persistent session records. Bat tracking and calibrated 3D come after measurement validation.

## Verified build

Seven tests passed on this Mac, including actual model inference on a synthetic blank clip and Streamlit interface initialization. The local server health endpoint returned `ok`. This verifies software execution, not real-swing measurement accuracy. VS Code was launched with this folder; its window could not be visually verified because screen access was not approved.
