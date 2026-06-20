<template>
  <div class="thresholds-page container">
    <div class="page-header">
      <div>
        <h2>阈值设置</h2>
        <p class="subtitle">配置水质指标的安全范围，超出范围将触发预警</p>
      </div>
      <div v-if="thresholdsStore.currentSettings?.updated_at" class="last-updated">
        <span>上次更新: {{ formatTime(thresholdsStore.currentSettings.updated_at) }}</span>
      </div>
    </div>

    <div v-if="thresholdsStore.error" class="error-banner">
      <span>⚠️</span>
      <span>{{ thresholdsStore.error }}</span>
    </div>

    <form @submit.prevent="handleSubmit" class="settings-form">
      <div class="form-section card">
        <div class="section-header">
          <span class="section-icon">🌡️</span>
          <h3>水温阈值设置</h3>
        </div>
        <p class="section-desc">鱼类适宜生长的水温范围，超出可能影响鱼类健康</p>
        <div class="range-input-group">
          <div class="range-item">
            <label class="input-label">
              <span class="label-text">下限温度</span>
              <span class="label-unit">°C</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model.number="formData.temp_min"
                type="number"
                step="0.1"
                min="-10"
                max="50"
                class="range-input"
                :class="{ 'has-error': formErrors.temp_min }"
              />
              <input
                v-model.number="formData.temp_min"
                type="range"
                min="-10"
                max="50"
                step="0.5"
                class="range-slider min-slider"
              />
            </div>
            <span v-if="formErrors.temp_min" class="error-text">{{ formErrors.temp_min }}</span>
          </div>
          <div class="range-visual">
            <div class="visual-track">
              <div
                class="visual-fill"
                :style="tempVisualStyle"
              ></div>
              <div class="visual-min" :style="{ left: tempMinPercent + '%' }">
                {{ formData.temp_min }}°C
              </div>
              <div class="visual-max" :style="{ left: tempMaxPercent + '%' }">
                {{ formData.temp_max }}°C
              </div>
            </div>
            <div class="visual-labels">
              <span>-10°C</span>
              <span>20°C</span>
              <span>50°C</span>
            </div>
          </div>
          <div class="range-item">
            <label class="input-label">
              <span class="label-text">上限温度</span>
              <span class="label-unit">°C</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model.number="formData.temp_max"
                type="number"
                step="0.1"
                min="-10"
                max="50"
                class="range-input"
                :class="{ 'has-error': formErrors.temp_max }"
              />
              <input
                v-model.number="formData.temp_max"
                type="range"
                min="-10"
                max="50"
                step="0.5"
                class="range-slider max-slider"
              />
            </div>
            <span v-if="formErrors.temp_max" class="error-text">{{ formErrors.temp_max }}</span>
          </div>
        </div>
      </div>

      <div class="form-section card">
        <div class="section-header">
          <span class="section-icon">💧</span>
          <h3>pH 值阈值设置</h3>
        </div>
        <p class="section-desc">水体酸碱度指标，保持中性偏弱碱性有利于鱼类生长</p>
        <div class="range-input-group">
          <div class="range-item">
            <label class="input-label">
              <span class="label-text">pH 下限</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model.number="formData.ph_min"
                type="number"
                step="0.1"
                min="0"
                max="14"
                class="range-input"
                :class="{ 'has-error': formErrors.ph_min }"
              />
              <input
                v-model.number="formData.ph_min"
                type="range"
                min="0"
                max="14"
                step="0.1"
                class="range-slider min-slider"
              />
            </div>
            <span v-if="formErrors.ph_min" class="error-text">{{ formErrors.ph_min }}</span>
          </div>
          <div class="range-visual">
            <div class="ph-scale">
              <div
                v-for="i in 15"
                :key="i"
                class="ph-segment"
                :class="{ active: isPhInRange(i - 1) }"
                :style="{ background: getPhColor(i - 1) }"
              ></div>
            </div>
            <div class="ph-labels">
              <span>0</span><span>2</span><span>4</span><span>6</span><span>7</span><span>8</span><span>10</span><span>12</span><span>14</span>
            </div>
          </div>
          <div class="range-item">
            <label class="input-label">
              <span class="label-text">pH 上限</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model.number="formData.ph_max"
                type="number"
                step="0.1"
                min="0"
                max="14"
                class="range-input"
                :class="{ 'has-error': formErrors.ph_max }"
              />
              <input
                v-model.number="formData.ph_max"
                type="range"
                min="0"
                max="14"
                step="0.1"
                class="range-slider max-slider"
              />
            </div>
            <span v-if="formErrors.ph_max" class="error-text">{{ formErrors.ph_max }}</span>
          </div>
        </div>
      </div>

      <div class="form-section card">
        <div class="section-header">
          <span class="section-icon">🫧</span>
          <h3>溶解氧阈值设置</h3>
        </div>
        <p class="section-desc">水体中溶解的氧气量，是鱼类生存的关键指标</p>
        <div class="range-input-group">
          <div class="range-item">
            <label class="input-label">
              <span class="label-text">溶解氧下限</span>
              <span class="label-unit">mg/L</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model.number="formData.do_min"
                type="number"
                step="0.1"
                min="0"
                max="20"
                class="range-input"
                :class="{ 'has-error': formErrors.do_min }"
              />
              <input
                v-model.number="formData.do_min"
                type="range"
                min="0"
                max="20"
                step="0.1"
                class="range-slider min-slider"
              />
            </div>
            <span v-if="formErrors.do_min" class="error-text">{{ formErrors.do_min }}</span>
          </div>
          <div class="range-visual do-visual">
            <div class="do-bubbles">
              <div
                v-for="i in 21"
                :key="i"
                class="bubble"
                :class="{ active: isDoInRange(i - 1) }"
                :style="{ left: ((i - 1) / 20 * 100) + '%', animationDelay: (i * 0.1) + 's' }"
              ></div>
            </div>
            <div class="do-labels">
              <span>0</span><span>5</span><span>10</span><span>15</span><span>20 mg/L</span>
            </div>
          </div>
          <div class="range-item">
            <label class="input-label">
              <span class="label-text">溶解氧上限</span>
              <span class="label-unit">mg/L</span>
            </label>
            <div class="input-wrapper">
              <input
                v-model.number="formData.do_max"
                type="number"
                step="0.1"
                min="0"
                max="20"
                class="range-input"
                :class="{ 'has-error': formErrors.do_max }"
              />
              <input
                v-model.number="formData.do_max"
                type="range"
                min="0"
                max="20"
                step="0.1"
                class="range-slider max-slider"
              />
            </div>
            <span v-if="formErrors.do_max" class="error-text">{{ formErrors.do_max }}</span>
          </div>
        </div>
      </div>

      <div class="form-actions">
        <button
          type="button"
          class="btn btn-secondary"
          @click="resetToDefaults"
          :disabled="thresholdsStore.isLoading"
        >
          恢复默认值
        </button>
        <button
          type="submit"
          class="btn btn-primary btn-submit"
          :disabled="thresholdsStore.isLoading || !isFormDirty"
        >
          <span v-if="thresholdsStore.isLoading" class="loading-spinner"></span>
          {{ thresholdsStore.isLoading ? '保存中...' : '保存设置' }}
        </button>
      </div>
    </form>

    <div v-if="saveSuccess" class="success-toast">
      <span>✅</span>
      <span>阈值设置保存成功！</span>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useThresholdsStore } from '@/stores/thresholds'

const thresholdsStore = useThresholdsStore()
const saveSuccess = ref(false)

const DEFAULT_FORM = {
  temp_min: 15,
  temp_max: 30,
  ph_min: 6.5,
  ph_max: 8.5,
  do_min: 5,
  do_max: 12
}

const formData = reactive({ ...DEFAULT_FORM })
const formErrors = reactive({
  temp_min: '',
  temp_max: '',
  ph_min: '',
  ph_max: '',
  do_min: '',
  do_max: ''
})
const initialData = reactive({ ...DEFAULT_FORM })

const isFormDirty = computed(() => {
  return Object.keys(DEFAULT_FORM).some(key => formData[key] !== initialData[key])
})

const tempMinPercent = computed(() => ((formData.temp_min + 10) / 60) * 100)
const tempMaxPercent = computed(() => ((formData.temp_max + 10) / 60) * 100)
const tempVisualStyle = computed(() => ({
  left: tempMinPercent.value + '%',
  width: (tempMaxPercent.value - tempMinPercent.value) + '%'
}))

const isPhInRange = (val) => val >= formData.ph_min && val <= formData.ph_max
const isDoInRange = (val) => val >= formData.do_min && val <= formData.do_max

const getPhColor = (val) => {
  if (val <= 2) return '#e74c3c'
  if (val <= 4) return '#e67e22'
  if (val <= 6) return '#f1c40f'
  if (val <= 8) return '#2ecc71'
  if (val <= 10) return '#3498db'
  if (val <= 12) return '#9b59b6'
  return '#8e44ad'
}

const validateForm = () => {
  let valid = true
  Object.keys(formErrors).forEach(key => formErrors[key] = '')

  if (formData.temp_min >= formData.temp_max) {
    formErrors.temp_min = '下限必须小于上限'
    valid = false
  }
  if (formData.ph_min >= formData.ph_max) {
    formErrors.ph_min = '下限必须小于上限'
    valid = false
  }
  if (formData.do_min >= formData.do_max) {
    formErrors.do_min = '下限必须小于上限'
    valid = false
  }

  if (formData.temp_min < -10 || formData.temp_min > 50) {
    formErrors.temp_min = '温度范围: -10 ~ 50°C'
    valid = false
  }
  if (formData.temp_max < -10 || formData.temp_max > 50) {
    formErrors.temp_max = '温度范围: -10 ~ 50°C'
    valid = false
  }
  if (formData.ph_min < 0 || formData.ph_min > 14) {
    formErrors.ph_min = 'pH 范围: 0 ~ 14'
    valid = false
  }
  if (formData.ph_max < 0 || formData.ph_max > 14) {
    formErrors.ph_max = 'pH 范围: 0 ~ 14'
    valid = false
  }
  if (formData.do_min < 0 || formData.do_min > 20) {
    formErrors.do_min = '溶解氧范围: 0 ~ 20 mg/L'
    valid = false
  }
  if (formData.do_max < 0 || formData.do_max > 20) {
    formErrors.do_max = '溶解氧范围: 0 ~ 20 mg/L'
    valid = false
  }

  return valid
}

const handleSubmit = async () => {
  if (!validateForm()) return
  try {
    await thresholdsStore.saveSettings({ ...formData })
    Object.assign(initialData, formData)
    saveSuccess.value = true
    setTimeout(() => { saveSuccess.value = false }, 3000)
  } catch (_e) {
    // error handled in store
  }
}

const resetToDefaults = () => {
  Object.assign(formData, DEFAULT_FORM)
  Object.keys(formErrors).forEach(key => formErrors[key] = '')
}

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

watch(() => thresholdsStore.currentSettings, (settings) => {
  if (settings) {
    const data = {
      temp_min: settings.temp_min,
      temp_max: settings.temp_max,
      ph_min: settings.ph_min,
      ph_max: settings.ph_max,
      do_min: settings.do_min,
      do_max: settings.do_max
    }
    Object.assign(formData, data)
    Object.assign(initialData, data)
  }
}, { immediate: true })

onMounted(() => {
  thresholdsStore.fetchLatest()
})
</script>

<style scoped>
.thresholds-page {
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 900px;
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

.last-updated {
  padding: 8px 16px;
  background: #f6ffed;
  border-radius: 20px;
  color: #52c41a;
  font-size: 13px;
  font-weight: 500;
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

.settings-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-section {
  padding: 28px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.section-icon {
  font-size: 28px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.section-desc {
  font-size: 13px;
  color: #888;
  margin-bottom: 24px;
  padding-left: 40px;
}

.range-input-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.range-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  font-weight: 500;
  color: #555;
}

.label-unit {
  font-size: 12px;
  color: #999;
  font-weight: normal;
}

.input-wrapper {
  display: grid;
  grid-template-columns: 140px 1fr;
  gap: 20px;
  align-items: center;
}

.range-input {
  width: 100%;
  padding: 10px 14px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  font-family: 'SF Mono', Monaco, monospace;
  outline: none;
  transition: all 0.3s;
  background: #fafafa;
}

.range-input:focus {
  border-color: #1890ff;
  background: white;
  box-shadow: 0 0 0 3px rgba(24, 144, 255, 0.1);
}

.range-input.has-error {
  border-color: #ff4d4f;
  background: #fff2f0;
}

.range-slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 8px;
  border-radius: 4px;
  background: #f0f0f0;
  outline: none;
  cursor: pointer;
}

.range-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  border: 3px solid #1890ff;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.range-slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 3px 10px rgba(24, 144, 255, 0.3);
}

.range-slider::-moz-range-thumb {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: white;
  border: 3px solid #1890ff;
  cursor: pointer;
}

.range-slider.min-slider::-webkit-slider-thumb {
  border-color: #fa8c16;
}

.range-slider.max-slider::-webkit-slider-thumb {
  border-color: #eb2f96;
}

.error-text {
  font-size: 12px;
  color: #ff4d4f;
}

.range-visual {
  padding: 0 10px;
}

.visual-track {
  position: relative;
  height: 40px;
  background: linear-gradient(to right, #ff7875, #ffd666, #95de64, #69c0ff, #b37feb);
  border-radius: 20px;
  overflow: visible;
  margin-bottom: 8px;
}

.visual-fill {
  position: absolute;
  top: -3px;
  height: calc(100% + 6px);
  background: rgba(82, 196, 26, 0.25);
  border-top: 3px solid #52c41a;
  border-bottom: 3px solid #52c41a;
  z-index: 1;
}

.visual-min,
.visual-max {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  z-index: 2;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.visual-min {
  color: #fa8c16;
  border: 2px solid #fa8c16;
}

.visual-max {
  color: #eb2f96;
  border: 2px solid #eb2f96;
}

.visual-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
}

.ph-scale {
  display: flex;
  height: 32px;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 8px;
  gap: 1px;
  background: #fff;
  padding: 2px;
}

.ph-segment {
  flex: 1;
  border-radius: 4px;
  opacity: 0.35;
  transition: all 0.3s;
}

.ph-segment.active {
  opacity: 1;
  transform: scaleY(1.1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.ph-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
}

.do-visual {
  position: relative;
}

.do-bubbles {
  position: relative;
  height: 40px;
  background: linear-gradient(to bottom, rgba(24, 144, 255, 0.03), rgba(24, 144, 255, 0.08));
  border-radius: 20px;
  margin-bottom: 8px;
  overflow: hidden;
}

.bubble {
  position: absolute;
  bottom: 4px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #69c0ff;
  transform: translateX(-50%);
  opacity: 0.2;
  transition: all 0.3s;
}

.bubble.active {
  opacity: 1;
  width: 14px;
  height: 14px;
  background: #1890ff;
  animation: bubbleRise 2s ease-in-out infinite;
}

@keyframes bubbleRise {
  0%, 100% {
    transform: translateX(-50%) translateY(0) scale(1);
    opacity: 1;
  }
  50% {
    transform: translateX(-50%) translateY(-12px) scale(1.2);
    opacity: 0.7;
  }
}

.do-labels {
  display: flex;
  justify-content: space-between;
  font-size: 11px;
  color: #999;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  padding: 4px 0;
}

.btn-secondary {
  padding: 12px 28px;
  border: 2px solid #d9d9d9;
  background: white;
  color: #666;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-secondary:hover {
  border-color: #bfbfbf;
  color: #333;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-submit {
  padding: 12px 36px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-submit:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-submit:not(:disabled):hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 16px rgba(24, 144, 255, 0.3);
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.success-toast {
  position: fixed;
  top: 100px;
  right: 40px;
  background: white;
  padding: 16px 24px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #52c41a;
  border-left: 4px solid #52c41a;
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(100px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@media (max-width: 640px) {
  .input-wrapper {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}
</style>
