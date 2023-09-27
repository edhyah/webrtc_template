const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
    cors: {
        origin: "http://localhost:3000",  // or simply "*"
        methods: ["GET", "POST"]
    }
});

app.use(cors());

// Set up static file serving for your client files
app.use(express.static(__dirname + '/../client'));


io.on('connection', (socket) => {
    console.log("Client connected:", socket.id);
    socket.on('offer', (offer) => {
        console.log("Received offer:", offer);
        socket.broadcast.emit('offer', offer);
    });

    socket.on('answer', (answer) => {
        socket.broadcast.emit('answer', answer);
    });

    socket.on('ice-candidate', (iceCandidate) => {
        socket.broadcast.emit('ice-candidate', iceCandidate);
    });
});

server.listen(3000, () => {
    console.log('Listening on port 3000');
});

