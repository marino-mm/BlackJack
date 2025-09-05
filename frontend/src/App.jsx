import {Fragment, useState} from 'react'
import './App.css'
import {Login} from "./components/Login.jsx";
import Chat from "./components/ChatRoom.jsx";
import GameRoom from "./components/GameRoom.jsx";
import {BrowserRouter, Route, Routes} from "react-router-dom";

function App() {
    const [username, setUsername] = useState('')
    const base = import.meta.env.BASE_URL

    return (
        <BrowserRouter basename={base}>
            <Routes>
                <Route
                    path="/"
                    element={
                        !username ? (
                            <>
                                <Login onSubmit={setUsername}/>
                                <VanillaButton/>
                            </>
                        ) : (
                            <>
                                <Chat username={username}/>
                                <VanillaButton/>
                            </>
                        )
                    }
                />
                <Route path="/test" element={<GameRoom/>}/>
            </Routes>
        </BrowserRouter>
    )
}

export default App

function VanillaButton() {
    return <button onClick={() => window.location.href = "/"}>Vanilla_Chatroom</button>
}