// index.js - GalGame启动文件
import GameCore from './core/GameCore.js';

(async () => {
    try {
        console.log('[GalGame] 💕 恋爱模拟器启动中...');
        
        // 检查callGenerate函数是否可用
        if (typeof window.callGenerate !== 'function') {
            console.warn('[GalGame] callGenerate函数不可用，某些功能可能受限');
        }
        
        // 创建并初始化游戏核心
        const gameCore = new GameCore();
        await gameCore.initialize();
        
        // 暴露到全局供调试使用
        window.gameCore = gameCore;
        
        console.log('[GalGame] ✅ 游戏准备就绪！');
        console.log('[GalGame] 💕 开始你的恋爱之旅吧！');
        
    } catch (error) {
        console.error('[GalGame] ❌ 游戏启动失败:', error);
        
        // 显示错误信息
        const errorContainer = document.getElementById('error-container');
        const errorMessage = document.getElementById('error-message');
        const loadingScreen = document.getElementById('loading-screen');
        
        if (errorContainer && errorMessage && loadingScreen) {
            loadingScreen.classList.add('hidden');
            errorMessage.textContent = `启动失败: ${error.message}`;
            errorContainer.classList.remove('hidden');
        }
    }
})();