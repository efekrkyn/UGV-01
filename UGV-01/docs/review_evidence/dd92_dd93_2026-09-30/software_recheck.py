from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
s={'__file__':str(ROOT/'tests/check_lite_gateway.py')}
exec((ROOT/'tests/check_lite_gateway.py').read_text().split('# Arming over the link:')[0],s)
rig=s['rig']; frames=s['frames']; KEY=s['KEY']; lib=s['lib']
def steps(clock,n):
    for _ in range(n): clock.sleep(.05)
def armed():
    clock,robot,link,permit,vehicle,ex=rig(); vehicle.request_arm();steps(clock,20);ex.new_task()
    assert vehicle.armed()
    return clock,robot,link,permit,vehicle,ex
clock,robot,link,permit,vehicle,ex=armed()
assert ex.execute('arm',{'pose':'reach_low'}).ok
assert ex.execute('gripper',{'action':'open'}).ok
assert ex.execute('gripper',{'action':'close'}).ok
assert ex.execute('arm',{'pose':'store'}).ok
send=link.send; link.send=lambda d:None if d[3:5]==b'\x21\x01' else send(d)
r=ex.execute('gripper',{'action':'open'}); assert not r.ok
assert vehicle.gripper_state()=='closed' and not vehicle.state()['gripper_empty']
link.send=send
assert ex.execute('arm',{'pose':'stow'}).ok
r=ex.execute('drive',{'distance_m':.1,'speed_mps':.1});assert not r.ok
print('A04 lost-open closure:',r.text,'x=',robot.x,'claw=',robot.out.servo_us[7])
clock,robot,link,permit,vehicle,ex=armed()
vehicle.set_arm('lift');steps(clock,4)
send=link.send;link.send=lambda d:None if d[3:5]==b'\x22\x01' else send(d)
vehicle.hold_arm()
for _ in range(250):
    clock.sleep(.05)
    if not vehicle.hold:break
assert vehicle.arm_fault and not vehicle.answered
print('A05 lost-hold closure:',vehicle.arm_fault,'count=',(vehicle.seq['path']-vehicle.cmd_from)&65535,'at=',vehicle.arm_pose())
clock,robot,link,permit,vehicle,ex=armed()
before=vehicle.arm['echo'];bad=frames.pack(frames.CMD,0x122,frames.arm_path(0,5,65535,99,vehicle.session),KEY)
assert lib.lite_core_receive(robot.core,bad,len(bad),robot.now_ms)==0
steps(clock,3); assert vehicle.arm['echo']==before
print('A06 rejected-path closure: echo=',vehicle.arm['echo'])
# Reset during an active arm movement: it must not fake success or resume the swept path.
clock,robot,link,permit,vehicle,ex=armed()
reset=[False]
def reset_on_move(t):
    if not reset[0] and vehicle.arm_pose()=='moving':
        reset[0]=True;lib.lite_core_init(robot.core,KEY,len(KEY),robot.now_ms)
clock.hooks.append(reset_on_move)
r=ex.execute('arm',{'pose':'reach_low'})
print('reset during arm:',r,'core=',robot.out.state,'act=',robot.out.act_en,'pose=',vehicle.arm_pose())
assert not r.ok and not robot.out.act_en and vehicle.arm_pose() in ('limp','unknown')
# Fresh explicit arm rebinds; it still cannot move while limp.
vehicle.request_arm();steps(clock,20)
print('explicit rebind after reset:',vehicle.armed(),'pose=',vehicle.arm_pose(),'duty=',list(robot.out.duty))
assert vehicle.armed() and vehicle.arm_pose()=='limp' and not any(robot.out.duty)
# A05 stress: repeated failed goals without starting a new lease session advance the 16-bit path counter while
# the taken-command echo stays zero. At 4096, 12-bit echo-zero can alias into the next 255-command window.
clock,robot,link,permit,vehicle,ex=armed()
send=link.send;link.send=lambda d:None if d[3:5]==b'\x22\x01' else send(d)
for i in range(17):
    r=ex.execute('arm',{'pose':'stow'})
    print('all path lost retry',i+1,'ok=',r.ok,'seq=',vehicle.seq['path'],'echo=',vehicle.arm['echo'],'answered=',vehicle.answered)
    if r.ok:break

assert i == 16 and r.ok and vehicle.answered and vehicle.arm["echo"] == 0, "the repeated-loss alias must reproduce"
