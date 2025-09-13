import {Fragment, useContext, useEffect, useRef, useState} from 'react'
import useWebSocket, {ReadyState} from "react-use-websocket";


function GameRoom() {
    const [house, setHouse] = useState({name: "House", hands: [{cards: []}]})
    //const [tableSlots, setTableSlots] = useState(new Array(5).fill({name: "Empty", hands: [{cards: []}]}))
    const [tableSlots, setTableSlots] = useState(() =>
        Array.from({length: 5}, () => ({
            name: "Empty",
            hands: [{cards: []}]
        }))
    );

    const [username, setUsername] = useState('Test' + '_' + createRandomString(5))

    const [isYourTurn, setTurn] = useState(false)

    function createRandomString(length) {
        const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
        let result = "";
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }


    const dev = true
    let wsUrl = null
    if (dev) {
        wsUrl = "http://localhost:8000/game/ws";
    } else {
        const loc = window.location;
        const wsProtocol = loc.protocol === "https:" ? "wss" : "ws";
        wsUrl = `${wsProtocol}://${loc.host}/game/ws`;
    }

    const {sendJsonMessage, readyState, lastJsonMessage} = useWebSocket(wsUrl)
    const [hasSentInitial, setHasSentInitial] = useState(false)

    useEffect(() => {
        if (readyState === ReadyState.OPEN && !hasSentInitial) {
            sendJsonMessage({"username": username})
            setHasSentInitial(true);
        }
    }, [readyState, hasSentInitial, sendJsonMessage]);

    const prevReadyState = useRef(null);
    useEffect(() => {
        if (prevReadyState.current !== readyState) {
            console.log(`[WebSocket] Status changed: ${ReadyState[readyState]}`);
            prevReadyState.current = readyState;
        }
    }, [readyState]);

    useEffect(() => {
        if (lastJsonMessage) {
            // console.log(lastJsonMessage)
            if (lastJsonMessage.messageType === 'PingPong') {
                sendJsonMessage({'messageType': "PingPong", 'message': 'Pong'})
                // console.log('Pong Sent')
            }
            if (lastJsonMessage.messageType === 'UpdateSlots') {
                const new_slots = lastJsonMessage.slot_list.map(slot => {
                    return slot === null ? {name: "Empty", hands: [{cards: []}]} : slot
                })
                console.log(new_slots)
                setTableSlots(new_slots)
            }
            if (lastJsonMessage.messageType === 'UpdateHouse') {
                const new_house_hand = {...house, hands: lastJsonMessage.houseHand}
                console.log(new_house_hand)
                setHouse(new_house_hand)
            }
            if (lastJsonMessage.messageType === 'UpdateActivPlayer') {
                if (username === lastJsonMessage.activ_player_username){
                    setTurn(true)
                }
                else{
                    setTurn(false)
                }
            }
        }

    }, [lastJsonMessage, sendJsonMessage])

    const send_action = ({action}) => {
        const message = {'messageType': "Action", 'message': action}
        sendJsonMessage(message)
        //console.log(`Send_action: ${JSON.stringify(message)}`)
    }

    const change_seat = ({slot_index}) => {
        sendJsonMessage({'messageType': "MoveSlot", 'new_slot_index': slot_index})
    }

    return (
        <div>
            <div className="grid w-full grid-cols-5 grid-rows-2 border-4 border-blue-400 gap-4 p-5">
                <div className="col-span-5 flex flex-col border-4 border-red-500 min-h-10 justify-center items-center">
                    <PlayerHands player={house}/>
                </div>
                {tableSlots.map((slot, index) => (
                    <PlayerHands key={index}
                                 className="h-full border-4 border-green-300 flex items-center justify-center"
                                 player={slot}
                                 onClick={() => change_seat({slot_index: index})}/>))}

            </div>
            <ActionBar send_action={send_action} isYourTurn={isYourTurn}></ActionBar>
        </div>
    )
}

export default GameRoom;

function PlayerHands({player, onClick}) {

    return (
        <div className="grid grid-cols-1 border-purple-700 border-1 m-2" onClick={onClick}>
            <h3 className="font-bold text-lg">{player.name}</h3>
            <div className="grid grid-cols-1 gap-2 justify-center p-1">
                {player.hands.map((hand, index) => (
                    <Hand key={index} hand={hand}/>
                ))}
            </div>
        </div>
    )
}

function Hand({hand}) {
    return  hand.isActiveHand? (
        <div className="border-3 border-red-600 flex flex-wrap m-1">
            {hand.cards.map((card, index) =>
                <Card key={index} rank={card.rank} suit={card.suit} isActiveHand={hand.isActiveHand}/>
            )}
        </div>
    ) : (
        <div className="border-1 border-amber-950 flex flex-wrap m-1">
            {hand.cards.map((card, index) =>
                <Card key={index} rank={card.rank} suit={card.suit}/>
            )}
        </div>
    )
}

function Card({rank, suit, isActiveHand}) {

    return isActiveHand? (
        <div className="flex items-center gap-1 border border-rose-200 px-2 py-1 rounded w-max text-sm m-1">
            <p className="">{rank}</p>
            <p className="">{suit}</p>
        </div>
    ) : (
        <div className="flex items-center gap-1 border border-b-rose-200 px-2 py-1 rounded w-max text-sm m-1">
            <p>{rank}</p>
            <p>{suit}</p>
        </div>
    )
}

function ActionBar({send_action, isYourTurn}) {
    const buttonStyles = "border-4 border-gray-400\n" +
        "    py-2 px-4 rounded\n" +
        "    disabled:pointer-events-none\n" +
        "    disabled:opacity-50 disabled:cursor-not-allowed\n" +
        "    disabled:hover:bg-transparent"



    return (
        <>
            <div className="grid grid-cols-4 gap-4 h-fit w-full border-4 border-yellow-200 p-4 ">
                <button className={buttonStyles} onClick={() => send_action({action: 'hit'})}
                        disabled={!isYourTurn}>Hit
                </button>
                <button className={buttonStyles} onClick={() => send_action({action: 'stand'})}
                        disabled={!isYourTurn}>Stand
                </button>
                <button className={buttonStyles} onClick={() => send_action({action: 'double_down'})}
                        disabled={!isYourTurn}>Double Down
                </button>
                <button className={buttonStyles} onClick={() => send_action({action: 'split'})}
                        disabled={!isYourTurn}>Split
                </button>
            </div>
            <p>{isYourTurn ? ("It is your turn.") : ("It is not your turn.")}</p>
        </>
    )
}
