<template>
  <div class="metric-card" :class="statusClass">
    <div class="card-header">
      <span class="metric-icon">{{ icon }}</span>
      <span class="metric-name">{{ name }}</span>
      <span v-if="statusBadge" class="status-badge" :class="statusBadge">{{ statusText }}</span>
    </div>
    <div class="card-body">
      <div class="metric-value">
        <span class="value">{{ displayValue }}</span>
        <span class="unit">{{ unit }}</span>
      </div>
    </div>
    <div class="card-footer">
      <span class="range-label">安全范围:</span>
      <span class="range-value">{{ range.min }} ~ {{ range.max }} {{ unit }}</span>
    </div>
    <div class="progress-bar">
      <div
        class="progress-fill"
        :class="statusClass"
        :style="{ width: progressWidth + '%' }"
      ></div>
      <div class="safe-zone" :style="safeZoneStyle"></div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  icon: { type: String, required: true },
  value: { type: Number, default: null },
  unit: { type: String, default: '' },
  range: { type: Object, default: () => ({ min: 0, max: 100 }) },
  status: { type: String, default: 'normal' },
  minScale: { type: Number, default: 0 },
  maxScale: { type: Number, default: 100 }
})

const displayValue = computed(() => {
  if (props.value === null || props.value === undefined) return '--'
  return Number(props.value).toFixed(2)
})

const statusClass = computed(() => {
  if (props.value === null || props.value === undefined) return 'status-unknown'
  return `status-${props.status}`
})

const statusBadge = computed(() => {
  if (props.value === null || props.value === undefined) return null
  return props.status
})

const statusText = computed(() => {
  const map = { normal: '正常', low: '偏低', high: '偏高', unknown: '未知' }
  return map[props.status] || '未知'
})

const progressWidth = computed(() => {
  if (props.value === null || props.value === undefined) return 0
  const percent = ((props.value - props.minScale) / (props.maxScale - props.minScale)) * 100
  return Math.max(0, Math.min(100, percent))
})

const safeZoneStyle = computed(() => {
  const left = ((props.range.min - props.minScale) / (props.maxScale - props.minScale)) * 100
  const width = ((props.range.max - props.range.min) / (props.maxScale - props.minScale)) * 100
  return {
    left: `${Math.max(0, left)}%`,
    width: `${Math.min(100, width)}%`
  }
})
</script>

<style scoped>
.metric-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  overflow: hidden;
  transition: all 0.3s;
  border: 2px solid transparent;
}

.metric-card.status-normal {
  border-color: #52c41a;
}

.metric-card.status-low,
.metric-card.status-high {
  border-color: #ff4d4f;
  animation: pulse 2s infinite;
}

.metric-card.status-unknown {
  border-color: #d9d9d9;
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 4px 12px rgba(255, 77, 79, 0.1); }
  50% { box-shadow: 0 4px 20px rgba(255, 77, 79, 0.25); }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.metric-icon {
  font-size: 28px;
}

.metric-name {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.normal {
  background: #f6ffed;
  color: #52c41a;
}

.status-badge.low,
.status-badge.high {
  background: #fff2f0;
  color: #ff4d4f;
}

.card-body {
  margin-bottom: 16px;
}

.metric-value {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.value {
  font-size: 42px;
  font-weight: 700;
  color: #1a1a1a;
  font-family: 'SF Mono', Monaco, monospace;
}

.unit {
  font-size: 16px;
  color: #888;
}

.card-footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
  font-size: 13px;
  color: #666;
}

.range-label {
  color: #999;
}

.range-value {
  font-weight: 500;
  color: #555;
}

.progress-bar {
  position: relative;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: visible;
}

.progress-fill {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
  z-index: 2;
}

.progress-fill.status-normal {
  background: linear-gradient(90deg, #52c41a, #73d13d);
}

.progress-fill.status-low,
.progress-fill.status-high {
  background: linear-gradient(90deg, #ff4d4f, #ff7875);
}

.progress-fill.status-unknown {
  background: #bfbfbf;
}

.safe-zone {
  position: absolute;
  top: -2px;
  height: calc(100% + 4px);
  background: rgba(82, 196, 26, 0.15);
  border-top: 2px dashed #52c41a;
  border-bottom: 2px dashed #52c41a;
  z-index: 1;
}
</style>
