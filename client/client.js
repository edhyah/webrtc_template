const socket = io.connect('http://localhost:3000');
const config = { iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] };
const pc = new RTCPeerConnection(config);

pc.ontrack = (event) => {
    document.querySelector('video').srcObject = event.streams[0];
};

pc.onicecandidate = (event) => {
    if (event.candidate) {
        socket.emit('ice-candidate', event.candidate);
    }
};

socket.on('offer', async (offer) => {
    const remoteOffer = new RTCSessionDescription(offer);
    await pc.setRemoteDescription(remoteOffer);
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    socket.emit('answer', answer);
});

// Now, we initiate an offer from the client to the server
async function start() {
    const offer = await pc.createOffer();
    console.log("Created and sending offer:", offer);
    await pc.setLocalDescription(offer);
    socket.emit('offer', offer);
}

// Call start when the page is loaded
start();

