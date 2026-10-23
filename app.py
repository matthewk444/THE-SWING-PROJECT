import hashlib
import json
import tempfile
from pathlib import Path
import streamlit as st
from swing import analyze, overlay, review

st.set_page_config(page_title='THE SWING PROJECT',page_icon='⚾',layout='wide')
st.title('⚾ THE SWING PROJECT')
st.link_button('Open Live Swing Lab — camera capture & reference matching', 'http://127.0.0.1:8502')
st.caption('Evidence-first swing review • local prototype • hitter development & scouting research')
st.info('Upload one full-body swing, inspect the tracking, and mark the events. Measurements describe the camera view; feedback is a coach-review prompt, not a validated diagnosis.')
with st.expander('Recording checklist and privacy',expanded=True):
    st.write('Use one hitter, a fixed side-view camera, good light, and visible feet and head. Prefer 120–240 fps capture when available; export an unmirrored clip. Keep the camera location consistent between sessions. Trim to ≤20 playback seconds / 1,800 frames / 100 MB.')
    st.write('This app does not upload your video or call an LLM. Uploaded clips are processed in temporary local files and removed after each operation. Results remain in session memory until cleared. MediaPipe documentation describes performance/utilization telemetry; this is not a guarantee of zero network traffic.')
player=st.text_input('Player label (optional)',max_chars=100)
hand=st.selectbox('Hitter bats', ['Right','Left'])
upload=st.file_uploader('Swing video',type=['mp4','mov','avi'])
if st.button('Clear analysis'):
    st.session_state.pop('analysis',None)
if upload:
    data=upload.getvalue()
    if len(data)>100*1024*1024:
        st.error('File exceeds 100 MB. Trim or compress the clip.')
        st.stop()
    digest=hashlib.sha256(data).hexdigest()
    st.video(data)
    if st.button('Analyze swing',type='primary'):
        st.session_state.pop('analysis',None)
        try:
            with tempfile.TemporaryDirectory(prefix='swing-') as directory:
                path=Path(directory)/('clip'+Path(upload.name).suffix.lower())
                path.write_bytes(data)
                bar=st.progress(0.0,text='Tracking body landmarks…')
                result=analyze(path,bar.progress)
                bar.empty()
                st.session_state['analysis']=(digest,result)
        except Exception as exc:
            st.error(f'Analysis could not finish: {exc}')
    saved=st.session_state.get('analysis')
    if saved and saved[0]==digest:
        result=saved[1]
        n=len(result['frames'])
        tracked=sum(bool(f) for f in result['frames'])
        st.write(f'{n} frames decoded · pose detected in {tracked/n:.0%} of frames')
        if tracked==0:
            st.warning('No person detected. Refilm with the hitter fully visible; no mechanics can be assessed.')
        idx=st.slider('Inspect frame',0,n-1,0)
        with tempfile.TemporaryDirectory(prefix='swing-review-') as directory:
            path=Path(directory)/('clip'+Path(upload.name).suffix.lower())
            path.write_bytes(data)
            try:
                st.image(overlay(path,result,idx),caption=f'Frame {idx} · green lines show landmarks passing the score gate')
            except ValueError as exc:
                st.error(str(exc))
        st.subheader('Mark the swing events')
        st.caption('Use the frame slider to identify these events. Frame numbers start at zero. Contact is approximate unless clearly visible.')
        a,b,c=st.columns(3)
        start=a.number_input('Start of review window',0,n-1,0,key=digest+'start')
        plant=b.number_input('Lead foot planted',0,n-1,min(n-2,n//3),key=digest+'plant')
        contact=c.number_input('Bat–ball contact',0,n-1,min(n-1,2*n//3),key=digest+'contact')
        confirmed=st.checkbox('I inspected the overlay and selected visible start, plant, and contact frames.',key=f'{digest}-{start}-{plant}-{contact}-confirmed')
        if not confirmed:
            st.info('The initial frame values are placeholders. Confirm the events before generating observations. If contact is not visible, use a clearer clip.')
            st.stop()
        try:
            report=review(result,int(start),int(plant),int(contact),hand,player or 'Unnamed hitter')
            st.subheader('Observations & next experiment')
            for line in report['feedback']:
                st.write('• '+line)
            st.json(report['metrics'])
            st.download_button('Download review JSON',json.dumps(report,indent=2,allow_nan=False),'swing-review.json','application/json')
            st.download_button('Download frame landmarks',json.dumps(result,allow_nan=False),'swing-landmarks.json','application/json')
        except ValueError as exc:
            st.warning(str(exc))
else:
    st.write('Start with a short clip of your own swing or footage you have permission to analyze.')
