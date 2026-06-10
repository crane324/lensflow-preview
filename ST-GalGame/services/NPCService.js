// services/NPCService.js
// NPC管理服务

class NPCService {
    constructor(eventBus) {
        this.eventBus = eventBus;
        this.npcTemplates = new Map();
        this.initializeNPCTemplates();
    }

    /**
     * 初始化NPC模板
     */
    initializeNPCTemplates() {
        // 青梅竹马 - 樱
        this.npcTemplates.set('sakura', {
            id: 'sakura',
            name: '樱',
            avatar: 'sakura.png',
            personality: 'tsundere',
            personalityDescription: '傲娇',
            description: '你的青梅竹马，从小一起长大。表面上总是对你很凶，但内心其实很关心你。',
            traits: {
                // 性格特征
                prideful: 0.8,      // 自尊心强
                caring: 0.7,        // 关心他人
                honest: 0.6,        // 坦率
                shy: 0.7            // 害羞
            },
            dialoguePatterns: {
                // 对话模式（根据好感度）
                veryLow: [
                    '哼，别来烦我！',
                    '你这个笨蛋...',
                    '我才不想理你呢！'
                ],
                low: [
                    '有什么事吗？',
                    '...什么啊',
                    '别突然叫我啦'
                ],
                neutral: [
                    '嗯？怎么了？',
                    '找我有事？',
                    '说吧，什么事'
                ],
                high: [
                    '嗯...怎么了？（脸红）',
                    '你...你找我干嘛',
                    '真是的...有话快说'
                ],
                veryHigh: [
                    '你来了...（小声）',
                    '一直在等你呢...',
                    '笨蛋...我喜欢你'
                ]
            },
            unlockConditions: {
                // 解锁条件
                unlocked: true,
                requiredFlags: []
            },
            specialEvents: [
                {
                    id: 'first_meeting',
                    name: '初次相遇',
                    trigger: { type: 'first_talk' },
                    description: '与樱的第一次对话'
                },
                {
                    id: 'confession',
                    name: '告白',
                    trigger: { type: 'relationship', value: 80 },
                    description: '好感度达到80时触发'
                }
            ]
        });

        // 温柔学姐 - 雪
        this.npcTemplates.set('yuki', {
            id: 'yuki',
            name: '雪',
            avatar: 'yuki.png',
            personality: 'gentle',
            personalityDescription: '温柔',
            description: '温柔体贴的学姐，总是用温暖的笑容对待每个人。对你特别照顾。',
            traits: {
                gentle: 0.9,        // 温柔
                mature: 0.8,        // 成熟
                caring: 0.9,        // 关心他人
                patient: 0.8        // 耐心
            },
            dialoguePatterns: {
                veryLow: [
                    '你...是不是有什么误会？',
                    '我做错什么了吗？',
                    '希望你能给我一个解释的机会'
                ],
                low: [
                    '有什么我能帮忙的吗？',
                    '你看起来心情不太好',
                    '要不要聊聊？'
                ],
                neutral: [
                    '你好呀~',
                    '今天过得怎么样？',
                    '需要学姐帮忙吗？'
                ],
                high: [
                    '看到你我就很开心呢',
                    '一直在想你...',
                    '能和你在一起真好'
                ],
                veryHigh: [
                    '我最喜欢你了',
                    '想永远和你在一起',
                    '你就是我的全部'
                ]
            },
            unlockConditions: {
                unlocked: true,
                requiredFlags: []
            },
            specialEvents: [
                {
                    id: 'library_meeting',
                    name: '图书馆相遇',
                    trigger: { type: 'location', value: 'library' },
                    description: '在图书馆遇到雪学姐'
                }
            ]
        });

        // 活泼学妹 - 花
        this.npcTemplates.set('hana', {
            id: 'hana',
            name: '花',
            avatar: 'hana.png',
            personality: 'energetic',
            personalityDescription: '活泼',
            description: '充满活力的学妹，总是蹦蹦跳跳的。对你充满崇拜，经常缠着你。',
            traits: {
                energetic: 0.9,     // 活力
                cheerful: 0.9,      // 开朗
                innocent: 0.8,      // 天真
                clingy: 0.7         // 粘人
            },
            dialoguePatterns: {
                veryLow: [
                    '呜呜...前辈讨厌我吗？',
                    '我做错什么了吗？',
                    '对不起...'
                ],
                low: [
                    '前辈...？',
                    '是我惹你生气了吗？',
                    '我会改的！'
                ],
                neutral: [
                    '前辈！',
                    '前辈在干嘛呀？',
                    '陪我玩嘛~'
                ],
                high: [
                    '最喜欢前辈了！',
                    '前辈前辈！看我看我！',
                    '能一直和前辈在一起吗？'
                ],
                veryHigh: [
                    '前辈是我的！',
                    '我要永远跟着前辈！',
                    '前辈...我爱你！'
                ]
            },
            unlockConditions: {
                unlocked: false,
                requiredFlags: ['sakura_relationship_30'] // 需要先和樱达到30好感度
            },
            specialEvents: [
                {
                    id: 'unlock',
                    name: '解锁花',
                    trigger: { type: 'flag', value: 'sakura_relationship_30' },
                    description: '与樱的好感度达到30后解锁'
                }
            ]
        });
    }

    /**
     * 获取NPC模板
     */
    getNPCTemplate(npcId) {
        return this.npcTemplates.get(npcId);
    }

    /**
     * 获取所有NPC模板
     */
    getAllNPCTemplates() {
        return Array.from(this.npcTemplates.values());
    }

    /**
     * 根据好感度获取对话模式
     */
    getDialoguePattern(npcId, relationship) {
        const template = this.getNPCTemplate(npcId);
        if (!template) return null;

        const patterns = template.dialoguePatterns;
        
        if (relationship < -50) {
            return patterns.veryLow;
        } else if (relationship < 0) {
            return patterns.low;
        } else if (relationship < 50) {
            return patterns.neutral;
        } else if (relationship < 80) {
            return patterns.high;
        } else {
            return patterns.veryHigh;
        }
    }

    /**
     * 获取随机对话示例
     */
    getRandomDialogue(npcId, relationship) {
        const patterns = this.getDialoguePattern(npcId, relationship);
        if (!patterns || patterns.length === 0) return null;
        
        return patterns[Math.floor(Math.random() * patterns.length)];
    }

    /**
     * 检查NPC是否可以解锁
     */
    canUnlockNPC(npcId, gameState) {
        const template = this.getNPCTemplate(npcId);
        if (!template) return false;

        const conditions = template.unlockConditions;
        
        // 如果已经解锁，返回true
        if (conditions.unlocked) return true;

        // 检查所有必需的标记
        for (const flag of conditions.requiredFlags) {
            if (!gameState.gameFlags.get(flag)) {
                return false;
            }
        }

        return true;
    }

    /**
     * 获取NPC性格描述
     */
    getPersonalityDescription(personality) {
        const descriptions = {
            'tsundere': {
                name: '傲娇',
                description: '表面冷淡甚至有些凶，但内心温柔关心他人',
                tips: '不要被表面的态度吓到，要看到她内心的温柔'
            },
            'gentle': {
                name: '温柔',
                description: '温柔体贴，总是用温暖的态度对待他人',
                tips: '真诚地对待她，她会给予你更多的关心'
            },
            'energetic': {
                name: '活泼',
                description: '充满活力，开朗乐观，喜欢和人亲近',
                tips: '多陪她玩耍，回应她的热情'
            },
            'shy': {
                name: '害羞',
                description: '内向害羞，不善于表达，但内心细腻',
                tips: '要有耐心，慢慢打开她的心扉'
            },
            'cool': {
                name: '冷酷',
                description: '冷静理智，不轻易表露情感',
                tips: '用真诚打动她，让她看到你的真心'
            }
        };

        return descriptions[personality] || {
            name: personality,
            description: '独特的性格',
            tips: '用心了解她'
        };
    }

    /**
     * 获取好感度等级描述
     */
    getRelationshipLevel(relationship) {
        if (relationship < -50) {
            return { level: '厌恶', color: '#e74c3c', emoji: '😠' };
        } else if (relationship < 0) {
            return { level: '冷淡', color: '#e67e22', emoji: '😐' };
        } else if (relationship < 30) {
            return { level: '普通', color: '#95a5a6', emoji: '🙂' };
        } else if (relationship < 60) {
            return { level: '友好', color: '#3498db', emoji: '😊' };
        } else if (relationship < 80) {
            return { level: '亲密', color: '#9b59b6', emoji: '😍' };
        } else {
            return { level: '恋人', color: '#e91e63', emoji: '💕' };
        }
    }

    /**
     * 创建NPC实例
     */
    createNPCInstance(npcId) {
        const template = this.getNPCTemplate(npcId);
        if (!template) return null;

        return {
            id: template.id,
            name: template.name,
            avatar: template.avatar,
            personality: template.personality,
            description: template.description,
            relationship: 0,
            unlocked: template.unlockConditions.unlocked,
            metCount: 0,
            lastMetTime: null,
            specialEventsTriggered: []
        };
    }
}

export default NPCService;