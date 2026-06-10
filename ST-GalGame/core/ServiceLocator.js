// core/ServiceLocator.js
class ServiceLocator {
    constructor() {
        this.services = new Map();
    }

    register(name, service) {
        this.services.set(name, service);
        console.log(`[ServiceLocator] Registered service: ${name}`);
    }

    get(name) {
        const service = this.services.get(name);
        if (!service) {
            throw new Error(`Service '${name}' not found`);
        }
        return service;
    }

    has(name) {
        return this.services.has(name);
    }
}

export default ServiceLocator;