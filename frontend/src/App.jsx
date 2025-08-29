import {Fragment, useState} from 'react'
import './App.css'
import {Login} from "./components/Login.jsx";
import Chat from "./components/ChatRoom.jsx";

function App() {
    const [username, setUsername] = useState('')
    return !username ? (
        <>
            <Login onSubmit={setUsername}/>
            <VanillaButton/>
        </>) : (
        <>
            <Chat username={username} />
            <VanillaButton/>
        </>
    )
}

export default App

function VanillaButton(){
    function redirect_to_vanilla(){
        window.location.href = "/vanilla_js/"
    }
    return (
        <button onClick={redirect_to_vanilla}>Vanilla_Chatroom</button>
    )
}