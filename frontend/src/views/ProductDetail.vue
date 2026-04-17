<template>
  <div class="product-detail-page">
    <div class="breadcrumb">
      <router-link to="/">首页</router-link>
      <span>/</span>
      <span>{{ product?.category || '商品详情' }}</span>
    </div>

    <div v-if="product" class="product-container">
      <div class="product-gallery">
        <div class="main-image">
          <img :src="currentImage || defaultImage" @error="handleImageError" />
        </div>
        <div class="thumbnail-list" v-if="productImages.length > 1">
          <div
            v-for="(img, index) in productImages"
            :key="index"
            class="thumbnail"
            :class="{ active: currentImage === img }"
            @click="currentImage = img"
          >
            <img :src="img" @error="handleImageError" />
          </div>
        </div>
      </div>

      <div class="product-info">
        <h1 class="product-title">{{ product.name }}</h1>
        <div class="product-tags">
          <el-tag v-if="product.is_hot" type="danger">热门</el-tag>
          <el-tag type="info">{{ product.category }}</el-tag>
        </div>

        <div class="price-section">
          <span class="price-label">价格</span>
          <span class="price">¥{{ currentPrice.toFixed(2) }}</span>
          <span v-if="product.sales > 0" class="sales">已售 {{ product.sales }}</span>
        </div>

        <div class="stock-section">
          <span class="stock-label">库存</span>
          <span class="stock" :class="{ low: currentStock <= 5 }">{{ currentStock }} 件</span>
          <span v-if="currentStock <= 5" class="stock-warning">仅剩 {{ currentStock }} 件</span>
        </div>

        <div class="sku-section" v-if="product.has_sku && skus.length > 0">
          <div class="spec-group" v-for="spec in specs" :key="spec.spec_name">
            <div class="spec-name">{{ spec.spec_name }}</div>
            <div class="spec-values">
              <el-tag
                v-for="val in spec.spec_values"
                :key="val"
                :type="selectedSpecs[spec.spec_name] === val ? 'primary' : 'info'"
                class="spec-tag"
                @click="selectSpec(spec.spec_name, val)"
              >
                {{ val }}
              </el-tag>
            </div>
          </div>
        </div>

        <div class="quantity-section">
          <span class="quantity-label">数量</span>
          <el-input-number
            v-model="quantity"
            :min="1"
            :max="currentStock"
            size="large"
          />
        </div>

        <div class="action-buttons">
          <el-button type="primary" size="large" class="btn-cart" @click="handleAddToCart" :disabled="currentStock === 0">
            <el-icon><ShoppingCart /></el-icon>
            加入购物车
          </el-button>
          <el-button type="warning" size="large" class="btn-buy" @click="handleBuyNow" :disabled="currentStock === 0">
            立即购买
          </el-button>
        </div>
      </div>
    </div>

    <el-card class="description-card" v-if="product">
      <template #header>
        <span class="card-header-title">商品详情</span>
      </template>
      <div class="description-content">
        <p>{{ product.description || '暂无描述' }}</p>
      </div>
    </el-card>

    <el-card class="reviews-card" v-if="product">
      <template #header>
        <div class="card-header">
          <span class="card-header-title">商品评价 ({{ reviews.length }})</span>
        </div>
      </template>
      <el-empty v-if="reviews.length === 0" description="暂无评价" :image-size="60" />
      <div v-else class="reviews-list">
        <div v-for="review in reviews" :key="review.id" class="review-item">
          <div class="review-header">
            <div class="user-avatar">{{ (review.user_nickname || 'U').charAt(0) }}</div>
            <div class="user-info">
              <div class="user-name">{{ review.user_nickname || '用户' }}</div>
              <div class="review-rating">
                <el-rate v-model="review.rating" disabled show-score text-color="#ff9900" />
              </div>
            </div>
            <div class="review-time">{{ formatTime(review.created_at) }}</div>
          </div>
          <div v-if="review.content" class="review-content">{{ review.content }}</div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProduct, getProductReviews, addToCart } from '@/api/shopping'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const reviews = ref([])
const skus = ref([])
const specs = ref([])
const selectedSpecs = ref({})
const currentImage = ref('')
const quantity = ref(1)
const currentUser = ref(null)

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZGIi8+CjxwYXRoIGQ9Ik02MCAxMjBMODUgODVMMTE1IDExMEwxNDUgNzVMMTcwIDEyMEg2MFoiIGZpbGw9IiNEOUQzREMvPgo8Y2lyY2xlIGN4PSI4NSIgY3k9IjgwIiByPSIxNSIgZmlsbD0iI0Q5RDNEQyIvPgo8L3N2Zz4K'

const productImages = computed(() => {
  if (!product.value) return []
  const images = [product.value.image]
  if (product.value.images) {
    try {
      const extraImages = JSON.parse(product.value.images)
      if (Array.isArray(extraImages)) {
        images.push(...extraImages.filter(img => img))
      }
    } catch (e) {
      // ignore
    }
  }
  return images.filter(img => img)
})

const currentSKU = computed(() => {
  if (!product.value?.has_sku || skus.value.length === 0) return null
  return skus.value.find(sku => {
    try {
      const skuSpecs = JSON.parse(sku.spec_json)
      return Object.keys(selectedSpecs.value).every(key => skuSpecs[key] === selectedSpecs.value[key])
    } catch (e) {
      return false
    }
  })
})

const currentPrice = computed(() => {
  return currentSKU.value?.price || product.value?.price || 0
})

const currentStock = computed(() => {
  return currentSKU.value?.stock || product.value?.stock || 0
})

async function loadProduct() {
  const productId = route.params.id
  if (!productId) return
  try {
    const res = await getProduct(productId)
    product.value = res.data
    if (productImages.value.length > 0) {
      currentImage.value = productImages.value[0]
    }
    await loadReviews()
  } catch (e) {
    ElMessage.error('加载商品失败')
    router.push('/')
  }
}

async function loadReviews() {
  if (!product.value) return
  try {
    const res = await getProductReviews(product.value.id)
    reviews.value = res.data || []
  } catch (e) {
    console.error('Load reviews failed', e)
  }
}

function selectSpec(specName, value) {
  selectedSpecs.value[specName] = value
  selectedSpecs.value = { ...selectedSpecs.value }
}

function handleImageError(e) {
  e.target.src = defaultImage
}

async function handleAddToCart() {
  const token = localStorage.getItem('token')
  if (!token) {
    const confirm = await ElMessageBox.confirm('请先登录后再加入购物车', '提示', {
      confirmButtonText: '去登录',
      cancelButtonText: '取消',
      type: 'warning'
    }).catch(() => {})
    if (confirm) {
      router.push('/login')
    }
    return
  }
  if (currentStock.value < quantity.value) {
    ElMessage.warning('库存不足')
    return
  }
  await addToCart({
    user_id: currentUser.value.id,
    product_id: product.value.id,
    sku_id: currentSKU.value?.id,
    quantity: quantity.value
  })
  ElMessage.success('已加入购物车')
}

async function handleBuyNow() {
  const token = localStorage.getItem('token')
  if (!token) {
    const confirm = await ElMessageBox.confirm('请先登录后再购买', '提示', {
      confirmButtonText: '去登录',
      cancelButtonText: '取消',
      type: 'warning'
    }).catch(() => {})
    if (confirm) {
      router.push('/login')
    }
    return
  }
  if (currentStock.value < quantity.value) {
    ElMessage.warning('库存不足')
    return
  }
  if (product.value.stock < 1) {
    ElMessage.warning('该商品库存不足')
    return
  }
  const checkoutItem = {
    id: Date.now(),
    product_id: product.value.id,
    sku_id: currentSKU.value?.id,
    quantity: quantity.value,
    product: product.value
  }
  localStorage.setItem('checkoutItems', JSON.stringify([checkoutItem]))
  router.push('/orders?checkout=true')
}

function formatTime(timeStr) {
  return new Date(timeStr).toLocaleString('zh-CN')
}

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
  loadProduct()
})

watch(() => route.params.id, () => {
  loadProduct()
})
</script>

<style scoped>
.product-detail-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.breadcrumb {
  margin-bottom: 20px;
  color: #666;
  font-size: 14px;
}

.breadcrumb a {
  color: #409eff;
  text-decoration: none;
}

.breadcrumb span {
  margin: 0 8px;
}

.product-container {
  display: flex;
  gap: 40px;
  background: white;
  padding: 30px;
  border-radius: 12px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.product-gallery {
  width: 400px;
  flex-shrink: 0;
}

.main-image {
  width: 400px;
  height: 400px;
  border-radius: 8px;
  overflow: hidden;
  background: #f5f7fa;
  margin-bottom: 16px;
}

.main-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.thumbnail-list {
  display: flex;
  gap: 12px;
}

.thumbnail {
  width: 70px;
  height: 70px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.3s;
}

.thumbnail:hover {
  border-color: #d9d9d9;
}

.thumbnail.active {
  border-color: #409eff;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
}

.product-title {
  margin: 0 0 16px 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.product-tags {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: 15px;
  padding: 20px;
  background: #fff5f5;
  border-radius: 8px;
  margin-bottom: 20px;
}

.price-label {
  color: #666;
  font-size: 14px;
}

.price {
  font-size: 32px;
  font-weight: bold;
  color: #ff4d4f;
}

.sales {
  color: #999;
  font-size: 14px;
}

.stock-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.stock-label {
  color: #666;
  font-size: 14px;
}

.stock {
  font-size: 16px;
  font-weight: 500;
}

.stock.low {
  color: #ff4d4f;
}

.stock-warning {
  color: #ff4d4f;
  font-size: 14px;
}

.sku-section {
  margin-bottom: 20px;
}

.spec-group {
  margin-bottom: 16px;
}

.spec-name {
  font-size: 14px;
  color: #666;
  margin-bottom: 10px;
}

.spec-values {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.spec-tag {
  cursor: pointer;
  user-select: none;
}

.quantity-section {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 30px;
}

.quantity-label {
  color: #666;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 16px;
}

.btn-cart, .btn-buy {
  flex: 1;
  border-radius: 8px;
  font-weight: 500;
  height: 48px;
  font-size: 16px;
}

.btn-cart {
  background: linear-gradient(135deg, #409eff 0%, #66b1ff 100%);
  border: none;
}

.btn-cart:hover {
  background: linear-gradient(135deg, #66b1ff 0%, #409eff 100%);
}

.btn-buy {
  background: linear-gradient(135deg, #ff9800 0%, #ffb74d 100%);
  border: none;
}

.btn-buy:hover {
  background: linear-gradient(135deg, #ffb74d 0%, #ff9800 100%);
}

.description-card, .reviews-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header-title {
  font-weight: 600;
  font-size: 16px;
}

.description-content {
  line-height: 1.8;
  color: #333;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.review-item {
  padding-bottom: 24px;
  border-bottom: 1px solid #f0f0f0;
}

.review-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.review-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.review-time {
  color: #999;
  font-size: 12px;
}

.review-content {
  color: #333;
  line-height: 1.6;
}
</style>
