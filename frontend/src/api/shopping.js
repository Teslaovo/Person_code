import axios from 'axios'

const api = axios.create({
  baseURL: '/api/shop'
})

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
  if (error.response?.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('currentUser')
  }
  return Promise.reject(error.response?.data || error)
})

export function getProducts(params = {}) {
  return api.get('/api/products', { params })
}

export function getCategories() {
  return api.get('/api/products/categories')
}

export function getHotProducts(limit = 10) {
  return api.get('/api/products/hot', { params: { limit } })
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

export function updateCart(id, data) {
  return api.put(`/api/cart/${id}`, data)
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

export function updateOrderStatus(id, status) {
  return api.put(`/api/orders/${id}/status`, { status })
}

export function shipOrder(id, data) {
  return api.post(`/api/orders/${id}/ship`, data)
}

export function getFavorites(userId) {
  return api.get(`/api/favorites/${userId}`)
}

export function addFavorite(data) {
  return api.post('/api/favorites', data)
}

export function removeFavorite(userId, productId) {
  return api.delete(`/api/favorites/${userId}/${productId}`)
}

export function removeFavoriteItem(favoriteId) {
  return api.delete(`/api/favorites/item/${favoriteId}`)
}

export function getMessages(userId, otherUserId = null) {
  const params = otherUserId ? { other_user_id: otherUserId } : {}
  return api.get(`/api/messages/${userId}`, { params })
}

export function getUnreadCount(userId) {
  return api.get(`/api/messages/unread/${userId}`)
}

export function sendMessage(data) {
  return api.post('/api/messages', data)
}

export function markMessageRead(messageId) {
  return api.put(`/api/messages/${messageId}/read`)
}

export function markConversationRead(userId, otherUserId) {
  return api.put(`/api/messages/${userId}/${otherUserId}/read`)
}

export function getConversations(userId) {
  return api.get(`/api/messages/conversations/${userId}`)
}
