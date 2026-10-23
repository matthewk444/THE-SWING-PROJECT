"""Runtime smoke tests; blank footage is deliberately not athlete validation."""
import cv2
import numpy as np
from pathlib import Path
from streamlit.testing.v1 import AppTest
from swing import analyze, overlay, review

def test_blank_clip_inference_and_abstention(tmp_path):
    path=tmp_path/'blank.avi'
    writer=cv2.VideoWriter(str(path),cv2.VideoWriter_fourcc(*'MJPG'),30,(320,240))
    assert writer.isOpened()
    for _ in range(6):
        writer.write(np.zeros((240,320,3),dtype=np.uint8))
    writer.release()
    r=analyze(path)
    assert len(r['frames'])==6
    assert all(not f for f in r['frames'])
    assert all(b>a for a,b in zip(r['timestamps_ms'],r['timestamps_ms'][1:]))
    assert overlay(path,r,2).shape==(240,320,3)
    assert review(r,0,2,4,'Right')['metrics']['lead_knee_at_contact_deg'] is None

def test_app_starts():
    app=AppTest.from_file(Path(__file__).resolve().parents[1]/'app.py').run(timeout=30)
    assert not app.exception
    assert app.title[0].value=='⚾ THE SWING PROJECT'
