"""Camera-plane swing review. No calibrated 3D or performance prediction."""
from pathlib import Path
import math
import cv2
import numpy as np

MODEL = Path(__file__).parent / 'models' / 'pose_landmarker_full.task'
EDGES = [(11,12),(11,13),(13,15),(12,14),(14,16),(11,23),(12,24),
         (23,24),(23,25),(25,27),(24,26),(26,28)]

def angle(a, b, c):
    u, v = np.array(a)-b, np.array(c)-b
    norm = np.linalg.norm(u)*np.linalg.norm(v)
    return None if norm < 1e-8 else float(np.degrees(np.arccos(np.clip(np.dot(u,v)/norm,-1,1))))

def point(frame, index, width, height, threshold=0.65):
    if not frame or len(frame) <= index:
        return None
    p = frame[index]
    if min(p['visibility'], p['presence']) < threshold or not (0 <= p['x'] <= 1 and 0 <= p['y'] <= 1):
        return None
    return np.array([p['x']*width, p['y']*height])

def review(result, start, plant, contact, handedness, player='Unnamed hitter'):
    frames = result['frames']
    if not 0 <= start <= plant < contact < len(frames):
        raise ValueError('Choose start ≤ foot plant < contact, within the video.')
    w, h = result['width'], result['height']
    # Right-handed hitter's lead leg is anatomical left; mirrored video must be corrected.
    hip, knee, ankle = (23,25,27) if handedness == 'Right' else (24,26,28)
    def knee_at(i):
        pts = [point(frames[i], j, w, h) for j in (hip,knee,ankle)]
        return angle(*pts) if all(p is not None for p in pts) else None
    ref = frames[start]
    shoulders = [point(ref,j,w,h) for j in (11,12)]
    hips = [point(ref,j,w,h) for j in (23,24)]
    scale = None
    if all(p is not None for p in shoulders+hips):
        scale = float(np.linalg.norm(np.mean(shoulders,axis=0)-np.mean(hips,axis=0)))
        if scale < 20:
            scale = None
    samples = [point(f,0,w,h) for f in frames[start:contact+1]]
    valid = [p for p in samples if p is not None]
    coverage = len(valid)/len(samples)
    head_range = None
    if scale and coverage >= 0.8:
        head_range = float(np.ptp([p[0] for p in valid])/scale)
    kp, kc = knee_at(plant), knee_at(contact)
    metrics = {'lead_knee_at_plant_deg':kp, 'lead_knee_at_contact_deg':kc,
               'nose_horizontal_range_torso_lengths':head_range,
               'nose_tracking_coverage':coverage}
    feedback = []
    if kp is not None and kc is not None:
        feedback.append(f'Projected lead-knee angle changes from {kp:.1f}° at plant to {kc:.1f}° at contact. Review these two frames with a coach; camera perspective can change the angle. No ideal target is assumed.')
    else:
        feedback.append('Lead-knee comparison withheld: required landmarks are obscured, outside the frame, or have low model scores. Refilm with the full lead leg visible.')
    if head_range is not None:
        feedback.append(f'Visible nose horizontal range is {head_range:.2f} starting torso lengths over the selected window. Compare several swings from the same fixed camera before changing your movement.')
    else:
        feedback.append('Head-movement metric withheld: insufficient nose coverage or starting torso reference. Use a fixed, unobstructed full-body camera view.')
    feedback.append('Development experiment: record five comparable swings, review contact quality with a coach, change one cue, then repeat. These observations do not establish the cause of a hitting problem.')
    return {'schema_version':1,'player':player,'handedness':handedness,
            'events':{'start_frame':start,'plant_frame':plant,'contact_frame':contact},
            'metrics':metrics,'feedback':feedback,
            'limitations':['2D projected measurements; not validated for baseball coaching.',
                          'Events are manually selected. Landmark scores are not calibrated accuracy.',
                          'No bat speed, exit velocity, true 3D separation, injury prediction, or scouting grade.',
                          'Clip playback timing may differ from capture timing; no physical timing is inferred.']}

def analyze(path, progress=None):
    import mediapipe as mp
    from mediapipe.tasks import python
    from mediapipe.tasks.python import vision
    if not MODEL.exists():
        raise ValueError('Pose model missing. Run the model download command in README.md.')
    cap = cv2.VideoCapture(str(path))
    try:
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        w,h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if not math.isfinite(fps) or fps <= 0 or w <= 0 or h <= 0:
            raise ValueError('Cannot decode video metadata. Export a standard MP4 and retry.')
        if count > 1800 or (count > 0 and count/fps > 20):
            raise ValueError('Trim to one swing: at most 20 playback seconds and 1,800 frames.')
        options = vision.PoseLandmarkerOptions(base_options=python.BaseOptions(model_asset_path=str(MODEL)),
                    running_mode=vision.RunningMode.VIDEO, num_poses=1)
        frames, timestamps = [], []
        previous = -1
        with vision.PoseLandmarker.create_from_options(options) as detector:
            while True:
                ok, bgr = cap.read()
                if not ok:
                    break
                if len(frames) >= 1800 or len(frames)/fps > 20:
                    raise ValueError('Decoded clip exceeds the 20-second / 1,800-frame limit.')
                # Strict monotonic timestamps for tracking, not biomechanical timing.
                timestamp = max(previous+1, round(len(frames)*1000/fps))
                previous = timestamp
                rgb = cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
                if max(w,h) > 1280:
                    rgb = cv2.resize(rgb,(round(w*1280/max(w,h)),round(h*1280/max(w,h))))
                prediction = detector.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB,data=np.ascontiguousarray(rgb)),timestamp)
                frames.append([{'x':float(p.x),'y':float(p.y),'visibility':float(p.visibility or 0),
                                'presence':float(p.presence or 0)} for p in prediction.pose_landmarks[0]] if prediction.pose_landmarks else [])
                timestamps.append(timestamp)
                if progress and len(frames)%10 == 0:
                    progress(min(len(frames)/max(count,1),1.0))
        if len(frames) < 3:
            raise ValueError('Need at least three decodable frames.')
        return {'width':w,'height':h,'playback_fps':fps,'frames':frames,'timestamps_ms':timestamps}
    finally:
        cap.release()

def overlay(path,result,index):
    cap = cv2.VideoCapture(str(path))
    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES,index)
        ok,bgr=cap.read()
        if not ok:
            raise ValueError('Unable to decode selected frame.')
        pts = [point(result['frames'][index],j,result['width'],result['height']) for j in range(33)]
        for a,b in EDGES:
            if pts[a] is not None and pts[b] is not None:
                cv2.line(bgr,tuple(pts[a].astype(int)),tuple(pts[b].astype(int)),(80,220,80),3)
        return cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
    finally:
        cap.release()
