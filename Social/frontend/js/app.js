/**
 * Social - 数字人生成模块 前端逻辑
 *
 * Step 1: 导入聊天记录（4 种方式）
 *   - 微信一键导入
 *   - 上传文件（txt/json/csv/html）
 *   - 粘贴文本
 *   - 上传照片（辅助）
 * Step 2: 基础信息问卷
 * Step 3: AI 个性化追问 + 深度探索
 * Step 4: 生成完整数字人档案
 */

const API_BASE = '/api/persona';

// ========== 全局状态 ==========
const state = {
    personaId: null,
    currentStep: 1,
    persona: null,
    answers: {},
};

// ========== 初始化 ==========
document.addEventListener('DOMContentLoaded', () => {
    renderStep(1);
});

// ========== 渲染步骤 ==========
async function renderStep(step) {
    state.currentStep = step;
    updateProgress(step);

    const content = document.getElementById('stepContent');

    switch (step) {
        case 1: content.innerHTML = renderStep1(); bindStep1Events(); break;
        case 2: content.innerHTML = renderStep2(); await loadQuestionnaire(2); bindStep23Events(2); break;
        case 3: content.innerHTML = renderStep3(); await loadQuestionnaire(3); bindStep23Events(3); break;
        case 4: renderStep4(); break;
    }
}

// ================================================================
// Step 1: 聊天记录导入（四种方式）
// ================================================================

function renderStep1() {
    return `
    <div class="bg-white rounded-2xl shadow-sm p-6 md:p-8 card-hover">
        <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-full bg-indigo-100 flex items-center justify-center text-xl">📝</div>
            <div>
                <h2 class="text-lg font-bold text-gray-800">导入聊天记录</h2>
                <p class="text-sm text-gray-500">让我从你的聊天方式中认识你</p>
            </div>
        </div>

        <!-- 方式一：微信一键导入（推荐） -->
        <div class="mb-4 p-4 bg-gradient-to-r from-green-50 to-emerald-50 border border-green-200 rounded-xl">
            <div class="flex items-start gap-3">
                <div class="text-2xl flex-shrink-0">💚</div>
                <div class="flex-1">
                    <h3 class="font-bold text-green-800 mb-1">方式一：一键导入微信聊天记录（推荐）</h3>
                    <p class="text-sm text-green-700 mb-3">自动读取你电脑上的微信聊天数据，无需手动导出</p>
                    <div id="wechatStatus" class="text-xs text-green-600 mb-2">
                        <span class="loading-spinner inline-block mr-1" style="width:14px;height:14px;border-width:2px;"></span> 检测微信状态中...
                    </div>
                    <button id="wechatImportBtn"
                        class="px-5 py-2.5 bg-green-500 text-white font-semibold rounded-xl hover:bg-green-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                        disabled>
                        <i class="fa fa-wechat mr-1"></i> 一键导入微信聊天
                    </button>
                </div>
            </div>
        </div>

        <div class="flex items-center gap-3 my-5">
            <div class="flex-1 h-px bg-gray-200"></div>
            <span class="text-sm text-gray-400">或者</span>
            <div class="flex-1 h-px bg-gray-200"></div>
        </div>

        <!-- 方式二：上传文件 -->
        <div class="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-xl">
            <div class="flex items-start gap-3">
                <div class="text-2xl flex-shrink-0">📁</div>
                <div class="flex-1">
                    <h3 class="font-bold text-blue-800 mb-1">方式二：上传聊天记录文件</h3>
                    <p class="text-sm text-blue-700 mb-3">支持微信/QQ 导出的 txt、json、csv、html 文件</p>
                    <div class="flex items-center gap-2">
                        <label class="px-5 py-2.5 bg-blue-500 text-white font-semibold rounded-xl hover:bg-blue-600 transition cursor-pointer">
                            <i class="fa fa-upload mr-1"></i> 选择文件
                            <input type="file" id="chatFileUpload" accept=".txt,.json,.csv,.html,.htm,.log" class="hidden">
                        </label>
                        <span id="uploadFileName" class="text-sm text-gray-500">未选择文件</span>
                    </div>
                    <button id="uploadFileBtn" class="hidden mt-3 px-5 py-2.5 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition">
                        <i class="fa fa-magic mr-1"></i> 分析这个文件
                    </button>
                </div>
            </div>
        </div>

        <!-- 方式三：粘贴文本 -->
        <div class="mb-4 p-4 bg-amber-50 border border-amber-200 rounded-xl">
            <div class="flex items-start gap-3">
                <div class="text-2xl flex-shrink-0">📋</div>
                <div class="flex-1">
                    <h3 class="font-bold text-amber-800 mb-1">方式三：直接粘贴聊天记录</h3>
                    <p class="text-sm text-amber-700 mb-2">把聊天记录复制粘贴到下面</p>
                    <textarea id="chatText" rows="8"
                        class="w-full border border-amber-200 rounded-xl p-3 text-sm resize-y focus:ring-2 focus:ring-amber-500 focus:border-transparent"
                        placeholder="粘贴你的聊天记录...格式示例：张三: 今天天气真好  李四: 是啊！..."></textarea>
                    <button id="analyzeTextBtn" class="mt-2 px-5 py-2.5 bg-amber-500 text-white font-semibold rounded-xl hover:bg-amber-600 transition">
                        <i class="fa fa-magic mr-1"></i> 分析文字内容
                    </button>
                </div>
            </div>
        </div>

        <!-- 方式四：照片（辅助） -->
        <div class="p-4 bg-pink-50 border border-pink-200 rounded-xl">
            <div class="flex items-start gap-3">
                <div class="text-2xl flex-shrink-0">📸</div>
                <div class="flex-1">
                    <h3 class="font-bold text-pink-800 mb-1">辅助：上传照片分析风格偏好</h3>
                    <p class="text-sm text-pink-700 mb-2">AI 从你的照片中推断视觉风格和生活偏好</p>
                    <div class="flex items-center gap-2">
                        <label class="px-5 py-2.5 bg-pink-500 text-white font-semibold rounded-xl hover:bg-pink-600 transition cursor-pointer">
                            <i class="fa fa-photo mr-1"></i> 上传照片
                            <input type="file" id="photoUpload" accept=".jpg,.jpeg,.png,.gif,.webp,.bmp" class="hidden">
                        </label>
                        <span id="photoFileName" class="text-sm text-gray-500">未选择照片</span>
                    </div>
                    <div id="photoResult" class="hidden mt-3"></div>
                </div>
            </div>
        </div>

        <div id="analysisResult" class="hidden mt-6"></div>
    </div>
    `;
}

function bindStep1Events() {
    checkWechatStatus();

    // 微信一键导入
    const wechatBtn = document.getElementById('wechatImportBtn');
    if (wechatBtn) wechatBtn.addEventListener('click', wechatAutoImport);

    // 文件上传
    const fileInput = document.getElementById('chatFileUpload');
    if (fileInput) {
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            document.getElementById('uploadFileName').textContent = file.name;
            const uploadBtn = document.getElementById('uploadFileBtn');
            uploadBtn.classList.remove('hidden');
            uploadBtn.onclick = () => uploadChatFile(file);
        });
    }

    // 文本分析
    const analyzeTextBtn = document.getElementById('analyzeTextBtn');
    if (analyzeTextBtn) analyzeTextBtn.addEventListener('click', analyzeChatText);

    // 照片上传
    const photoInput = document.getElementById('photoUpload');
    if (photoInput) {
        photoInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (!file) return;
            document.getElementById('photoFileName').textContent = file.name;
            uploadAndAnalyzePhoto(file);
        });
    }
}

// ========== 微信相关 ==========

async function checkWechatStatus() {
    try {
        const res = await fetch('/api/wechat/status');
        const data = await res.json();
        const statusDiv = document.getElementById('wechatStatus');
        const importBtn = document.getElementById('wechatImportBtn');

        if (data.can_auto_import) {
            statusDiv.innerHTML = '<span style="color:#16a34a;font-weight:bold;">✅ ' + data.message + '</span>';
            importBtn.disabled = false;
            importBtn.innerHTML = '<i class="fa fa-wechat mr-1"></i> 一键导入微信聊天';
        } else {
            statusDiv.innerHTML = '<span style="color:#d97706;">⚠️ ' + data.message + '</span>';
            if (data.help) statusDiv.innerHTML += '<br><span style="color:#6b7280;">' + data.help + '</span>';
            importBtn.disabled = false;
            importBtn.innerHTML = '<i class="fa fa-wechat mr-1"></i> 尝试导入（请先打开微信桌面版）';
        }
    } catch (err) {
        document.getElementById('wechatStatus').innerHTML =
            '<span style="color:#6b7280;">微信状态检测暂不可用，可尝试其他导入方式</span>';
    }
}

async function wechatAutoImport() {
    showLoading('正在从微信读取聊天记录...这可能需要 10-30 秒');

    try {
        const formData = new FormData();
        formData.append('max_messages', '3000');

        const res = await fetch('/api/wechat/auto-import', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.success) {
            state.persona = data.persona;
            state.personaId = data.persona.id;
            showAnalysisResult(true, data.message);
        } else {
            showAnalysisResult(false, data.detail || '导入失败');
        }
    } catch (err) {
        showAnalysisResult(false, '请求失败：' + err.message + '。请确保已打开微信桌面版（不是小程序）');
    } finally {
        hideLoading();
    }
}

// ========== 文件上传分析 ==========

async function uploadChatFile(file) {
    showLoading('正在解析文件...');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(API_BASE + '/upload-file', { method: 'POST', body: formData });
        const data = await res.json();

        if (data.success) {
            state.persona = data.persona;
            state.personaId = data.persona.id;
            showAnalysisResult(true, data.message);
        } else {
            showAnalysisResult(false, data.detail || '导入失败');
        }
    } catch (err) {
        showAnalysisResult(false, '请求失败：' + err.message);
    } finally {
        hideLoading();
    }
}

// ========== 文本分析 ==========

async function analyzeChatText() {
    const chatText = document.getElementById('chatText').value.trim();
    if (!chatText) { alert('请先粘贴聊天记录'); return; }

    showLoading('AI 正在分析你的聊天记录...这可能需要 10-30 秒');

    try {
        const res = await fetch(API_BASE + '/analyze-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chat_text: chatText, chat_format: 'auto' }),
        });
        const data = await res.json();

        if (data.success) {
            state.persona = data.persona;
            state.personaId = data.persona.id;
            showAnalysisResult(true, data.message);
        } else {
            showAnalysisResult(false, data.message || '分析失败');
        }
    } catch (err) {
        showAnalysisResult(false, '请求失败：' + err.message);
    } finally {
        hideLoading();
    }
}

// ========== 照片分析 ==========

async function uploadAndAnalyzePhoto(file) {
    showLoading('AI 正在分析你的照片...');

    try {
        const formData = new FormData();
        formData.append('file', file);

        const res = await fetch(API_BASE + '/analyze-photo', { method: 'POST', body: formData });
        const data = await res.json();

        const resultDiv = document.getElementById('photoResult');
        resultDiv.classList.remove('hidden');

        if (data.success) {
            resultDiv.innerHTML = '<div style="background:#fce7f3;border:1px solid #f9a8d4;border-radius:12px;padding:12px;font-size:14px;color:#9d174d;">' +
                '<i class="fa fa-check-circle mr-1"></i> ' + data.message +
                '<br><span style="font-size:12px;color:#be185d;">' + (data.next_step || '') + '</span></div>';
        } else {
            resultDiv.innerHTML = '<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:12px;font-size:14px;color:#991b1b;">' +
                (data.detail || '分析失败') + '</div>';
        }
    } catch (err) {
        const resultDiv = document.getElementById('photoResult');
        resultDiv.classList.remove('hidden');
        resultDiv.innerHTML = '<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:12px;font-size:14px;color:#991b1b;">' +
            '分析失败：' + err.message + '<br><span style="font-size:12px;">（DeepSeek 可能不支持图片分析，请尝试上传聊天记录）</span></div>';
    } finally {
        hideLoading();
    }
}

function showAnalysisResult(success, message) {
    const resultDiv = document.getElementById('analysisResult');
    resultDiv.classList.remove('hidden');

    if (success) {
        resultDiv.innerHTML = '<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:12px;padding:16px;font-size:14px;color:#166534;">' +
            '<i class="fa fa-check-circle mr-1"></i> <strong>' + message + '</strong></div>' +
            '<button onclick="renderStep(2)" class="mt-4 w-full py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold rounded-xl hover:opacity-90 transition">' +
            '下一步：填写基础信息 <i class="fa fa-arrow-right ml-2"></i></button>';
    } else {
        resultDiv.innerHTML = '<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:16px;font-size:14px;color:#991b1b;">' +
            '<i class="fa fa-exclamation-circle mr-1"></i> ' + message + '</div>';
    }

    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// ================================================================
// Step 2/3: 问卷
// ================================================================

function renderStep2() {
    return `
    <div class="bg-white rounded-2xl shadow-sm p-6 md:p-8 card-hover">
        <div class="flex items-center gap-3 mb-6">
            <div class="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center text-xl">📋</div>
            <div>
                <h2 class="text-lg font-bold text-gray-800" id="stageTitle">基础信息</h2>
                <p class="text-sm text-gray-500" id="stageDesc">先简单了解一下你</p>
            </div>
        </div>
        <div id="questionsContainer" class="space-y-5">
            <div class="text-center text-gray-400 py-8">
                <div class="loading-spinner mx-auto mb-3"></div>正在准备问题...
            </div>
        </div>
        <button id="submitAnswersBtn" class="hidden w-full mt-6 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold rounded-xl hover:opacity-90 transition">
            提交并继续 <i class="fa fa-arrow-right ml-2"></i>
        </button>
    </div>`;
}

function renderStep3() { return renderStep2(); }

function bindStep23Events(stage) {
    const submitBtn = document.getElementById('submitAnswersBtn');
    if (submitBtn) submitBtn.addEventListener('click', () => submitAnswers(stage));
}

// ========== 问卷加载 ==========

async function loadQuestionnaire(stage) {
    const params = new URLSearchParams({ stage: stage });
    if (state.personaId) params.append('persona_id', state.personaId);

    try {
        const res = await fetch(API_BASE + '/questionnaire?' + params);
        const data = await res.json();

        const container = document.getElementById('questionsContainer');
        const titleEl = document.getElementById('stageTitle');
        const descEl = document.getElementById('stageDesc');
        const submitBtn = document.getElementById('submitAnswersBtn');

        if (titleEl) titleEl.textContent = data.stage_name || '问卷调查';
        if (descEl) descEl.textContent = data.greeting || '';

        container.innerHTML = (data.questions || []).map((q, i) => `
            <div class="border border-gray-100 rounded-xl p-4 hover:border-indigo-200 transition">
                <label class="block text-sm font-medium text-gray-700 mb-2">${i + 1}. ${q.question}</label>
                ${q.hint ? '<p class="text-xs text-gray-400 mb-2">' + q.hint + '</p>' : ''}
                ${q.type === 'choice' && q.options ? `
                    <div class="flex flex-wrap gap-2">
                        ${q.options.map(opt => `
                            <label class="flex items-center gap-2 cursor-pointer px-3 py-2 border border-gray-200 rounded-xl hover:border-indigo-300 transition">
                                <input type="radio" name="q_${q.id}" value="${opt}" class="text-indigo-600">
                                <span class="text-sm text-gray-600">${opt}</span>
                            </label>
                        `).join('')}
                    </div>
                ` : `
                    <input type="text" name="q_${q.id}"
                        class="w-full border border-gray-200 rounded-xl p-3 text-sm focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        placeholder="${q.hint || '输入你的回答...'}">
                `}
            </div>
        `).join('');

        if (submitBtn) submitBtn.classList.remove('hidden');
    } catch (err) {
        console.error('加载问卷失败:', err);
    }
}

// ========== 提交回答 ==========

async function submitAnswers(stage) {
    const answers = { _stage: String(stage), _persona_id: state.personaId || '' };
    const container = document.getElementById('questionsContainer');
    const inputs = container.querySelectorAll('input[type="text"], input[type="radio"]:checked');

    inputs.forEach(input => {
        const name = input.name.replace('q_', '');
        if (input.type === 'radio') answers[name] = input.value;
        else if (!answers[name]) answers[name] = input.value;
    });

    // 验证
    let hasEmpty = false;
    container.querySelectorAll('.border').forEach(div => {
        const textInput = div.querySelector('input[type="text"]');
        const radios = div.querySelectorAll('input[type="radio"]');
        const checkedRadio = div.querySelector('input[type="radio"]:checked');
        if (textInput && !textInput.value.trim()) { div.style.borderColor = '#fca5a5'; div.style.background = '#fef2f2'; hasEmpty = true; }
        else if (radios.length > 0 && !checkedRadio) { div.style.borderColor = '#fca5a5'; div.style.background = '#fef2f2'; hasEmpty = true; }
        else { div.style.borderColor = ''; div.style.background = ''; }
    });

    if (hasEmpty) { alert('请填写所有问题再提交哦～'); return; }

    showLoading('保存中...');

    try {
        const res = await fetch(API_BASE + '/submit-answers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ answers }),
        });
        const data = await res.json();

        if (data.success) {
            state.persona = data.persona;
            state.personaId = data.persona.id;
            Object.assign(state.answers, answers);

            if (data.next_step && data.next_step.includes('stage=')) {
                renderStep(parseInt(data.next_step.split('stage=')[1]));
            } else if (stage === 3) {
                await analyzePreferences();
                renderStep(4);
            } else {
                renderStep(stage + 1);
            }
        }
    } catch (err) {
        console.error('提交失败:', err);
    } finally {
        hideLoading();
    }
}

// ========== 偏好分析 ==========

async function analyzePreferences() {
    if (!state.persona) return;
    showLoading('分析匹配偏好中...');
    try {
        const res = await fetch(API_BASE + '/analyze-preferences', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_profile: state.persona.user_profile, match_preference: null }),
        });
        const data = await res.json();
        if (data.success) state.persona = data.persona;
    } catch (err) {
        console.error('偏好分析失败:', err);
    } finally {
        hideLoading();
    }
}

// ========== Step 4: 数字人档案展示 ==========

function renderStep4() {
    const persona = state.persona;
    if (!persona) {
        document.getElementById('stepContent').innerHTML = '<div class="bg-white rounded-2xl shadow-sm p-6 md:p-8 card-hover text-center"><div class="loading-spinner mx-auto mb-4"></div><p class="text-gray-500">正在生成你的数字人档案...</p></div>';
        generatePersona();
        return;
    }

    const p = persona.personality || {};
    const up = persona.user_profile || {};
    const mp = persona.match_preference || {};
    const bf = p.big_five || {};
    const cs = p.conversation_style || {};
    const ep = p.emotion_profile || {};
    const ss = p.social_strategy || {};
    const tp = p.topic_preferences || {};
    const v = p.values || {};

    const radarData = [
        { label: '开放性', value: bf.openness || 5 },
        { label: '尽责性', value: bf.conscientiousness || 5 },
        { label: '外向性', value: bf.extraversion || 5 },
        { label: '宜人性', value: bf.agreeableness || 5 },
        { label: '情绪稳定', value: 10 - (bf.neuroticism || 5) },
    ];

    document.getElementById('stepContent').innerHTML = `
    <div class="space-y-6 fade-in">
        <div class="bg-white rounded-2xl shadow-sm p-6 md:p-8 card-hover text-center">
            <div class="w-20 h-20 rounded-full bg-gradient-to-r from-indigo-500 to-purple-600 flex items-center justify-center text-white text-3xl mx-auto mb-3">${(up.nickname || '?')[0]}</div>
            <h2 class="text-2xl font-bold text-gray-800">${up.nickname || '未命名'}</h2>
            <p class="text-gray-500 text-sm mt-1">${p.summary || '独特的灵魂'}</p>
            <span class="inline-block mt-2 px-3 py-1 bg-green-50 text-green-700 text-xs font-semibold rounded-full">置信度 ${Math.round((p.confidence || 0) * 100)}%</span>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6 card-hover">
            <h3 class="font-bold text-gray-800 mb-4 flex items-center gap-2"><span class="text-lg">🧠</span> 大五人格特质</h3>
            <div class="space-y-3">
                ${radarData.map(d => '<div class="flex items-center gap-3"><span class="text-sm text-gray-600 w-20 text-right">' + d.label + '</span><div class="flex-1 bg-gray-100 rounded-full h-4 overflow-hidden"><div class="h-full rounded-full bg-gradient-to-r from-indigo-500 to-purple-600" style="width:' + (d.value * 10) + '%"></div></div><span class="text-sm font-bold text-gray-700 w-8">' + d.value + '</span></div>').join('')}
            </div>
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6 card-hover">
            <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2"><span class="text-lg">💬</span> 对话风格</h3>
            <div class="flex flex-wrap gap-2 mb-3">
                <span class="px-3 py-1 bg-indigo-50 text-indigo-700 rounded-full text-sm font-medium">${cs.primary_style || '未分析'}</span>
                ${(cs.secondary_styles || []).map(s => '<span class="px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-sm">' + s + '</span>').join('')}
            </div>
            <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="p-3 bg-gray-50 rounded-xl"><span class="text-gray-500">句子长度</span><span class="float-right font-medium text-gray-700">${cs.sentence_length || '-'}</span></div>
                <div class="p-3 bg-gray-50 rounded-xl"><span class="text-gray-500">表情使用</span><span class="float-right font-medium text-gray-700">${cs.emoji_usage || '-'}</span></div>
                <div class="p-3 bg-gray-50 rounded-xl"><span class="text-gray-500">提问频率</span><span class="float-right font-medium text-gray-700">${cs.question_frequency || '-'}</span></div>
                <div class="p-3 bg-gray-50 rounded-xl"><span class="text-gray-500">幽默类型</span><span class="float-right font-medium text-gray-700">${cs.humor_type || '-'}</span></div>
            </div>
            ${cs.description ? '<p class="mt-3 text-sm text-gray-500 italic">"' + cs.description + '"</p>' : ''}
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6 card-hover">
            <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2"><span class="text-lg">💗</span> 情绪画像</h3>
            <div class="flex items-center gap-4 mb-3">
                <span class="px-3 py-1 bg-pink-50 text-pink-700 rounded-full text-sm font-medium">${ep.baseline || '未分析'}</span>
                <span class="text-sm text-gray-500">情绪表达 ${ep.expressiveness || 0}/10</span>
            </div>
            ${ep.positive_triggers && ep.positive_triggers.length ? '<p class="text-sm text-gray-600 mb-1"><span class="text-green-600">+</span> 正面触发：' + ep.positive_triggers.join('、') + '</p>' : ''}
            ${ep.negative_triggers && ep.negative_triggers.length ? '<p class="text-sm text-gray-600"><span class="text-red-600">-</span> 负面触发：' + ep.negative_triggers.join('、') + '</p>' : ''}
        </div>

        <div class="bg-white rounded-2xl shadow-sm p-6 card-hover">
            <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2"><span class="text-lg">🤝</span> 社交策略</h3>
            <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="p-3 bg-gray-50 rounded-xl"><span class="text-gray-500">发起对话</span><span class="float-right font-medium text-gray-700">${ss.initiation || '-'}</span></div>
                <div class="p-3 bg-gray-50 rounded-xl"><span class="text-gray-500">自我暴露</span><span class="float-right font-medium text-gray-700">${ss.self_disclosure || '-'}</span></div>
                <div class="p-3 bg-gray-50 rounded-xl"><span class="text-gray-500">回应方式</span><span class="float-right font-medium text-gray-700">${ss.response_style || '-'}</span></div>
                <div class="p-3 bg-gray-50 rounded-xl"><span class="text-gray-500">冲突处理</span><span class="float-right font-medium text-gray-700">${ss.conflict_handling || '-'}</span></div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-white rounded-2xl shadow-sm p-6 card-hover">
                <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2"><span class="text-lg">🎯</span> 话题偏好</h3>
                <div class="flex flex-wrap gap-2">${(tp.top_interests || []).map(t => '<span class="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-sm">' + t + '</span>').join('')}${!tp.top_interests || !tp.top_interests.length ? '<span class="text-gray-400 text-sm">暂无数据</span>' : ''}</div>
            </div>
            <div class="bg-white rounded-2xl shadow-sm p-6 card-hover">
                <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2"><span class="text-lg">✨</span> 价值观</h3>
                <div class="flex flex-wrap gap-2">${(v.primary_values || []).map(val => '<span class="px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-sm">' + val + '</span>').join('')}${!v.primary_values || !v.primary_values.length ? '<span class="text-gray-400 text-sm">暂无数据</span>' : ''}</div>
            </div>
        </div>

        ${mp.preferred_personality && mp.preferred_personality.length ? `
        <div class="bg-white rounded-2xl shadow-sm p-6 card-hover">
            <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2"><span class="text-lg">💘</span> 匹配偏好 - 你的理想型</h3>
            <div class="space-y-2">
                <div class="flex flex-wrap gap-2"><span class="text-sm text-gray-500">性格：</span>${(mp.preferred_personality || []).map(t => '<span class="px-2 py-0.5 bg-pink-50 text-pink-700 rounded-full text-xs">' + t + '</span>').join('')}</div>
                <div class="flex flex-wrap gap-2"><span class="text-sm text-gray-500">沟通：</span>${(mp.preferred_style || []).map(s => '<span class="px-2 py-0.5 bg-purple-50 text-purple-700 rounded-full text-xs">' + s + '</span>').join('')}</div>
                ${mp.description ? '<p class="mt-3 text-sm text-gray-500 italic">"' + mp.description + '"</p>' : ''}
            </div>
        </div>` : ''}

        ${persona.persona_prompt ? `
        <div class="bg-white rounded-2xl shadow-sm p-6 card-hover">
            <h3 class="font-bold text-gray-800 mb-3 flex items-center gap-2"><span class="text-lg">🤖</span> 数字人 System Prompt</h3>
            <pre class="bg-gray-900 text-green-400 rounded-xl p-4 text-xs overflow-x-auto max-h-64">${escapeHtml(persona.persona_prompt)}</pre>
        </div>` : ''}

        <div class="flex gap-3">
            <button onclick="renderStep(1)" class="flex-1 py-3 border border-gray-200 text-gray-600 rounded-xl hover:bg-gray-50 transition"><i class="fa fa-refresh mr-2"></i>重新创建</button>
            <button onclick="copyPersonaPrompt()" class="flex-1 py-3 bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold rounded-xl hover:opacity-90 transition"><i class="fa fa-copy mr-2"></i>复制 System Prompt</button>
        </div>
    </div>`;
}

async function generatePersona() {
    if (!state.personaId) return;
    try {
        const res = await fetch(API_BASE + '/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ persona_id: state.personaId }),
        });
        const data = await res.json();
        if (data.success) { state.persona = data.persona; renderStep(4); }
    } catch (err) { console.error('生成失败:', err); }
}

// ========== 辅助函数 ==========

function updateProgress(step) {
    for (let i = 1; i <= 4; i++) {
        const dot = document.getElementById('step' + i + 'Dot');
        const line = document.getElementById('line' + i);
        if (!dot) continue;
        if (i < step) { dot.className = 'w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold step-done'; dot.innerHTML = '<i class="fa fa-check"></i>'; }
        else if (i === step) { dot.className = 'w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-bold step-active'; dot.innerHTML = i; }
        else { dot.className = 'w-8 h-8 rounded-full flex items-center justify-center text-gray-400 bg-gray-100 text-sm font-bold'; dot.innerHTML = i; }
        if (line) line.className = i < step ? 'w-12 h-0.5 bg-green-400' : 'w-12 h-0.5 bg-gray-200';
    }
}

function showLoading(text) { document.getElementById('loadingText').textContent = text || '处理中...'; document.getElementById('loadingOverlay').classList.remove('hidden'); }
function hideLoading() { document.getElementById('loadingOverlay').classList.add('hidden'); }
function escapeHtml(str) { const div = document.createElement('div'); div.textContent = str; return div.innerHTML; }
function copyPersonaPrompt() {
    if (state.persona && state.persona.persona_prompt) {
        navigator.clipboard.writeText(state.persona.persona_prompt).then(() => alert('✅ System Prompt 已复制到剪贴板'));
    }
}
