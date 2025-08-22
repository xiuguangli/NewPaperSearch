import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd(), '')
  const isDev = mode === 'development'

  return {
    plugins: [vue()],
    base: '/', // 统一使用根路径
    server: {
      port: parseInt(env.VITE_DEV_PORT) || 5173,
      fs: {
        // 允许访问上层目录
        allow: ['..']
      },
      // 添加API代理配置
      proxy: {
        '/api': {
          target: env.VITE_API_PROXY_TARGET || 'http://127.0.0.1:5000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '/api')
        }
      }
    },
    define: {
      // 确保 Vue Devtools 在开发环境中可用
      __VUE_PROD_DEVTOOLS__: isDev
    }
  }
})
