<template>
  <div class="chart-card">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div v-if="statusInfo" class="chart-status" :class="statusInfo.status">
        <span class="dot"></span>
        {{ statusInfo.text }}
      </div>
    </div>
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  title: { type: String, required: true },
  data: { type: Array, default: () => [] },
  dataKey: { type: String, required: true },
  unit: { type: String, default: '' },
  safeRange: { type: Object, default: () => ({ min: 0, max: 100 }) },
  yMin: { type: Number, default: 0 },
  yMax: { type: Number, default: 100 },
  color: { type: String, default: '#1890ff' },
  currentValue: { type: Number, default: null }
})

const chartRef = ref(null)
let chartInstance = null

const statusInfo = computed(() => {
  if (props.currentValue === null) return null
  if (props.currentValue < props.safeRange.min) {
    return { status: 'low', text: '当前值偏低' }
  } else if (props.currentValue > props.safeRange.max) {
    return { status: 'high', text: '当前值偏高' }
  }
  return { status: 'normal', text: '正常范围' }
})

const formatTime = (isoString) => {
  const date = new Date(isoString)
  const h = String(date.getHours()).padStart(2, '0')
  const m = String(date.getMinutes()).padStart(2, '0')
  const s = String(date.getSeconds()).padStart(2, '0')
  return `${h}:${m}:${s}`
}

const initChart = () => {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  updateChart()
}

const updateChart = () => {
  if (!chartInstance) return

  const reversedData = [...props.data].reverse()
  const xData = reversedData.map(item => formatTime(item.created_at))
  const yData = reversedData.map(item => item[props.dataKey])

  const option = {
    grid: {
      top: 20,
      right: 20,
      bottom: 40,
      left: 60
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const item = params[0]
        return `<div style="font-weight:600;margin-bottom:6px;">${item.axisValue}</div>
                <div style="display:flex;align-items:center;gap:8px;">
                  <span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:${props.color};"></span>
                  <span>${props.title}:</span>
                  <span style="font-weight:600;">${item.value.toFixed(2)} ${props.unit}</span>
                </div>`
      }
    },
    xAxis: {
      type: 'category',
      data: xData,
      axisLine: { lineStyle: { color: '#e0e0e0' } },
      axisLabel: { color: '#666', fontSize: 11 },
      axisTick: { show: false }
    },
    yAxis: {
      type: 'value',
      min: props.yMin,
      max: props.yMax,
      axisLine: { show: false },
      axisLabel: { color: '#666', fontSize: 11, formatter: `{value} ${props.unit}` },
      splitLine: { lineStyle: { color: '#f5f5f5', type: 'dashed' } }
    },
    series: [
      {
        name: '下限',
        type: 'line',
        data: new Array(xData.length).fill(props.safeRange.min),
        lineStyle: { color: '#52c41a', type: 'dashed', width: 1 },
        symbol: 'none',
        silent: true
      },
      {
        name: '上限',
        type: 'line',
        data: new Array(xData.length).fill(props.safeRange.max),
        lineStyle: { color: '#52c41a', type: 'dashed', width: 1 },
        symbol: 'none',
        areaStyle: {
          color: 'rgba(82, 196, 26, 0.08)'
        },
        silent: true
      },
      {
        name: props.title,
        type: 'line',
        data: yData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { color: props.color, width: 2.5 },
        itemStyle: { color: props.color },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: props.color + '40' },
            { offset: 1, color: props.color + '05' }
          ])
        }
      }
    ]
  }

  chartInstance.setOption(option)
}

const handleResize = () => {
  chartInstance?.resize()
}

watch(() => props.data, () => {
  updateChart()
}, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
})
</script>

<style scoped>
.chart-card {
  background: white;
  border-radius: 16px;
  padding: 20px 24px 24px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.chart-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.chart-status {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.chart-status.normal {
  background: #f6ffed;
  color: #52c41a;
}

.chart-status.low,
.chart-status.high {
  background: #fff2f0;
  color: #ff4d4f;
}

.chart-status .dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.chart-container {
  width: 100%;
  height: 280px;
}
</style>
