// config.js - 项目配置文件

// CDN基础路径配置
const CDN_BASE_URL = 'https://cdn.jsdelivr.net/gh/halfmadnya/ST-GalGame@main/';

// 判断是否从CDN加载
const isLocalFile = window.location.protocol === 'file:';
const BASE_URL = isLocalFile ? CDN_BASE_URL : './';

// 导出配置
window.GameConfig = {
    BASE_URL: BASE_URL,
    CDN_BASE_URL: CDN_BASE_URL,
    isLocalFile: isLocalFile,
    
    // 获取资源路径
    getPath: function(relativePath) {
        return BASE_URL + relativePath;
    },
    
    // 获取模块路径
    getModulePath: function(modulePath) {
        return BASE_URL + modulePath;
    },
    
    // 获取配置文件路径
    getConfigPath: function(configPath) {
        return BASE_URL + configPath;
    },
    
    // 获取样式路径
    getStylePath: function(stylePath) {
        return BASE_URL + stylePath;
    }
};

console.log('[Config] Base URL:', BASE_URL);
console.log('[Config] Is Local File:', isLocalFile);