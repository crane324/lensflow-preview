// utils/PromptParser.js
// 提示词解析器 - 负责解析YAML配置文件

class PromptParser {
    constructor() {
        this.config = null;
    }

    /**
     * 解析配置内容（支持JSON和YAML）
     * @param {string} content - 配置文件内容
     * @param {string} format - 格式类型 ('json' 或 'yaml')
     * @returns {Object} 解析后的配置对象
     */
    parse(content, format = 'json') {
        try {
            if (format === 'json') {
                this.config = JSON.parse(content);
            } else {
                // YAML格式（保留兼容性）
                this.config = this._simpleYAMLParse(content);
            }
            console.log('[PromptParser] Parsed config:', Object.keys(this.config));
            return this.config;
        } catch (error) {
            console.error('配置解析失败:', error);
            throw new Error(`配置解析错误: ${error.message}`);
        }
    }

    /**
     * 解析YAML配置内容（向后兼容）
     * @param {string} yamlContent - YAML文件内容
     * @returns {Object} 解析后的配置对象
     */
    parseYAML(yamlContent) {
        return this.parse(yamlContent, 'yaml');
    }

    /**
     * 解析JSON配置内容
     * @param {string} jsonContent - JSON文件内容
     * @returns {Object} 解析后的配置对象
     */
    parseJSON(jsonContent) {
        return this.parse(jsonContent, 'json');
    }

    /**
     * 简化的YAML解析器（保留用于向后兼容）
     * @private
     */
    _simpleYAMLParse(content) {
        console.warn('[PromptParser] YAML格式支持有限，建议使用JSON格式');
        return {
            version: "1.0.0",
            variables: {},
            prompt_templates: {},
            composition_strategies: {},
            extensions: {}
        };
    }

    /**
     * 验证配置文件结构
     * @param {Object} config - 配置对象
     * @returns {boolean} 是否有效
     */
    validateConfig(config) {
        const requiredFields = ['version', 'variables', 'prompt_templates', 'composition_strategies'];
        
        for (const field of requiredFields) {
            if (!config[field]) {
                throw new Error(`配置文件缺少必需字段: ${field}`);
            }
        }

        // 验证版本号格式
        if (!this._isValidVersion(config.version)) {
            throw new Error(`无效的版本号格式: ${config.version}`);
        }

        // 验证变量定义
        this._validateVariables(config.variables);

        // 验证提示词模板
        this._validatePromptTemplates(config.prompt_templates);

        return true;
    }

    /**
     * 验证版本号格式
     * @private
     */
    _isValidVersion(version) {
        return /^\d+\.\d+\.\d+$/.test(version);
    }

    /**
     * 验证变量定义
     * @private
     */
    _validateVariables(variables) {
        for (const [varName, varDef] of Object.entries(variables)) {
            if (!varDef.type) {
                throw new Error(`变量 ${varName} 缺少类型定义`);
            }

            if (!['number', 'string', 'boolean'].includes(varDef.type)) {
                throw new Error(`变量 ${varName} 的类型无效: ${varDef.type}`);
            }

            // 验证数值类型的范围
            if (varDef.type === 'number' && varDef.range) {
                if (!Array.isArray(varDef.range) || varDef.range.length !== 2) {
                    throw new Error(`变量 ${varName} 的范围定义无效`);
                }
            }

            // 验证字符串类型的可选值
            if (varDef.type === 'string' && varDef.values) {
                if (!Array.isArray(varDef.values)) {
                    throw new Error(`变量 ${varName} 的可选值定义无效`);
                }
            }
        }
    }

    /**
     * 验证提示词模板
     * @private
     */
    _validatePromptTemplates(templates) {
        for (const [templateName, template] of Object.entries(templates)) {
            if (!template.type) {
                throw new Error(`模板 ${templateName} 缺少类型定义`);
            }

            if (!['static', 'conditional', 'enum'].includes(template.type)) {
                throw new Error(`模板 ${templateName} 的类型无效: ${template.type}`);
            }

            // 验证条件模板
            if (template.type === 'conditional' || template.type === 'enum') {
                if (!template.variable) {
                    throw new Error(`模板 ${templateName} 缺少变量引用`);
                }

                if (!template.conditions || !Array.isArray(template.conditions)) {
                    throw new Error(`模板 ${templateName} 缺少条件定义`);
                }

                // 验证每个条件
                for (const condition of template.conditions) {
                    if (!condition.content) {
                        throw new Error(`模板 ${templateName} 的条件缺少内容`);
                    }

                    if (template.type === 'conditional' && !condition.range) {
                        throw new Error(`条件模板 ${templateName} 的条件缺少范围定义`);
                    }

                    if (template.type === 'enum' && condition.value === undefined) {
                        throw new Error(`枚举模板 ${templateName} 的条件缺少值定义`);
                    }
                }
            }

            // 验证静态模板
            if (template.type === 'static' && !template.content) {
                throw new Error(`静态模板 ${templateName} 缺少内容`);
            }
        }
    }

    /**
     * 获取变量定义
     * @param {string} variableName - 变量名
     * @returns {Object|null} 变量定义
     */
    getVariableDefinition(variableName) {
        if (!this.config || !this.config.variables) {
            return null;
        }
        return this.config.variables[variableName] || null;
    }

    /**
     * 获取提示词模板
     * @param {string} templateName - 模板名
     * @returns {Object|null} 模板定义
     */
    getPromptTemplate(templateName) {
        if (!this.config || !this.config.prompt_templates) {
            return null;
        }
        return this.config.prompt_templates[templateName] || null;
    }

    /**
     * 获取组合策略
     * @param {string} strategyName - 策略名
     * @returns {Object|null} 策略定义
     */
    getCompositionStrategy(strategyName) {
        if (!this.config || !this.config.composition_strategies) {
            return null;
        }
        return this.config.composition_strategies[strategyName] || null;
    }

    /**
     * 获取所有模板名称
     * @returns {string[]} 模板名称列表
     */
    getAllTemplateNames() {
        if (!this.config || !this.config.prompt_templates) {
            return [];
        }
        return Object.keys(this.config.prompt_templates);
    }

    /**
     * 获取所有策略名称
     * @returns {string[]} 策略名称列表
     */
    getAllStrategyNames() {
        if (!this.config || !this.config.composition_strategies) {
            return [];
        }
        return Object.keys(this.config.composition_strategies);
    }

    /**
     * 获取配置版本
     * @returns {string} 版本号
     */
    getVersion() {
        return this.config?.version || '0.0.0';
    }

    /**
     * 获取扩展配置
     * @returns {Object} 扩展配置
     */
    getExtensions() {
        return this.config?.extensions || {};
    }
}

export default PromptParser;