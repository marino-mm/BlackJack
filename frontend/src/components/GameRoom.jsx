import {Fragment, useContext, useEffect, useRef, useState} from 'react'
import useWebSocket, {ReadyState} from "react-use-websocket";


function GameRoom() {
    const [house, setHouse] = useState({
        name: "House",
        hands: [[{rank: 'A', suit: '♠'}, {rank: 'K', suit: '♠'}, {rank: 'K', suit: '♠'}]]
    })
    const [tableSlots, setTableSlots] = useState(new Array(5).fill({name: "Empty", hands: [[]]}))

    const dev = true
    let wsUrl = null
    if (dev){
        wsUrl = "http://localhost:8000/game/ws";
    }
    else{
        const loc = window.location;
        const wsProtocol = loc.protocol === "https:" ? "wss" : "ws";
        wsUrl = `${wsProtocol}://${loc.host}/ws`;
    }

    const { sendJsonMessage, readyState, lastJsonMessage } = useWebSocket(wsUrl)
    const [hasSentInitial, setHasSentInitial] = useState(false)

    useEffect(() => {
        if (readyState === ReadyState.OPEN && !hasSentInitial) {
            sendJsonMessage({"username": "test"})
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
            console.log(lastJsonMessage)
            if (lastJsonMessage.messageType === 'PingPong') {
                sendJsonMessage({'messageType': "PingPong", 'message': 'Pong'})
                console.log('Pong Sent')
            }
            if (lastJsonMessage.messageType === 'MoveSlot') {
                const new_slots = lastJsonMessage.slot_list.map(slot => {
                    return slot === null ? {name: "Empty", hands: [[]]} : slot
                })
                console.log(new_slots)
                setTableSlots(new_slots)
            }
        }

    }, [lastJsonMessage, sendJsonMessage])

    const hit = () =>{
        const message = {'messageType': "Action", 'message': "hit"}
        sendJsonMessage(message)
        //console.log("hit")
    }

    const change_seat = ({slot_index}) =>{
        /*
        const username = "Moje ime"
        const currentIndex = tableSlots.findIndex(slot => slot.name === username)
        const new_slots = [...tableSlots]
        if (currentIndex !== -1) {
            new_slots[currentIndex] = {...new_slots[currentIndex], name: "Empty"}
        }
        new_slots[slot_index] = {...new_slots[slot_index], name: username}
        setTableSlots(new_slots)
        */
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
                                 onClick={() => change_seat({ slot_index: index })}/>))}

            </div>
            <ActionBar hit={hit}></ActionBar>
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
    return (
        <div className="border-1 border-b-amber-950 flex flex-wrap m-1">
            {hand.map((card, index) =>
                <Card key={index} rank={card.rank} suit={card.suit}/>
            )}
        </div>
    )
}

function Card({rank, suit}) {

    return (
        <div className="flex items-center gap-1 border border-b-rose-200 px-2 py-1 rounded w-max text-sm m-1">
            <p>{rank}</p>
            <p>{suit}</p>
        </div>
    )
}

function ActionBar({hit, stand, doubleDown, split}) {
    const buttonStyles = "border-4 border-gray-400\n" +
        "    py-2 px-4 rounded\n" +
        "    disabled:pointer-events-none\n" +
        "    disabled:opacity-50 disabled:cursor-not-allowed\n" +
        "    disabled:hover:bg-transparent"
    const [isYourTurn, setTurn] = useState(true)

    const swithcTurn = () => {
        setTurn(!isYourTurn)
    }

    return (
        <>
            <div className="grid grid-cols-4 gap-4 h-fit w-full border-4 border-yellow-200 p-4 ">
                <button className={buttonStyles} onClick={hit} disabled={!isYourTurn}>Hit</button>
                <button className={buttonStyles} onClick={stand} disabled={!isYourTurn}>Stand</button>
                <button className={buttonStyles} onClick={doubleDown} disabled={!isYourTurn}>Double Down</button>
                <button className={buttonStyles} onClick={split} disabled={!isYourTurn}>Split</button>
            </div>
            <button onClick={swithcTurn}>Switch</button>
            <p>{isYourTurn ? ("It is your turn.") : ("It is not your turn.")}</p>
        </>
    )
}

function FriendsCursors({cursors}) {

    return
}