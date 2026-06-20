import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { thresholdsApi } from '@/api'

const DEFAULT_THRESHOLDS = {
  temp_min: 15,
  temp_max: 30,
  ph_min: 6.5,
  ph_max: 8.5,
  do_min: 5,
  do_max: 12
}

export const useThresholdsStore = defineStore('thresholds', () => {
  const currentSettings = ref(null)
  const settingsList = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  const thresholds = computed(() => {
    if (currentSettings.value) {
      return currentSettings.value
    }
    return { ...DEFAULT_THRESHOLDS }
  })

  const tempRange = computed(() => ({ min: thresholds.value.temp_min, max: thresholds.value.temp_max }))
  const phRange = computed(() => ({ min: thresholds.value.ph_min, max: thresholds.value.ph_max }))
  const doRange = computed(() => ({ min: thresholds.value.do_min, max: thresholds.value.do_max }))

  function checkTemperature(value) {
    const { min, max } = tempRange.value
    return {
      isNormal: value >= min && value <= max,
      status: value < min ? 'low' : value > max ? 'high' : 'normal'
    }
  }

  function checkPh(value) {
    const { min, max } = phRange.value
    return {
      isNormal: value >= min && value <= max,
      status: value < min ? 'low' : value > max ? 'high' : 'normal'
    }
  }

  function checkDissolvedOxygen(value) {
    const { min, max } = doRange.value
    return {
      isNormal: value >= min && value <= max,
      status: value < min ? 'low' : value > max ? 'high' : 'normal'
    }
  }

  function checkAll(data) {
    if (!data) return null
    return {
      temperature: checkTemperature(data.temperature),
      ph: checkPh(data.ph),
      dissolvedOxygen: checkDissolvedOxygen(data.dissolved_oxygen)
    }
  }

  async function fetchLatest() {
    isLoading.value = true
    error.value = null
    try {
      const data = await thresholdsApi.getLatest()
      currentSettings.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || '获取阈值设置失败'
    } finally {
      isLoading.value = false
    }
  }

  async function fetchList(limit = 50, offset = 0) {
    isLoading.value = true
    error.value = null
    try {
      const data = await thresholdsApi.list(limit, offset)
      settingsList.value = data
    } catch (e) {
      error.value = e.response?.data?.detail || '获取设置列表失败'
    } finally {
      isLoading.value = false
    }
  }

  async function saveSettings(data) {
    isLoading.value = true
    error.value = null
    try {
      let result
      if (currentSettings.value?.id) {
        result = await thresholdsApi.update(currentSettings.value.id, data)
      } else {
        result = await thresholdsApi.create(data)
      }
      currentSettings.value = result
      return result
    } catch (e) {
      error.value = e.response?.data?.detail || '保存阈值设置失败'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    currentSettings.value = null
    settingsList.value = []
    error.value = null
  }

  return {
    currentSettings,
    settingsList,
    isLoading,
    error,
    thresholds,
    tempRange,
    phRange,
    doRange,
    checkTemperature,
    checkPh,
    checkDissolvedOxygen,
    checkAll,
    fetchLatest,
    fetchList,
    saveSettings,
    reset
  }
})
