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

export function getProductReviews(productId, params = {}) {
  return api.get(`/api/reviews/product/${productId}`, { params })
}

export function getUserReviews(userId, params = {}) {
  return api.get(`/api/reviews/user/${userId}`, { params })
}

export function getPendingReviews(userId, orderId) {
  return api.get(`/api/reviews/pending/${userId}/${orderId}`)
}

export function createReview(data) {
  return api.post('/api/reviews', data)
}

export function updateReview(id, data) {
  return api.put(`/api/reviews/${id}`, data)
}

export function deleteReview(id) {
  return api.delete(`/api/reviews/${id}`)
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

export function getProductSpecs(productId) {
  return api.get(`/api/products/${productId}/specs`)
}

export function getProductSkus(productId) {
  return api.get(`/api/products/${productId}/skus`)
}

export function getProductWithSkus(productId) {
  return api.get(`/api/products/${productId}/with-skus`)
}

export function createProductSpec(productId, data) {
  return api.post(`/api/products/${productId}/specs`, data)
}

export function updateSpec(specId, data) {
  return api.put(`/api/specs/${specId}`, data)
}

export function deleteSpec(specId) {
  return api.delete(`/api/specs/${specId}`)
}

export function createProductSku(productId, data) {
  return api.post(`/api/products/${productId}/skus`, data)
}

export function updateSku(skuId, data) {
  return api.put(`/api/skus/${skuId}`, data)
}

export function deleteSku(skuId) {
  return api.delete(`/api/skus/${skuId}`)
}

export function getCoupons(params = {}) {
  return api.get('/api/coupons', { params })
}

export function getCoupon(couponId) {
  return api.get(`/api/coupons/${couponId}`)
}

export function createCoupon(data) {
  return api.post('/api/coupons', data)
}

export function updateCoupon(couponId, data) {
  return api.put(`/api/coupons/${couponId}`, data)
}

export function deleteCoupon(couponId) {
  return api.delete(`/api/coupons/${couponId}`)
}

export function getUserCoupons(userId, status = null) {
  const params = status ? { status } : {}
  return api.get(`/api/user-coupons/${userId}`, { params })
}

export function claimCoupon(userId, couponId) {
  return api.post('/api/user-coupons/claim', null, { params: { user_id: userId, coupon_id: couponId } })
}

export function useCoupon(userCouponId, orderId) {
  return api.put(`/api/user-coupons/${userCouponId}/use`, null, { params: { order_id: orderId } })
}

export function calculateDiscount(couponId, totalAmount, productIds = null, category = null) {
  const params = { coupon_id: couponId, total_amount: totalAmount }
  if (productIds) params.product_ids = productIds
  if (category) params.category = category
  return api.post('/api/coupons/calculate', null, { params })
}

export function getAfterSales(params = {}) {
  return api.get('/api/after-sales', { params })
}

export function getAfterSale(afterSaleId) {
  return api.get(`/api/after-sales/${afterSaleId}`)
}

export function getUserAfterSales(userId) {
  return api.get(`/api/after-sales/user/${userId}`)
}

export function getOrderAfterSales(orderId) {
  return api.get(`/api/after-sales/order/${orderId}`)
}

export function createAfterSale(data) {
  return api.post('/api/after-sales', data)
}

export function updateAfterSale(afterSaleId, data, approvedBy = null) {
  const params = approvedBy ? { approved_by: approvedBy } : {}
  return api.put(`/api/after-sales/${afterSaleId}`, data, { params })
}

export function getLowStockProducts() {
  return api.get('/api/products/low-stock')
}

export function getOutOfStockProducts() {
  return api.get('/api/products/out-of-stock')
}

export function getStockAlerts(isResolved = null) {
  const params = isResolved !== null ? { is_resolved: isResolved } : {}
  return api.get('/api/stock-alerts', { params })
}

export function resolveStockAlert(alertId) {
  return api.post(`/api/stock-alerts/${alertId}/resolve`)
}

export function addSearchHistory(keyword, userId = null) {
  const params = { keyword }
  if (userId !== null) params.user_id = userId
  return api.post('/api/search/history', null, { params })
}

export function getSearchHistory(userId, limit = 10) {
  return api.get(`/api/search/history/${userId}`, { params: { limit } })
}

export function getHotSearches(limit = 10) {
  return api.get('/api/search/hot', { params: { limit } })
}

export function getSearchSuggestions(keyword, limit = 10) {
  return api.get('/api/search/suggestions', { params: { keyword, limit } })
}

export function getProductsFiltered(params = {}) {
  return api.get('/api/products/filter', { params })
}

export function batchUpdateProductsStatus(productIds, isActive) {
  return api.put('/api/products/batch/status', null, {
    params: { product_ids: productIds.join(','), is_active: isActive }
  })
}

export function getPromotions(params = {}) {
  return api.get('/api/promotions', { params })
}

export function getPromotion(promotionId) {
  return api.get(`/api/promotions/${promotionId}`)
}

export function createPromotion(data) {
  return api.post('/api/promotions', data)
}

export function updatePromotion(promotionId, data) {
  return api.put(`/api/promotions/${promotionId}`, data)
}

export function deletePromotion(promotionId) {
  return api.delete(`/api/promotions/${promotionId}`)
}

export function getActivePromotions() {
  return api.get('/api/promotions/active')
}

export function getProductRecommendations(productId, recType = null) {
  const params = recType ? { rec_type: recType } : {}
  return api.get(`/api/products/${productId}/recommendations`, { params })
}

export function addProductRecommendation(data) {
  return api.post('/api/products/recommendations', data)
}

export function getSalesStats(period = 'daily') {
  return api.get('/api/stats/sales', { params: { period } })
}

export function getProductSalesRank(limit = 10) {
  return api.get('/api/stats/products/rank', { params: { limit } })
}

export function getUserGrowthStats(days = 30) {
  return api.get('/api/stats/users/growth', { params: { days } })
}

export function getOrderConversionStats() {
  return api.get('/api/stats/orders/conversion')
}

export function getSummaryStats() {
  return api.get('/api/stats/summary')
}
