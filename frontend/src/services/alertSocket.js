class AlertSocket {
  constructor(url) {
    this.url = url
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 10
    this.reconnectDelay = 2000
    this.heartbeatInterval = null
    this.listeners = new Map()
    this.isManualClose = false
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  off(event, callback) {
    if (!this.listeners.has(event)) return
    if (!callback) {
      this.listeners.delete(event)
    } else {
      const cbs = this.listeners.get(event)
      const idx = cbs.indexOf(callback)
      if (idx > -1) cbs.splice(idx, 1)
    }
  }

  _emit(event, data) {
    if (!this.listeners.has(event)) return
    for (const cb of this.listeners.get(event)) {
      try {
        cb(data)
      } catch (e) {
        console.error(`[AlertSocket] 监听器异常 (${event}):`, e)
      }
    }
  }

  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return
    }
    this.isManualClose = false
    try {
      this.ws = new WebSocket(this.url)
    } catch (e) {
      console.error('[AlertSocket] 创建连接失败:', e)
      this._scheduleReconnect()
      return
    }

    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      this._startHeartbeat()
      this._emit('open', {})
    }

    this.ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data)
        if (msg.type === 'pong') return
        this._emit('message', msg)
        if (msg.type) {
          this._emit(msg.type, msg)
        }
      } catch (e) {
        console.error('[AlertSocket] 解析消息失败:', e, event.data)
      }
    }

    this.ws.onerror = (err) => {
      this._emit('error', err)
    }

    this.ws.onclose = () => {
      this._stopHeartbeat()
      this._emit('close', {})
      if (!this.isManualClose) {
        this._scheduleReconnect()
      }
    }
  }

  _scheduleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      this._emit('reconnect_failed', {})
      return
    }
    this.reconnectAttempts++
    const delay = Math.min(this.reconnectDelay * this.reconnectAttempts, 15000)
    this._emit('reconnecting', { attempt: this.reconnectAttempts, delay })
    setTimeout(() => this.connect(), delay)
  }

  _startHeartbeat() {
    this._stopHeartbeat()
    this.heartbeatInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        try {
          this.ws.send('ping')
        } catch (e) {
          console.warn('[AlertSocket] 心跳发送失败:', e)
        }
      }
    }, 25000)
  }

  _stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval)
      this.heartbeatInterval = null
    }
  }

  disconnect() {
    this.isManualClose = true
    this._stopHeartbeat()
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  get status() {
    if (!this.ws) return 'DISCONNECTED'
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING: return 'CONNECTING'
      case WebSocket.OPEN: return 'OPEN'
      case WebSocket.CLOSING: return 'CLOSING'
      case WebSocket.CLOSED: return 'CLOSED'
      default: return 'UNKNOWN'
    }
  }
}

const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
const wsHost = window.location.hostname
const wsPort = '8000'
const WS_URL = `${wsProtocol}//${wsHost}:${wsPort}/ws/alerts`

export const alertSocket = new AlertSocket(WS_URL)
export default alertSocket
