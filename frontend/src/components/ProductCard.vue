<template>
  <el-card class="product-card" shadow="hover">
    <div class="image-wrapper" @click="handleViewDetail">
      <img :src="product.image || defaultImage" class="product-image" @error="handleImageError" />
      <div class="favorite-btn" @click.stop="toggleFavorite">
        <el-icon :color="isFavorited ? '#ff4d4f' : '#999'"><Star /></el-icon>
      </div>
      <div class="stock-tag" v-if="product.stock <= 5 && product.stock > 0">
        仅剩{{ product.stock }}件
      </div>
      <div class="out-of-stock" v-if="product.stock === 0">
        暂时缺货
      </div>
      <div class="promotion-tag" v-if="activePromotion">
        {{ getPromotionTag(activePromotion) }}
      </div>
    </div>
    <div class="product-info" @click="handleViewDetail">
      <h3 class="product-name">{{ product.name }}</h3>
      <p class="description">{{ product.description }}</p>
      <div class="price-row">
        <div class="price-wrapper">
          <span class="price" :class="{ 'promotion-price': showPromotionPrice }">
            ¥{{ displayPrice.toFixed(2) }}
          </span>
          <span class="original-price" v-if="showPromotionPrice">
            ¥{{ product.price.toFixed(2) }}
          </span>
        </div>
        <span class="stock">库存{{ product.stock }}</span>
      </div>
    </div>
    <div class="button-group">
      <el-button type="primary" class="btn-cart" @click="$emit('add-to-cart', product)" :disabled="product.stock === 0">
        <el-icon><ShoppingCart /></el-icon>
        加入购物车
      </el-button>
      <el-button type="warning" class="btn-buy" @click="$emit('buy-now', product)" :disabled="product.stock === 0">
        立即购买
      </el-button>
    </div>
  </el-card>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { addFavorite, removeFavorite, getFavorites } from '@/api/shopping'

const props = defineProps(['product', 'favorites', 'activePromotion'])
const emit = defineEmits(['add-to-cart', 'buy-now', 'toggle-favorite', 'view-detail'])

const isFavorited = computed(() => {
  if (!props.favorites) return false
  return props.favorites.some(f => f.product_id === props.product.id)
})

const displayPrice = computed(() => {
  console.log('=== ProductCard displayPrice ===')
  console.log('Product:', props.product.name, 'id:', props.product.id, 'original price:', props.product.price)
  console.log('Active promotion:', props.activePromotion)

  if (!props.activePromotion) {
    console.log('Result: No active promotion, using original price')
    return props.product.price
  }

  // 满减活动不修改商品单价，只显示标签
  if (props.activePromotion.type === 'fullreduce') {
    console.log('Result: Full reduce promotion, not changing unit price')
    return props.product.price
  }

  try {
    console.log('Promotion config string:', props.activePromotion.config)
    const config = JSON.parse(props.activePromotion.config || '{}')
    console.log('Parsed config:', config)
    console.log('Promotion type:', props.activePromotion.type)

    switch (props.activePromotion.type) {
      case 'flashsale':
        console.log('Flash sale - config.flash_price:', config.flash_price, 'type:', typeof config.flash_price)
        const flashPrice = Number(config.flash_price)
        console.log('Flash price after Number():', flashPrice)
        if (!isNaN(flashPrice) && flashPrice >= 0) {
          console.log('Result: Using flash sale price:', flashPrice)
          return flashPrice
        }
        console.log('Result: Invalid flash price, using original')
        return props.product.price
      case 'newuser':
        const newUserPrice = Number(config.new_user_price)
        if (!isNaN(newUserPrice) && newUserPrice >= 0) {
          console.log('Result: Using new user price:', newUserPrice)
          return newUserPrice
        }
        return props.product.price
      case 'groupon':
        const discountRate = Number(config.discount_rate)
        if (!isNaN(discountRate) && discountRate > 0 && discountRate <= 1) {
          const grouponPrice = props.product.price * discountRate
          console.log('Result: Using groupon price:', grouponPrice)
          return grouponPrice
        }
        return props.product.price
      default:
        console.log('Result: Unknown promo type, using original price')
        return props.product.price
    }
  } catch (e) {
    console.error('Error parsing promo config:', e)
    return props.product.price
  }
})

// 是否显示促销价（原价划线）
const showPromotionPrice = computed(() => {
  if (!props.activePromotion) return false
  if (props.activePromotion.type === 'fullreduce') return false
  return displayPrice.value !== props.product.price
})

function getPromotionTag(promo) {
  const tags = {
    flashsale: '秒杀',
    fullreduce: '满减',
    groupon: '拼团',
    newuser: '新人专享'
  }
  return tags[promo.type] || '活动'
}

const currentUser = ref(null)

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
})

async function toggleFavorite() {
  const token = localStorage.getItem('token')
  if (!token) {
    ElMessage.warning('请先登录')
    return
  }
  if (!currentUser.value) {
    ElMessage.warning('请先登录')
    return
  }
  emit('toggle-favorite', props.product)
}

function handleViewDetail() {
  emit('view-detail', props.product)
}

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZGIi8+CjxwYXRoIGQ9Ik02MCAxMjBMODUgODVMMTE1IDExMEwxNDUgNzVMMTcwIDEyMEg2MFoiIGZpbGw9IiNEOUQzREMvPgo8Y2lyY2xlIGN4PSI4NSIgY3k9IjgwIiByPSIxNSIgZmlsbD0iI0Q5RDNEQyIvPgo8L3N2Zz4K'

function handleImageError(e) {
  e.target.src = defaultImage
}
</script>

<style scoped>
.product-card {
  margin-bottom: 20px;
  transition: all 0.3s ease;
  border-radius: 12px;
  overflow: hidden;
}

.product-card:hover {
  transform: translateY(-5px);
}

.image-wrapper {
  width: 100%;
  height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
  position: relative;
  cursor: pointer;
}

.favorite-btn {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 36px;
  height: 36px;
  background: white;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  transition: all 0.3s ease;
  z-index: 10;
}

.favorite-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.favorite-btn .el-icon {
  font-size: 20px;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.product-card:hover .product-image {
  transform: scale(1.05);
}

.stock-tag {
  position: absolute;
  top: 10px;
  right: 10px;
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a5a 100%);
  color: white;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.out-of-stock {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: rgba(0, 0, 0, 0.6);
  color: white;
  padding: 8px 20px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.promotion-tag {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  z-index: 5;
}

.product-info {
  padding: 15px;
  cursor: pointer;
}

.product-name {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
  height: 44px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.description {
  color: #999;
  font-size: 12px;
  height: 32px;
  overflow: hidden;
  line-height: 1.5;
  margin-bottom: 12px;
}

.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.price-wrapper {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.price {
  color: #ff4d4f;
  font-size: 22px;
  font-weight: bold;
}

.price.promotion-price {
  color: #ff4d4f;
}

.original-price {
  color: #999;
  font-size: 14px;
  text-decoration: line-through;
}

.stock {
  color: #999;
  font-size: 13px;
}

.button-group {
  display: flex;
  gap: 8px;
  padding: 0 15px 15px;
}

.btn-cart, .btn-buy {
  flex: 1;
  border-radius: 8px;
  font-weight: 500;
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
</style>
