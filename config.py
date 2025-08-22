#!/usr/bin/env python3
"""
配置管理工具
用于在整个项目中统一管理环境变量配置
"""

import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """统一配置管理类"""
    
    # -----------------------------------------------------------------------------
    # Flask 应用配置
    # -----------------------------------------------------------------------------
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    
    # -----------------------------------------------------------------------------
    # 前端配置
    # -----------------------------------------------------------------------------
    VITE_DEV_PORT = int(os.getenv('VITE_DEV_PORT', 5173))
    VITE_API_PROXY_TARGET = os.getenv('VITE_API_PROXY_TARGET', 'http://localhost:5000')
    
    # -----------------------------------------------------------------------------
    # MongoDB 数据库配置
    # -----------------------------------------------------------------------------
    MONGO_HOST = os.getenv('MONGO_HOST', 'localhost')
    MONGO_PORT = int(os.getenv('MONGO_PORT', 27017))
    MONGO_USER = os.getenv('MONGO_USER', 'lxg')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '@Zero1008')
    MONGO_DATABASE = os.getenv('MONGO_DATABASE', 'papersearch')
    
    # MongoDB URI (如果设置了会优先使用)
    MONGO_URI = os.getenv('MONGO_URI')
    
    # -----------------------------------------------------------------------------
    # 日志配置
    # -----------------------------------------------------------------------------
    LOG_DIR = os.getenv('LOG_DIR', 'logs')
    LOG_RETENTION_DAYS = os.getenv('LOG_RETENTION_DAYS', '30 days')
    LOG_MAX_SIZE = os.getenv('LOG_MAX_SIZE', '100 MB')
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # -----------------------------------------------------------------------------
    # API 服务配置
    # -----------------------------------------------------------------------------
    API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:5000')
    API_VERSION = os.getenv('API_VERSION', 'v1')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',')
    
    # -----------------------------------------------------------------------------
    # 外部 API 配置
    # -----------------------------------------------------------------------------
    GEMINI_API_KEYS = os.getenv('GEMINI_API_KEYS', '').split(',') if os.getenv('GEMINI_API_KEYS') else []
    GEMINI_PROMPT_DEFAULT = os.getenv('GEMINI_PROMPT_DEFAULT', '用中文讲一下这篇文章的内容，并举一个例子说明问题和方法流程。')
    GEMINI_PROMPT_DETAILED = os.getenv('GEMINI_PROMPT_DETAILED', '')
    
    # -----------------------------------------------------------------------------
    # 生产环境配置
    # -----------------------------------------------------------------------------
    PRODUCTION_HOST = os.getenv('PRODUCTION_HOST', '')
    PRODUCTION_PORT = int(os.getenv('PRODUCTION_PORT', 80))
    PRODUCTION_MONGO_HOST = os.getenv('PRODUCTION_MONGO_HOST', '')
    PRODUCTION_MONGO_PORT = int(os.getenv('PRODUCTION_MONGO_PORT', 27017))
    PRODUCTION_MONGO_USER = os.getenv('PRODUCTION_MONGO_USER', '')
    PRODUCTION_MONGO_PASSWORD = os.getenv('PRODUCTION_MONGO_PASSWORD', '')
    PRODUCTION_MONGO_DATABASE = os.getenv('PRODUCTION_MONGO_DATABASE', 'papersearch')
    
    # -----------------------------------------------------------------------------
    # 开发配置开关
    # -----------------------------------------------------------------------------
    DEV_MODE = os.getenv('DEV_MODE', 'true').lower() == 'true'
    SHOW_ERROR_DETAILS = os.getenv('SHOW_ERROR_DETAILS', 'true').lower() == 'true'
    ENABLE_API_LOGGING = os.getenv('ENABLE_API_LOGGING', 'true').lower() == 'true'
    
    @classmethod
    def get_mongo_connection_string(cls):
        """获取MongoDB连接字符串"""
        if cls.MONGO_URI:
            return cls.MONGO_URI
        
        if cls.MONGO_USER and cls.MONGO_PASSWORD:
            return f"mongodb://{cls.MONGO_USER}:{cls.MONGO_PASSWORD}@{cls.MONGO_HOST}:{cls.MONGO_PORT}/{cls.MONGO_DATABASE}"
        else:
            return f"mongodb://{cls.MONGO_HOST}:{cls.MONGO_PORT}/{cls.MONGO_DATABASE}"
    
    @classmethod
    def print_config(cls):
        """打印当前配置（隐藏敏感信息）"""
        print("=== PaperSearch 配置信息 ===")
        print(f"Flask服务: {cls.FLASK_HOST}:{cls.FLASK_PORT} (调试模式: {cls.FLASK_DEBUG})")
        print(f"Vite开发服务: localhost:{cls.VITE_DEV_PORT}")
        print(f"MongoDB: {cls.MONGO_HOST}:{cls.MONGO_PORT}/{cls.MONGO_DATABASE}")
        print(f"日志级别: {cls.LOG_LEVEL}")
        print(f"日志目录: {cls.LOG_DIR}")
        print(f"CORS来源: {', '.join(cls.CORS_ORIGINS)}")
        print(f"Gemini API密钥数量: {len(cls.GEMINI_API_KEYS)}")
        print(f"开发模式: {cls.DEV_MODE}")
        print("=" * 30)

def main():
    """主函数：打印配置信息"""
    Config.print_config()

if __name__ == '__main__':
    main()
