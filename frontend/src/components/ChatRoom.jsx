import {Fragment, useState, useContext} from "react";
import './ChatRoom.css'
import {CurrentUserContext} from "../context/ChatRoomContext.jsx";

function Chat({username}) {
    const [chatMessages, setMessages] = useState([])
    return (
        <CurrentUserContext value={username}>
            <div>
                <ChatBody chatMessages={chatMessages}/>
                <ChatFooter onSend={(input) => setMessages([...chatMessages, input])}/>
            </div>
        </CurrentUserContext>
    )
}
export default Chat

function ChatBody({chatMessages}) {
     return (
        <Fragment>
            {chatMessages.map(message => <ChatMessage message={message}></ChatMessage>)}
        </Fragment>
    )
}

function ChatMessage({ message }) {
    const currentUser = useContext(CurrentUserContext)
    const messageClassName = currentUser  === message.user ? ("myMessage") : ("foreignMessage")
    return <div className={messageClassName}>{message.user}: {message.message}</div>;
}

function ChatFooter({onSend}) {
    const [inputMessage, setInputMessage] = useState('');
    const currentUser = useContext(CurrentUserContext)
    const handleSend = () => {
        onSend({ user: currentUser, message: inputMessage })
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