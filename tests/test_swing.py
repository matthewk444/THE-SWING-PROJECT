import math
import pytest
from swing import angle, review

def frame():
    points=[dict(x=.5,y=.5,visibility=.99,presence=.99) for _ in range(33)]
    for i,x,y in [(11,.4,.2),(12,.6,.2),(23,.4,.5),(24,.6,.5),(25,.4,.7),(27,.4,.9),(26,.8,.5),(28,.8,.8)]:
        points[i].update(x=x,y=y)
    return points

def result(frames):
    return dict(frames=frames,width=1920,height=1080)

def test_angles_and_degenerate():
    assert angle([0,0],[0,1],[1,1])==pytest.approx(90)
    assert angle([0,0],[0,0],[1,1]) is None

def test_lead_leg_and_pixels():
    r=result([frame(),frame(),frame()])
    assert review(r,0,1,2,'Right')['metrics']['lead_knee_at_contact_deg']==pytest.approx(180)
    assert review(r,0,1,2,'Left')['metrics']['lead_knee_at_contact_deg']==pytest.approx(90)

def test_missing_never_invents_advice():
    report=review(result([[],[],[]]),0,1,2,'Right')
    assert report['metrics']['lead_knee_at_contact_deg'] is None
    assert report['metrics']['nose_horizontal_range_torso_lengths'] is None

def test_low_score_and_invalid_events():
    f=frame(); f[25]['visibility']=.1
    r=result([f,f,f])
    assert review(r,0,1,2,'Right')['metrics']['lead_knee_at_contact_deg'] is None
    with pytest.raises(ValueError): review(r,0,2,1,'Right')
    with pytest.raises(ValueError): review(r,0,1,3,'Right')

def test_normalization_uses_pixel_aspect():
    frames=[frame() for _ in range(3)]
    frames[-1][0]['x']+=.1
    value=review(result(frames),0,1,2,'Right')['metrics']['nose_horizontal_range_torso_lengths']
    assert value==pytest.approx(192/324)
