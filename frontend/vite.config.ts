import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vue/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'
import { VitePWA } from 'vite-plugin-pwa' // 👈 1. PWA 플러그인 임포트 추가

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
    VitePWA({ // 👈 2. PWA 세부 설정 추가
      registerType: 'autoUpdate',
      manifest: {
        name: 'JanJan (잔잔)',
        short_name: 'JanJan',
        description: 'Django & Vue 기반 JanJan 서비스',
        theme_color: '#ffffff',
        background_color: '#ffffff',
        display: 'standalone',
        start_url: '/',
        icons: [
          {
            src: 'app-logo.png', // public 폴더에 복사해둔 로고 파일명
            sizes: '192x192',
            type: 'image/png'
          },
          {
            src: 'app-logo.png',
            sizes: '512x512',
            type: 'image/png'
          }
        ]
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
})