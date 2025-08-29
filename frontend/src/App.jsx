import {Fragment, useState} from 'react'
import './App.css'

function App() {

    return (
        <di>
            <h1>CHAT ROOM</h1>
            <Chat/>
            <VanillaButton/>
        </di>
    )
}

export default App

function Chat() {
    const [chatMessages, setMessages] = useState([])

    return (
        <div>
            <ChatBody chatMessages={chatMessages}/>
            <ChatFooter onSend={(input) => setMessages([...chatMessages, input])}/>
        </div>
    )
}

function ChatBody({chatMessages}) {
     return (
        <Fragment>
            {chatMessages.map(message => <ChatMessage {...message}></ChatMessage>)}
        </Fragment>
    )
}

function ChatMessage(props) {
    const user = props.user
    const message = props.message
    return <div>{user}: {message}</div>
}

function ChatFooter({onSend}) {
    const username = 'Test'
    const [inputMessage, setInputMessage] = useState('');

    const handleSend = () => {
        onSend({ user: username, message: inputMessage })
        setInputMessage('')
    }
    return (
        <div>
            <input
                type='text'
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                        handleSend()
                    }
                    else {
                        console.log(e)
                    }
                }}
                placeholder='Type your message...'>
            </input>
            <button
                onClick={handleSend}
                >Send</button>
        </div>
    )
}

function VanillaButton(){
    function redirect_to_vanilla(){
        window.location.href = "/vanilla_js/"
    }

    return (
        <button onClick={redirect_to_vanilla}>Vanilla_Chatroom</button>
    )
}