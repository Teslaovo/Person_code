<template>
  <el-dialog v-model="visible" :title="product?.name" width="800px" class="product-detail-dialog" @closed="handleClosed">
    <div v-if="product" class="product-detail">
      <div class="product-main">
        <div class="product-image">
          <img :src="product.image || defaultImage" @error="handleImageError" />
        </div>
        <div class="product-info">
          <h2 class="product-name">{{ product.name }}</h2>
          <div class="product-category">
            <el-tag size="small">{{ product.category }}</el-tag>
            <el-tag v-if="product.is_hot" type="danger" size="small">热门</el-tag>
          </div>
          <p class="product-description">{{ product.description }}</p>
          <div class="price-section">
            <span class="price">¥{{ product.price.toFixed(2) }}</span>
            <span class="sales">销量 {{ product.sales }}</span>
          </div>
          <div class="stock-section">
            库存：{{ product.stock }} 件
          </div>
        </div>
      </div>

      <el-divider />

      <div class="reviews-section">
        <div class="reviews-header">
          <h3>商品评价</h3>
          <span class="reviews-count">{{ reviews.length }} 条评价</span>
        </div>

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
      </div>
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { getProductReviews } from '@/api/shopping'
import { ElMessage } from 'element-plus'

const props = defineProps(['modelValue', 'product'])
const emit = defineEmits(['update:modelValue'])

const visible = ref(false)
const reviews = ref([])

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZGIi8+CjxwYXRoIGQ9Ik02MCAxMjBMODUgODVMMTE1IDExMEwxNDUgNzVMMTcwIDEyMEg2MFoiIGZpbGw9IiNEOUQzREMvPgo8Y2lyY2xlIGN4PSI4NSIgY3k9IjgwIiByPSIxNSIgZmlsbD0iI0Q5RDNEQyIvPgo8L3N2Zz4K'

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.product) {
    loadReviews()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

async function loadReviews() {
  if (!props.product) return
  try {
    const res = await getProductReviews(props.product.id)
    reviews.value = res.data || []
  } catch (e) {
    console.error('Load reviews failed', e)
  }
}

function handleImageError(e) {
  e.target.src = defaultImage
}

function formatTime(timeStr) {
  return new Date(timeStr).toLocaleString('zh-CN')
}

function handleClosed() {
  reviews.value = []
}
</script>

<style scoped>
.product-detail-dialog :deep(.el-dialog__body) {
  padding: 20px;
}

.product-main {
  display: flex;
  gap: 30px;
}

.product-image {
  width: 300px;
  height: 300px;
  border-radius: 12px;
  overflow: hidden;
  background: #f5f7fa;
  flex-shrink: 0;
}

.product-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
}

.product-name {
  margin: 0 0 15px 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
}

.product-category {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.product-description {
  color: #666;
  line-height: 1.6;
  margin-bottom: 20px;
}

.price-section {
  display: flex;
  align-items: baseline;
  gap: 15px;
  margin-bottom: 15px;
}

.price-section .price {
  font-size: 32px;
  font-weight: bold;
  color: #ff4d4f;
}

.price-section .sales {
  color: #999;
  font-size: 14px;
}

.stock-section {
  color: #666;
  font-size: 14px;
}

.reviews-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 20px;
}

.reviews-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.reviews-count {
  color: #999;
  font-size: 14px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.review-item {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
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
