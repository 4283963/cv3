import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import alertSocket from '@/services/alertSocket'

export const useAlertStore = defineStore('alert', () => {
  const popups = ref([])
  const history = ref([])
  const connectionStatus = ref('DISCONNECTED')
  const soundEnabled = ref(true)
  const desktopNotifyEnabled = ref(true)
  const unreadCount = ref(0)

  let audioCtx = null

  const activeAlertCount = computed(() => popups.value.length)

  function addPopup(alert) {
    const popup = {
      ...alert,
      popupId: `popup-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      createdAt: Date.now(),
      autoCloseTimer: null
    }
    popups.value.unshift(popup)
    if (popups.value.length > 5) {
      popups.value.pop()
    }
    if (soundEnabled.value) playAlertSound()
    if (desktopNotifyEnabled.value) sendDesktopNotification(alert)
    unreadCount.value++
    return popup
  }

  function dismissPopup(popupId) {
    const idx = popups.value.findIndex(p => p.popupId === popupId)
    if (idx > -1) {
      const popup = popups.value[idx]
      if (popup.autoCloseTimer) clearTimeout(popup.autoCloseTimer)
      popups.value.splice(idx, 1)
    }
  }

  function dismissAll() {
    popups.value.forEach(p => {
      if (p.autoCloseTimer) clearTimeout(p.autoCloseTimer)
    })
    popups.value = []
  }

  function markAllRead() {
    unreadCount.value = 0
  }

  function clearHistory() {
    history.value = []
  }

  function playAlertSound() {
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)()
      }
      if (audioCtx.state === 'suspended') audioCtx.resume()
      const now = audioCtx.currentTime
      const pattern = [880, 1100, 880, 1100]
      pattern.forEach((freq, i) => {
        const osc = audioCtx.createOscillator()
        const gain = audioCtx.createGain()
        osc.type = 'square'
        osc.frequency.setValueAtTime(freq, now + i * 0.18)
        gain.gain.setValueAtTime(0.0001, now + i * 0.18)
        gain.gain.exponentialRampToValueAtTime(0.22, now + i * 0.18 + 0.02)
        gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.18 + 0.16)
        osc.connect(gain)
        gain.connect(audioCtx.destination)
        osc.start(now + i * 0.18)
        osc.stop(now + i * 0.18 + 0.16)
      })
    } catch (e) {
      console.warn('告警音播放失败:', e)
    }
  }

  function sendDesktopNotification(alert) {
    if (typeof Notification === 'undefined' || Notification.permission !== 'granted') return
    const body = alert.abnormals.map(a =>
      `${a.metric_name} ${a.status === 'high' ? '偏高' : '偏低'}: ${Number(a.value).toFixed(2)}${a.unit} (安全 ${a.safe_min}~${a.safe_max}${a.unit})`
    ).join('\n')
    try {
      const n = new Notification(`🚨 ${alert.pond_name} 水质告警`, {
        body,
        tag: alert.alert_id,
        requireInteraction: true,
        icon: 'data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>🐟</text></svg>'
      })
      n.onclick = () => {
        window.focus()
        n.close()
      }
    } catch (e) {
      console.warn('桌面通知失败:', e)
    }
  }

  async function requestNotifyPermission() {
    if (typeof Notification === 'undefined') {
      return 'unsupported'
    }
    if (Notification.permission === 'granted') return 'granted'
    const result = await Notification.requestPermission()
    if (result === 'granted') {
      new Notification('✅ 桌面通知已开启', { body: '水质异常时会第一时间弹窗提醒' })
    }
    return result
  }

  function toggleSound() {
    soundEnabled.value = !soundEnabled.value
    return soundEnabled.value
  }

  function initSocket() {
    alertSocket.on('open', () => {
      connectionStatus.value = 'OPEN'
    })
    alertSocket.on('close', () => {
      connectionStatus.value = 'CLOSED'
    })
    alertSocket.on('reconnecting', (info) => {
      connectionStatus.value = `RECONNECTING(${info.attempt})`
    })
    alertSocket.on('error', () => {
      connectionStatus.value = 'ERROR'
    })
    alertSocket.on('alert', (alert) => {
      history.value.unshift(alert)
      if (history.value.length > 100) history.value.pop()
      addPopup(alert)
    })
    alertSocket.on('connected', () => {
      connectionStatus.value = 'OPEN'
    })
    alertSocket.connect()
  }

  function destroySocket() {
    alertSocket.disconnect()
  }

  return {
    popups,
    history,
    connectionStatus,
    soundEnabled,
    desktopNotifyEnabled,
    unreadCount,
    activeAlertCount,
    addPopup,
    dismissPopup,
    dismissAll,
    markAllRead,
    clearHistory,
    playAlertSound,
    requestNotifyPermission,
    toggleSound,
    initSocket,
    destroySocket
  }
})
