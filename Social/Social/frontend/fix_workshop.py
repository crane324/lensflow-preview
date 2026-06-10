import re

with open('workshop.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Basic Info 中文标签
content = content.replace('<tr><td>Name</td>', '<tr><td>昵称</td>')
content = content.replace('<tr><td>Age</td>', '<tr><td>年龄</td>')
content = content.replace('<tr><td>Skills</td>', '<tr><td>技能特长</td>')
content = content.replace('<tr><td>Personality</td>', '<tr><td>性格类型</td>')

# 2. 按钮文字
content = content.replace('AI 智能生成', '🎲 随机生成人设')
content = content.replace(
    'placeholder="在这里写下你的自我介绍，或点击右下角粉色按钮让 AI 帮你生成..."',
    'placeholder="在这里写下你的自我介绍，或点击「随机生成人设」按钮自动填充..."')

# 3. About Me 按钮区添加"开始匹配"
old_btn = '<button class="update-btn" onclick="generateProfile()"><i class="fa fa-magic"></i> AI 智能生成</button>'
new_btn = '<button class="update-btn" onclick="generateProfile()"><i class="fa fa-magic"></i> 🎲 随机生成人设</button>\n                <button class="update-btn" id="goMatchBtn" onclick="goToMatch()" style="display:none;margin-left:8px;border-color:#FF6B9D;color:#FF6B9D;"><i class="fa fa-heart"></i> 💕 开始匹配</button>'
content = content.replace(old_btn, new_btn)

# 4. updateStatusUI 结尾加匹配按钮显示
old = "tag.style.background=m.bg||''; tag.style.color=m.c||''; }"
new = "tag.style.background=m.bg||''; tag.style.color=m.c||'';\n    var mb=document.getElementById('goMatchBtn');if(mb)mb.style.display=(s==='generated')?'inline-flex':'none'; }"
content = content.replace(old, new)

# 5. loadFromStorage 中生成状态恢复时也显示匹配按钮
old_gen = "if(profileStatus==='generated')updateStatusUI('generated');"
new_gen = "if(profileStatus==='generated'){updateStatusUI('generated');var mb2=document.getElementById('goMatchBtn');if(mb2)mb2.style.display='inline-flex';}"
content = content.replace(old_gen, new_gen)

# 6. 替换 buildAiProfile 为人设档案库
old_func_start = "function buildAiProfile() {"
old_func_end = "}"
# Find the function
idx_start = content.index(old_func_start)
# Find the matching closing brace
brace_count = 0
idx_end = idx_start
for i in range(idx_start, len(content)):
    if content[i] == '{': brace_count += 1
    elif content[i] == '}':
        brace_count -= 1
        if brace_count == 0:
            idx_end = i + 1
            break

persona_db = '''// ========== 人设档案库（8个完整模版，保证一致性） ==========
var PERSONA_DB = [
    {name:'林悦',age:24,gender:'female',hbd:'3月12日',skills:'手冲咖啡 · 插画设计 · 尤克里里',personality:'温和均衡 · 文艺清新',mbti:'INFP-T',values:'自由探索型 · 成长学习型',interests:['咖啡','插画','独立音乐','旅行','烘焙','逛书店'],bio:'你好，我是林悦。我是一个独立插画师，周末最喜欢泡在咖啡馆里画画。B型血，INFP人格，相信生活应该有诗意和远方。最近在学尤克里里，虽然弹得还不怎么样，但每次拨弦的时候都觉得世界变温柔了。希望遇到一个能一起看展、一起发呆的人。'},
    {name:'陈墨',age:27,gender:'male',hbd:'8月5日',skills:'数据分析 · 摄影 · 攀岩',personality:'理性逻辑 · 外冷内热',mbti:'INTJ-T',values:'事业成就型 · 自由探索型',interests:['摄影','攀岩','科技数码','天文学','围棋','科幻小说'],bio:'你好，我是陈墨。在互联网公司做数据科学，业余时间喜欢背着相机去拍星轨。AB型血，INTJ人格，话不多但心里有片宇宙。最近读完《三体》第三遍，依然被震撼。希望能遇到一个有趣的人，一起探索这个世界未尽的角落。'},
    {name:'苏糖',age:22,gender:'female',hbd:'6月28日',skills:'烘焙 · 日语N2 · 长跑',personality:'活泼开朗 · 话痨分享型',mbti:'ENFP-A',values:'家庭归属型 · 成长学习型',interests:['烘焙','日剧','长跑','宠物','桌游','星座'],bio:'嗨！我是苏糖～朋友们说我是行走的小太阳。在一家烘焙工作室做甜品师，最拿手的是提拉米苏。O型血，ENFP人格，遇到开心的事会忍不住分享给全世界。养了一只叫布丁的柯基。希望能遇到一个愿意陪我疯、也能陪我安静看日落的人。'},
    {name:'沈岸',age:29,gender:'male',hbd:'11月20日',skills:'烹饪 · 木工 · 潜水执照',personality:'成熟稳重 · 温暖细腻',mbti:'ISFJ-T',values:'家庭归属型 · 稳定安全型',interests:['烹饪','木工','潜水','旅行','古典音乐','园艺'],bio:'你好，我是沈岸。在一家设计工作室做产品经理，同时也是个业余木匠。A型血，ISFJ人格，喜欢把粗糙的木头变成有温度的物件。每年会去一个没去过的地方潜水，海底的世界让人忘记一切烦恼。希望能遇到一个愿意一起慢慢生活的人。'},
    {name:'姜莱',age:25,gender:'female',hbd:'9月17日',skills:'服装设计 · 法语 · 瑜伽教练',personality:'独立强势 · 感性温暖',mbti:'ENTJ-A',values:'自由探索型 · 事业成就型',interests:['时尚设计','法语','瑜伽','看展','爵士乐','精酿啤酒'],bio:'Bonjour！我是姜莱，一个在创业的服装设计师。从小就想做自己的品牌，现在正在这条路上狂奔。A型血，ENTJ人格，做事雷厉风行但内心其实很柔软。周末喜欢去美术馆看新展，或者去精酿酒吧尝尝新口味。希望遇到一个不会被我的日程表吓跑、也懂欣赏生活美感的人。'},
    {name:'陆川',age:26,gender:'male',hbd:'2月14日',skills:'吉他弹唱 · 写作 · 攀岩',personality:'幽默风趣 · 文艺清新',mbti:'ENFP-A',values:'成长学习型 · 自由探索型',interests:['吉他','写作','户外运动','脱口秀','诗歌','公路旅行'],bio:'你好，我叫陆川，在广告公司做文案。B型血，ENFP人格，属于那种想到什么就会立刻去做的人。周末经常开着车去不知名的小镇瞎逛，车里永远放着吉他——虽然弹得一般，但每次在篝火旁弹给朋友听的时候都很开心。希望遇到一个不嫌弃我偶尔太跳脱、也愿意一起在路上的人。'},
    {name:'温晴',age:23,gender:'female',hbd:'12月1日',skills:'花艺设计 · 心理咨询师 · 钢琴',personality:'内向安静 · 善良细腻',mbti:'ISFP-T',values:'稳定安全型 · 家庭归属型',interests:['花艺','心理学','钢琴','养猫','诗集','雨天散步'],bio:'你好，我是温晴。在一家心理咨询中心工作，同时也是个花艺爱好者。O型血，ISFP人格，话不多但心里什么都知道。我的阳台上种满了花，还养了两只流浪猫。周末最喜欢下雨天——窝在沙发里看书、弹钢琴、听雨声。希望遇到一个能静静待在一起也很舒服的人。'},
    {name:'江屿',age:28,gender:'male',hbd:'5月8日',skills:'全栈开发 · 调酒 · 冲浪',personality:'外向活跃 · 冒险精神',mbti:'ESTP-A',values:'自由探索型 · 事业成就型',interests:['编程','调酒','冲浪','摩托车','科幻','露营'],bio:'Hey！我是江屿，一个爱冲浪的程序员。AB型血，ESTP人格，周末不是在海上就是在去海边的路上。在科技公司写代码是工作，在酒吧调酒是爱好——我调的长岛冰茶朋友们说能拿出手。骑摩托车环过台湾岛，下一个目标是骑去西藏。希望遇到一个不害怕冒险、也享受当下的人。'}
];
var _lastPersonaIndex = -1;

function buildAiProfile() {
    var idx;
    do { idx = Math.floor(Math.random() * PERSONA_DB.length); }
    while (idx === _lastPersonaIndex && PERSONA_DB.length > 1);
    _lastPersonaIndex = idx;
    var p = PERSONA_DB[idx];
    var profile = {name:p.name,age:p.age,hbd:p.hbd,gender:p.gender,skills:p.skills,personality:p.personality,mbti:p.mbti,values:p.values,interests:p.interests.slice(),bio:p.bio};
    localStorage.setItem('social_my_persona', JSON.stringify(profile));
    return profile;
}'''

content = content[:idx_start] + persona_db + '\n' + content[idx_end:]

# 7. 替换 applyProfile 中的 AI 生成填充逻辑
old_apply = '''if (!document.getElementById('bioText').innerText.trim() || document.getElementById('bioText').innerText === document.getElementById('bioText').getAttribute('placeholder')) document.getElementById('bioText').innerText = p.bio;
        if (!document.getElementById('infoAge').value) document.getElementById('infoAge').value = p.age;
        if (!document.getElementById('infoHBD').value) document.getElementById('infoHBD').value = p.hbd;
        if (!document.getElementById('infoSkills').value) document.getElementById('infoSkills').value = p.skills;
        if (!document.getElementById('infoPersonality').value) document.getElementById('infoPersonality').value = p.personality;
        if (!document.getElementById('infoMBTI').value) document.getElementById('infoMBTI').value = p.mbti;
        if (!document.getElementById('infoValues').value) document.getElementById('infoValues').value = p.values;
        if (interestsList.length === 0) { interestsList = p.interests; renderInterests(); }'''

new_apply = '''// 人设档案库全量填充
        document.getElementById('infoName').value = p.name;
        document.getElementById('bioText').innerText = p.bio;
        document.getElementById('infoAge').value = p.age;
        document.getElementById('infoHBD').value = p.hbd;
        document.getElementById('infoSkills').value = p.skills;
        document.getElementById('infoPersonality').value = p.personality;
        document.getElementById('infoMBTI').value = p.mbti;
        document.getElementById('infoValues').value = p.values;
        interestsList = p.interests; renderInterests();'''

content = content.replace(old_apply, new_apply)

# 8. 添加 goToMatch 函数
old_console = "console.log('🤖 AI分身工坊 · 星露谷像素风 · BigFive+依恋测评 · 智能回填不覆盖');"
new_console = '''// ========== 跳转匹配大厅 ==========
function goToMatch() {
    autoSave();
    var persona = {
        name: document.getElementById('infoName').value || '未命名',
        age: document.getElementById('infoAge').value || '',
        hbd: document.getElementById('infoHBD').value || '',
        skills: document.getElementById('infoSkills').value || '',
        personality: document.getElementById('infoPersonality').value || '',
        mbti: document.getElementById('infoMBTI').value || '',
        values: document.getElementById('infoValues').value || '',
        interests: interestsList,
        bio: document.getElementById('bioText').innerText || '',
        avatarDataUrl: avatarDataUrl || null,
        pixelMode: pixelMode || false,
    };
    localStorage.setItem('social_my_persona', JSON.stringify(persona));
    window.location.href = 'match.html';
}

console.log('🤖 AI分身工坊 · 8人设档案库 · 星露谷像素风 · BigFive+依恋测评');'''

content = content.replace(old_console, new_console)

with open('workshop.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK')
