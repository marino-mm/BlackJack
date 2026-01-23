"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
let context = new Map();
function connect_to_ws() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}${window.location.host}/game/ws`;
    let player_input = document.getElementById('input-name');
    let player_name = player_input.value;
    if (player_name === '') {
        alert("Username can't be empty!!");
    }
    const socket = new WebSocket(wsUrl);
    socket.addEventListener("open", (event) => {
        console.log(JSON.stringify({ "username": player_name }));
        socket.send(JSON.stringify({ "username": player_name }));
    });
    socket.addEventListener("message", (event) => {
        let json_message = event.data;
        if (json_message.get('PingPong') === undefined) {
            socket.send(JSON.stringify({ 'PingPong': 'Pong' }));
        }
        update_context(json_message);
        update_frontend(json_message);
    });
}
function update_frontend(data) {
    let game_phase_ele = document.getElementById('game-phase');
    game_phase_ele.innerHTML = context.get('game-phase');
}
function update_context(data) {
    console.log(JSON.stringify(data));
}
function to_do() { }
//# sourceMappingURL=script.js.map