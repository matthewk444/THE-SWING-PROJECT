# Live swing feedback and MLB reference matching

## What do current products establish, and where can this product differ?

### Takeaway
Differentiate through trustworthy capture guidance, automatic between-rep review, evidence-linked observations and comparable references. A skeleton overlay or a list of mechanical faults alone is not a strong product distinction.

### Cited Findings
- Onform officially offers automatic swing capture, up to four camera angles, slow motion, drawings, voice commentary and side-by-side/overlay comparisons. These are product capabilities described by the vendor, not independent proof of performance improvement. [Onform baseball](https://onform.com/sports/baseball/)
- Onform's live drawing feature works in the camera view before recording, supporting setup feedback and screen mirroring. This is a useful distinction between live setup guidance and mechanical advice during an explosive swing. [Onform documentation](https://support.onform.com/article/110-live-drawing-helps-analyze-setup-form-before-recording)
- SwingAI advertises a ten-second side-on clip, analysis under thirty seconds, one focus/drill, and coach overrides. Its inspected page still says available Spring 2026 despite the present October 2026 research date; availability and efficacy were not verified by using the product. Marketing mockup percentages should not be treated as measured evidence. [SwingAI official page](https://getswingai.com/)
- Reboot Motion positions itself as organizational biomechanics infrastructure with APIs, motion-capture/video processing and single-camera capture. Its requested-analysis API supports primary, comparison and population segments, requires customer credentials, and creates reports from organization-provided data. It is not an openly available MLB reference dataset. [Reboot official site](https://rebootmotion.com/); [API comparison tutorial](https://docs.rebootmotion.com/tutorials/create-requested-analyses)

### Inferences
- Proposed user flow: Choose handedness and session type → Set up camera → Capture → Automatic short replay → One observation with evidence → Choose a next-rep focus → Review a short set → Compare against personal baseline or a compatible reference.
- Live Setup: full-body framing outline, feet/lead knee visibility, one-person check, camera stability and lighting guidance. Display READY only when basic capture conditions pass; this means ready to capture, not good mechanics. Audio capture prompts are optional.
- During Swing: record quietly, retain a pre/post ring buffer and use a state machine with a cooldown to prevent duplicate detections. Avoid a stream of instructions during the movement. The useful near-real-time moment is after the swing completes.
- Review: show the clip at reduced speed with visible event markers. A result card should say what was observed, which frames support it, whether it differs from the player's comparable swings and what remains uncertain. Example: "Your lead-knee angle in this camera view changed between foot plant and contact. Review the highlighted frames with your coach." A camera-obscured knee should instead produce "Move camera so the lead knee is visible."
- First establish a handful of comparable baseline swings. Ask a coach to select one experiment for the next set, then compare outcome and repeatability rather than reward resemblance to an MLB hitter. Keep any drill suggestion explicitly separate from the measured observation.
- A meaningful initial differentiator is the loop of Capture → Evidence → One experiment → Repeat comparison, plus honest abstention. This is a product proposal, not a proven market advantage.

### Gaps
- No independent efficacy validation was found on the inspected vendor pages. No accounts were created and no product latency or availability was tested. Product features may differ by device or plan.

## What can MLB swing similarity mean without overstating it?

### Takeaway
Present a nearest-reference retrieval feature, not a percentage of professional ability. Separate aligned motion shape from real timing, and require compatible views and trustworthy reference metadata.

### Cited Findings
- A Waseda research paper proposes skeleton-based temporal synchronization of baseball motion videos using movement information and left/right inversion correction. It evaluates motion-matching accuracy; that is not validation of talent grading, outcome prediction or a prescribed ideal swing. [Osawa et al., Motion Matching Based on Pose Similarity Using Movement of Body Parts](https://www.ams.giti.waseda.ac.jp/data/pdf-files/2022_GCCE_osawa.pdf)
- A 2025 preprint on baseball pitching explicitly identifies a limitation of dynamic time warping: temporal alignment can erase meaningful rhythm differences. Its proposed coordination metric is pitching research, not a validated batting prescription. [Fujii and Tachibana preprint](https://arxiv.org/abs/2503.14821)
- Statcast defines attack angle/direction through the bat sweet spot's movement at impact and swing-path tilt through the bat path over the preceding 40 milliseconds. These are bat metrics, not 2D body-pose measurements. MLB also notes timing affects attack angle and direction. [Official Statcast definitions](https://baseballsavant.mlb.com/leaderboard/bat-tracking/swing-path-attack-angle)
- A primary 18-collegiate-player 2D study found no meaningful head/stride movement correlations and discusses limitations of generalization and the absence of an established definition of keeping a still head. It does not support a simplistic "less head movement always better" rule. [Haag, Baseball Research Journal](https://sabr.org/journal/article/baseball-swing-stride-and-head-movement-relationships/)

### Inferences
- The reference unit should be a specific attributable clip/swing, with player, batting side, camera/view, session/context, event frames, frame timing, source, permissions and extraction version. Do not silently make one clip the timeless template of an entire player.
- Match only compatible body-pose features extracted by the same pipeline. Do not compare a youth's image-plane hand path to an MLB player's Statcast swing length in feet or attack angle and call it the same quantity. Public MLB aggregate statistics may enrich an informational player card but are not the matching signal for a body-pose comparison.
- Recommended initial scoring: event-anchored phase alignment, fixed-scale translation normalization, confidence masking, robust distances on a small documented feature set. Preserve camera aspect ratio. Handle left/right mirroring explicitly with lead/trail joint identities and a visible mirrored label. Camera orientation should be a filter; 2D normalization does not remove perspective.
- Show top available reference clips with reasons: "closest visible stride pattern in this library" and "different projected lead-knee motion." Include library size, view/context caveats and a no-compatible-reference state. Use ranked reference candidates or raw documented distances internally; do not convert arbitrary distance into "87% like Ohtani", pro readiness or a 20–80 scouting grade.
- Keep timing differences in milliseconds separate from phase-normalized shape plots. If using DTW, bound warping, anchor meaningful events and expose alignment. It must not transform a late sequence into an apparently identical rhythm.
- Prefer personal best/recent baseline as the default comparison; MLB reference is optional exploration. Similarity is descriptive and is not evidence that copying the reference will improve performance.

### Gaps
- No validated method was found for interpreting a phone-video-to-MLB motion score as talent, mechanical quality or future performance. No professionally licensed reference corpus or same-view multi-angle ground truth has been acquired for this project.
- No tested feature weights or distance thresholds exist. Coach relevance and retrieval ranking must be evaluated on held-out hitters and recording environments.

## Which acceptance tests make the experience credible?

### Takeaway
Test operational reliability and scientific claims separately. A working webcam demo is not evidence of accurate hitting analysis.

### Cited Findings
- Onform's documentation notes skeleton tracking can be affected by lighting, obstruction, bulky clothing and complex backgrounds; these are concrete failure cases to include in a capture test matrix. [Official Onform user guide](https://support.onform.com/article/153-user-guide-onform-video-analysis-app)
- The Waseda matching paper explicitly addresses left/right inversion and changing movement speed; these motivate adversarial alignment tests instead of a visually pleasing happy-path demo. [Motion matching paper](https://www.ams.giti.waseda.ac.jp/data/pdf-files/2022_GCCE_osawa.pdf)

### Inferences
- Functional gates: denied/missing camera produces a clear recovery path; stop releases the camera; no player/multiple players/occluded feet suppresses technique output; lighting failure offers a capture fix; repeating start-stop creates no duplicate loops; empty reference library never displays fabricated MLB matches; stale results cannot appear under a new player or swing.
- Capture gates: verify actual sample timestamps, dropped-frame handling, frame dimensions and aspect ratio; test slow-motion imports where playback and acquisition fps differ. Pause/resume and mobile backgrounding must invalidate stale timing. Display unavailable timing when acquisition speed is unknown.
- Swing segmentation: evaluate against manually labeled complete swings plus practice waggles, check swings, swing-and-miss clips, empty scenes and multiple people. Report event precision/recall, duplicate captures, missed swings and onset/end timing error, not merely aggregate model confidence.
- Latency proposal, explicitly a design target rather than a measured claim: quality cues within 500 ms and a usable replay/first observation within five seconds after swing completion on a named supported device. Measure p50/p95 over a session and thermal load; do not promise these before measurement. Capture must remain smooth when optional analysis is slow.
- Geometry invariants: translating/resizing a clip must preserve normalized features; horizontal mirroring with correct joint remapping must preserve canonical lead/trail results; non-square dimensions must not alter angle definitions; missing joints must not be replaced with zeros or interpolated through entire occluded phases.
- Matching tests: self-reference ranks first; modest capture noise does not radically reorder references; a different viewpoint gets rejected or clearly flagged; time-stretched copies can retain similar shape while showing changed duration; unmatched/out-of-library examples can abstain. Rank stability and expert-rated top-k relevance should be reported by camera, handedness and age/skill group.
- Pilot proposal: collect 20–40 consenting hitters with repeated sessions, several camera conditions and two independent coach reviewers. This is an operational starting point, not a powered efficacy sample. Split evaluation by hitter/session/site and predefine a held-out set. Validate displayed 2D measurements against manual digitization; use calibrated reference systems for any future 3D claims.
- Every generated observation should trace to stored values, source frames and rule/model version. Advice should disappear when evidence is insufficient. Separately test whether coaches find the cue understandable/actionable and whether a prospective training comparison improves independent outcomes; similarity alone cannot answer that.

### Gaps
- No acceptance results are claimed here. Thresholds require a benchmark on actual target devices and footage; no clinical or development efficacy study has been conducted.
