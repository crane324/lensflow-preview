# 💕 GalGame 恋爱模拟器

一个基于LLM驱动的恋爱模拟游戏Demo，通过动态提示词系统根据NPC好感度自动调整对话内容和角色态度。

## ✨ 特性

### 🎮 游戏特性
- **多角色系统**：与不同性格的NPC互动（傲娇、温柔、活泼）
- **好感度系统**：通过对话影响NPC对你的态度（-100到100）
- **动态对话**：AI根据好感度生成符合角色性格的回应
- **故事进度**：随着游戏推进解锁新角色和剧情
- **特殊事件**：好感度达到特定值时触发特殊剧情

### 🤖 技术特性
- **动态提示词系统**：基于好感度自动选择合适的提示词
- **角色性格系统**：每个NPC都有独特的性格特征和对话模式
- **事件触发机制**：灵活的事件系统支持各种剧情触发
- **实时反馈**：对话即时影响好感度并更新UI显示
- **模块化架构**：清晰的MVC架构，易于扩展

## 🚀 快速开始

### 环境要求

- 支持ES6模块的现代浏览器
- 小白X插件环境或支持 `callGenerate` 函数的iframe环境

### 部署方式

#### 方式1：CDN部署（推荐）

项目已部署到CDN，可以直接在本地使用：

1. **下载index.html**到本地
2. **在小白X环境中打开**
3. **所有资源自动从CDN加载**

CDN地址：
```
https://cdn.jsdelivr.net/gh/halfmadnya/ST-GalGame@main/
```

#### 方式2：本地部署

1. 克隆整个仓库
2. 修改 `config.js` 中的 `BASE_URL` 为 `'./'`
3. 在本地服务器中运行

### 启动游戏

1. 在支持的环境中打开 `index.html`
2. 等待游戏初始化完成（资源从CDN加载）
3. 点击左侧角色卡片选择对话对象
4. 在底部输入框输入你想说的话
5. 观察好感度变化，享受恋爱之旅！

> 💡 **提示**：首次加载可能需要几秒钟，因为需要从CDN下载资源。

## 📖 游戏指南

### 角色介绍

#### 樱（Sakura）- 青梅竹马 🌸
- **性格**：傲娇（Tsundere）
- **特点**：表面冷淡但内心温柔
- **攻略提示**：不要被她的态度吓到，要看穿她的口是心非

#### 雪（Yuki）- 温柔学姐 ❄️
- **性格**：温柔（Gentle）
- **特点**：成熟体贴，善于照顾他人
- **攻略提示**：真诚对待，展现你成熟的一面

#### 花（Hana）- 活泼学妹 🌺
- **性格**：活泼（Energetic）
- **特点**：充满活力，天真可爱
- **解锁条件**：与樱的好感度达到30
- **攻略提示**：多陪她玩耍，回应她的热情

### 好感度系统

| 等级 | 范围 | 表情 | 态度描述 |
|------|------|------|----------|
| 厌恶 | -100~-50 | 😠 | 非常反感，主动避开 |
| 冷淡 | -49~-10 | 😐 | 保持距离，缺乏热情 |
| 普通 | -9~20 | 🙂 | 正常交流，不亲不疏 |
| 友好 | 21~50 | 😊 | 有好感，愿意互动 |
| 亲密 | 51~75 | 😍 | 明显喜欢，经常想见 |
| 恋人 | 76~100 | 💕 | 深深爱着，想永远在一起 |

### 提升好感度的方法

**✅ 增加好感度**：
- 说让角色开心的话
- 关心角色的感受
- 符合角色性格的互动
- 在适当时机表达好感

**❌ 减少好感度**：
- 说伤人的话
- 忽视角色的感受
- 不符合角色性格的要求
- 过于冷淡或过于热情（时机不对）

## 🏗️ 项目结构

```
LLM-游戏最小实现demo/
├── index.html                          # 主页面
├── README.md                           # 项目说明
│
├── assets/                             # 资源文件
│   └── styles/
│       └── galgame.css                 # GalGame样式
│
├── config/                             # 配置文件
│   └── prompts/
│       ├── galgame-prompts.yaml        # GalGame提示词配置
│       ├── dynamic-prompts.yaml        # 通用动态提示词配置
│       └── README.md                   # 配置说明
│
├── core/                               # 核心模块
│   ├── EventBus.js                     # 事件总线
│   ├── ServiceLocator.js               # 服务定位器
│   └── GameCore.js                     # 游戏核心
│
├── models/                             # 数据模型
│   └── GameState.js                    # 游戏状态（含NPC系统）
│
├── services/                           # 服务层
│   ├── LLMService.js                   # LLM服务
│   ├── DynamicPromptService.js         # 动态提示词服务
│   ├── GameStateService.js             # 状态管理服务
│   └── NPCService.js                   # NPC管理服务
│
├── controllers/                        # 控制器
│   └── GameController.js               # 游戏控制器
│
├── views/                              # 视图层
│   └── GameView.js                     # 游戏视图
│
├── utils/                              # 工具类
│   └── PromptParser.js                 # 提示词解析器
│
├── docs/                               # 文档
│   ├── galgame-guide.md                # GalGame使用指南
│   └── dynamic-prompts-guide.md        # 动态提示词系统指南
│
└── examples/                           # 示例代码
    └── dynamic-prompts-example.js      # 动态提示词使用示例
```

## 📦 部署说明

### CDN配置

项目使用jsDelivr CDN加载资源：
- **自动检测**：本地文件自动使用CDN
- **配置文件**：`config.js` 管理所有路径
- **JSON格式**：使用JSON配置文件，浏览器原生支持

### 文件说明

- `index.html` - 主页面，可单独下载使用
- `config.js` - 配置文件，从CDN加载
- `config/prompts/galgame-prompts.json` - 提示词配置（JSON格式）

详细部署说明请查看：[DEPLOYMENT.md](DEPLOYMENT.md)

## 🔧 技术架构

### 核心技术栈

- **前端框架**：原生JavaScript + ES6模块
- **AI集成**：LLM API（通过callGenerate）
- **配置管理**：YAML格式配置文件
- **架构模式**：MVC + 事件驱动

### 系统架构

```
┌─────────────────────────────────────────────────┐
│                   GameCore                       │
│  ┌───────────────────────────────────────────┐  │
│  │           EventBus (事件总线)              │  │
│  └───────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────┐  │
│  │      ServiceLocator (服务定位器)          │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
         │                    │
    ┌────┴────┐          ┌────┴────┐
    │ Services │          │  Views  │
    └────┬────┘          └────┬────┘
         │                    │
    ┌────┴──────────────┐    │
    │ Controllers        │────┘
    └───────────────────┘
```

### 动态提示词系统

```
用户输入 → 获取游戏状态 → 提取动态变量
    ↓
选择提示词模板（基于好感度区间）
    ↓
组合最终提示词 → 调用LLM → 生成回应
    ↓
解析回应 → 更新好感度 → 更新UI
```

## 🎨 自定义开发

### 添加新角色

1. **在GameState中定义NPC**（`models/GameState.js`）
2. **在NPCService中添加模板**（`services/NPCService.js`）
3. **配置提示词**（`config/prompts/galgame-prompts.yaml`）

详细步骤请参考：[GalGame开发指南](docs/galgame-guide.md#开发指南)

### 修改提示词

编辑 `config/prompts/galgame-prompts.yaml`：

```yaml
npc_relationship:
  type: "conditional"
  variable: "npc_relationship"
  conditions:
    - range: [51, 75]
      label: "亲密"
      content: |
        ## NPC好感度：亲密
        你的自定义提示词内容...
```

### 添加特殊事件

在 `controllers/GameController.js` 中：

```javascript
checkSpecialEvents(gameState, npc) {
    if (npc.relationship >= 60) {
        // 触发你的特殊事件
    }
}
```

## 📚 文档

- [GalGame使用指南](docs/galgame-guide.md) - 完整的游戏指南和开发文档
- [动态提示词系统指南](docs/dynamic-prompts-guide.md) - 动态提示词系统详解
- [配置文件说明](config/prompts/README.md) - YAML配置文件格式说明

## 🎯 核心功能实现

### 1. 动态提示词系统

根据NPC好感度自动选择合适的提示词：

```javascript
// 获取动态变量
const variables = gameState.getAllDynamicVariables();

// 生成提示词（自动根据好感度选择）
const prompt = gameStateService.generateGamePrompt({
    variables: variables,
    strategy: 'default'
});
```

### 2. 好感度管理

```javascript
// 更新好感度
gameState.updateNPCRelationship(+5);  // 增加5点
gameState.updateNPCRelationship(-3);  // 减少3点

// 获取当前好感度
const relationship = gameState.getCurrentNPC().relationship;
```

### 3. NPC系统

```javascript
// 选择NPC
gameState.setCurrentNPC('sakura');

// 获取NPC信息
const npc = gameState.getCurrentNPC();
console.log(npc.name, npc.personality, npc.relationship);
```

## 🐛 调试

按 `Ctrl+D` 打开调试面板，查看：
- 游戏状态
- 事件日志
- 错误信息

## 🔮 未来计划

- [ ] 存档系统
- [ ] CG收集
- [ ] 多结局系统
- [ ] 语音系统
- [ ] 背景音乐
- [ ] 选项系统
- [ ] 成就系统
- [ ] 时间系统

## 📝 更新日志

### v2.0.0 - GalGame版本
- ✨ 完全改造为GalGame恋爱模拟器
- ✨ 实现动态提示词系统
- ✨ 添加好感度系统
- ✨ 实现多角色系统
- ✨ 添加特殊事件触发
- 🎨 全新的GalGame风格UI
- 📚 完整的文档和指南

### v1.0.0 - RPG版本
- 基础的RPG游戏框架
- LLM驱动的游戏叙事
- 函数调用系统

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可

MIT License

## 💖 致谢

感谢所有为这个项目做出贡献的开发者！

---

**开始你的恋爱之旅吧！** 💕

如有问题，请查看[完整文档](docs/galgame-guide.md)或提交Issue。