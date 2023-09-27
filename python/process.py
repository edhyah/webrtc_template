import cv2
import numpy as np
from aiortc import RTCPeerConnection, VideoStreamTrack, RTCSessionDescription
from aiohttp import web
import subprocess
import socketio
import json

sio = socketio.AsyncClient()

# Set your webcam resolution
WIDTH, HEIGHT = 640, 480

# FFmpeg command for encoding in real-time
command = [
    'ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', '{}x{}'.format(WIDTH, HEIGHT),
    '-pix_fmt', 'rgb24',
    '-r', '30',  # assuming webcam supports 30 fps
    '-i', '-',
    '-an',
    '-vcodec', 'libx264',
    '-preset', 'ultrafast',
    'output.mp4'
]

def process_frame(frame):
    return frame

class FrameTransformer(VideoStreamTrack):
    kind = "video"
    _direction = "sendonly"

    def __init__(self):
        super().__init__()
        self.cap = cv2.VideoCapture(0)
        self.proc = subprocess.Popen(
            # The same FFmpeg command, but now sending output to stdout
            command + ['-f', 'h264', '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE
        )

    async def recv(self):
        ret, frame = self.cap.read()
        if not ret:
            raise Exception("Error reading frame")

        # Convert from BGR to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        processed_frame = process_frame(frame_rgb)

        # Write frame to FFmpeg for encoding
        self.proc.stdin.write(processed_frame.tobytes())

        # Read encoded frame from FFmpeg
        encoded_frame = self.proc.stdout.read()
        return encoded_frame

'''
async def offer(request):
    print('Offer being made')
    params = await request.json()
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc.addTrack(FrameTransformer())

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    print('Offer sending')
    return web.Response(
        content_type="application/json",
        text=json.dumps({
            "sdp": pc.localDescription.sdp,
            "type": pc.localDescription.type
        })
    )
'''

@sio.event
async def connect():
    print("Connected to the signaling server")

@sio.event
async def offer(data):
    print('Offer received from client')
    offer = RTCSessionDescription(sdp=data["sdp"], type=data["type"])

    pc = RTCPeerConnection()
    pc.addTrack(FrameTransformer())

    await pc.setRemoteDescription(offer)
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    print('Sending answer to client')
    await sio.emit('answer', {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    })

async def start_app():
    # Connect to the signaling server
    await sio.connect('http://localhost:3000')
    app = web.Application()
    # ... [your existing routes, if any]
    app.router.add_post("/offer", offer)
    return app

web.run_app(start_app())

#app = web.Application()
#app.router.add_post("/offer", offer)
#web.run_app(app)

