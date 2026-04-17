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
      <div class="search-wrapper">
        <div class="search-box">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索商品..."
            size="large"
            clearable
            @keyup.enter="handleSearch"
            @focus="showSearchSuggestions = true"
            @input="handleSearchInput"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" size="large" class="search-btn" @click="handleSearch">
            搜索
          </el-button>
        </div>

        <div class="search-dropdown" v-if="showSearchSuggestions && (searchHistory.length > 0 || hotSearches.length > 0 || suggestions.length > 0)">
          <div class="search-history" v-if="searchHistory.length > 0">
            <div class="history-header">
              <span>搜索历史</span>
              <el-button type="danger" link size="small" @click="clearSearchHistory">清空</el-button>
            </div>
            <div class="history-list">
              <div
                v-for="(item, index) in searchHistory"
                :key="index"
                class="history-item"
                @click="selectHistoryKeyword(item.keyword)"
              >
                <el-icon><Clock /></el-icon>
                <span>{{ item.keyword }}</span>
              </div>
            </div>
          </div>

          <div class="hot-searches" v-if="hotSearches.length > 0">
            <div class="hot-header">
              <el-icon><Flame /></el-icon>
              <span>热门搜索</span>
            </div>
            <div class="hot-list">
              <el-tag
                v-for="(item, index) in hotSearches"
                :key="item.id"
                class="hot-tag"
                @click="selectHistoryKeyword(item.keyword)"
              >
                <span class="hot-rank" :class="'rank-' + (index + 1)">{{ index + 1 }}</span>
                {{ item.keyword }}
              </el-tag>
            </div>
          </div>

          <div class="search-suggestions" v-if="suggestions.length > 0">
            <div class="suggestion-header">搜索建议</div>
            <div class="suggestion-list">
              <div
                v-for="(item, index) in suggestions"
                :key="index"
                class="suggestion-item"
                @click="selectHistoryKeyword(item)"
              >
                <el-icon><Search /></el-icon>
                <span>{{ item }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="filter-section" v-if="showFilter">
      <el-card class="filter-card">
        <div class="filter-row">
          <span class="filter-label">价格区间：</span>
          <el-radio-group v-model="priceRange" size="small" @change="applyFilters">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="0-100">0-100</el-radio-button>
            <el-radio-button label="100-500">100-500</el-radio-button>
            <el-radio-button label="500-2000">500-2000</el-radio-button>
            <el-radio-button label="2000-10000">2000-10000</el-radio-button>
            <el-radio-button label="10000+">10000+</el-radio-button>
          </el-radio-group>
        </div>
        <div class="filter-row">
          <span class="filter-label">销量：</span>
          <el-radio-group v-model="salesFilter" size="small" @change="applyFilters">
            <el-radio-button label="">全部</el-radio-button>
            <el-radio-button label="100">100+</el-radio-button>
            <el-radio-button label="500">500+</el-radio-button>
            <el-radio-button label="1000">1000+</el-radio-button>
          </el-radio-group>
        </div>
        <div class="filter-row">
          <span class="filter-label">排序：</span>
          <el-radio-group v-model="sortBy" size="small" @change="applyFilters">
            <el-radio-button label="">默认</el-radio-button>
            <el-radio-button label="price-asc">价格从低到高</el-radio-button>
            <el-radio-button label="price-desc">价格从高到低</el-radio-button>
            <el-radio-button label="sales-desc">销量从高到低</el-radio-button>
          </el-radio-group>
        </div>
      </el-card>
    </div>

    <div class="promotions-section">
      <div class="section-header">
        <el-icon class="section-icon" :size="24"><Star /></el-icon>
        <h3 class="section-title">限时活动</h3>
      </div>
      <div v-if="activePromotions.length === 0" style="text-align: center; padding: 40px; color: #999;">
        暂无活动
      </div>
      <div v-else class="promotions-list">
        <div
          v-for="promo in activePromotions"
          :key="promo.id"
          class="promotion-item"
          :style="{ background: getPromotionTypeStyle(promo.type).background }"
          @click="handlePromotionClick(promo)"
        >
          <div class="promo-icon">{{ getPromotionTypeStyle(promo.type).icon }}</div>
          <div class="promo-content">
            <div class="promo-name">{{ promo.name }}</div>
            <div class="promo-type">{{ getPromotionTypeName(promo.type) }}</div>
          </div>
          <div class="promo-arrow">
            <el-icon><Right /></el-icon>
          </div>
        </div>
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
          @click="goToDetail(product.id)"
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
        <el-button class="filter-toggle" @click="showFilter = !showFilter">
          <el-icon><Filter /></el-icon>
          筛选
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
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="product in sortedProducts" :key="product.id">
          <product-card
            :product="product"
            :favorites="favorites"
            :active-promotion="getProductPromotion(product)"
            @add-to-cart="handleAddToCart"
            @buy-now="handleBuyNow"
            @toggle-favorite="handleToggleFavorite"
            @view-detail="goToDetail"
          />
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  getProducts,
  getCategories,
  getHotProducts,
  addToCart,
  getFavorites,
  addFavorite,
  removeFavorite,
  getSearchHistory,
  getHotSearches,
  getSearchSuggestions,
  addSearchHistory,
  getProductsFiltered,
  getActivePromotions,
  getPromotions
} from '@/api/shopping'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const products = ref([])
const hotProducts = ref([])
const categories = ref(['全部'])
const currentCategory = ref('全部')
const searchKeyword = ref('')
const currentUser = ref(null)
const favorites = ref([])
const searchHistory = ref([])
const hotSearches = ref([])
const suggestions = ref([])
const showSearchSuggestions = ref(false)
const showFilter = ref(false)
const priceRange = ref('')
const salesFilter = ref('')
const sortBy = ref('')
const activePromotions = ref([])

const sortedProducts = computed(() => {
  let result = [...products.value]
  if (sortBy.value === 'price-asc') {
    result.sort((a, b) => a.price - b.price)
  } else if (sortBy.value === 'price-desc') {
    result.sort((a, b) => b.price - a.price)
  } else if (sortBy.value === 'sales-desc') {
    result.sort((a, b) => (b.sales || 0) - (a.sales || 0))
  }
  return result
})

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZGIi8+CjxwYXRoIGQ9Ik02MCAxMjBMODUgODVMMTE1IDExMEwxNDUgNzVMMTcwIDEyMEg2MFoiIGZpbGw9IiNEOUQzREMvPgo8Y2lyY2xlIGN4PSI4NSIgY3k9IjgwIiByPSIxNSIgZmlsbD0iI0Q5RDNEQyIvPgo8L3N2Zz4K'

let clickOutsideHandler = null

onMounted(() => {
  loadUser()
  loadCategories()
  loadHotProducts()
  loadProducts()
  loadFavorites()
  loadHotSearches()
  loadSearchHistory()
  loadActivePromotions()

  clickOutsideHandler = (e) => {
    if (!e.target.closest('.search-wrapper')) {
      showSearchSuggestions.value = false
    }
  }
  document.addEventListener('click', clickOutsideHandler)
})

onUnmounted(() => {
  if (clickOutsideHandler) {
    document.removeEventListener('click', clickOutsideHandler)
  }
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

async function loadHotSearches() {
  try {
    const res = await getHotSearches(10)
    hotSearches.value = res.data || []
  } catch (e) {
    console.error('Load hot searches failed', e)
  }
}

async function loadSearchHistory() {
  if (!currentUser.value) return
  try {
    const res = await getSearchHistory(currentUser.value.id, 10)
    searchHistory.value = res.data || []
  } catch (e) {
    console.error('Load search history failed', e)
  }
}

async function loadActivePromotions() {
  try {
    console.log('Loading all promotions...')
    const res = await getPromotions()
    console.log('All promotions response:', res)
    activePromotions.value = res.data || []
    console.log('Promotions array:', activePromotions.value)
  } catch (e) {
    console.error('Load promotions failed', e)
  }
}

function getPromotionTypeStyle(type) {
  const styles = {
    flashsale: { background: 'linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%)', icon: '🔥' },
    fullreduce: { background: 'linear-gradient(135deg, #52c41a 0%, #95de64 100%)', icon: '💰' },
    groupon: { background: 'linear-gradient(135deg, #faad14 0%, #ffc53d 100%)', icon: '👥' },
    newuser: { background: 'linear-gradient(135deg, #1890ff 0%, #69c0ff 100%)', icon: '🎉' }
  }
  return styles[type] || { background: 'linear-gradient(135deg, #999 0%, #bbb 100%)', icon: '📢' }
}

function getPromotionTypeName(type) {
  const names = {
    flashsale: '限时秒杀',
    fullreduce: '满减活动',
    groupon: '拼团',
    newuser: '新人专享'
  }
  return names[type] || type
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

async function handleSearchInput() {
  if (searchKeyword.value.length > 0) {
    try {
      const res = await getSearchSuggestions(searchKeyword.value, 8)
      suggestions.value = res.data || []
    } catch (e) {
      suggestions.value = []
    }
  } else {
    suggestions.value = []
  }
}

async function handleSearch() {
  showSearchSuggestions.value = false
  if (searchKeyword.value.trim()) {
    if (currentUser.value) {
      try {
        await addSearchHistory(searchKeyword.value.trim(), currentUser.value.id)
        loadSearchHistory()
      } catch (e) {
        console.error('Add search history failed', e)
      }
    }
  }
  await applyFilters()
}

function selectHistoryKeyword(keyword) {
  searchKeyword.value = keyword
  showSearchSuggestions.value = false
  handleSearch()
}

async function clearSearchHistory() {
  searchHistory.value = []
  ElMessage.success('已清空搜索历史')
}

async function applyFilters() {
  try {
    const params = {}
    if (currentCategory.value && currentCategory.value !== '全部') {
      params.category = currentCategory.value
    }
    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (priceRange.value) {
      const [min, max] = priceRange.value.split('-')
      if (min) params.min_price = parseFloat(min)
      if (max && max !== '+') params.max_price = parseFloat(max)
    }
    if (salesFilter.value) {
      params.min_sales = parseInt(salesFilter.value)
    }

    const res = priceRange.value || salesFilter.value
      ? await getProductsFiltered(params)
      : await getProducts(params)
    products.value = res.data || []
  } catch (e) {
    console.error('Apply filters failed', e)
  }
}

function selectCategory(category) {
  currentCategory.value = category
  searchKeyword.value = ''
  priceRange.value = ''
  salesFilter.value = ''
  sortBy.value = ''
  showSearchSuggestions.value = false
  applyFilters()
}

function goToDetail(productId) {
  if (typeof productId === 'object' && productId.id) {
    productId = productId.id
  }
  router.push(`/product/${productId}`)
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

function handlePromotionClick(promo) {
  console.log('Promotion clicked:', promo)
  if (promo.product_ids) {
    const productIds = promo.product_ids.split(',').map(id => parseInt(id.trim()))
    if (productIds.length > 0 && productIds[0]) {
      router.push(`/product/${productIds[0]}`)
      return
    }
  }
  if (promo.category) {
    currentCategory.value = promo.category
    ElMessage.success(`已切换到${promo.category}分类`)
  } else {
    ElMessage.info('活动详情页开发中')
  }
}

function getProductPromotion(product) {
  console.log('=== Checking promotion for product ===')
  console.log('Product:', { id: product.id, name: product.name, category: product.category })
  console.log('All promotions:', activePromotions.value)

  if (!activePromotions.value || activePromotions.value.length === 0) {
    console.log('Result: No promotions available')
    return null
  }

  for (const promo of activePromotions.value) {
    console.log('--- Checking promo:', promo.name)
    console.log('Promo details:', { type: promo.type, status: promo.status, category: promo.category, product_ids: promo.product_ids, config: promo.config })

    if (promo.status !== 'active') {
      console.log('Skip: promo not active')
      continue
    }

    // 1. 优先匹配指定商品
    if (promo.product_ids && promo.product_ids.trim() !== '') {
      try {
        const productIdsStr = promo.product_ids.split(',').map(id => id.trim())
        const productIds = productIdsStr.map(id => parseInt(id)).filter(id => !isNaN(id))
        console.log('Checking product IDs in promo:', productIds)
        if (productIds.includes(product.id)) {
          console.log('Result: MATCHED - product ID in promo product_ids')
          return promo
        }
      } catch (e) {
        console.error('Error parsing product_ids:', e)
      }
    }

    // 2. 其次匹配分类
    if (promo.category && promo.category.trim() !== '') {
      if (promo.category === product.category) {
        console.log('Result: MATCHED - category match')
        return promo
      }
    }

    // 3. 最后匹配全场活动
    if ((!promo.category || promo.category.trim() === '') &&
        (!promo.product_ids || promo.product_ids.trim() === '')) {
      console.log('Result: MATCHED - global promo')
      return promo
    }
  }

  console.log('Result: NO matching promo found')
  return null
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
  margin-bottom: 20px;
}

.search-wrapper {
  position: relative;
  max-width: 600px;
  margin: 0 auto;
}

.search-box {
  display: flex;
  gap: 12px;
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

.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  margin-top: 8px;
  padding: 16px;
  z-index: 1000;
}

.search-history,
.hot-searches,
.search-suggestions {
  margin-bottom: 16px;
}

.search-history:last-child,
.hot-searches:last-child,
.search-suggestions:last-child {
  margin-bottom: 0;
}

.history-header,
.hot-header,
.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #999;
  margin-bottom: 12px;
}

.hot-header {
  display: flex;
  gap: 6px;
  color: #ff4d4f;
  font-weight: 500;
}

.history-list,
.suggestion-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-item,
.suggestion-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  color: #666;
  font-size: 14px;
  transition: background 0.2s;
}

.history-item:hover,
.suggestion-item:hover {
  background: #f5f7fa;
  color: #667eea;
}

.hot-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hot-tag {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
}

.hot-rank {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #999;
}

.hot-rank.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #fff;
}

.hot-rank.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #fff;
}

.hot-rank.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #daa06d 100%);
  color: #fff;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.filter-row:last-child {
  margin-bottom: 0;
}

.filter-label {
  font-size: 14px;
  color: #666;
  white-space: nowrap;
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
}

.hot-product-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
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
  align-items: center;
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

.filter-toggle {
  margin-left: auto;
  border-radius: 20px;
  padding: 8px 16px;
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

.promotions-section {
  margin-bottom: 30px;
  background: linear-gradient(135deg, #fffaf0 0%, #fff5e6 100%);
  padding: 24px;
  border-radius: 12px;
}

.promotions-section .section-icon {
  color: #fa8c16;
}

.promotions-list {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.promotions-list::-webkit-scrollbar {
  height: 6px;
}

.promotions-list::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.promotion-item {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 280px;
  padding: 16px 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.promotion-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.promo-icon {
  font-size: 32px;
  line-height: 1;
}

.promo-content {
  flex: 1;
  min-width: 0;
}

.promo-name {
  font-size: 15px;
  font-weight: 600;
  color: white;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.promo-type {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.promo-arrow {
  color: white;
  font-size: 20px;
  opacity: 0.9;
}
</style>
