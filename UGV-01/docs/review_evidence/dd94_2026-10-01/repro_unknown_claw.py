from pathlib import Path
import json
import sys
# Diagnostic counterexample: assertions below confirm the defective behavior.
# Use the explicit reviewed checkout, never an implicit current directory.
repo = sys.argv[1]
source = Path(repo) / 'tests/check_lite_gateway.py'
ns = {'__file__': str(source)}
exec(compile(source.read_text().split('# Arming over the link:')[0], str(source), 'exec'), ns)
clock, robot, link, permit, vehicle, ex = ns['rig']()
vehicle.request_arm()
for _ in range(20): clock.sleep(0.05)
ex.new_task()
assert ex.execute('arm', {'pose': 'ready'}).ok
assert ex.execute('gripper', {'action': 'open'}).ok
vehicle.disarm()
for _ in range(5): clock.sleep(0.05)
vehicle.request_arm()
for _ in range(20): clock.sleep(0.05)
assert vehicle.state()['arm'] == 'limp'
assert robot.out.servo_us[7] == 0
before = vehicle.state()
result = ex.execute('gripper', {'action': 'close'})
after = vehicle.state()
assert result.ok, result
assert robot.out.servo_us[7] == 0
print(json.dumps({'before':before, 'result':{'ok':result.ok,'text':result.text}, 'after':after,'claw_pwm_us':robot.out.servo_us[7]}, indent=2))
