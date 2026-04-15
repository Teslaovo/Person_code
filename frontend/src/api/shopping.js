import axios from 'axios'

const api = axios.create({
  baseURL: '/api/shop'
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

api.interceptors.response.use(res => {
  if (res.data.code === 200) {
    return res.data
  }
  return Promise.reject(res.data)
}, error => {
  // 401 未授权 - 清除 token，但不强制跳转（公开接口不需要登录）
  if (error.response?.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('currentUser')
  }
  return Promise.reject(error.response?.data || error)
})

export function getProducts() {
  return api.get('/api/products')
}

export function getProduct(id) {
  return api.get(`/api/products/${id}`)
}

export function createProduct(data) {
  return api.post('/api/products', data)
}

export function uploadProductImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/api/upload/image', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export function updateProduct(id, data) {
  return api.put(`/api/products/${id}`, data)
}

export function deleteProduct(id) {
  return api.delete(`/api/products/${id}`)
}

export function getAllOrders() {
  return api.get('/api/orders')
}

export function getCart(userId) {
  return api.get(`/api/cart/${userId}`)
}

export function addToCart(data) {
  return api.post('/api/cart', data)
}

export function updateCart(id, quantity) {
  return api.put(`/api/cart/${id}`, { quantity })
}

export function deleteCartItem(id) {
  return api.delete(`/api/cart/${id}`)
}

export function createOrder(data) {
  return api.post('/api/orders', data)
}

export function getOrders(userId) {
  return api.get(`/api/orders/${userId}`)
}

export function getOrderDetail(id) {
  return api.get(`/api/orders/detail/${id}`)
}
