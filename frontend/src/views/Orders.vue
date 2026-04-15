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
            <span v-if="isAdmin" class="user-id">用户ID: {{ order.user_id }}</span>
            <el-tag :type="order.status === 'paid' ? 'success' : 'info'">
              {{ order.status === 'paid' ? '已支付' : order.status }}
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
          <el-table :data="order.items" size="small">
            <el-table-column prop="product_id" label="商品ID" width="100" />
            <el-table-column prop="quantity" label="数量" width="100" />
            <el-table-column prop="price" label="单价">
              <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
            </el-table-column>
          </el-table>
          <div class="order-total">订单总额: <span class="price">¥{{ order.total_price.toFixed(2) }}</span></div>
        </el-card>
      </el-timeline-item>
    </el-timeline>
    <el-empty v-else description="暂无订单" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { getOrders, getAllOrders, createOrder } from '@/api/shopping'
import { getAddresses } from '@/api/user'
import { ElMessage } from 'element-plus'

const route = useRoute()
const orders = ref([])
const addresses = ref([])
const showCheckout = ref(false)
const checkoutItems = ref([])
const creating = ref(false)
const currentUser = ref(null)
const selectedAddressId = ref(null)
const selectedAddress = ref(null)

const isAdmin = computed(() => currentUser.value?.role === 'admin')

const checkoutTotal = computed(() => {
  return checkoutItems.value.reduce((sum, item) => sum + item.product.price * item.quantity, 0)
})

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
    loadOrders()
    loadAddresses()
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
    ElMessage.success('订单创建成功')
    showCheckout.value = false
    checkoutItems.value = []
    loadOrders()
  } catch (e) {
    ElMessage.error(e.message || e.detail || '订单创建失败')
  } finally {
    creating.value = false
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
.order-total {
  margin-top: 15px;
  text-align: right;
}
.order-total .price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}
</style>
