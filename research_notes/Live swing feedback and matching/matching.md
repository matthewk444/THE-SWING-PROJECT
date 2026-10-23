# Named-player swing resemblance and legitimate references

## Can we obtain a small openly licensed actual MLB reference set now?

### Takeaway
One credible, explicitly licensed named MLB batting-video candidate was found, but no ready-made, validated, openly licensed multi-player MLB pose bank was established. Build user-supplied named reference comparison now; do not fabricate MLB templates or advertise a league-wide nearest-player result.

### Cited Findings
- Wikimedia Commons hosts **Dustin PedroiaBatting.ogv**, own work by **Elgaard**, dated **April 18, 2014**, showing Pedroia against Toronto. The file is **6.72 seconds, 1920×1080**, listed under **CC BY-SA 3.0** with attribution, license-link, change-notice, and share-alike requirements. Its page provides the original download and SHA-1 `f44221d2bc7096908668b6904c1facc9619668d5`. [File and license](https://commons.wikimedia.org/wiki/File:Dustin_PedroiaBatting.ogv)
- The Commons baseball-video category includes that clip, pitching clips, interviews, historical footage, and other baseball material. This is a discovery source, not a curated swing-matching bank. [Category](https://commons.wikimedia.org/wiki/Category:Videos_of_baseball)
- MLB-YouTube offers broadcast activity annotations for 20 postseason games, not a licensed player-pose reference gallery; its inspected repository lists download/extraction scripts and action labels, without establishing commercial footage permission. [Original repository](https://github.com/piergiaj/mlb-youtube)
- OpenBiomechanics identifies athletes anonymously; its data have noncommercial and professional-organization restrictions. It cannot legitimately provide named MLB-player templates. [Datasheet](https://github.com/drivelineresearch/openbiomechanics/blob/main/DATASHEET.md)
- An existing baseball swing capstone asks users to place professional clips into `data/raw/pros/` and warns its comparison is not definitive quality diagnosis. It is an implementation example, not proof of a licensed reference bank. [Capstone repository](https://github.com/andrew9990828/baseball-swing-analysis-capstone)

### Inferences
- The Pedroia clip is a legitimate candidate for a **single real-reference demonstration**, subject to visual and pose quality review. It has not been downloaded or analyzed in this research, so usable full-body coverage, swing completeness, camera view, and pose reliability remain unknown.
- One reference supports “Compare to this Dustin Pedroia clip,” not “You swing most like Dustin Pedroia.” A multi-reference ranking must say “closest among your N eligible reference clips.”
- Keep licensed media and any distributed adaptations in a separately attributed reference package; do not casually assume pose extraction erases source-license obligations. Avoid endorsement claims.
- The practical MVP accepts reference uploads with player label, actual batting side, camera view, source URL, creator, license/permission statement, date, clip timestamps, and optional MLB ID. A user-entered player label is unverified metadata, not identity recognition.
- Preserve per-reference provenance: original file hash, source page, retrieval date, model/version, processing settings, event boundaries, quality metrics, and transformations. Never generate a numerical player signature based only on reputation or manually invented angles.

### Gaps
- No curated bank of several named MLB players with full swing pose sequences and clear redistribution rights was found in this bounded search.
- No conclusion about a video's usability can be made from its license alone. The Pedroia candidate requires actual review before deployment.
- Contemporary MLB video access, dataset access, and commercial model/footage rights are separate questions; this research does not establish authorization for broadcast reuse.

## How should pose-sequence resemblance work?

### Takeaway
Use normalized, quality-filtered movement sequences and constrained temporal alignment. Separate pose resemblance from timing, and report relative distance rather than an invented percentage probability.

### Cited Findings
- MediaPipe predicts 33 approximate body landmarks in image/world coordinates and offers image, video, and live-stream modes with detection/tracking thresholds. These are model estimates; the listed landmarks do not include the bat. [Official guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker)
- DTW aligns multidimensional sequences of unequal lengths through a monotonic path minimizing accumulated frame distance. Exact dynamic programming is quadratic in sequence lengths. `tslearn` supports Sakoe–Chiba band, Itakura slope, and path-length constraints. DTW does not satisfy the triangle inequality. [Official DTW guide](https://tslearn.readthedocs.io/en/stable/user_guide/dtw.html)
- A path-length-constrained DTW implementation returns both alignment path and cost, enabling an inspectable synchronized comparison. [API documentation](https://tslearn.readthedocs.io/en/stable/gen_modules/metrics/tslearn.metrics.dtw_path_limited_warping_length.html)

### Inferences
- Pipeline: trim one swing → confirm hitter/crop → extract landmarks → reject unusable frames → normalize coordinates → derive feature sequence → align within corresponding swing phases → rank eligible references → show synchronized playback and feature contributions.
- Correct image aspect ratio before angles/distances. Center at pelvis and use a robust torso/body scale. Do not independently normalize every joint or remove all frame-to-frame displacement; that would erase actual movement. Keep head/hip displacement relative to a fixed stance anchor as separate features.
- Prefer initial features such as visible elbow/knee angles, trunk inclination, normalized wrist paths, stance/stride pattern, and head displacement. These are projected-view descriptors, not verified 3D biomechanics or bat-path measurements.
- Use confidence-weighted frame costs only when enough comparable joints exist. Mask missing joints and impose a minimum coverage requirement; do not allow missing features to make a reference appear closer. Reject prolonged gaps instead of large interpolations.
- Establish onset/plant/contact/follow-through anchors manually at first. Constrain DTW inside phases so a stance does not align to follow-through. Use path-normalized cost for display, explicitly documenting whether the optimization itself is sum-cost or normalized-cost.
- Report two separate outputs: shape resemblance after alignment and actual phase durations in milliseconds. Aggressive warping can hide timing differences relevant to development.
- For short standardized sequences, exact constrained DTW is a reasonable first baseline. Compare against simpler phase-resampled Euclidean distance before adding learned embeddings.
- Use several genuine swings per player eventually. Aggregate robustly per player rather than letting a player with many clips win more often. Do not average unaligned raw skeletons into a fictitious representative swing.

### Gaps
- No validated baseball-specific weights, similarity thresholds, or percentage calibration were established. Initial weights and rejection cutoffs are engineering choices requiring evaluation.
- A low DTW distance does not imply equal swing quality, power, bat speed, or professional potential.

## What confounders and validation gates are necessary?

### Takeaway
Match only comparable capture conditions initially. A ranked result can always be produced mathematically, but must be withheld when the reference bank or video quality is inadequate.

### Cited Findings
- Google's pose task is optimized for on-device fitness applications and returns estimated landmarks; its documentation does not validate this system for bat-speed measurement or MLB-player resemblance. [Official guide](https://developers.google.com/edge/mediapipe/solutions/vision/pose_landmarker)
- DTW's temporal flexibility is explicitly controllable through constraints. This supports exposing alignment and limiting distortion rather than treating time-warped distance as raw mechanical equivalence. [DTW guide](https://tslearn.readthedocs.io/en/stable/user_guide/dtw.html)

### Inferences
- Camera azimuth/elevation, perspective, crop, zoom, moving cameras, occlusion, body proportions, clothing, motion blur, FPS, slow-motion playback, bat, pitch location, drill type, and intended swing effort can change apparent resemblance. Filter by declared view and drill; show uncertainty rather than claiming view invariance.
- Default to the same batting side. Optional mirror-normalized comparison must reflect coordinates **and swap anatomical left/right labels**, then label it as mirrored. Screen mirroring alone is not anatomical normalization. For switch hitters, store the actual side of that swing.
- Do not use single-camera inferred world coordinates as a universal camera-invariant truth. Treat 3D comparison as experimental until validated with controlled multiview/reference data.
- MVP outputs: reference name and provenance, rank among eligible references, lower-is-closer distance, observed shared features, largest differences, overlap coverage, and synchronized overlays. Do not present “92% like Ohtani” without an explicitly calibrated meaning.
- Minimum QA: self-match; repeat export; translation/scale/aspect handling; correctly mirrored handedness; time-stretch with preserved timing difference; missing-pose refusal; different-camera refusal; reference labels/provenance preserved. Never use synthetic fixtures as named MLB references.
- Research validation: hold out entire players/sessions where relevant, test same-player versus different-player retrieval under matched and mismatched views, have blinded coaches judge resemblance, and report ranking stability under landmark noise. Include an “insufficient references” or “no reliable match” state.
- Suggested initial product language: **“Movement resemblance among your reference clips. This does not measure hitting ability or recommend copying another player's swing.”**

### Gaps
- No published accuracy claim for the proposed matching pipeline can be made before real-reference evaluation.
- A small hand-picked bank is not representative of MLB and cannot identify the globally closest MLB swing.
