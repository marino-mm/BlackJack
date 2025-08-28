import {useState} from 'react'
import './App.css'

function App() {
    const [count, setCount] = useState(0)
    return (
        <di>
            <h1>CHAT ROOM</h1>
            <Chat/>
            <VanillaButton/>
        </di>
    )
}

export default App

function ChatMessage(props) {
    return (
        <p>{props.username}: {props.message}</p>
    )
}

function Chat() {
    return (
        <div>
            <ChatBody/>
            <ChatFooter/>
        </div>
    )
}

function ChatBody() {
    const chatMassages = []
    return (
        <div></div>
    )
}

function ChatFooter() {
    return (
        <div>
            <input type='textarea'></input>
            <button>Send</button>
        </div>
    )
}

function VanillaButton(){
    function rederect_to_vanilla(){
        window.location.href = "/vanilla_js/"
    }

    return (
        <button onClick={rederect_to_vanilla}>Vanilla_Chatroom</button>
    )
}