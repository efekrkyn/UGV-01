import asyncio,json,subprocess,sys
from pathlib import Path
ROOT=str(Path(__file__).resolve().parents[3])
server='''import sys,time
sys.path.insert(0,ROOT+'/software')
from ugv_lite.gateway import Gateway,serve
from ugv_ai.executor import Permit
class Clock:
    monotonic=staticmethod(time.monotonic)
class Vehicle:
    def confirm_arm_parked(self):pass
    def send_stop(self):pass
class Executor:
    def request_stop(self,x):pass
p=Permit(Clock()); g=Gateway(p,Executor(),Vehicle(),lambda x:None,lambda x:None)
old=g.detach
def detach(send):
    old(send);print('detach permit='+str(p.ok()),flush=True)
g.detach=detach
serve(g,port=18766)
'''
p=subprocess.Popen([sys.executable,'-c',f'ROOT={ROOT!r}\n'+server],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
async def run():
    from websockets.asyncio.client import connect
    from websockets.exceptions import InvalidStatus,ConnectionClosed
    for _ in range(50):
        try:
            owner=await connect('ws://127.0.0.1:18766/ai',origin='http://127.0.0.1:18766');break
        except OSError:await asyncio.sleep(.05)
    for origin in ('https://untrusted.example',None):
        try:await connect('ws://127.0.0.1:18766/ai',origin=origin)
        except InvalidStatus as e:print('foreign/missing origin:',origin,e.response.status_code);assert e.response.status_code==403
        else:raise AssertionError('unexpectedly accepted')
    async with connect('ws://127.0.0.1:18766/ai',origin='http://127.0.0.1:18766') as second:
        try:await second.recv()
        except ConnectionClosed as e:print('second owner refused:',e.rcvd.code);assert e.rcvd.code==1008
        else:raise AssertionError('second owner accepted')
    await owner.send(json.dumps({'type':'lease','ai':True}))
    await owner.send(json.dumps({'type':'bogus'}))
    print('owner reply:',await owner.recv())
    await owner.close();await asyncio.sleep(.05)
    async with connect('ws://127.0.0.1:18766/ai',origin='http://127.0.0.1:18766') as reconnect:
        await reconnect.send(json.dumps({'type':'bogus-reconnect'}));print('reconnect reply:',await reconnect.recv())
try:asyncio.run(run())
finally:
    p.terminate();p.wait(3);print(p.stdout.read())
