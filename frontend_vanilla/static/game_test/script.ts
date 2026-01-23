function connect_to_ws() : void{
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}${window.location.host}/game/ws`;

    let player_input = document.getElementById('input-name') as HTMLInputElement;
    let player_name = player_input.value;
    if (player_name === ''){
        alert("Username can't be empty!!");
        return;
    }
    
    const socket = new WebSocket(wsUrl);

    socket.addEventListener("open", (event) => {
        socket.send(JSON.stringify({"username": player_name}));
    });

    socket.addEventListener("message", (event) => {
        let json_message = JSON.parse(event.data);        
        if ('PingPong' in json_message){
            console.log(json_message);
            socket.send(JSON.stringify({'messageType' : 'PingPong'}));
        }
        // update_context(json_message);
        // update_frontend(json_message);
    });
}


function update_frontend(data: Map<string, any>) : void{
    let game_phase_ele = document.getElementById('game-phase') as HTMLElement;    
    // game_phase_ele.innerHTML = context.get('game-phase');
}

function update_context(data: Map<string, any>) {
    console.log(JSON.stringify(data));
}

function to_do(): void{}

function init(): void{
    let context = new Map<string, any>();
}
init();