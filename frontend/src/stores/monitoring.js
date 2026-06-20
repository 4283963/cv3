import { defineStore } from 'pinia'
import { ref, computed, watch, getCurrentInstance } from 'vue'
import { monitoringApi } from '@/api'
import { useThresholdsStore } from '@/stores/thresholds'

export const useMonitoringStore = defineStore('monitoring', () => {
  const latestData = ref(null)
  const dataList = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const pollInterval = ref(null)
  const isPolling = ref(false)
  const pollCount = ref(0)

  const alerts = ref([])
  const lastAlertKey = ref('')

  function getThresholds() {
    return useThresholdsStore()
  }

  const statusCheck = computed(() => {
    if (!latestData.value) return null
    return getThresholds().checkAll(latestData.value)
  })

  const isDataNormal = computed(() => {
    if (!statusCheck.value) return null
    return {
      temperature: statusCheck.value.temperature.isNormal,
      ph: statusCheck.value.ph.isNormal,
      dissolvedOxygen: statusCheck.value.dissolvedOxygen.isNormal
    }
  })

  const hasAlert = computed(() => {
    if (!statusCheck.value) return false
    return Object.values(statusCheck.value).some(s => !s.isNormal)
  })

  const abnormalMetrics = computed(() => {
    if (!statusCheck.value) return []
    const thresholds = getThresholds()
    const result = []
    const metricNames = {
      temperature: '水温',
      ph: 'pH 值',
      dissolvedOxygen: '溶解氧'
    }
    const units = {
      temperature: '°C',
      ph: '',
      dissolvedOxygen: 'mg/L'
    }
    const valueKeys = {
      temperature: 'temperature',
      ph: 'ph',
      dissolvedOxygen: 'dissolved_oxygen'
    }
    const rangeKeys = {
      temperature: 'tempRange',
      ph: 'phRange',
      dissolvedOxygen: 'doRange'
    }
    for (const [key, check] of Object.entries(statusCheck.value)) {
      if (!check.isNormal) {
        result.push({
          key,
          name: metricNames[key],
          value: latestData.value[valueKeys[key]],
          unit: units[key],
          status: check.status,
          range: thresholds[rangeKeys[key]]
        })
      }
    }
    return result
  })

  function pushAlert(metrics) {
    const key = metrics.map(m => `${m.key}:${m.status}:${m.value}`).join('|')
    if (key === lastAlertKey.value) return
    lastAlertKey.value = key

    const alert = {
      id: Date.now(),
      timestamp: new Date().toISOString(),
      metrics
    }
    alerts.value.unshift(alert)
    if (alerts.value.length > 50) {
      alerts.value.pop()
    }
  }

  function clearAlerts() {
    alerts.value = []
    lastAlertKey.value = ''
  }

  watch(abnormalMetrics, (newVal, oldVal) => {
    if (newVal.length > 0 && JSON.stringify(newVal) !== JSON.stringify(oldVal)) {
      pushAlert(newVal)
    }
  }, { deep: true })

  async function fetchLatest() {
    isLoading.value = true
    error.value = null
    try {
      const data = await monitoringApi.getLatest()
      latestData.value = data
      if (data && !dataList.value.find(d => d.id === data.id)) {
        dataList.value.unshift(data)
        if (dataList.value.length > 60) {
          dataList.value.pop()
        }
      }
      pollCount.value++
      if (pollCount.value % 10 === 0) {
        getThresholds().fetchLatest().catch(() => {})
      }
    } catch (e) {
      error.value = e.response?.data?.detail || '获取数据失败'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchList(limit = 60, offset = 0) {
    isLoading.value = true
    error.value = null
    try {
      const data = await monitoringApi.list(limit, offset)
      dataList.value = data
      if (data.length > 0 && !latestData.value) {
        latestData.value = data[0]
      }
    } catch (e) {
      error.value = e.response?.data?.detail || '获取数据列表失败'
    } finally {
      isLoading.value = false
    }
  }

  async function createData(data) {
    try {
      const result = await monitoringApi.create(data)
      latestData.value = result
      dataList.value.unshift(result)
      return result
    } catch (e) {
      error.value = e.response?.data?.detail || '创建数据失败'
      throw e
    }
  }

  function startPolling(interval = 3000) {
    if (isPolling.value) return
    isPolling.value = true
    fetchLatest()
    pollInterval.value = setInterval(() => {
      fetchLatest()
    }, interval)
  }

  function stopPolling() {
    if (pollInterval.value) {
      clearInterval(pollInterval.value)
      pollInterval.value = null
    }
    isPolling.value = false
  }

  function updatePollingInterval(interval) {
    if (isPolling.value) {
      stopPolling()
      startPolling(interval)
    }
  }

  function reset() {
    stopPolling()
    latestData.value = null
    dataList.value = []
    error.value = null
    alerts.value = []
    lastAlertKey.value = ''
    pollCount.value = 0
  }

  return {
    latestData,
    dataList,
    isLoading,
    error,
    isPolling,
    alerts,
    statusCheck,
    isDataNormal,
    hasAlert,
    abnormalMetrics,
    fetchLatest,
    fetchList,
    createData,
    startPolling,
    stopPolling,
    updatePollingInterval,
    clearAlerts,
    reset
  }
})
