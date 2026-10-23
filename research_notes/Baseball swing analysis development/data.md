# Baseball swing datasets, Statcast, and data strategy

## What public data can support this project?

### Takeaway
Use public datasets to research measurement and contextualize outcomes; collect consented, standardized player video to develop the actual coaching product. None of the inspected datasets supplies a validated mapping from a phone swing video to the best intervention for that individual.

### Cited Findings
- Baseball Savant's bat-tracking leaderboard says coverage begins in the second half of 2023. It defines swing speed at the bat's sweet spot and swing length as bat-head travel through 3D space; current competitive-swing filtering is more nuanced than simply averaging every swing. [MLB leaderboard](https://baseballsavant.mlb.com/leaderboard/bat-tracking)
- CSV documentation includes pitch context, player IDs, exit velocity, launch angle, attack angle, attack direction, swing-path tilt, and bat/ball intercept relative to hitter position. These are distinct physical quantities; attack angle is not launch angle. [Savant CSV dictionary](https://baseballsavant.mlb.com/csv-docs)
- `pybaseball` provides Python access to pitch-level Statcast data, including `statcast(start_dt=..., end_dt=...)`, with MIT-licensed code. [pybaseball](https://github.com/jldbc/pybaseball)
- Driveline OpenBiomechanics (OBP) lists 677 hitting trials from 98 athletes, including 604 paired HitTrax records. The cohort is predominantly collegiate, ages 17–31, with 496 right-handed and 181 left-handed trials. Its machine setting is approximately 65 mph from 40 feet. Athlete identifiers are anonymized and data collection had IRB approval. [OBP datasheet](https://github.com/drivelineresearch/openbiomechanics/blob/main/DATASHEET.md)
- OBP provides cleaned C3D marker motion capture, full time-series signals, metadata, and point-of-interest tables. Large C3D/full-signal archives now come from GitHub Releases; summary CSVs stay in the repository. Its example swing viewer explicitly describes derived contact/bat metrics as exploratory. [OBP hitting documentation](https://github.com/drivelineresearch/openbiomechanics/blob/main/baseball_hitting/README.md)
- MLB-YouTube contains 20 postseason games from 2017, over 42 hours, and 4,290 activity clips, including 2,506 labeled swing examples. Labels cover actions/results such as swing, hit, strike, foul, and bunt rather than mechanics diagnoses. [Original dataset repository](https://github.com/piergiaj/mlb-youtube)
- BaseballCV lists detection datasets and pretrained tracking models, plus 50 unannotated amateur batting-practice videos. These can support localization research, but unannotated videos do not provide corrective-coaching labels. [BaseballCV](https://github.com/BaseballCV/BaseballCV)

### Inferences
- Recommended separate pipelines: (1) video → observable movement and confidence; (2) imported Statcast → contextual player profile; (3) coach-reviewed hypotheses and experiments. Do not pretend Savant exposes full skeleton trajectories or that publicly available video is a supervised coaching dataset.
- For tonight, implement local video upload/review, manual event tagging, deterministic measurements, confidence flags, player/session records, and a clearly labeled synthetic demo. Add a Savant CSV adapter without automatically bulk-downloading video.
- OBP is a strong research reference for metric definitions and repeatability, subject to its rights restrictions. It is too small and domain-specific to establish universal mechanics rules or youth scouting norms.

### Gaps
- No inspected source supplied a large, clearly commercially licensed baseball dataset with synchronized consumer-camera video, lab ground truth, coach labels, and longitudinal intervention outcomes.
- Public CSV availability does not establish availability of all original Hawk-Eye trajectories. Video-to-pitch alignment and field missingness must be audited empirically.
- Dataset links were inspected, but archives/videos were not downloaded or validated for completeness during this research.

## What rights and collection requirements matter for a hitter/scout product?

### Takeaway
Code licenses, model-weight licenses, source-video rights, and dataset rights must be tracked separately. The most relevant biomechanics dataset has restrictions directly relevant to professional scouting.

### Cited Findings
- OBP data and biomechanics documentation use CC BY-NC-SA 4.0 with an additional stated exclusion: professional-sports/financial-analysis organization employees, contractors, associates, or significant shareholders require a separate written paid license. The license also discusses future profit intent. [Actual data license](https://github.com/drivelineresearch/openbiomechanics/blob/main/LICENSE-DATA.md)
- OBP source code is separately MIT-licensed; that permission does not extend to its data or biomechanics documentation. [Code license](https://github.com/drivelineresearch/openbiomechanics/blob/main/LICENSE-CODE.md)
- BaseballCV describes AGPL community and commercial licensing; review component/model licenses before proprietary team integration. [Licensing section](https://github.com/BaseballCV/BaseballCV#-license)
- MLB's terms restrict reuse beyond specified personal use. Public access is not blanket commercial permission. [MLB terms](https://www.mlb.com/official-information/terms-of-use?affiliate_id=false)

### Inferences
- Do not bundle OBP data, derivative trained weights, or MLB broadcasts into the initial product. Keep adapters and source links; clear intended use with rights holders before commercial/team deployment.
- Recommended collection record: consent and permitted uses; athlete ID; age band/handedness; session/date; camera position and frame rate; bat length/weight; drill type; pitch speed/location if known; event frames; measured ball outcomes; coach annotations; annotation confidence; storage/deletion preference. Separate identity from motion data and use local storage by default.
- Obtain explicit athlete permission for analysis, separate opt-in for training/reuse, and guardian permission where appropriate. These are product requirements proposed here, not an assertion that one universal consent form satisfies all jurisdictions.
- Build a rights manifest per data source and dependency. Audit code, weights, annotations, footage, and intended commercial use independently.

### Gaps
- No commercial-use authorization for the specific project was established. The absence of an obvious license in MLB-YouTube's inspected root is not permission.
- No universal legal determination is made about dataset-derived weights or particular scouting deployments.

## How can measurements become credible advice and scouting information?

### Takeaway
Predictive associations are not proof that a mechanical change will help a hitter. Validate measurements first, then test coach-reviewed changes longitudinally with player-specific baselines.

### Cited Findings
- Powers and Yurko's 2025 preprint explains that timing changes the location along the swing where metrics are measured, and pitch recognition confounds swing/outcome associations. Their analysis conditions on count and pitch location and estimates contact/power tradeoffs. [Original research](https://arxiv.org/abs/2507.01238)
- OBP's datasheet cautions users about repeated trials per athlete and differing marker/force sample rates. [OBP datasheet](https://github.com/drivelineresearch/openbiomechanics/blob/main/DATASHEET.md)
- OBP's computer-vision materials distinguish provisional camera calibration from final lab-frame calibration and experimental reconstruction from independent biomechanical validation. [OBP computer vision documentation](https://github.com/drivelineresearch/openbiomechanics/blob/main/computer_vision/README.md)

### Inferences
- Split evaluation by athlete and session, not random adjacent frames; otherwise similar swings leak between training and testing. Keep a later-time test set for progress predictions.
- Annotate stride/plant/contact windows with two reviewers; compare event errors in milliseconds, landmark visibility, test-retest variation, and measurement error against reference equipment before publishing metrics.
- Start with questions such as “Does your head displacement vary between these comparable sessions?” and “Review this timing change with your coach.” Avoid claims like “Your hips must rotate X degrees” from uncalibrated 2D video.
- Match comparisons by camera view, drill, pitch type/location/speed, count, handedness, bat, and athlete level. Record fatigue and task intent where feasible. Report sample counts, missingness, uncertainty, and within-player changes.
- A trustworthy scouting output should separate directly observed features, context-adjusted statistics, and unvalidated hypotheses. Do not issue a single talent score or predict professional potential from a few swings.
- A pilot target of 10–20 consenting hitters with multiple sessions and repeated swings is a practical planning estimate for workflow/measurement validation, not a sufficient sample for proving universal advice. Later effectiveness evaluation needs prespecified outcomes and appropriate sample-size analysis.
- Coaching engine should initially be a transparent rule/report layer over verified observations, reviewed by a qualified hitting coach. An LLM may explain structured measurements, but should not invent measurements, diagnoses, or causal advice.

### Gaps
- The consulted sources do not establish a validated threshold for “good” head movement, stride length, hip–shoulder separation, or generic mechanics advice from one consumer camera.
- No evidence reviewed proves an initial model will improve player performance. That claim requires prospective testing of recommendations against a comparison condition.
