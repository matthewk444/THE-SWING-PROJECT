# Swing biomechanics, valid feedback, and delivery effort

## What can the first product responsibly measure and explain?

### Takeaway
Build a video review and within-hitter comparison assistant first. Single-camera pose estimates are useful candidate observations, but a scientific-looking skeleton does not itself validate 3D rotations, forces, or batting outcomes.

### Cited Findings
- OpenCap's peer-reviewed 2023 system uses two or more smartphone views, triangulation, biomechanical constraints and simulations. Its ten-person validation covered walking, squatting, chair rise and drop jumps; mean joint-angle absolute error was 4.5 degrees. These are not batting accuracy results. The paper explicitly discusses generalization to tasks and populations absent from training data. [OpenCap original paper](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011462)
- A 29-player elite batting study used a DARI markerless system to study active hip motion; lead and trail hip active ranges differed. It studied asymptomatic players and does not establish one universally optimal swing. Full page access was blocked, so only its indexed abstract/method excerpts were verified. [Original study](https://pmc.ncbi.nlm.nih.gov/articles/PMC8220628/)
- In a 26-player high-school pitching-machine experiment, knowing the next pitch type reduced timing errors relative to randomized unknown pitches. The study used optical motion capture and a force platform. [Kidokoro et al., 2020](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0230385)
- A bat-grip experiment in 14 adult hitters found different timing and kinematics for normal versus choke-up grip, including lower bat velocity with the choke-up grip. [Effects of Bat Grip on Baseball Hitting Kinematics](https://doi.org/10.1123/jab.25.3.203)

### Inferences
- Proposed MVP metrics, pending validation: manually confirmed foot-plant-to-contact interval; normalized projected head and pelvis displacement; projected lead-knee included angle; projected stride displacement relative to a fixed in-plane reference; and distributions of those measurements across comparable swings. Name these explicitly as 2D observations, not anatomical 3D angles. A nose point is a head-position proxy, not a direct head center.
- Use image pixel coordinates or correct for frame aspect ratio before geometry. Normalized x and y coordinates have different units on nonsquare images. Preserve handedness, view direction and a fixed camera reference. Avoid normalizing by shoulder width during rotation because the denominator changes with foreshortening.
- Require full body visibility, a stationary camera, useful lighting and a clear view of relevant joints; test 120/240 fps capture when available. Higher frame rate is a proposed capture preference, not a guaranteed accuracy threshold. Verify original capture speed: slow-motion files can play at 30 fps despite higher acquisition frame rate. A 240 fps acquisition interval is 4.17 ms; 30 fps is 33.3 ms (arithmetic, not measured system performance).
- Keep absent or occluded contact events unknown. A wrist velocity peak is not proof of bat-ball contact. Store manual event definitions and annotation uncertainty, including no-stride swings and swing-and-miss alternatives.
- Single-view shoulder-line minus hip-line orientation is not true transverse-plane hip–shoulder separation. Body-pose output alone must not become measured bat speed, attack angle, exit velocity, ground reaction force, joint torque, weight transfer percentage, injury prediction or an MLB scouting grade.
- First feedback format: observation with frame evidence; confidence/visibility limitations; a question for the coach; one controlled practice experiment; a repeat measurement and external outcome. Example: compare head-displacement variability over five comparable tee swings, review video with a coach, then repeat under the same setup. Do not prescribe a universal target value or claim that reducing movement necessarily improves hitting.
- Separate tee, front toss, machine and live pitching; tag pitch location/speed, bat dimensions, handedness and intent. Do not treat mechanically different successful swings as automatically flawed. Scouting value initially comes from organized evidence, comparable longitudinal clips, measurements and coach notes.

### Gaps
- No study found here validates this project's chosen pose model, camera protocol or metrics on baseball hitters. No defensible universal ideal angle, stride percentage or head-displacement threshold was established.
- No evidence found that automated feedback from the proposed MVP improves batting outcomes. This must be studied independently of landmark detection accuracy.

## How should accuracy and player benefit be validated?

### Takeaway
Separate measurement validity, consistency, coaching agreement and actual player benefit. Passing software tests is not a biomechanics validation study.

### Cited Findings
- The original pitchAI validation compared single-camera pitching to optical marker-based capture using time-series RMSE and discrete-event Bland–Altman analyses, among other statistics. It is pitching evidence, not batting evidence, but illustrates a reference-comparison design. [Original pitchAI validation](https://www.tandfonline.com/doi/abs/10.1080/14763141.2022.2137425)
- The OpenCap study compared against marker-based motion capture and force plates, and separately assessed changes under experimental movement conditions. [OpenCap validation design](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011462)

### Inferences
- Proposed pilot (planning numbers, not statistical power claims): 20–40 consenting hitters, 5–10 swings per capture condition, two sessions, both batting sides, several body sizes and skill levels. Start with adults; broaden age populations only after appropriate consent and explicit validation.
- Annotate events and visible joint locations independently by two trained reviewers; adjudicate disagreements. Store source video, timestamps, capture fps, view, event definition, annotator identity/version and confidence. Compare automatic events to consensus labels in milliseconds and frames.
- Measure 2D landmark error relative to visible body scale, angle/displacement error against manually digitized same-view references, and detection coverage/abstention rates. Manual 2D labels validate 2D extraction only; obtain synchronized calibrated multicamera or marker-based lab data before claiming 3D joint accuracy. Use external bat sensors/radar/ball tracking for independent outcome comparisons.
- Report MAE, bias and limits of agreement, per-player error, subgroup/device/lighting performance, and failure rates. Do not rely on correlation alone. Estimate test–retest noise and display a change as inconclusive if smaller than measured uncertainty.
- Split any learned-model evaluation by hitter and recording session/site. Frames or swings from the same hitter should not appear across train/test partitions. Hold out a final unseen test set before tuning thresholds.
- Ask coaches to rate whether observations are visible, useful and actionable without showing algorithm grades first. Later run a preregistered prospective comparison of coach+tool versus usual coaching with baseline and follow-up, comparable pitch tasks and independent contact-quality outcomes. Choose sample size from pilot variability and meaningful outcome targets, not a guessed number.
- Predefine metric-specific release gates after pilot error estimation. Publish a short model card with intended camera setup, population, limitations, model/version, dataset provenance and error intervals. Preserve coach edits rather than overwrite them.

### Gaps
- Need partner hitters, coach reviewers and reference equipment access. No measured baseline errors or power calculation exist yet. Lab validation prices require quotes.

## What architecture, effort and budget make sense?

### Takeaway
An overnight deliverable can be a real analysis scaffold with reproducible examples and clear limitations. A trustworthy coaching product requires a data collection and validation program beyond the UI.

### Cited Findings
- OpenCap exposes Apache-2.0 source repositories and combines video pose estimation, synchronization, triangulation and inverse kinematics. The paper distinguishes its academic hosted service from commercial use support. Reusing code does not imply access to hosted services or validation on baseball swings. [Original paper and code availability](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1011462)

### Inferences
- Suggested architecture: local video import → metadata/quality checks → pose inference adapter → timestamped landmarks → coach-confirmed event editor → deterministic geometry with missing-data guards → evidence-linked observations → session comparisons/export. Keep measurement code separate from advice. If an LLM is added, let it verbalize approved structured evidence and cite frames; it should not invent missing measurements or decide that a hitter has a flaw.
- Use a local Python prototype with OpenCV and a pose-model adapter; Streamlit is suitable for quick analyst review. Save immutable raw input and versioned JSON results, with SQLite for player/session indexing later. Avoid uploading identifiable player video by default. Track permission to store/use footage, deletion and training consent separately.
- Planning estimates assuming one experienced developer, existing laptop and access to consenting footage: tonight, 4–8 hours for research, runnable scaffold, synthetic/reference demonstration and checks; 2–4 weeks for controlled-video MVP with overlays, event correction and exports; another 4–8 weeks for a coach pilot and measurement evaluation; 3–6+ months for custom bat tracking, calibrated 3D or materially validated recommendations. These phases overlap and are not delivery commitments.
- Planning-only cash allowances, excluding labor and assuming existing phones/laptop: $0–$100/month for local-first early software/service usage; $100–$500 for mounts, lighting and calibration supplies if needed; $2,000–$15,000 reserved for a small organized annotation/coach/reference-data pilot. These are discretionary budget envelopes, not researched vendor quotes. Lab work may substantially exceed them. Calculate labor as actual hours × agreed rate; the largest uncertainty is data/reference access and review time.
- A practical moat is consented, varied swing video linked to trusted labels and outcomes, plus a workflow coaches trust. Training a huge new foundation model is unnecessary for the first useful product.

### Gaps
- No current vendor pricing quotes, measured inference throughput, hosting workload, user count, data licensing arrangement or available hardware inventory. Final costs must follow a pilot benchmark and partner quotes.
