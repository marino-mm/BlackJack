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
        return message.timeRemaining !== undefined
    }
    update(message){
        this.context.setTimeRemaining(message.timeRemaining)
    }
}

class UpdateGameState extends UpdateStrategy{

    is_applicable(message){
        return message.eventName !== undefined
    }
    update(message){
        this.context.setEventName(message.eventName)
    }
}

class UpdateHouseHand extends UpdateStrategy{
    is_applicable(message){
        return message.houseHand !== undefined
    }
    update(message){
        const house = this.context.house
        const new_house_hand = {...house, hands: message.houseHand}
        this.context.setHouse(new_house_hand)
    }
}

class UpdateActivePlayer extends UpdateStrategy{
    is_applicable(message){
        return message.activ_player_username !== undefined
    }
    update(message){
        this.context.setTurn(this.context.username === message.activ_player_username)
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