// services/DynamicPromptService.js
// 动态提示词管理服务 - 负责加载、选择和组合提示词

import PromptParser from '../utils/PromptParser.js';

class DynamicPromptService {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.parser = new PromptParser();
        this.config = null;
        this.cache = new Map();
        this.computedVariableFunctions = new Map();
        this.isInitialized = false;
    }

    /**
     * 初始化服务 - 加载配置文件
     * @param {string} configPath - 配置文件路径
     */
    async initialize(configPath = 'config/prompts/galgame-prompts.json') {
        try {
            // 使用配置的基础URL
            const fullPath = window.GameConfig ? window.GameConfig.getConfigPath(configPath) : configPath;
            
            // 加载配置文件
            const content = await this._loadConfigFile(fullPath);
            
            // 根据文件扩展名判断格式
            const format = configPath.endsWith('.json') ? 'json' : 'yaml';
            
            // 解析配置
            this.config = this.parser.parse(content, format);
            
            // 验证配置
            this.parser.validateConfig(this.config);
            
            // 加载扩展配置
            await this._loadExtensions();
            
            this.isInitialized = true;
            this.eventBus?.emit('prompt:initialized', { version: this.config.version }, 'game');
            
            console.log(`动态提示词服务已初始化 - 版本: ${this.config.version}`);
        } catch (error) {
            console.error('初始化动态提示词服务失败:', error);
            throw error;
        }
    }

    /**
     * 加载配置文件
     * @private
     */
    async _loadConfigFile(path) {
        try {
            console.log('[DynamicPromptService] Loading config from:', path);
            const response = await fetch(path);
            if (!response.ok) {
                throw new Error(`无法加载配置文件: ${path} (${response.status})`);
            }
            const content = await response.text();
            console.log('[DynamicPromptService] Config loaded successfully, length:', content.length);
            return content;
        } catch (error) {
            console.error('加载配置文件失败:', error);
            throw error;
        }
    }

    /**
     * 加载扩展配置
     * @private
     */
    async _loadExtensions() {
        const extensions = this.parser.getExtensions();
        
        if (extensions.additional_files && Array.isArray(extensions.additional_files)) {
            for (const filePath of extensions.additional_files) {
                try {
                    await this._loadAdditionalConfig(filePath);
                } catch (error) {
                    console.warn(`加载扩展配置失败: ${filePath}`, error);
                }
            }
        }
    }

    /**
     * 加载额外的配置文件
     * @private
     */
    async _loadAdditionalConfig(path) {
        try {
            // 使用配置的基础URL
            const fullPath = window.GameConfig ? window.GameConfig.getConfigPath(path) : path;
            console.log(`加载额外配置: ${fullPath}`);
            // 实现加载额外配置文件的逻辑
            // 可以合并到主配置中
        } catch (error) {
            console.warn(`加载额外配置失败: ${path}`, error);
        }
    }

    /**
     * 注册计算变量函数
     * @param {string} variableName - 变量名
     * @param {Function} computeFunction - 计算函数
     */
    registerComputedVariable(variableName, computeFunction) {
        if (typeof computeFunction !== 'function') {
            throw new Error('计算函数必须是一个函数');
        }
        this.computedVariableFunctions.set(variableName, computeFunction);
        console.log(`已注册计算变量: ${variableName}`);
    }

    /**
     * 生成动态提示词
     * @param {Object} variables - 变量值对象
     * @param {string} strategy - 组合策略名称（默认为'default'）
     * @returns {string} 组合后的提示词
     */
    generatePrompt(variables = {}, strategy = 'default') {
        if (!this.isInitialized) {
            throw new Error('服务未初始化，请先调用 initialize()');
        }

        // 检查缓存
        const cacheKey = this._generateCacheKey(variables, strategy);
        if (this._isCacheValid(cacheKey)) {
            return this.cache.get(cacheKey).content;
        }

        try {
            // 计算所有变量（包括计算变量）
            const computedVariables = this._computeAllVariables(variables);

            // 获取组合策略
            const compositionStrategy = this.parser.getCompositionStrategy(strategy);
            if (!compositionStrategy) {
                throw new Error(`未找到组合策略: ${strategy}`);
            }

            // 按策略顺序组合提示词
            const promptParts = [];
            for (const templateName of compositionStrategy.order) {
                const template = this.parser.getPromptTemplate(templateName);
                if (!template) {
                    console.warn(`未找到模板: ${templateName}`);
                    continue;
                }

                const content = this._resolveTemplate(template, computedVariables);
                if (content) {
                    promptParts.push(content);
                }
            }

            // 组合最终提示词
            const finalPrompt = promptParts.join('\n\n');

            // 缓存结果
            this._cachePrompt(cacheKey, finalPrompt);

            // 触发事件
            this.eventBus?.emit('prompt:generated', { 
                strategy, 
                variables: computedVariables,
                length: finalPrompt.length 
            }, 'game');

            return finalPrompt;
        } catch (error) {
            console.error('生成提示词失败:', error);
            throw error;
        }
    }

    /**
     * 计算所有变量（包括计算变量）
     * @private
     */
    _computeAllVariables(variables) {
        const result = { ...variables };

        // 执行计算变量函数
        for (const [varName, computeFunc] of this.computedVariableFunctions.entries()) {
            try {
                result[varName] = computeFunc(result);
            } catch (error) {
                console.error(`计算变量 ${varName} 失败:`, error);
            }
        }

        return result;
    }

    /**
     * 解析模板内容
     * @private
     */
    _resolveTemplate(template, variables) {
        switch (template.type) {
            case 'static':
                return this._resolveStaticTemplate(template);
            
            case 'conditional':
                return this._resolveConditionalTemplate(template, variables);
            
            case 'enum':
                return this._resolveEnumTemplate(template, variables);
            
            default:
                console.warn(`未知的模板类型: ${template.type}`);
                return null;
        }
    }

    /**
     * 解析静态模板
     * @private
     */
    _resolveStaticTemplate(template) {
        return template.content;
    }

    /**
     * 解析条件模板（基于数值范围）
     * @private
     */
    _resolveConditionalTemplate(template, variables) {
        const variableValue = variables[template.variable];
        
        if (variableValue === undefined) {
            console.warn(`变量 ${template.variable} 未定义`);
            return null;
        }

        // 查找匹配的条件
        for (const condition of template.conditions) {
            const [min, max] = condition.range;
            if (variableValue >= min && variableValue <= max) {
                return condition.content;
            }
        }

        console.warn(`变量 ${template.variable} 的值 ${variableValue} 不在任何范围内`);
        return null;
    }

    /**
     * 解析枚举模板（基于精确值匹配）
     * @private
     */
    _resolveEnumTemplate(template, variables) {
        const variableValue = variables[template.variable];
        
        if (variableValue === undefined) {
            console.warn(`变量 ${template.variable} 未定义`);
            return null;
        }

        // 查找匹配的条件
        const condition = template.conditions.find(c => c.value === variableValue);
        
        if (!condition) {
            console.warn(`变量 ${template.variable} 的值 ${variableValue} 没有匹配的条件`);
            return null;
        }

        return condition.content;
    }

    /**
     * 生成缓存键
     * @private
     */
    _generateCacheKey(variables, strategy) {
        const sortedVars = Object.keys(variables).sort().map(k => `${k}:${variables[k]}`).join('|');
        return `${strategy}::${sortedVars}`;
    }

    /**
     * 检查缓存是否有效
     * @private
     */
    _isCacheValid(cacheKey) {
        const extensions = this.parser.getExtensions();
        if (!extensions.cache?.enabled) {
            return false;
        }

        const cached = this.cache.get(cacheKey);
        if (!cached) {
            return false;
        }

        const ttl = extensions.cache.ttl || 300;
        const age = (Date.now() - cached.timestamp) / 1000;
        
        return age < ttl;
    }

    /**
     * 缓存提示词
     * @private
     */
    _cachePrompt(cacheKey, content) {
        const extensions = this.parser.getExtensions();
        if (!extensions.cache?.enabled) {
            return;
        }

        this.cache.set(cacheKey, {
            content,
            timestamp: Date.now()
        });

        // 限制缓存大小
        if (this.cache.size > 100) {
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
    }

    /**
     * 清除缓存
     */
    clearCache() {
        this.cache.clear();
        this.eventBus?.emit('prompt:cache:cleared', {}, 'game');
        console.log('提示词缓存已清除');
    }

    /**
     * 获取可用的策略列表
     * @returns {string[]} 策略名称列表
     */
    getAvailableStrategies() {
        return this.parser.getAllStrategyNames();
    }

    /**
     * 获取可用的模板列表
     * @returns {string[]} 模板名称列表
     */
    getAvailableTemplates() {
        return this.parser.getAllTemplateNames();
    }

    /**
     * 获取变量定义
     * @param {string} variableName - 变量名
     * @returns {Object|null} 变量定义
     */
    getVariableDefinition(variableName) {
        return this.parser.getVariableDefinition(variableName);
    }

    /**
     * 验证变量值
     * @param {string} variableName - 变量名
     * @param {any} value - 变量值
     * @returns {boolean} 是否有效
     */
    validateVariableValue(variableName, value) {
        const definition = this.getVariableDefinition(variableName);
        if (!definition) {
            return false;
        }

        // 类型检查
        if (typeof value !== definition.type) {
            return false;
        }

        // 范围检查（数值类型）
        if (definition.type === 'number' && definition.range) {
            const [min, max] = definition.range;
            return value >= min && value <= max;
        }

        // 枚举值检查（字符串类型）
        if (definition.type === 'string' && definition.values) {
            return definition.values.includes(value);
        }

        return true;
    }

    /**
     * 获取服务状态
     * @returns {Object} 状态信息
     */
    getStatus() {
        return {
            initialized: this.isInitialized,
            version: this.parser.getVersion(),
            cacheSize: this.cache.size,
            strategiesCount: this.getAvailableStrategies().length,
            templatesCount: this.getAvailableTemplates().length,
            computedVariablesCount: this.computedVariableFunctions.size
        };
    }
}

export default DynamicPromptService;