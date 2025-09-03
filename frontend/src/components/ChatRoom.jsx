import {Fragment, useState, useContext, useEffect} from "react";
import './ChatRoom.css'
import {CurrentUserContext} from "../context/ChatRoomContext.jsx";
import useWebSocket, {ReadyState} from "react-use-websocket";

function Chat({username}) {
    const [chatMessages, setMessages] = useState([])
    const [hasSentInitial, setHasSentInitial] = useState(false);


    const loc = window.location;
    const wsProtocol = loc.protocol === "https:" ? "wss" : "ws";
    const wsUrl = `${wsProtocol}://${loc.host}/ws`;
    //const wsUrl = "http://localhost:8000/ws";

    const { sendJsonMessage, readyState, lastJsonMessage } = useWebSocket(wsUrl)

    useEffect(() => {
        if (readyState === ReadyState.OPEN && !hasSentInitial) {
            console.log("✅ WebSocket is connected!");
            sendJsonMessage({"username": username})
            setHasSentInitial(true);
        }
    }, [readyState, hasSentInitial, sendJsonMessage, username]);

    useEffect(() => {
        if (lastJsonMessage) {
            if (lastJsonMessage.message !== undefined){
                setMessages([...chatMessages, lastJsonMessage])
            }
            /*
            if (lastJsonMessage.user_list !== undefined){
                context.set('user_list', data.user_list)
                upldate_user_list()
                remove_cursor(data.user_list)
                render_cursors()
            }
            if (lastJsonMessage.cursor !== undefined) {
                add_or_update_cursor(data.cursor)
                render_cursors()
            }
            */
            console.log(lastJsonMessage)
        }
    }, [lastJsonMessage])

    const onSendMessage = (input) => {
        sendJsonMessage(input)
        //setMessages([...chatMessages, input])
    }

    return (
        <CurrentUserContext value={username}>
            <div>
                <ChatBody chatMessages={chatMessages}/>
                <ChatFooter onSend={onSendMessage}/>
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