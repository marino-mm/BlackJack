class UpdateStrategy {
    constructor(context = {}) {
        this.context = context;
    }
    is_applicable(message) {}
    update(message) {}
}

class PingPongStrategy extends UpdateStrategy{
    is_applicable(message) {
        return message.PingPong !== undefined
    }
    update(message) {
        this.context.sendJsonMessage({'messageType': 'PingPong', 'message': 'Pong'})
    }
}

class UpdateSlotStrategy extends UpdateStrategy{
    is_applicable(message){
        return message.slot_list !== undefined
    }

    update(message) {
        const new_slots = message.slot_list.map(slot => {
            return slot === null ? {name: "Empty", hands: [{cards: []}]} : slot
        })
        this.context.setTableSlots(new_slots)
    }
}

class UpdateCountdownTimer extends UpdateStrategy{
    is_applicable(message){
        return message.time_remaining !== undefined
    }
    update(message){
        this.context.setTimeRemaining(message.time_remaining)
    }
}

class UpdateGameState extends UpdateStrategy{

    is_applicable(message){
        return message.event_name !== undefined
    }
    update(message){
        this.context.setEventName(message.event_name)
    }
}

class UpdateHouseHand extends UpdateStrategy{
    is_applicable(message){
        return message.house_hand !== undefined
    }
    update(message){
        const house = this.context.house
        const new_house_hand = {...house, hands: message.house_hand}
        this.context.setHouse(new_house_hand)
    }
}

class UpdateActivePlayer extends UpdateStrategy{
    is_applicable(message){
        return message.active_player_username !== undefined
    }
    update(message){
        this.context.setTurn(this.context.username === message.active_player_username)
    }
}

export {
    PingPongStrategy,
    UpdateSlotStrategy,
    UpdateCountdownTimer,
    UpdateGameState,
    UpdateHouseHand,
    UpdateActivePlayer
};