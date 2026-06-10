// services/LLMService.js

class LLMService {
    constructor(eventBus) {
        this.eventBus = eventBus;
    }

    async generateResponse(prompt, options = {}) {
        try {
            const defaultOptions = {
                components: {
                    list: [
                        'ALL_PREON',
                        {
                            role: 'system',
                            content: prompt,
                            position: 'BEFORE_PROMPT'
                        }
                    ]
                },
                api: {
                    inherit: true,
                    overrides: {
                        temperature: 0.8,
                        maxTokens: 1000
                    }
                },
                streaming: {
                    enabled: true,
                    onChunk: (chunk, acc) => {
                        this.eventBus.emit('llm:streaming', { chunk, accumulated: acc }, 'game');
                    }
                },
                debug: { enabled: true }
            };

            const mergedOptions = { ...defaultOptions, ...options };
            
            this.eventBus.emit('llm:request:start', mergedOptions, 'game');
            
            const response = await window.callGenerate(mergedOptions);
            
            this.eventBus.emit('llm:response:complete', response, 'game');
            
            return response;
        } catch (error) {
            this.eventBus.emit('llm:error', error, 'game');
            throw error;
        }
    }
}

// 每个服务类都需要添加：
export default LLMService;