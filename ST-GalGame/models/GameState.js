// models/GameState.js
class GameState {
    constructor() {
        this.player = {
            name: '玩家',
            gender: 'male', // male, female
            avatar: 'default'
        };
        
        // NPC系统
        this.npcs = new Map();
        this.currentNPC = null; // 当前对话的NPC
        
        // 场景系统
        this.scene = {
            currentScene: 'school_entrance',
            background: 'school_entrance.jpg',
            bgm: 'daily_life.mp3',
            timeOfDay: 'morning', // morning, afternoon, evening, night
            weather: 'sunny'
        };
        
        // 对话历史
        this.conversation = {
            history: [],
            context: ''
        };
        
        // 游戏进度标记
        this.gameFlags = new Map();
        
        // 动态变量存储
        this.dynamicVariables = new Map();
        
        // 初始化默认NPC和动态变量
        this._initializeNPCs();
        this._initializeDynamicVariables();
    }

    /**
     * 初始化NPC数据
     * @private
     */
    _initializeNPCs() {
        // 示例NPC：青梅竹马
        this.npcs.set('sakura', {
            id: 'sakura',
            name: '樱',
            avatar: 'sakura.png',
            relationship: 0, // -100 到 100
            personality: 'tsundere', // 傲娇
            description: '你的青梅竹马，性格有些傲娇但内心温柔',
            unlocked: true
        });
        
        // 示例NPC：学姐
        this.npcs.set('yuki', {
            id: 'yuki',
            name: '雪',
            avatar: 'yuki.png',
            relationship: 0,
            personality: 'gentle', // 温柔
            description: '温柔体贴的学姐，总是照顾着你',
            unlocked: true
        });
        
        // 示例NPC：学妹
        this.npcs.set('hana', {
            id: 'hana',
            name: '花',
            avatar: 'hana.png',
            relationship: 0,
            personality: 'energetic', // 活泼
            description: '活泼可爱的学妹，对你充满崇拜',
            unlocked: false // 需要解锁
        });
    }

    /**
     * 初始化默认动态变量
     * @private
     */
    _initializeDynamicVariables() {
        // 当前NPC关系值（会根据currentNPC动态更新）
        this.dynamicVariables.set('npc_relationship', 0);
        
        // 故事阶段
        this.dynamicVariables.set('story_phase', 'opening');
        
        // 对话氛围
        this.dynamicVariables.set('conversation_mood', 'neutral'); // happy, neutral, tense, romantic
    }

    /**
     * 更新玩家信息
     */
    updatePlayer(updates) {
        Object.assign(this.player, updates);
    }

    /**
     * 更新场景信息
     */
    updateScene(updates) {
        Object.assign(this.scene, updates);
    }

    /**
     * 获取NPC信息
     */
    getNPC(npcId) {
        return this.npcs.get(npcId);
    }

    /**
     * 更新NPC信息
     */
    updateNPC(npcId, updates) {
        const npc = this.npcs.get(npcId);
        if (npc) {
            Object.assign(npc, updates);
            
            // 如果是当前NPC，同步更新动态变量
            if (this.currentNPC === npcId) {
                this.dynamicVariables.set('npc_relationship', npc.relationship);
            }
        }
    }

    /**
     * 设置当前对话NPC
     */
    setCurrentNPC(npcId) {
        const npc = this.npcs.get(npcId);
        if (npc && npc.unlocked) {
            this.currentNPC = npcId;
            // 同步关系值到动态变量
            this.dynamicVariables.set('npc_relationship', npc.relationship);
            return true;
        }
        return false;
    }

    /**
     * 获取当前NPC
     */
    getCurrentNPC() {
        return this.currentNPC ? this.npcs.get(this.currentNPC) : null;
    }

    /**
     * 获取所有已解锁的NPC
     */
    getUnlockedNPCs() {
        return Array.from(this.npcs.values()).filter(npc => npc.unlocked);
    }

    /**
     * 解锁NPC
     */
    unlockNPC(npcId) {
        const npc = this.npcs.get(npcId);
        if (npc) {
            npc.unlocked = true;
            return true;
        }
        return false;
    }

    addToHistory(message) {
        this.conversation.history.push({
            timestamp: Date.now(),
            ...message
        });
        
        // 保持历史记录在合理范围内
        if (this.conversation.history.length > 20) {
            this.conversation.history = this.conversation.history.slice(-15);
        }
    }

    /**
     * 设置动态变量
     * @param {string} name - 变量名
     * @param {any} value - 变量值
     */
    setDynamicVariable(name, value) {
        this.dynamicVariables.set(name, value);
    }

    /**
     * 获取动态变量
     * @param {string} name - 变量名
     * @returns {any} 变量值
     */
    getDynamicVariable(name) {
        return this.dynamicVariables.get(name);
    }

    /**
     * 批量设置动态变量
     * @param {Object} variables - 变量对象
     */
    setDynamicVariables(variables) {
        for (const [name, value] of Object.entries(variables)) {
            this.dynamicVariables.set(name, value);
        }
    }

    /**
     * 获取所有动态变量
     * @returns {Object} 所有动态变量
     */
    getAllDynamicVariables() {
        return Object.fromEntries(this.dynamicVariables);
    }

    /**
     * 更新当前NPC关系值
     * @param {number} delta - 变化量
     */
    updateNPCRelationship(delta) {
        if (!this.currentNPC) {
            console.warn('没有当前对话的NPC');
            return 0;
        }
        
        const npc = this.npcs.get(this.currentNPC);
        if (npc) {
            npc.relationship = Math.max(-100, Math.min(100, npc.relationship + delta));
            // 同步到动态变量
            this.dynamicVariables.set('npc_relationship', npc.relationship);
            return npc.relationship;
        }
        return 0;
    }

    /**
     * 设置对话氛围
     * @param {string} mood - 氛围 ('happy', 'neutral', 'tense', 'romantic')
     */
    setConversationMood(mood) {
        const validMoods = ['happy', 'neutral', 'tense', 'romantic'];
        if (!validMoods.includes(mood)) {
            console.warn(`无效的对话氛围: ${mood}`);
            return;
        }
        this.setDynamicVariable('conversation_mood', mood);
    }

    /**
     * 设置故事阶段
     * @param {string} phase - 阶段名称 ('opening', 'development', 'climax', 'ending')
     */
    setStoryPhase(phase) {
        const validPhases = ['opening', 'development', 'climax', 'ending'];
        if (!validPhases.includes(phase)) {
            console.warn(`无效的故事阶段: ${phase}`);
            return;
        }
        this.setDynamicVariable('story_phase', phase);
    }

    /**
     * 设置难度等级
     * @param {string} level - 难度等级 ('easy', 'normal', 'hard', 'nightmare')
     */
    setDifficultyLevel(level) {
        const validLevels = ['easy', 'normal', 'hard', 'nightmare'];
        if (!validLevels.includes(level)) {
            console.warn(`无效的难度等级: ${level}`);
            return;
        }
        this.setDynamicVariable('difficulty_level', level);
    }

    /**
     * 获取上下文状态（用于生成提示词）
     */
    getContextualState() {
        const currentNPC = this.getCurrentNPC();
        
        return {
            player: this.player,
            scene: this.scene,
            currentNPC: currentNPC ? {
                name: currentNPC.name,
                relationship: currentNPC.relationship,
                personality: currentNPC.personality
            } : null,
            recentHistory: this.conversation.history.slice(-5),
            dynamicVariables: this.getAllDynamicVariables()
        };
    }

    /**
     * 获取游戏统计信息
     */
    getGameStats() {
        const npcs = Array.from(this.npcs.values());
        return {
            totalNPCs: npcs.length,
            unlockedNPCs: npcs.filter(n => n.unlocked).length,
            averageRelationship: npcs.reduce((sum, n) => sum + n.relationship, 0) / npcs.length,
            currentScene: this.scene.currentScene,
            conversationCount: this.conversation.history.length
        };
    }
}

export default GameState;