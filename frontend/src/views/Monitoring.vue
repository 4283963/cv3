<template>
  <div class="monitoring-page container">
    <div class="page-header">
      <div>
        <h2>实时监测</h2>
        <p class="subtitle">实时监控鱼塘水质指标，确保水环境安全</p>
      </div>
      <div class="header-actions">
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
        </div>
      </div>
    </div>

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
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useMonitoringStore } from '@/stores/monitoring'
import { useThresholdsStore } from '@/stores/thresholds'
import MetricCard from '@/components/MetricCard.vue'
import TrendChart from '@/components/TrendChart.vue'

const monitoringStore = useMonitoringStore()
const thresholdsStore = useThresholdsStore()
const pollInterval = ref(3000)

const statusResult = computed(() => {
  return thresholdsStore.checkAll(monitoringStore.latestData)
})

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

const getRowStatus = (item) => {
  const checks = thresholdsStore.checkAll(item)
  if (!checks) return 'unknown'
  const abnormal = Object.values(checks).some(c => !c.isNormal)
  return abnormal ? 'abnormal' : 'normal'
}

const getRowStatusText = (item) => {
  return getRowStatus(item) === 'normal' ? '正常' : '异常'
}

onMounted(async () => {
  await thresholdsStore.fetchLatest()
  await monitoringStore.fetchList(60)
  monitoringStore.startPolling(pollInterval.value)
})

onBeforeUnmount(() => {
  monitoringStore.stopPolling()
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

.polling-btn {
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
}
</style>
