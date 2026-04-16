<template>
  <div class="mall">
    <div v-if="!currentUser" class="top-bar">
      <div class="welcome-section">
        <el-icon class="welcome-icon" :size="28"><ShoppingBag /></el-icon>
        <span class="welcome-text">欢迎来到 Rayshopping 商城</span>
      </div>
      <div class="auth-buttons">
        <el-button class="btn-login" @click="$router.push('/login')">登录</el-button>
        <el-button type="primary" class="btn-register" @click="$router.push('/register')">注册</el-button>
      </div>
    </div>

    <div class="search-section">
      <div class="search-box">
        <el-input
          v-model="searchKeyword"
          placeholder="搜索商品..."
          size="large"
          clearable
          @keyup.enter="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" size="large" class="search-btn" @click="handleSearch">
          搜索
        </el-button>
      </div>
    </div>

    <div class="hot-section" v-if="hotProducts.length > 0">
      <div class="section-header">
        <el-icon class="section-icon" :size="24"><Star /></el-icon>
        <h3 class="section-title">热门推荐</h3>
      </div>
      <div class="hot-products">
        <div
          v-for="product in hotProducts"
          :key="product.id"
          class="hot-product-item"
          @click="scrollToProduct(product.id)"
        >
          <img :src="product.image || defaultImage" class="hot-product-image" @error="handleImageError" />
          <div class="hot-product-info">
            <div class="hot-product-name">{{ product.name }}</div>
            <div class="hot-product-price">¥{{ product.price.toFixed(2) }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="category-section">
      <div class="category-tabs">
        <el-button
          v-for="cat in categories"
          :key="cat"
          :type="currentCategory === cat ? 'primary' : 'default'"
          class="category-tab"
          @click="selectCategory(cat)"
        >
          {{ cat }}
        </el-button>
      </div>
    </div>

    <div class="products-section">
      <div class="section-header">
        <h3 class="section-title">
          {{ currentCategory === '全部' ? '全部商品' : currentCategory }}
          <span v-if="searchKeyword" class="search-keyword"> - 搜索: {{ searchKeyword }}</span>
        </h3>
        <div class="product-count">共 {{ products.length }} 件商品</div>
      </div>

      <el-empty v-if="products.length === 0" description="没有找到相关商品" />

      <el-row :gutter="24" class="products-grid" v-else>
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="product in products" :key="product.id" :ref="(el) => setProductRef(el, product.id)">
          <product-card :product="product" :favorites="favorites" @add-to-cart="handleAddToCart" @buy-now="handleBuyNow" @toggle-favorite="handleToggleFavorite" />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts, getCategories, getHotProducts, addToCart, getFavorites, addFavorite, removeFavorite } from '@/api/shopping'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ShoppingBag, Search, Star } from '@element-plus/icons-vue'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const products = ref([])
const hotProducts = ref([])
const categories = ref(['全部'])
const currentCategory = ref('全部')
const searchKeyword = ref('')
const currentUser = ref(null)
const productRefs = ref({})
const favorites = ref([])

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZGIi8+CjxwYXRoIGQ9Ik02MCAxMjBMODUgODVMMTE1IDExMEwxNDUgNzVMMTcwIDEyMEg2MFoiIGZpbGw9IiNEOUQzREMvPgo8Y2lyY2xlIGN4PSI4NSIgY3k9IjgwIiByPSIxNSIgZmlsbD0iI0Q5RDNEQyIvPgo8L3N2Zz4K'

onMounted(() => {
  loadUser()
  loadCategories()
  loadHotProducts()
  loadProducts()
  loadFavorites()
})

function loadUser() {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
}

async function loadCategories() {
  try {
    const res = await getCategories()
    categories.value = res.data || ['全部']
  } catch (e) {
    console.error('Load categories failed', e)
  }
}

async function loadHotProducts() {
  try {
    const res = await getHotProducts(8)
    hotProducts.value = res.data || []
  } catch (e) {
    console.error('Load hot products failed', e)
  }
}

async function loadProducts() {
  try {
    const params = {}
    if (currentCategory.value && currentCategory.value !== '全部') {
      params.category = currentCategory.value
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    const res = await getProducts(params)
    products.value = res.data || []
  } catch (e) {
    console.error('Load products failed', e)
  }
}

function selectCategory(category) {
  currentCategory.value = category
  searchKeyword.value = ''
  loadProducts()
}

function handleSearch() {
  loadProducts()
}

function setProductRef(el, productId) {
  if (el) {
    productRefs.value[productId] = el
  }
}

async function scrollToProduct(productId) {
  // 检查商品是否在当前列表中
  const productInList = products.value.find(p => p.id === productId)

  if (!productInList) {
    // 如果商品不在当前列表，切换到全部分类并清除搜索
    currentCategory.value = '全部'
    searchKeyword.value = ''
    await loadProducts()
  }

  // 等待 DOM 更新完成
  await nextTick()

  // 获取元素并滚动
  const el = productRefs.value[productId]
  if (el && el.$el) {
    // el 是 Vue 组件实例，需要获取实际 DOM 元素
    el.$el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    // 添加高亮效果提示用户
    highlightProduct(el.$el)
  }
}

function highlightProduct(el) {
  const card = el.querySelector('.product-card')
  if (card) {
    card.style.transition = 'box-shadow 0.3s ease, transform 0.3s ease'
    card.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.6)'
    card.style.transform = 'scale(1.02)'

    setTimeout(() => {
      card.style.boxShadow = ''
      card.style.transform = ''
    }, 2000)
  }
}

async function handleAddToCart(product) {
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
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null')
  await addToCart({
    user_id: currentUser.id,
    product_id: product.id,
    quantity: 1
  })
  ElMessage.success('已加入购物车')
}

async function handleBuyNow(product) {
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

  if (product.stock < 1) {
    ElMessage.warning('该商品库存不足')
    return
  }

  const checkoutItem = {
    id: Date.now(),
    product_id: product.id,
    quantity: 1,
    product: product
  }

  localStorage.setItem('checkoutItems', JSON.stringify([checkoutItem]))
  router.push('/orders?checkout=true')
}

async function loadFavorites() {
  const token = localStorage.getItem('token')
  if (!token || !currentUser.value) return
  try {
    const res = await getFavorites(currentUser.value.id)
    favorites.value = res.data || []
  } catch (e) {
    console.error('Load favorites failed', e)
  }
}

async function handleToggleFavorite(product) {
  if (!currentUser.value) return
  const isFavorited = favorites.value.some(f => f.product_id === product.id)
  try {
    if (isFavorited) {
      await removeFavorite(currentUser.value.id, product.id)
      favorites.value = favorites.value.filter(f => f.product_id !== product.id)
      ElMessage.success('已取消收藏')
    } else {
      const res = await addFavorite({ user_id: currentUser.value.id, product_id: product.id })
      favorites.value.push(res.data)
      ElMessage.success('已收藏')
    }
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  }
}

function handleImageError(e) {
  e.target.src = defaultImage
}
</script>

<style scoped>
.mall {
  padding-bottom: 30px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  margin-bottom: 24px;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}

.welcome-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.welcome-icon {
  color: white;
}

.welcome-text {
  color: white;
  font-size: 18px;
  font-weight: 500;
}

.auth-buttons {
  display: flex;
  gap: 12px;
}

.btn-login {
  background: rgba(255, 255, 255, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: 500;
  border-radius: 8px;
  padding: 10px 24px;
}

.btn-login:hover {
  background: rgba(255, 255, 255, 0.3);
  color: white;
}

.btn-register {
  background: white;
  color: #667eea;
  font-weight: 600;
  border-radius: 8px;
  padding: 10px 24px;
  border: none;
}

.btn-register:hover {
  background: #f0f2ff;
  color: #667eea;
}

.search-section {
  margin-bottom: 30px;
}

.search-box {
  display: flex;
  gap: 12px;
  max-width: 600px;
  margin: 0 auto;
}

.search-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 0 32px;
  font-weight: 500;
}

.search-btn:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

.hot-section {
  margin-bottom: 30px;
  background: linear-gradient(135deg, #fff5f5 0%, #fff0f0 100%);
  padding: 24px;
  border-radius: 12px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.section-icon {
  color: #ff4d4f;
}

.section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.hot-products {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.hot-products::-webkit-scrollbar {
  height: 6px;
}

.hot-products::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.hot-product-item {
  display: flex;
  gap: 12px;
  min-width: 200px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  border: 2px solid transparent;
}

.hot-product-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
  border-color: #667eea;
}

.hot-product-image {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 6px;
  background: #f5f7fa;
}

.hot-product-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.hot-product-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.hot-product-price {
  color: #ff4d4f;
  font-size: 16px;
  font-weight: 600;
}

.category-section {
  margin-bottom: 24px;
}

.category-tabs {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.category-tab {
  border-radius: 20px;
  padding: 8px 20px;
  font-weight: 500;
  border: 1px solid #d9d9d9;
}

.category-tab:not(.el-button--primary):hover {
  color: #667eea;
  border-color: #667eea;
}

.category-tab.el-button--primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
}

.products-section {
  margin-top: 20px;
}

.products-section .section-header {
  justify-content: space-between;
  margin-bottom: 24px;
}

.search-keyword {
  color: #667eea;
  font-weight: 500;
}

.product-count {
  color: #999;
  font-size: 14px;
}

.products-grid {
  margin: 0;
}
</style>
