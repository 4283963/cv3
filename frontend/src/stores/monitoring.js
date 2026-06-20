import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { monitoringApi } from '@/api'

export const useMonitoringStore = defineStore('monitoring', () => {
  const latestData = ref(null)
  const dataList = ref([])
  const isLoading = ref(false)
  const error = ref(null)
  const pollInterval = ref(null)
  const isPolling = ref(false)

  const isDataNormal = computed(() => {
    if (!latestData.value) return null
    return {
      temperature: true,
      ph: true,
      dissolvedOxygen: true
    }
  })

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
  }

  return {
    latestData,
    dataList,
    isLoading,
    error,
    isPolling,
    isDataNormal,
    fetchLatest,
    fetchList,
    createData,
    startPolling,
    stopPolling,
    updatePollingInterval,
    reset
  }
})
