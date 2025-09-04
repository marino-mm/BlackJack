import {Fragment, useState, useContext, useEffect} from "react";
import {CurrentUserContext} from "../context/ChatRoomContext.jsx";
import useWebSocket, {ReadyState} from "react-use-websocket";

function Chat({username}) {
    const [chatMessages, setMessages] = useState([])
    const [userList, setUserList] = useState([])
    const [hasSentInitial, setHasSentInitial] = useState(false);

    const dev = true
    let wsUrl = null
    if (dev){
        wsUrl = "http://localhost:8000/ws";
    }
    else{
        const loc = window.location;
        const wsProtocol = loc.protocol === "https:" ? "wss" : "ws";
        wsUrl = `${wsProtocol}://${loc.host}/ws`;
    }



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

            if (lastJsonMessage.user_list !== undefined){
                setUserList(lastJsonMessage.user_list)
            }
            /*
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
                <ChatUserList userList={userList}/>
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

function ChatUserList({userList}) {
     return (
        <Fragment>
            {userList.map(user => <div>{user}</div>)}
        </Fragment>
    )
}

function ChatMessage({message}) {
    const currentUser = useContext(CurrentUserContext);
    const isCurrentUser = currentUser === message.user;

    const baseClasses = "px-3 py-2 my-1 max-w-[60%] font-sans shadow-sm text-black";
    const messageClasses = isCurrentUser
        ? "bg-[#A8E6CF] rounded-tl-[15px] rounded-tr-[15px] rounded-bl-[15px] self-end"
        : "bg-[#74B9FF] rounded-tl-[15px] rounded-tr-[15px] rounded-br-[15px] self-start";

    return (
        <div className={`flex flex-col ${isCurrentUser ? 'items-end' : 'items-start'}`}>
            <div className={`${baseClasses} ${messageClasses}`}>
                <span className="font-bold">{message.user}:</span> {message.message}
            </div>
        </div>
    );
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