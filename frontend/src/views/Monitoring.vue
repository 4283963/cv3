<template>
  <div class="monitoring-page container">
    <div class="page-header">
      <div>
        <h2>实时监测</h2>
        <p class="subtitle">实时监控鱼塘水质指标，确保水环境安全</p>
      </div>
      <div class="header-actions">
        <div v-if="monitoringStore.hasAlert" class="alert-pill" :class="{ blink: isNewAlert }">
          <span class="pulse-dot"></span>
          <span>告警中 ({{ monitoringStore.abnormalMetrics.length }})</span>
        </div>
        <div class="polling-control">
          <span class="polling-label">刷新频率:</span>
          <select v-model="pollInterval" @change="handleIntervalChange" class="interval-select">
            <option :value="2000">2 秒</option>
            <option :value="3000">3 秒</option>
            <option :value="5000">5 秒</option>
            <option :value="10000">10 秒</option>
          </select>
          <button
            class="btn polling-btn"
            :class="monitoringStore.isPolling ? 'btn-stop' : 'btn-start'"
            @click="togglePolling"
          >
            {{ monitoringStore.isPolling ? '⏸ 暂停' : '▶ 开始' }}
          </button>
          <button
            class="btn sound-btn"
            :class="{ active: alertStore.soundEnabled }"
            @click="alertStore.toggleSound()"
            :title="alertStore.soundEnabled ? '关闭告警声音' : '开启告警声音'"
          >
            {{ alertStore.soundEnabled ? '🔔' : '🔕' }}
          </button>
        </div>
      </div>
    </div>

    <transition name="slide-down">
      <div v-if="monitoringStore.hasAlert" class="alert-banner">
        <div class="alert-left">
          <div class="alert-icon">🚨</div>
          <div class="alert-content">
            <div class="alert-title">水质指标异常！请立即处理</div>
            <div class="alert-metrics">
              <div
                v-for="metric in monitoringStore.abnormalMetrics"
                :key="metric.key"
                class="alert-metric-item"
              >
                <span class="metric-tag">{{ metric.name }}</span>
                <span class="metric-direction">
                  {{ metric.status === 'high' ? '↑ 偏高' : '↓ 偏低' }}
                </span>
                <span class="metric-current">
                  当前: <strong>{{ Number(metric.value).toFixed(2) }} {{ metric.unit }}</strong>
                </span>
                <span class="metric-range">
                  (安全范围: {{ metric.range.min }} ~ {{ metric.range.max }} {{ metric.unit }})
                </span>
              </div>
            </div>
          </div>
        </div>
        <div class="alert-right">
          <div class="alert-time">{{ formatAlertTime(monitoringStore.latestData?.created_at) }}</div>
          <button
            v-if="Notification.permission !== 'granted'"
            class="notify-btn"
            @click="requestNotifyPermission"
          >
            🔔 开启桌面通知
          </button>
        </div>
      </div>
    </transition>

    <div v-if="monitoringStore.error" class="error-banner">
      <span>⚠️</span>
      <span>{{ monitoringStore.error }}</span>
      <button @click="monitoringStore.fetchLatest()" class="retry-btn">重试</button>
    </div>

    <div class="metrics-grid">
      <MetricCard
        name="水温"
        icon="🌡️"
        :value="monitoringStore.latestData?.temperature"
        unit="°C"
        :range="thresholdsStore.tempRange"
        :status="tempStatus"
        :minScale="0"
        :maxScale="40"
      />
      <MetricCard
        name="pH 值"
        icon="💧"
        :value="monitoringStore.latestData?.ph"
        unit=""
        :range="thresholdsStore.phRange"
        :status="phStatus"
        :minScale="0"
        :maxScale="14"
      />
      <MetricCard
        name="溶解氧"
        icon="🫧"
        :value="monitoringStore.latestData?.dissolved_oxygen"
        unit="mg/L"
        :range="thresholdsStore.doRange"
        :status="doStatus"
        :minScale="0"
        :maxScale="20"
      />
    </div>

    <div class="status-overview card">
      <h3>整体状态概览</h3>
      <div class="overview-content">
        <div class="status-main" :class="overallStatusClass">
          <div class="status-icon">{{ overallStatusIcon }}</div>
          <div class="status-text">
            <div class="status-title">{{ overallStatusTitle }}</div>
            <div class="status-desc" v-if="latestTime">
              更新时间: {{ formatTime(latestTime) }}
            </div>
            <div class="status-desc" v-else>
              等待数据...
            </div>
          </div>
        </div>
        <div class="status-details">
          <div class="detail-item">
            <span class="detail-label">水温</span>
            <span class="detail-value" :class="tempStatus">
              {{ monitoringStore.latestData?.temperature?.toFixed(2) || '--' }} °C
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">pH 值</span>
            <span class="detail-value" :class="phStatus">
              {{ monitoringStore.latestData?.ph?.toFixed(2) || '--' }}
            </span>
          </div>
          <div class="detail-item">
            <span class="detail-label">溶解氧</span>
            <span class="detail-value" :class="doStatus">
              {{ monitoringStore.latestData?.dissolved_oxygen?.toFixed(2) || '--' }} mg/L
            </span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="alertStore.history.length > 0" class="alerts-history card">
      <div class="history-header">
        <h3>告警历史 (最近 {{ alertStore.history.length }} 条)</h3>
        <button class="btn btn-secondary btn-small" @click="alertStore.clearHistory()">
          清空
        </button>
      </div>
      <div class="history-list">
        <div
          v-for="alert in alertStore.history.slice(0, 10)"
          :key="alert.alert_id"
          class="history-item"
        >
          <div class="history-time">
            {{ formatTime(alert.timestamp) }} · {{ alert.pond_name }}
          </div>
          <div class="history-metrics">
            <span
              v-for="m in alert.abnormals"
              :key="m.metric"
              class="history-tag"
              :class="m.status"
            >
              {{ m.metric_name }} {{ m.status === 'high' ? '↑' : '↓' }} {{ Number(m.value).toFixed(2) }}{{ m.unit }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <div class="charts-section">
      <h3 class="section-title">数据趋势（最近60条记录）</h3>
      <div class="charts-grid">
        <TrendChart
          title="水温"
          :data="monitoringStore.dataList"
          dataKey="temperature"
          unit="°C"
          :safeRange="thresholdsStore.tempRange"
          :yMin="0"
          :yMax="40"
          color="#fa8c16"
          :currentValue="monitoringStore.latestData?.temperature"
        />
        <TrendChart
          title="pH 值"
          :data="monitoringStore.dataList"
          dataKey="ph"
          unit=""
          :safeRange="thresholdsStore.phRange"
          :yMin="4"
          :yMax="11"
          color="#1890ff"
          :currentValue="monitoringStore.latestData?.ph"
        />
        <TrendChart
          title="溶解氧"
          :data="monitoringStore.dataList"
          dataKey="dissolved_oxygen"
          unit="mg/L"
          :safeRange="thresholdsStore.doRange"
          :yMin="0"
          :yMax="18"
          color="#52c41a"
          :currentValue="monitoringStore.latestData?.dissolved_oxygen"
        />
      </div>
    </div>

    <div v-if="monitoringStore.dataList.length > 0" class="data-table card">
      <h3>历史数据记录</h3>
      <div class="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>采集时间</th>
              <th>水温 (°C)</th>
              <th>pH 值</th>
              <th>溶解氧 (mg/L)</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in monitoringStore.dataList.slice(0, 20)" :key="item.id">
              <td>{{ index + 1 }}</td>
              <td>{{ formatTime(item.created_at) }}</td>
              <td :class="thresholdsStore.checkTemperature(item.temperature).status">
                {{ item.temperature.toFixed(2) }}
              </td>
              <td :class="thresholdsStore.checkPh(item.ph).status">
                {{ item.ph.toFixed(2) }}
              </td>
              <td :class="thresholdsStore.checkDissolvedOxygen(item.dissolved_oxygen).status">
                {{ item.dissolved_oxygen.toFixed(2) }}
              </td>
              <td>
                <span
                  class="row-status"
                  :class="getRowStatus(item)"
                >
                  {{ getRowStatusText(item) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { useThresholdsStore } from '@/stores/thresholds'
import { useAlertStore } from '@/stores/alert'
import MetricCard from '@/components/MetricCard.vue'
import TrendChart from '@/components/TrendChart.vue'

const monitoringStore = useMonitoringStore()
const thresholdsStore = useThresholdsStore()
const alertStore = useAlertStore()
const pollInterval = ref(3000)
const isNewAlert = ref(false)
let blinkTimer = null

const statusResult = computed(() => monitoringStore.statusCheck)

const tempStatus = computed(() => statusResult.value?.temperature?.status || 'unknown')
const phStatus = computed(() => statusResult.value?.ph?.status || 'unknown')
const doStatus = computed(() => statusResult.value?.dissolvedOxygen?.status || 'unknown')

const latestTime = computed(() => monitoringStore.latestData?.created_at)

const overallStatusClass = computed(() => {
  const checks = [tempStatus.value, phStatus.value, doStatus.value]
  if (checks.some(s => s === 'unknown')) return 'status-unknown'
  if (checks.some(s => s === 'low' || s === 'high')) return 'status-alert'
  return 'status-ok'
})

const overallStatusIcon = computed(() => {
  switch (overallStatusClass.value) {
    case 'status-ok': return '✅'
    case 'status-alert': return '🚨'
    default: return '⏳'
  }
})

const overallStatusTitle = computed(() => {
  switch (overallStatusClass.value) {
    case 'status-ok': return '水质状态良好'
    case 'status-alert': return '发现异常指标，请及时处理'
    default: return '等待检测数据...'
  }
})

const formatTime = (isoString) => {
  if (!isoString) return '--'
  const date = new Date(isoString)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  const s = String(date.getSeconds()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${min}:${s}`
}

const formatAlertTime = (isoString) => {
  if (!isoString) return '--'
  const date = new Date(isoString)
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  const s = String(date.getSeconds()).padStart(2, '0')
  return `${h}:${min}:${s}`
}

const togglePolling = () => {
  if (monitoringStore.isPolling) {
    monitoringStore.stopPolling()
  } else {
    monitoringStore.startPolling(pollInterval.value)
  }
}

const handleIntervalChange = () => {
  if (monitoringStore.isPolling) {
    monitoringStore.updatePollingInterval(pollInterval.value)
  }
}

const requestNotifyPermission = () => {
  alertStore.requestNotifyPermission()
}

const getRowStatus = (item) => {
  const checks = thresholdsStore.checkAll(item)
  if (!checks) return 'unknown'
  const abnormal = Object.values(checks).some(c => !c.isNormal)
  return abnormal ? 'abnormal' : 'normal'
}

const getRowStatusText = (item) => {
  return getRowStatus(item) === 'normal' ? '正常' : '异常'
}

let lastLocalAlertKey = ''
watch([tempStatus, phStatus, doStatus], () => {
  const key = [tempStatus.value, phStatus.value, doStatus.value].join('|')
  if (overallStatusClass.value === 'status-alert' && key !== lastLocalAlertKey) {
    lastLocalAlertKey = key
    isNewAlert.value = true
    if (blinkTimer) clearTimeout(blinkTimer)
    blinkTimer = setTimeout(() => { isNewAlert.value = false }, 3000)
  } else if (overallStatusClass.value !== 'status-alert') {
    lastLocalAlertKey = ''
  }
})

onMounted(async () => {
  await thresholdsStore.fetchLatest()
  await monitoringStore.fetchList(60)
  monitoringStore.startPolling(pollInterval.value)
})

onBeforeUnmount(() => {
  monitoringStore.stopPolling()
  if (blinkTimer) clearTimeout(blinkTimer)
})
</script>

<style scoped>
.monitoring-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: white;
  padding: 20px 28px;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.page-header h2 {
  font-size: 22px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 4px;
}

.subtitle {
  font-size: 14px;
  color: #888;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.alert-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #fff2f0;
  border: 1px solid #ffccc7;
  border-radius: 20px;
  color: #ff4d4f;
  font-size: 13px;
  font-weight: 600;
}

.alert-pill.blink {
  animation: pillBlink 0.5s ease-in-out 3;
}

@keyframes pillBlink {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.08); background: #ff4d4f; color: white; }
}

.pulse-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ff4d4f;
  animation: pulse 1.2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.5); }
  50% { opacity: 0.7; transform: scale(1.1); box-shadow: 0 0 0 8px rgba(255, 77, 79, 0); }
}

.polling-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.polling-label {
  font-size: 14px;
  color: #666;
}

.interval-select {
  padding: 8px 14px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  outline: none;
  transition: border-color 0.3s;
}

.interval-select:focus {
  border-color: #1890ff;
}

.polling-btn, .sound-btn {
  padding: 8px 18px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-start {
  background: linear-gradient(135deg, #52c41a, #73d13d);
  color: white;
}

.btn-start:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.btn-stop {
  background: linear-gradient(135deg, #ff4d4f, #ff7875);
  color: white;
}

.btn-stop:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

.sound-btn {
  background: #f5f5f5;
  color: #666;
  padding: 8px 14px;
  font-size: 16px;
}

.sound-btn.active {
  background: #e6f7ff;
  color: #1890ff;
}

.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  max-height: 300px;
  overflow: hidden;
}

.slide-down-enter-from,
.slide-down-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-20px);
}

.alert-banner {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 20px;
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
  padding: 20px 24px;
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 24px rgba(255, 77, 79, 0.25);
  animation: bannerShake 0.5s ease-in-out;
}

@keyframes bannerShake {
  0%, 100% { transform: translateX(0); }
  20% { transform: translateX(-6px); }
  40% { transform: translateX(6px); }
  60% { transform: translateX(-4px); }
  80% { transform: translateX(4px); }
}

.alert-left {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  flex: 1;
}

.alert-icon {
  font-size: 48px;
  animation: iconShake 0.6s ease-in-out infinite;
  flex-shrink: 0;
}

@keyframes iconShake {
  0%, 100% { transform: rotate(0deg); }
  25% { transform: rotate(-12deg); }
  75% { transform: rotate(12deg); }
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 10px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.15);
}

.alert-metrics {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.alert-metric-item {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  font-size: 14px;
  background: rgba(255, 255, 255, 0.15);
  padding: 8px 14px;
  border-radius: 10px;
  backdrop-filter: blur(4px);
}

.metric-tag {
  background: rgba(255, 255, 255, 0.25);
  padding: 3px 10px;
  border-radius: 6px;
  font-weight: 600;
}

.metric-direction {
  font-weight: 700;
  font-size: 15px;
}

.metric-current strong {
  font-size: 16px;
}

.metric-range {
  opacity: 0.9;
  font-size: 12px;
}

.alert-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  flex-shrink: 0;
}

.alert-time {
  font-size: 13px;
  opacity: 0.9;
  font-family: 'SF Mono', Monaco, monospace;
}

.notify-btn {
  background: rgba(255, 255, 255, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.4);
  color: white;
  padding: 8px 14px;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.notify-btn:hover {
  background: white;
  color: #ff4d4f;
}

.error-banner {
  background: #fff2f0;
  border: 1px solid #ffccc7;
  padding: 14px 20px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: #ff4d4f;
  font-size: 14px;
}

.retry-btn {
  margin-left: auto;
  padding: 6px 16px;
  border: 1px solid #ff4d4f;
  background: white;
  color: #ff4d4f;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.retry-btn:hover {
  background: #ff4d4f;
  color: white;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.status-overview {
  padding: 24px 28px;
}

.status-overview h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  color: #333;
}

.overview-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  align-items: center;
}

.status-main {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px;
  border-radius: 16px;
}

.status-main.status-ok {
  background: linear-gradient(135deg, #f6ffed, #d9f7be);
}

.status-main.status-alert {
  background: linear-gradient(135deg, #fff2f0, #ffccc7);
  animation: alertPulse 2s infinite;
}

.status-main.status-unknown {
  background: linear-gradient(135deg, #fafafa, #f0f0f0);
}

@keyframes alertPulse {
  0%, 100% { box-shadow: 0 0 0 0 rgba(255, 77, 79, 0.2); }
  50% { box-shadow: 0 0 20px 5px rgba(255, 77, 79, 0.15); }
}

.status-icon {
  font-size: 52px;
}

.status-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 6px;
  color: #1a1a1a;
}

.status-desc {
  font-size: 13px;
  color: #666;
}

.status-details {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.detail-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 18px;
  background: #fafafa;
  border-radius: 10px;
}

.detail-label {
  font-size: 14px;
  color: #666;
  font-weight: 500;
}

.detail-value {
  font-size: 16px;
  font-weight: 600;
  font-family: 'SF Mono', Monaco, monospace;
}

.detail-value.normal {
  color: #52c41a;
}

.detail-value.low,
.detail-value.high {
  color: #ff4d4f;
}

.alerts-history {
  padding: 20px 24px;
}

.history-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.history-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.btn-small {
  padding: 6px 14px;
  font-size: 13px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-small:hover {
  border-color: #ff4d4f;
  color: #ff4d4f;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #fffbfb;
  border-left: 3px solid #ff4d4f;
  border-radius: 8px;
}

.history-time {
  font-size: 12px;
  color: #999;
  font-family: 'SF Mono', Monaco, monospace;
  flex-shrink: 0;
}

.history-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.history-tag {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  font-family: 'SF Mono', Monaco, monospace;
}

.history-tag.high {
  background: #fff2f0;
  color: #ff4d4f;
}

.history-tag.low {
  background: #fff7e6;
  color: #fa8c16;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 16px;
  padding-left: 4px;
}

.charts-section {
  display: flex;
  flex-direction: column;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
}

.data-table h3 {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #333;
}

.table-wrapper {
  overflow-x: auto;
  border-radius: 12px;
  border: 1px solid #f0f0f0;
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

thead {
  background: #fafafa;
}

th {
  padding: 14px 16px;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #f0f0f0;
}

td {
  padding: 12px 16px;
  border-bottom: 1px solid #f5f5f5;
  color: #333;
}

tbody tr:hover {
  background: #fafbfc;
}

tbody tr:last-child td {
  border-bottom: none;
}

td.normal {
  color: #52c41a;
  font-weight: 500;
}

td.low,
td.high {
  color: #ff4d4f;
  font-weight: 500;
}

.row-status {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.row-status.normal {
  background: #f6ffed;
  color: #52c41a;
}

.row-status.abnormal {
  background: #fff2f0;
  color: #ff4d4f;
}

@media (max-width: 768px) {
  .overview-content {
    grid-template-columns: 1fr;
  }

  .page-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .alert-banner {
    flex-direction: column;
    gap: 16px;
  }

  .alert-right {
    align-items: flex-start;
    flex-direction: row;
    justify-content: space-between;
    width: 100%;
  }
}
</style>
