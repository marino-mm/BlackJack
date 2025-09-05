import {useContext, useState} from 'react'
import {yourTurnContext} from "../context/GameRoom.jsx";

function GameRoom() {
    const [house, setHouse] = useState({name: "House", cards: []})
    const [tableSlots, settableSlots] = useState(new Array(5).fill(null))

    return (
        <div>
            <div className="grid w-full grid-cols-5 grid-rows-2 border-4 border-blue-400 gap-4 p-5">
                <div className="col-span-5 border-4 border-red-500 min-h-10">
                    <PlayerHand player={house}/>
                </div>
                {tableSlots.map((slot, index) => (
                    <div key={index}
                         className="h-full border-4 border-green-300 flex items-center justify-center">{index}</div>))}

            </div>
            <ActionBar></ActionBar>
        </div>
    )
}

export default GameRoom;

function PlayerHand({player}) {
    return (
        <div>
            <h3>{player.name}</h3>
            <p>{player.cards}</p>
        </div>
    )
}

function ActionBar({hit, stand, doubleDown, split}) {
    const buttonStyles = "border-4 border-gray-400\n" +
        "    py-2 px-4 rounded\n" +
        "    disabled:pointer-events-none\n" +
        "    disabled:opacity-50 disabled:cursor-not-allowed\n" +
        "    disabled:hover:bg-transparent"
    const [isYourTurn, setTurn] = useState(true )

    const swithcTurn = () =>{
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
            <p>{isYourTurn? ("It is your turn.") : ("It is not your turn.")}</p>
        </>
    )
}