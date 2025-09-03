import { createContext } from "react";

export const CurrentUserContext = createContext(null);
export const WebSocketContext = createContext(null);
export const AppMapContext = createContext(new Map())