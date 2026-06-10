// services/GameStateService.js
import GameState from '../models/GameState.js';
import DynamicPromptService from './DynamicPromptService.js';

class GameStateService {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.gameState = new GameState();
        this.dynamicPromptService = new DynamicPromptService(eventBus);
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.eventBus.on('game:action', this.handleGameAction.bind(this), 'game');
        this.eventBus.on('function:execute:complete', this.handleFunctionResult.bind(this), 'game');
    }

    /**
     * 初始化动态提示词服务
     * @param {string} configPath - 配置文件路径
     */
    async initializeDynamicPrompts(configPath) {
        try {
            await this.dynamicPromptService.initialize(configPath);
            console.log('动态提示词系统已集成到GameStateService');
        } catch (error) {
            console.error('初始化动态提示词失败:', error);
            // 降级到传统提示词生成
            console.warn('将使用传统提示词生成方式');
        }
    }

    getState() {
        return this.gameState;
    }

    updatePlayerStats(updates) {
        this.gameState.updatePlayer(updates);
        this.eventBus.emit('state:player:updated', this.gameState.player, 'game');
    }

    updateWorldState(updates) {
        this.gameState.updateWorld(updates);
        this.eventBus.emit('state:world:updated', this.gameState.world, 'game');
    }

    addConversationEntry(entry) {
        this.gameState.addToHistory(entry);
        this.eventBus.emit('state:conversation:updated', entry, 'game');
    }

    handleGameAction(actionData) {
        this.addConversationEntry({
            role: 'user',
            content: actionData.action,
            type: 'player_action'
        });
    }

    handleFunctionResult(data) {
        const { name, result } = data;
        
        // 根据函数结果更新游戏状态
        if (name === 'start_battle' && result.outcome === 'victory') {
            this.updatePlayerStats({
                experience: this.gameState.player.experience + result.experience
            });
        }
        
        this.addConversationEntry({
            role: 'system',
            content: `函数执行结果: ${name}`,
            result: result,
            type: 'function_result'
        });
    }

    /**
     * 生成游戏提示词
     * @param {Object} options - 生成选项
     * @param {Object} options.variables - 动态变量值
     * @param {string} options.strategy - 组合策略（默认'default'）
     * @param {boolean} options.useDynamic - 是否使用动态提示词（默认true）
     * @returns {string} 生成的提示词
     */
    generateGamePrompt(options = {}) {
        const {
            variables = {},
            strategy = 'default',
            useDynamic = true
        } = options;

        // 如果启用动态提示词且服务已初始化，使用动态生成
        if (useDynamic && this.dynamicPromptService.isInitialized) {
            try {
                return this._generateDynamicPrompt(variables, strategy);
            } catch (error) {
                console.error('动态提示词生成失败，降级到传统方式:', error);
                return this._generateLegacyPrompt();
            }
        }

        // 降级到传统提示词生成
        return this._generateLegacyPrompt();
    }

    /**
     * 使用动态提示词服务生成提示词
     * @private
     */
    _generateDynamicPrompt(variables, strategy) {
        const state = this.gameState.getContextualState();
        
        // 合并游戏状态到变量中
        const mergedVariables = {
            ...variables,
            // 可以从游戏状态中提取更多变量
            player_level: state.player.level,
            player_hp_percentage: (state.player.hp / state.player.maxHp) * 100,
            current_location: state.world.currentLocation
        };

        // 使用动态提示词服务生成
        let prompt = this.dynamicPromptService.generatePrompt(mergedVariables, strategy);

        // 添加当前游戏状态信息
        prompt += `\n\n## 当前游戏状态：
- 玩家：${state.player.name} (等级${state.player.level})
- 生命值：${state.player.hp}/${state.player.maxHp}
- 位置：${state.world.currentLocation}
- 时间：${state.world.timeOfDay}`;

        return prompt;
    }

    /**
     * 传统提示词生成方式（向后兼容）
     * @private
     */
    _generateLegacyPrompt() {
        const state = this.gameState.getContextualState();
        
        return `你是一个专业的游戏主持人(GM)，正在运行一个地牢探险RPG游戏。

## 当前游戏状态：
- 玩家：${state.player.name} (等级${state.player.level})
- 生命值：${state.player.hp}/${state.player.maxHp}
- 位置：${state.world.currentLocation}
- 时间：${state.world.timeOfDay}

## 游戏规则：
1. 根据玩家行动生动描述场景和结果
2. 在适当时机调用游戏功能
3. 保持故事的连贯性和挑战性

## 函数调用规则：
当需要调用游戏功能时，使用以下格式，并在调用后立即停止输出：

战斗系统：
<FUNCTION_CALL>
{
  "name": "start_battle",
  "arguments": {
    "enemies": [{"type": "哥布林", "level": 2, "count": 1}],
    "environment": "地牢走廊",
    "special_conditions": ["昏暗"]
  }
}
</FUNCTION_CALL>

解谜系统：
<FUNCTION_CALL>
{
  "name": "start_puzzle",
  "arguments": {
    "puzzle_type": "古代机关",
    "difficulty": "medium"
  }
}
</FUNCTION_CALL>

搜索系统：
<FUNCTION_CALL>
{
  "name": "search_area",
  "arguments": {
    "target": "古老的宝箱",
    "difficulty": "easy"
  }
}
</FUNCTION_CALL>

重要：输出函数调用后立即停止，等待系统执行完毕！`;
    }

    /**
     * 获取动态提示词服务实例
     * @returns {DynamicPromptService} 动态提示词服务
     */
    getDynamicPromptService() {
        return this.dynamicPromptService;
    }
}

export default GameStateService;