# 动态提示词配置目录

本目录包含动态提示词系统的配置文件。

## 文件说明

### dynamic-prompts.yaml
主配置文件，包含：
- **变量定义**：定义可用的动态变量及其类型、范围
- **提示词模板**：定义各种条件下的提示词内容
- **组合策略**：定义提示词的组合顺序
- **扩展配置**：缓存、额外文件等配置

## 快速开始

### 1. 定义新变量

在 `variables` 部分添加：

```yaml
variables:
  your_variable_name:
    type: "number"  # 或 "string", "boolean"
    description: "变量描述"
    range: [min, max]  # 数值类型
    # 或
    values: ["value1", "value2"]  # 字符串类型
```

### 2. 创建提示词模板

#### 静态模板（固定内容）

```yaml
prompt_templates:
  template_name:
    type: "static"
    content: |
      你的提示词内容...
```

#### 条件模板（数值范围）

```yaml
prompt_templates:
  template_name:
    type: "conditional"
    variable: "your_variable_name"
    conditions:
      - range: [min, max]
        label: "标签"
        content: |
          当变量在此范围时的提示词...
```

#### 枚举模板（精确匹配）

```yaml
prompt_templates:
  template_name:
    type: "enum"
    variable: "your_variable_name"
    conditions:
      - value: "specific_value"
        label: "标签"
        content: |
          当变量等于此值时的提示词...
```

### 3. 定义组合策略

```yaml
composition_strategies:
  strategy_name:
    description: "策略描述"
    order:
      - "template1"
      - "template2"
      - "template3"
```

## 模板类型详解

### Static（静态）
- 始终包含的固定内容
- 不依赖任何变量
- 适用于：基础规则、系统说明

### Conditional（条件）
- 基于数值变量的范围选择
- 变量值必须在某个区间内
- 适用于：关系值、声望、百分比等

### Enum（枚举）
- 基于字符串变量的精确匹配
- 变量值必须完全相等
- 适用于：阶段、状态、模式等

## 变量命名规范

- 使用小写字母和下划线
- 清晰描述变量含义
- 示例：
  - ✅ `npc_relationship`
  - ✅ `player_reputation`
  - ✅ `story_phase`
  - ❌ `nr`
  - ❌ `rep`
  - ❌ `phase`

## 内容编写建议

1. **简洁明确**：避免冗长的描述
2. **结构清晰**：使用标题和列表
3. **一致性**：保持相似模板的格式一致
4. **可读性**：使用适当的缩进和空行
5. **注释**：在复杂逻辑处添加注释

## 扩展配置

### 加载额外配置文件

```yaml
extensions:
  additional_files:
    - "config/prompts/custom-prompts.yaml"
    - "config/prompts/event-prompts.yaml"
```

### 缓存配置

```yaml
extensions:
  cache:
    enabled: true
    ttl: 300  # 缓存时间（秒）
```

## 示例配置

### 完整的变量+模板示例

```yaml
# 定义变量
variables:
  player_mood:
    type: "string"
    description: "玩家情绪"
    values: ["happy", "neutral", "angry"]

# 创建模板
prompt_templates:
  player_mood:
    type: "enum"
    variable: "player_mood"
    conditions:
      - value: "happy"
        label: "愉快"
        content: |
          玩家心情愉快，更容易接受建议。
      
      - value: "neutral"
        label: "中立"
        content: |
          玩家保持中立态度。
      
      - value: "angry"
        label: "愤怒"
        content: |
          玩家情绪激动，需要谨慎应对。

# 添加到策略
composition_strategies:
  default:
    order:
      - "base_gm"
      - "player_mood"  # 新增
      - "game_rules"
```

## 最佳实践

1. **版本控制**：配置文件应纳入Git管理
2. **备份**：修改前备份原文件
3. **测试**：修改后测试所有受影响的场景
4. **文档**：为复杂逻辑添加注释
5. **渐进式**：逐步添加新功能，避免一次性大改

## 故障排查

### 配置未生效
- 检查YAML语法是否正确
- 确认文件路径正确
- 查看控制台错误信息

### 变量值无效
- 确认值在定义的范围内
- 检查类型是否匹配
- 使用验证API测试

### 提示词未选择
- 确认变量值匹配某个条件
- 检查范围是否有遗漏
- 查看日志中的警告信息

## 相关文档

- [动态提示词系统使用指南](../../docs/dynamic-prompts-guide.md)
- [使用示例](../../examples/dynamic-prompts-example.js)

## 技术支持

如有问题，请查看：
1. 完整文档：`docs/dynamic-prompts-guide.md`
2. 代码示例：`examples/dynamic-prompts-example.js`
3. 源代码：`services/DynamicPromptService.js`