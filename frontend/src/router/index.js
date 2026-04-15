import { createRouter, createWebHistory } from 'vue-router'
import Mall from '@/views/Mall.vue'
import Cart from '@/views/Cart.vue'
import Orders from '@/views/Orders.vue'
import Users from '@/views/Users.vue'
import Products from '@/views/Products.vue'
import Addresses from '@/views/Addresses.vue'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'

const routes = [
  { path: '/login', component: Login, meta: { requiresAuth: false } },
  { path: '/register', component: Register, meta: { requiresAuth: false } },
  { path: '/', component: Mall, meta: { requiresAuth: false } },
  { path: '/cart', component: Cart, meta: { requiresAuth: true } },
  { path: '/orders', component: Orders, meta: { requiresAuth: true } },
  { path: '/addresses', component: Addresses, meta: { requiresAuth: true } },
  { path: '/users', component: Users, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/products', component: Products, meta: { requiresAuth: true, requiresAdmin: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const currentUser = JSON.parse(localStorage.getItem('currentUser') || 'null')

  if (to.meta.requiresAuth && !token) {
    next('/login')
    return
  }

  if ((to.path === '/login' || to.path === '/register') && token) {
    next('/')
    return
  }

  if (to.meta.requiresAdmin && currentUser?.role !== 'admin') {
    alert('需要管理员权限')
    next('/')
    return
  }

  next()
})

export default router
