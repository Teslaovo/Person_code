<template>
  <div class="orders">
    <h2>{{ isAdmin ? '客户订单' : '我的订单' }}</h2>

    <el-card v-if="showCheckout" class="checkout-card">
      <template #header>
        <div class="card-header">
          <span>确认订单</span>
          <el-button link @click="showCheckout = false">取消</el-button>
        </div>
      </template>
      <el-form label-width="80px">
        <el-form-item label="收货地址">
          <el-select v-model="selectedAddressId" placeholder="请选择收货地址" style="width: 100%" @change="onAddressSelect">
            <el-option v-for="addr in addresses" :key="addr.id" :label="getAddressLabel(addr)" :value="addr.id" />
          </el-select>
          <div style="margin-top: 10px">
            <router-link to="/addresses" style="color: #409eff">去管理地址</router-link>
          </div>
        </el-form-item>
        <el-form-item v-if="selectedAddress">
          <div class="selected-address">
            <div class="address-info">
              <span class="name">{{ selectedAddress.name }}</span>
              <span class="phone">{{ selectedAddress.phone }}</span>
            </div>
            <div class="address-detail">
              {{ selectedAddress.province }}{{ selectedAddress.city }}{{ selectedAddress.district || '' }}{{ selectedAddress.detail }}
            </div>
          </div>
        </el-form-item>
      </el-form>
      <el-table :data="checkoutItems">
        <el-table-column prop="product.name" label="商品" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column label="单价">
          <template #default="{ row }">¥{{ row.product.price.toFixed(2) }}</template>
        </el-table-column>
        <el-table-column label="小计">
          <template #default="{ row }">¥{{ (row.product.price * row.quantity).toFixed(2) }}</template>
        </el-table-column>
      </el-table>
      <div class="checkout-footer">
        <span class="total">总计: ¥{{ checkoutTotal.toFixed(2) }}</span>
        <el-button type="primary" size="large" :loading="creating" @click="submitOrder" :disabled="!selectedAddressId">提交订单</el-button>
      </div>
    </el-card>

    <el-timeline v-if="orders.length > 0">
      <el-timeline-item
        v-for="order in orders"
        :key="order.id"
        :timestamp="formatDate(order.created_at)"
        placement="top"
      >
        <el-card>
          <div class="order-header">
            <span class="order-id">订单 #{{ order.id }}</span>
            <span v-if="isAdmin" class="user-id">用户昵称：{{ getUserNickname(order.user_id) }}</span>
            <el-tag :type="getStatusType(order.status)">
              {{ getStatusText(order.status) }}
            </el-tag>
          </div>
          <div v-if="order.address_name" class="order-address">
            <div class="address-title">收货信息</div>
            <div class="address-content">
              <span class="name">{{ order.address_name }}</span>
              <span class="phone">{{ order.address_phone }}</span>
            </div>
            <div class="address-detail">
              {{ order.address_province }}{{ order.address_city }}{{ order.address_district || '' }}{{ order.address_detail }}
            </div>
          </div>
          <div v-if="order.tracking_number" class="order-tracking">
            <div class="tracking-title">物流信息</div>
            <div class="tracking-content">
              <span v-if="order.tracking_company" class="company">{{ order.tracking_company }}</span>
              <span class="number">{{ order.tracking_number }}</span>
            </div>
          </div>
          <el-table :data="order.items" size="small">
            <el-table-column label="商品">
              <template #default="{ row }">
                {{ getProductName(row.product_id) }}
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="price" label="单价">
              <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
            </el-table-column>
          </el-table>
          <div class="order-total">订单总额: <span class="price">¥{{ order.total_price.toFixed(2) }}</span></div>
          <div class="order-actions">
            <template v-if="!isAdmin">
              <el-button v-if="order.status === 'pending'" type="primary" size="small" @click="handlePay(order)">立即付款</el-button>
              <el-button v-if="order.status === 'pending'" size="small" @click="handleCancel(order)">取消订单</el-button>
              <el-button v-if="order.status === 'shipped'" type="success" size="small" @click="handleConfirm(order)">确认收货</el-button>
            </template>
            <template v-else>
              <el-button v-if="order.status === 'pending'" type="primary" size="small" @click="handleUpdateStatus(order, 'paid')">标记已付款</el-button>
              <el-button v-if="order.status === 'paid'" type="warning" size="small" @click="handleShip(order)">发货</el-button>
              <el-button v-if="order.status === 'shipped'" type="success" size="small" @click="handleUpdateStatus(order, 'completed')">标记完成</el-button>
              <el-button v-if="['pending', 'paid'].includes(order.status)" size="small" @click="handleCancel(order)">取消订单</el-button>
            </template>
          </div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
    <el-empty v-else description="暂无订单" />

    <!-- 发货对话框 -->
    <el-dialog v-model="showShipDialog" title="发货" width="500px">
      <el-form :model="shipForm" label-width="100px">
        <el-form-item label="物流公司">
          <el-input v-model="shipForm.tracking_company" placeholder="请输入物流公司名称" />
        </el-form-item>
        <el-form-item label="物流单号">
          <el-input v-model="shipForm.tracking_number" placeholder="请输入物流单号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showShipDialog = false">取消</el-button>
        <el-button type="primary" :loading="shipping" @click="submitShip">确认发货</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getOrders, getAllOrders, createOrder, getProducts, updateOrderStatus, shipOrder } from '@/api/shopping'
import { getAddresses, getUsers } from '@/api/user'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const orders = ref([])
const addresses = ref([])
const products = ref([])
const users = ref([])
const showCheckout = ref(false)
const checkoutItems = ref([])
const creating = ref(false)
const currentUser = ref(null)
const selectedAddressId = ref(null)
const selectedAddress = ref(null)
const showShipDialog = ref(false)
const shipping = ref(false)
const shipForm = ref({
  tracking_company: '',
  tracking_number: ''
})
const shippingOrderId = ref(null)

const isAdmin = computed(() => currentUser.value?.role === 'admin')

const checkoutTotal = computed(() => {
  return checkoutItems.value.reduce((sum, item) => sum + item.product.price * item.quantity, 0)
})

function getStatusType(status) {
  const map = {
    pending: 'warning',
    paid: 'primary',
    shipped: 'info',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

function getStatusText(status) {
  const map = {
    pending: '待付款',
    paid: '待发货',
    shipped: '待收货',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
    loadProducts()
    loadOrders()
    loadAddresses()
    if (isAdmin.value) {
      loadUsers()
    }
  }
  if (route.query.checkout) {
    const items = localStorage.getItem('checkoutItems')
    if (items) {
      checkoutItems.value = JSON.parse(items)
      showCheckout.value = true
      localStorage.removeItem('checkoutItems')
    }
  }
})

async function loadProducts() {
  const res = await getProducts()
  products.value = res.data || []
}

async function loadUsers() {
  try {
    const res = await getUsers()
    users.value = res.data || []
  } catch (e) {
    console.error('Load users failed', e)
  }
}

function getProductName(productId) {
  const product = products.value.find(p => p.id === productId)
  return product ? product.name : `商品 #${productId}`
}

function getUserNickname(userId) {
  const user = users.value.find(u => u.id === userId)
  return user ? (user.nickname || user.username) : `用户 #${userId}`
}

async function loadOrders() {
  if (!currentUser.value) return
  let res
  if (isAdmin.value) {
    res = await getAllOrders()
  } else {
    res = await getOrders(currentUser.value.id)
  }
  orders.value = res.data || []
}

async function loadAddresses() {
  if (!currentUser.value) return
  try {
    const res = await getAddresses()
    addresses.value = res.data || []
    if (addresses.value.length > 0) {
      const defaultAddr = addresses.value.find(a => a.is_default === 1)
      if (defaultAddr) {
        selectedAddressId.value = defaultAddr.id
        selectedAddress.value = defaultAddr
      } else {
        selectedAddressId.value = addresses.value[0].id
        selectedAddress.value = addresses.value[0]
      }
    }
  } catch (e) {
    console.error('Load addresses failed', e)
  }
}

function onAddressSelect(addrId) {
  selectedAddress.value = addresses.value.find(a => a.id === addrId)
}

function getAddressLabel(addr) {
  return `${addr.name} ${addr.phone} - ${addr.province}${addr.city}${addr.district || ''}${addr.detail}`
}

async function submitOrder() {
  if (!selectedAddressId.value) {
    ElMessage.warning('请选择收货地址')
    return
  }
  creating.value = true
  try {
    await createOrder({
      user_id: currentUser.value.id,
      items: checkoutItems.value.map(item => ({
        user_id: currentUser.value.id,
        product_id: item.product_id,
        quantity: item.quantity
      })),
      address_name: selectedAddress.value.name,
      address_phone: selectedAddress.value.phone,
      address_province: selectedAddress.value.province,
      address_city: selectedAddress.value.city,
      address_district: selectedAddress.value.district,
      address_detail: selectedAddress.value.detail
    })
    ElMessage.success('订单创建成功，请付款')
    showCheckout.value = false
    checkoutItems.value = []
    loadOrders()
  } catch (e) {
    ElMessage.error(e.message || e.detail || '订单创建失败')
  } finally {
    creating.value = false
  }
}

async function handlePay(order) {
  try {
    await ElMessageBox.confirm(`确认支付 ¥${order.total_price.toFixed(2)} 吗？`, '模拟支付', {
      confirmButtonText: '确认支付',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await updateOrderStatus(order.id, 'paid')
    ElMessage.success('支付成功')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || e.detail || '支付失败')
    }
  }
}

async function handleCancel(order) {
  try {
    await ElMessageBox.confirm('确定要取消订单吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await updateOrderStatus(order.id, 'cancelled')
    ElMessage.success('订单已取消')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || e.detail || '操作失败')
    }
  }
}

async function handleConfirm(order) {
  try {
    await ElMessageBox.confirm('确认已收到商品吗？', '提示', {
      confirmButtonText: '确认收货',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await updateOrderStatus(order.id, 'completed')
    ElMessage.success('确认收货成功')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error(e.message || e.detail || '操作失败')
    }
  }
}

async function handleUpdateStatus(order, status) {
  try {
    await updateOrderStatus(order.id, status)
    ElMessage.success('状态更新成功')
    loadOrders()
  } catch (e) {
    ElMessage.error(e.message || e.detail || '操作失败')
  }
}

function handleShip(order) {
  shippingOrderId.value = order.id
  shipForm.value = {
    tracking_company: '',
    tracking_number: ''
  }
  showShipDialog.value = true
}

async function submitShip() {
  if (!shipForm.value.tracking_number) {
    ElMessage.warning('请输入物流单号')
    return
  }
  shipping.value = true
  try {
    await shipOrder(shippingOrderId.value, shipForm.value)
    ElMessage.success('发货成功')
    showShipDialog.value = false
    loadOrders()
  } catch (e) {
    ElMessage.error(e.message || e.detail || '发货失败')
  } finally {
    shipping.value = false
  }
}

function formatDate(dateStr) {
  return new Date(dateStr).toLocaleString()
}
</script>

<style scoped>
.orders h2 {
  margin-bottom: 20px;
}
.checkout-card {
  margin-bottom: 30px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.selected-address {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
}
.address-info {
  margin-bottom: 8px;
}
.address-info .name {
  font-weight: bold;
  margin-right: 15px;
}
.address-info .phone {
  color: #666;
}
.address-detail {
  color: #666;
  line-height: 1.6;
}
.checkout-footer {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 20px;
}
.checkout-footer .total {
  font-size: 20px;
  font-weight: bold;
  color: #f56c6c;
}
.order-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 10px;
}
.order-id {
  font-weight: bold;
}
.user-id {
  color: #666;
  font-size: 14px;
}
.order-address {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 15px;
}
.order-address .address-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #333;
}
.order-address .address-content {
  margin-bottom: 5px;
}
.order-address .address-content .name {
  font-weight: bold;
  margin-right: 15px;
}
.order-address .address-content .phone {
  color: #666;
}
.order-tracking {
  background: #e6f7ff;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 15px;
}
.order-tracking .tracking-title {
  font-weight: bold;
  margin-bottom: 8px;
  color: #1890ff;
}
.order-tracking .tracking-content {
  display: flex;
  gap: 15px;
}
.order-tracking .company {
  color: #1890ff;
}
.order-tracking .number {
  font-family: monospace;
  color: #333;
}
.order-total {
  margin-top: 15px;
  text-align: right;
}
.order-total .price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}
.order-actions {
  margin-top: 15px;
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  flex-wrap: wrap;
}
</style>
