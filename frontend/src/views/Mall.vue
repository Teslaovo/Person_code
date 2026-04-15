<template>
  <div class="mall">
    <div v-if="!currentUser" class="auth-banner">
      <el-alert
        title="欢迎来到 Rayshopping 商城"
        type="info"
        description="请先登录或注册以使用完整功能"
        show-icon
        :closable="false"
      >
        <template #default>
          <el-button type="primary" @click="$router.push('/login')">去登录</el-button>
          <el-button @click="$router.push('/register')">去注册</el-button>
        </template>
      </el-alert>
    </div>
    <h2>商城首页</h2>
    <el-row :gutter="20">
      <el-col :span="6" v-for="product in products" :key="product.id">
        <product-card :product="product" @add-to-cart="handleAddToCart" @buy-now="handleBuyNow" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { getProducts, addToCart } from '@/api/shopping'
import { ElMessage, ElMessageBox } from 'element-plus'
import ProductCard from '@/components/ProductCard.vue'

const router = useRouter()
const products = ref([])
const currentUser = ref(null)

onMounted(() => {
  loadUser()
  loadProducts()
})

function loadUser() {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
}

async function loadProducts() {
  const res = await getProducts()
  products.value = res.data
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

  // 检查库存
  if (product.stock < 1) {
    ElMessage.warning('该商品库存不足')
    return
  }

  // 构造立即购买的商品项
  const checkoutItem = {
    id: Date.now(), // 临时ID
    product_id: product.id,
    quantity: 1,
    product: product
  }

  // 保存到 localStorage 并跳转到订单页面
  localStorage.setItem('checkoutItems', JSON.stringify([checkoutItem]))
  router.push('/orders?checkout=true')
}
</script>

<style scoped>
.mall h2 {
  margin: 20px 0;
}

.auth-banner {
  margin-bottom: 20px;
}
</style>
