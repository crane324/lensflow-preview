// core/GameCore.js - GalGame核心
import EventBus from './EventBus.js';
import ServiceLocator from './ServiceLocator.js';
import GameState from '../models/GameState.js';
import LLMService from '../services/LLMService.js';
import DynamicPromptService from '../services/DynamicPromptService.js';
import GameStateService from '../services/GameStateService.js';
import NPCService from '../services/NPCService.js';
import GameController from '../controllers/GameController.js';
import GameView from '../views/GameView.js';

class GameCore {
    constructor() {
        this.serviceLocator = new ServiceLocator();
        this.eventBus = new EventBus();
        this.initialized = false;
    }

    async initialize() {
        if (this.initialized) {
            console.warn('GameCore already initialized');
            return;
        }

        try {
            console.log('[GameCore] Initializing...');
            
            this.registerCoreServices();
            await this.initializeServices();
            this.createControllers();
            this.createViews();
            this.setupErrorHandling();
            
            this.initialized = true;
            console.log('[GameCore] Initialization complete');
            
            this.eventBus.emit('core:initialized', {}, 'system');
            
        } catch (error) {
            console.error('[GameCore] Initialization failed:', error);
            throw error;
        }
    }

    registerCoreServices() {
        this.serviceLocator.register('eventBus', this.eventBus);
        this.serviceLocator.register('gameStateService', new GameStateService(this.eventBus));
        this.serviceLocator.register('llmService', new LLMService(this.eventBus));
        this.serviceLocator.register('npcService', new NPCService(this.eventBus));
    }

    async initializeServices() {
        const gameStateService = this.serviceLocator.get('gameStateService');
        
        // 初始化动态提示词系统
        try {
            await gameStateService.initializeDynamicPrompts('config/prompts/galgame-prompts.json');
            console.log('[GameCore] Dynamic prompt system initialized');
        } catch (error) {
            console.warn('[GameCore] Failed to initialize dynamic prompts, using fallback:', error);
        }
        
        // 初始化NPC列表
        const gameState = gameStateService.getState();
        const npcService = this.serviceLocator.get('npcService');
        const unlockedNPCs = gameState.getUnlockedNPCs();
        
        console.log('[GameCore] Initialized with', unlockedNPCs.length, 'unlocked NPCs');
    }

    createControllers() {
        const gameController = new GameController(this.serviceLocator, this.eventBus);
        this.serviceLocator.register('gameController', gameController);
    }

    createViews() {
        const gameView = new GameView(this.eventBus);
        this.serviceLocator.register('gameView', gameView);
        window.gameView = gameView;
        
        // 初始化角色列表显示
        const gameState = this.serviceLocator.get('gameStateService').getState();
        const npcs = gameState.getUnlockedNPCs();
        gameView.initializeCharacterList(npcs);
    }

    setupErrorHandling() {
        window.addEventListener('error', (event) => {
            console.error('[GameCore] Global error:', event.error);
            this.eventBus.emit('core:error', { error: event.error }, 'system');
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('[GameCore] Unhandled promise rejection:', event.reason);
            this.eventBus.emit('core:promise:rejected', { reason: event.reason }, 'system');
        });
    }

    getService(name) {
        return this.serviceLocator.get(name);
    }

    shutdown() {
        this.eventBus.emit('core:shutdown', {}, 'system');
        this.serviceLocator.services.clear();
        this.initialized = false;
    }
}

export default GameCore;