/**
 * API配置文件
 * 包含API基础URL和AI问答功能所需的API参数
 */

// API基础URL配置
export const apiConfig = {
  // 后端API基础URL
  baseURL: 'http://127.0.0.1:8000',
}

export const aiChatConfig = {
  // 阿里云 DashScope 兼容模式 API 地址
  apiEndpoint: 'https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions',

  // Vite 仅会将 VITE_ 前缀的变量暴露给前端
  apiKey: import.meta.env.VITE_AI_API_KEY || '',

  // 使用的模型（qwen3-max-preview 已弃用，改用 qwen-plus）
  model: 'qwen-plus'
}
