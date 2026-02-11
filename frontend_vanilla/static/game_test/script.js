function getSocket() {
    if (!socket) {
        alert("First connect to server!!!!");
        throw new Error("WebSocket is not connected");
    }
    return socket;
}
function connect_to_ws() {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}${window.location.host}/game/ws`;
    let player_input = document.getElementById('input-name');
    let player_name = player_input.value;
    if (player_name === '') {
        alert("Username can't be empty!!");
        return;
    }
    socket = new WebSocket(wsUrl);
    socket.addEventListener("open", (event) => {
        getSocket().send(JSON.stringify({ "username": player_name }));
    });
    socket.addEventListener("message", (event) => {
        let json_message = JSON.parse(event.data);
        let timestamp = new Date;
        console.log(`${timestamp.toISOString()} ${event.data}`);
        if ('PingPong' in json_message) {
            getSocket().send(JSON.stringify({ 'messageType': 'PingPong', 'message': 'Pong' }));
        }
        else {
            update_frontend(json_message);
        }
    });
}
function update_frontend(data) {
    const mapper = {
        "game-phase": data.event_name,
        "game-time": data.time_remaining,
        "game-players": data.slot_list,
        "game-context": data
    };
    for (const [html_id, data_obj] of Object.entries(mapper)) {
        const html_element = document.getElementById(html_id);
        if (!html_element)
            continue;
        if (data_obj != null) {
            html_element.innerText = JSON.stringify(data_obj);
        }
        else {
            html_element.innerText = "";
        }
    }
}
function send_hit() {
    const socket = getSocket();
    socket.send(JSON.stringify({
        "messageType": "Action",
        "message": "hit"
    }));
}
function send_double_down() {
    const socket = getSocket();
    socket.send(JSON.stringify({
        "messageType": "Action",
        "message": "double_down"
    }));
}
function send_split() {
    const socket = getSocket();
    socket.send(JSON.stringify({
        "messageType": "Action",
        "message": "split"
    }));
}
function send_hold() {
    const socket = getSocket();
    socket.send(JSON.stringify({
        "messageType": "Action",
        "message": "stand"
    }));
}
function ws_disconect() {
    socket?.close();
    socket = null;
}
function send_move_seat() {
    const seat_numb_element = document.getElementById("input-seat-number");
    const seat_numb = Number(seat_numb_element.value);
    socket.send(JSON.stringify({
        "messageType": "MoveSlot",
        "new_slot_index": seat_numb
    }));
}
function add_listeners() {
    const html_funct_mapping = {
        "connect-button": connect_to_ws,
        "disconnect-button": ws_disconect,
        "hit-button": send_hit,
        "double-down-button": send_double_down,
        "split-button": send_split,
        "hold-button": send_hold,
        "move-button": send_move_seat,
    };
    for (const [html_id, funct] of Object.entries(html_funct_mapping)) {
        const html_element = document.getElementById(html_id);
        if (!html_element)
            continue;
        html_element.addEventListener("click", funct);
    }
}
// INIT PART
let socket = null;
add_listeners();
export {};
//# sourceMappingURL=script.js.map