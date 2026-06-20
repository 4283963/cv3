<template>
  <div class="alert-toast-container">
    <transition-group name="toast" tag="div" class="toast-list">
      <div
        v-for="popup in alertStore.popups"
        :key="popup.popupId"
        class="alert-toast"
        :class="{ 'is-new': isNew(popup) }"
        @mouseenter="pauseAutoClose(popup)"
        @mouseleave="resumeAutoClose(popup)"
      >
        <div class="toast-accent"></div>

        <div class="toast-header">
          <div class="toast-icon-wrap">
            <span class="toast-icon">🚨</span>
            <span class="pulse-ring"></span>
          </div>
          <div class="toast-titles">
            <div class="toast-title">水质告警</div>
            <div class="toast-subtitle">
              <span class="pond-name">🐟 {{ popup.pond_name }}</span>
              <span class="toast-time">{{ formatTime(popup.timestamp) }}</span>
            </div>
          </div>
          <button class="toast-close" @click="alertStore.dismissPopup(popup.popupId)">×</button>
        </div>

        <div class="toast-body">
          <div
            v-for="(item, idx) in popup.abnormals"
            :key="idx"
            class="abnormal-item"
            :class="item.status"
          >
            <div class="abnormal-left">
              <span class="abnormal-arrow">{{ item.status === 'high' ? '↑' : '↓' }}</span>
              <span class="abnormal-name">{{ item.metric_name }}</span>
              <span class="abnormal-status">{{ item.status === 'high' ? '偏高' : '偏低' }}</span>
            </div>
            <div class="abnormal-right">
              <div class="abnormal-value">
                <span class="current-value">{{ Number(item.value).toFixed(2) }}</span>
                <span class="current-unit">{{ item.unit }}</span>
              </div>
              <div class="abnormal-safe">
                安全: {{ item.safe_min }} ~ {{ item.safe_max }} {{ item.unit }}
              </div>
            </div>
          </div>
        </div>

        <div class="toast-progress">
          <div class="toast-progress-bar" :style="{ width: progressWidth(popup) + '%' }"></div>
        </div>
      </div>
    </transition-group>

    <div v-if="alertStore.popups.length > 1" class="toast-actions">
      <button class="action-btn dismiss-all" @click="alertStore.dismissAll()">
        全部关闭 ({{ alertStore.popups.length }})
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useAlertStore } from '@/stores/alert'

const alertStore = useAlertStore()
const tick = ref(0)
let progressTimer = null
const AUTO_CLOSE_MS = 12000

const formatTime = (isoString) => {
  if (!isoString) return '--'
  const d = new Date(isoString)
  const h = String(d.getHours()).padStart(2, '0')
  const m = String(d.getMinutes()).padStart(2, '0')
  const s = String(d.getSeconds()).padStart(2, '0')
  return `${h}:${m}:${s}`
}

const isNew = (popup) => {
  return Date.now() - popup.createdAt < 1000
}

const progressWidth = (popup) => {
  const elapsed = Date.now() - popup.createdAt
  const remaining = Math.max(0, AUTO_CLOSE_MS - elapsed)
  return (remaining / AUTO_CLOSE_MS) * 100
}

const pauseAutoClose = (popup) => {
  if (popup.autoCloseTimer) {
    clearTimeout(popup.autoCloseTimer)
    popup.autoCloseTimer = null
  }
  popup.pausedAt = Date.now()
}

const resumeAutoClose = (popup) => {
  if (popup.pausedAt) {
    const pausedDuration = Date.now() - popup.pausedAt
    popup.createdAt += pausedDuration
    popup.pausedAt = null
  }
  if (!popup.autoCloseTimer) {
    popup.autoCloseTimer = setTimeout(() => {
      alertStore.dismissPopup(popup.popupId)
    }, AUTO_CLOSE_MS - (Date.now() - popup.createdAt))
  }
}

const startAutoClose = (popup) => {
  if (popup.autoCloseTimer) clearTimeout(popup.autoCloseTimer)
  popup.autoCloseTimer = setTimeout(() => {
    alertStore.dismissPopup(popup.popupId)
  }, AUTO_CLOSE_MS)
}

const watchPopups = () => {
  alertStore.popups.forEach(p => {
    if (!p.autoCloseTimer && !p.pausedAt) {
      startAutoClose(p)
    }
  })
}

onMounted(() => {
  progressTimer = setInterval(() => {
    tick.value++
    watchPopups()
  }, 200)
})

onBeforeUnmount(() => {
  if (progressTimer) clearInterval(progressTimer)
})
</script>

<style scoped>
.alert-toast-container {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 12px;
  pointer-events: none;
}

.toast-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-toast {
  position: relative;
  width: 380px;
  background: linear-gradient(135deg, #fff5f5 0%, #ffffff 60%);
  border-radius: 16px;
  box-shadow:
    0 12px 32px rgba(255, 77, 79, 0.25),
    0 4px 12px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  pointer-events: auto;
  border: 1px solid #ffccc7;
}

.alert-toast.is-new {
  animation: toastIn 0.5s cubic-bezier(0.16, 1, 0.3, 1), shakeX 0.4s ease-in-out;
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateX(120%) scale(0.85);
  }
  to {
    opacity: 1;
    transform: translateX(0) scale(1);
  }
}

@keyframes shakeX {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-8px); }
  40% { transform: translateX(8px); }
  60% { transform: translateX(-5px); }
  80% { transform: translateX(5px); }
}

.toast-accent {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 5px;
  background: linear-gradient(90deg, #ff4d4f, #ff7875, #ff4d4f);
  background-size: 200% 100%;
  animation: accentSlide 2s linear infinite;
}

@keyframes accentSlide {
  from { background-position: 0% 0; }
  to { background-position: 200% 0; }
}

.toast-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 18px 12px;
  border-bottom: 1px dashed #ffd6d6;
}

.toast-icon-wrap {
  position: relative;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.toast-icon {
  font-size: 30px;
  animation: iconWobble 0.6s ease-in-out infinite;
  z-index: 2;
}

@keyframes iconWobble {
  0%, 100% { transform: rotate(0deg) scale(1); }
  25% { transform: rotate(-10deg) scale(1.1); }
  75% { transform: rotate(10deg) scale(1.1); }
}

.pulse-ring {
  position: absolute;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  border: 2px solid #ff4d4f;
  animation: ringPulse 1.5s ease-out infinite;
}

@keyframes ringPulse {
  0% { transform: scale(0.8); opacity: 0.8; }
  100% { transform: scale(1.6); opacity: 0; }
}

.toast-titles {
  flex: 1;
  min-width: 0;
}

.toast-title {
  font-size: 16px;
  font-weight: 700;
  color: #cf1322;
  letter-spacing: 0.5px;
}

.toast-subtitle {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 3px;
  font-size: 12px;
  color: #888;
}

.pond-name {
  color: #5c0011;
  font-weight: 600;
  background: #fff1f0;
  padding: 2px 8px;
  border-radius: 4px;
}

.toast-time {
  font-family: 'SF Mono', Monaco, monospace;
}

.toast-close {
  width: 26px;
  height: 26px;
  border: none;
  background: transparent;
  font-size: 22px;
  line-height: 1;
  color: #999;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.toast-close:hover {
  background: #fff1f0;
  color: #ff4d4f;
  transform: rotate(90deg);
}

.toast-body {
  padding: 12px 18px 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.abnormal-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(255, 77, 79, 0.06);
  border-left: 3px solid #ff4d4f;
}

.abnormal-item.high {
  border-left-color: #ff4d4f;
  background: rgba(255, 77, 79, 0.08);
}

.abnormal-item.low {
  border-left-color: #fa8c16;
  background: rgba(250, 140, 22, 0.08);
}

.abnormal-left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.abnormal-arrow {
  font-size: 18px;
  font-weight: 700;
}

.abnormal-item.high .abnormal-arrow {
  color: #ff4d4f;
}

.abnormal-item.low .abnormal-arrow {
  color: #fa8c16;
}

.abnormal-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.abnormal-status {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 500;
}

.abnormal-item.high .abnormal-status {
  background: #fff2f0;
  color: #ff4d4f;
}

.abnormal-item.low .abnormal-status {
  background: #fff7e6;
  color: #fa8c16;
}

.abnormal-right {
  text-align: right;
}

.abnormal-value {
  display: flex;
  align-items: baseline;
  gap: 2px;
  justify-content: flex-end;
}

.current-value {
  font-size: 18px;
  font-weight: 700;
  color: #cf1322;
  font-family: 'SF Mono', Monaco, monospace;
}

.current-unit {
  font-size: 12px;
  color: #888;
}

.abnormal-safe {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}

.toast-progress {
  height: 3px;
  background: #f5f5f5;
  overflow: hidden;
}

.toast-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #ff4d4f, #ff7875);
  transition: width 0.2s linear;
}

.toast-actions {
  pointer-events: auto;
}

.action-btn {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.dismiss-all {
  background: #ff4d4f;
  color: white;
}

.dismiss-all:hover {
  background: #ff7875;
  transform: translateY(-2px);
}

.toast-enter-active {
  transition: all 0.5s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-leave-active {
  transition: all 0.3s ease;
  position: absolute;
  width: 380px;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(120%) scale(0.85);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(120%) scale(0.85);
}

.toast-move {
  transition: transform 0.4s ease;
}

@media (max-width: 480px) {
  .alert-toast-container {
    right: 12px;
    left: 12px;
    bottom: 12px;
  }

  .alert-toast {
    width: 100%;
  }

  .toast-leave-active {
    width: 100%;
  }
}
</style>
