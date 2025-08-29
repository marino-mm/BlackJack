import {Fragment, use, useState} from "react";
import './ChatRoom.css'

function Chat({username}) {
    const [chatMessages, setMessages] = useState([])
    return (
        <div>
            <ChatBody username={username} chatMessages={chatMessages}/>
            <ChatFooter username={username} onSend={(input) => setMessages([...chatMessages, input])}/>
        </div>
    )
}
export default Chat

function ChatBody({username, chatMessages}) {
     return (
        <Fragment>
            {chatMessages.map(message => <ChatMessage currentUser={username} message={message}></ChatMessage>)}
        </Fragment>
    )
}

function ChatMessage({ currentUser, message }) {
    const messageClassName = currentUser === message.user ? ("myMessage") : ("foreignMessage")
    return <div className={messageClassName}>{message.user}: {message.message}</div>;
}

function ChatFooter({username, onSend}) {
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
                }}
                placeholder='Type your message...'>
            </input>
            <button
                onClick={handleSend}
                >Send</button>
        </div>
    )
}