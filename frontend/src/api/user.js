import axios from 'axios'

const api = axios.create({
  baseURL: '/api/user'
})

// 请求拦截器 - 添加 token
api.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
}, error => {
  return Promise.reject(error)
})

// 响应拦截器
api.interceptors.response.use(res => {
  if (res.data.code === 200) {
    return res.data
  }
  return Promise.reject(res.data)
}, error => {
  // 401 未授权 - 清除 token 跳转登录
  if (error.response?.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('currentUser')
    window.location.href = '/login'
  }
  return Promise.reject(error.response?.data || error)
})

// 登录
export function login(data) {
  return api.post('/api/login', data)
}

// 注册
export function register(data) {
  return api.post('/api/register', data)
}

// 获取当前用户信息
export function getCurrentUser() {
  return api.get('/api/users/me')
}

export function getUsers() {
  return api.get('/api/users')
}

export function getUser(id) {
  return api.get(`/api/users/${id}`)
}

export function createUser(data) {
  return api.post('/api/users', data)
}

export function updateUser(id, data) {
  return api.put(`/api/users/${id}`, data)
}

export function deleteUser(id) {
  return api.delete(`/api/users/${id}`)
}

// 地址管理
export function getAddresses() {
  return api.get('/api/addresses')
}

export function getAddress(id) {
  return api.get(`/api/addresses/${id}`)
}

export function createAddress(data) {
  return api.post('/api/addresses', data)
}

export function updateAddress(id, data) {
  return api.put(`/api/addresses/${id}`, data)
}

export function deleteAddress(id) {
  return api.delete(`/api/addresses/${id}`)
}
