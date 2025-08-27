import {useState} from 'react'
import './App.css'

function App() {
    const [count, setCount] = useState(0)

    return (
        <di>
            <h1>CHAT ROOM</h1>
            <Chat/>
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