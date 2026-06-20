<template>
  <div class="app-layout">
    <header class="app-header">
      <div class="header-content">
        <div class="logo">
          <span class="logo-icon">🐟</span>
          <h1>鱼塘水质监控系统</h1>
        </div>
        <nav class="nav-menu">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="nav-item"
            :class="{ active: $route.path === item.path }"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span class="nav-text">{{ item.name }}</span>
            <span v-if="item.badge && alertStore.unreadCount > 0" class="nav-badge">
              {{ alertStore.unreadCount }}
            </span>
          </router-link>
        </nav>
        <div class="header-right">
          <button
            class="ws-status"
            :class="wsStatusClass"
            @click="handleWsClick"
            :title="wsTitle"
          >
            <span class="ws-dot"></span>
            <span class="ws-text">{{ wsStatusText }}</span>
          </button>
          <button
            class="sound-toggle"
            :class="{ active: alertStore.soundEnabled }"
            @click="alertStore.toggleSound()"
            :title="alertStore.soundEnabled ? '告警声音已开启' : '告警声音已关闭'"
          >
            {{ alertStore.soundEnabled ? '🔔' : '🔕' }}
          </button>
        </div>
      </div>
    </header>
    <main class="app-main">
      <router-view />
    </main>
    <AlertToast />
  </div>
</template>

<script setup>
import { reactive, computed, onMounted, onBeforeUnmount } from 'vue'
import { useAlertStore } from '@/stores/alert'
import AlertToast from '@/components/AlertToast.vue'

const alertStore = useAlertStore()

const menuItems = reactive([
  { path: '/monitoring', name: '实时监测', icon: '📊', badge: false },
  { path: '/thresholds', name: '阈值设置', icon: '⚙️', badge: false }
])

const wsStatusClass = computed(() => {
  const s = alertStore.connectionStatus
  if (s === 'OPEN') return 'connected'
  if (s.startsWith('RECONNECTING')) return 'reconnecting'
  return 'disconnected'
})

const wsStatusText = computed(() => {
  const s = alertStore.connectionStatus
  if (s === 'OPEN') return '实时连接'
  if (s.startsWith('RECONNECTING')) return `重连中 ${s.match(/\d+/)?.[0] || ''}`
  if (s === 'CONNECTING') return '连接中'
  return '已断开'
})

const wsTitle = computed(() => {
  if (alertStore.connectionStatus === 'OPEN') {
    return 'WebSocket 已连接,后端会主动推送告警'
  }
  return 'WebSocket 未连接,点击尝试重新连接'
})

const handleWsClick = () => {
  if (alertStore.connectionStatus !== 'OPEN') {
    alertStore.initSocket()
  }
}

onMounted(() => {
  alertStore.initSocket()
})

onBeforeUnmount(() => {
  alertStore.destroySocket()
})
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #006d77 0%, #83c5be 100%);
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.logo-icon {
  font-size: 32px;
}

.logo h1 {
  color: white;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 1px;
}

.nav-menu {
  display: flex;
  gap: 8px;
  flex: 1;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 8px;
  color: rgba(255, 255, 255, 0.85);
  transition: all 0.3s;
  font-size: 15px;
  font-weight: 500;
  position: relative;
}

.nav-item:hover {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-item.active {
  background: white;
  color: #006d77;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.nav-icon {
  font-size: 18px;
}

.nav-badge {
  position: absolute;
  top: -2px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  background: #ff4d4f;
  color: white;
  border-radius: 9px;
  font-size: 11px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #006d77;
  animation: badgePulse 1.5s infinite;
}

@keyframes badgePulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.15); }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

.ws-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.ws-status:hover {
  background: rgba(255, 255, 255, 0.2);
}

.ws-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #999;
}

.ws-status.connected .ws-dot {
  background: #52c41a;
  box-shadow: 0 0 8px #52c41a;
  animation: dotBlink 2s infinite;
}

.ws-status.reconnecting .ws-dot {
  background: #faad14;
  animation: dotBlink 0.6s infinite;
}

.ws-status.disconnected .ws-dot {
  background: #ff4d4f;
}

@keyframes dotBlink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.sound-toggle {
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 20px;
  width: 36px;
  height: 36px;
  font-size: 18px;
  cursor: pointer;
  transition: all 0.3s;
}

.sound-toggle.active {
  background: rgba(255, 255, 255, 0.25);
}

.sound-toggle:hover {
  background: rgba(255, 255, 255, 0.3);
}

.app-main {
  flex: 1;
  padding: 24px;
}

@media (max-width: 768px) {
  .header-content {
    flex-wrap: wrap;
    height: auto;
    padding: 12px 16px;
    gap: 12px;
  }

  .logo h1 {
    font-size: 16px;
  }

  .nav-menu {
    order: 3;
    width: 100%;
    justify-content: flex-start;
  }

  .nav-item {
    padding: 8px 14px;
    font-size: 13px;
  }

  .header-right {
    margin-left: auto;
  }

  .ws-text {
    display: none;
  }
}
</style>
