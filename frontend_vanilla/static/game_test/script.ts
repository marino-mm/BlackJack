

let context = new Map<string, any>();

function connect_to_ws() : void{

    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}${window.location.host}/game/ws`;

    let player_input = document.getElementById('input-name') as HTMLInputElement;
    let player_name = player_input.value;
    if (player_name === ''){
        alert("Username can't be empty!!");
    }
    
    const socket = new WebSocket(wsUrl);

    socket.addEventListener("open", (event) => {
        console.log(JSON.stringify({"username": player_name}));
        socket.send(JSON.stringify({"username": player_name}));
    });

    socket.addEventListener("message", (event) => {
        let json_message: Map<string, any> = event.data;

        if (json_message.get('PingPong') === undefined){
            socket.send(JSON.stringify({'PingPong' : 'Pong'}));
        }

        update_context(json_message);
        update_frontend(json_message);
    });
}


function update_frontend(data: Map<string, any>) : void{
    let game_phase_ele = document.getElementById('game-phase') as HTMLElement;    
    game_phase_ele.innerHTML = context.get('game-phase');
}

function update_context(data: Map<string, any>) {
    console.log(JSON.stringify(data));
}

function to_do(): void{}