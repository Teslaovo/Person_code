<template>
  <el-container class="app-container" v-if="currentUser">
    <el-header class="app-header">
      <div class="logo">
        <h1>Rayshopping 购物平台</h1>
      </div>
      <el-menu
        :default-active="activeMenu"
        mode="horizontal"
        :router="true"
        class="nav-menu"
      >
        <el-menu-item index="/">商城</el-menu-item>
        <el-menu-item index="/cart" v-if="!isAdmin">购物车</el-menu-item>
        <el-menu-item index="/orders">{{ isAdmin ? '客户订单' : '我的订单' }}</el-menu-item>
        <el-menu-item index="/addresses" v-if="!isAdmin">收货地址</el-menu-item>
        <el-menu-item index="/users" v-if="isAdmin">用户管理</el-menu-item>
        <el-menu-item index="/products" v-if="isAdmin">商品管理</el-menu-item>
      </el-menu>
      <div class="current-user">
        <span>{{ currentUser.nickname || currentUser.username }} ({{ isAdmin ? '管理员' : '普通用户' }})</span>
        <el-button type="danger" size="small" @click="handleLogout">退出</el-button>
      </div>
    </el-header>
    <el-main class="app-main">
      <router-view />
    </el-main>
  </el-container>
  <div v-else>
    <router-view />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const currentUser = ref(null)

const isAdmin = computed(() => {
  return currentUser.value?.role === 'admin'
})

const activeMenu = computed(() => route.path)

function loadUser() {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    try {
      currentUser.value = JSON.parse(saved)
      console.log('Loaded user:', currentUser.value)
      console.log('Is admin:', isAdmin.value)
    } catch (e) {
      console.error('Failed to parse user data:', e)
      localStorage.removeItem('currentUser')
      localStorage.removeItem('token')
    }
  }
}

onMounted(() => {
  loadUser()
})

// 监听路由变化，重新加载用户数据
watch(() => route.path, () => {
  if (!currentUser.value) {
    loadUser()
  }
})

async function handleLogout() {
  await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  localStorage.removeItem('token')
  localStorage.removeItem('currentUser')
  currentUser.value = null
  ElMessage.success('已退出登录')
  router.push('/login')
}
</script>

<style scoped>
.app-container {
  min-height: 100vh;
}
.app-header {
  display: flex;
  align-items: center;
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 0 20px;
}
.logo h1 {
  margin: 0;
  font-size: 20px;
  margin-right: 40px;
}
.nav-menu {
  flex: 1;
  border-bottom: none;
}
.current-user {
  margin-left: 20px;
  display: flex;
  align-items: center;
  gap: 15px;
}
.current-user span {
  color: #666;
}
.app-main {
  background: #f5f7fa;
  padding: 20px;
}
</style>
