// core/EventBus.js
class EventBus {
    constructor() {
        this.events = new Map();
        this.debugMode = true;
    }

    on(eventName, callback, namespace = 'default') {
        const fullEventName = `${namespace}:${eventName}`;
        if (!this.events.has(fullEventName)) {
            this.events.set(fullEventName, []);
        }
        this.events.get(fullEventName).push(callback);
        
        if (this.debugMode) {
            console.log(`[EventBus] Registered: ${fullEventName}`);
        }
    }

    emit(eventName, data, namespace = 'default') {
        const fullEventName = `${namespace}:${eventName}`;
        const callbacks = this.events.get(fullEventName) || [];
        
        if (this.debugMode) {
            console.log(`[EventBus] Emitting: ${fullEventName}`, data);
        }
        
        callbacks.forEach(callback => {
            try {
                callback(data);
            } catch (error) {
                console.error(`[EventBus] Error in callback for ${fullEventName}:`, error);
            }
        });
    }

    off(eventName, callback, namespace = 'default') {
        const fullEventName = `${namespace}:${eventName}`;
        const callbacks = this.events.get(fullEventName) || [];
        const index = callbacks.indexOf(callback);
        if (index > -1) {
            callbacks.splice(index, 1);
        }
    }
}

export default EventBus;