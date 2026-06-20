import axios from 'axios'

const request = axios.create({
  baseURL: '/api',
  timeout: 10000
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

export const monitoringApi = {
  create: (data) => request.post('/monitoring/', data),
  getLatest: () => request.get('/monitoring/latest'),
  list: (limit = 100, offset = 0) => request.get('/monitoring/', { params: { limit, offset } }),
  getById: (id) => request.get(`/monitoring/${id}`),
  delete: (id) => request.delete(`/monitoring/${id}`)
}

export const thresholdsApi = {
  create: (data) => request.post('/thresholds/', data),
  getLatest: () => request.get('/thresholds/latest'),
  list: (limit = 50, offset = 0) => request.get('/thresholds/', { params: { limit, offset } }),
  update: (id, data) => request.put(`/thresholds/${id}`, data),
  delete: (id) => request.delete(`/thresholds/${id}`)
}

export default request
