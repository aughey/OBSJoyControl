from inputs import get_gamepad
import threading
import time
import math
import socket
from rotationintegrator import RotationIntegrator
from cameralayout import CameraLayout
import argparse

parser = argparse.ArgumentParser(description='Joystick to OBS Transform 3D controller')
parser.add_argument('--remotehost', default="127.0.0.1", help='Remote OBS host (default 127.0.0.1)')
parser.add_argument('--remoteport', type=int, default=5005, help="Remote OBS port number (default 5005)")
parser.add_argument('--horizontalfov', type=float, default=90, help="Full horizontal field of view (default 90)")
parser.add_argument('--downangle', type=float, default=0, help="Angle camera is pointed down from level (default 0)")
parser.add_argument("--max_zoom_ratio", type=float, default=3, help="Maximum zoom ratio.  2 will allow zoom of 2 times")
parser.add_argument('--pan_limit', type=float, default=45,help="Limit of the pan motion (default 45 degrees) [symetric]")
parser.add_argument('--tilt_limit', type=float, default=45,help="Limit of the tilt motion (default 45 degrees) [symetric]")

args = parser.parse_args()

print(args)
UDP_IP=args.remotehost
UDP_PORT=args.remoteport

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP

horizontal_fov = args.horizontalfov
down_angle = args.downangle

vertical_fov = CameraLayout.HorizontalToVertical(horizontal_fov)
cameralayout = CameraLayout(down_angle,horizontal_fov)

minfov = math.degrees(2.0 * 
    math.atan2(
        math.tan(math.radians(vertical_fov/2)) / args.max_zoom_ratio
        ,1))

rotation = RotationIntegrator(pan_limit=args.pan_limit, tilt_limit=args.tilt_limit, start_fov=vertical_fov, minfov=minfov, maxfov=vertical_fov, start_rotation=[down_angle,0,0])

def Tick(dt):
    [v,fov] = rotation.FixedUpdate(dt)
    calc_and_send(v,fov)

def TickThread():
    lasttick = time.time()
    
    while True:
        time.sleep(1.0/60.0)

        thistick = time.time()
        dt = thistick-lasttick
        lasttick = thistick

        Tick(dt)

x = threading.Thread(target=TickThread)
x.daemon = True
x.start()

def Join(a):
    return " ".join([str(v) for v in a])

def calc_and_send(camera_euler,camera_fov):
    values = cameralayout.Compute(camera_euler)
    
    message = Join(values) + " " + str(camera_fov)

    sock.sendto(bytes(message, "utf-8"), (UDP_IP, UDP_PORT))

def stick(v):
    v = (v + 0.5) / 32767.5
    deadzone = 0.08
    if abs(v) < deadzone:
        v = 0
    return v

xy=[0,0]
while 1:
    events = get_gamepad()
    for event in events:
        if event.code == 'ABS_RX':
            xy[0] = stick(event.state)
        elif event.code == 'ABS_RY':
            xy[1] = -stick(event.state)
        elif event.code == 'ABS_RZ':
            rotation.OnZoom(-event.state/128.0)
        elif event.code == 'ABS_Z':
            rotation.OnZoom(event.state/128.0)
        else:
            pass
            #print(event.ev_type, event.code, event.state)
    rotation.OnLook(xy)
