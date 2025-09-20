class UpdateStrategy {
    is_applicable(message) {}
    update(message) {}
}

class PingPongStrategy extends UpdateStrategy{
    is_aplicable(message) {
        return message.messageType === 'PingPong'
    }

    update(message) {
        sendJsonMessage({'messageType': "PingPong", 'message': 'Pong'})
    }
}

class UpdateSlotStrategy extends UpdateStrategy{

    is_applicable(message){
        return lastJsonMessage.slot_list !== undefined
    }

    update(message) {
        const new_slots = lastJsonMessage.slot_list.map(slot => {
            return slot === null ? {name: "Empty", hands: [{cards: []}]} : slot
        })
        setTableSlots(new_slots)
        console.log(new_slots)
    }
}

