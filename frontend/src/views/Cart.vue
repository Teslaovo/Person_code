<template>
  <div class="cart">
    <div class="page-header">
      <h2 class="page-title">
        <el-icon class="title-icon"><ShoppingCart /></el-icon>
        购物车
      </h2>
    </div>

    <el-empty v-if="cartItems.length === 0" description="购物车是空的，快去挑选心仪的商品吧~">
      <el-button type="primary" @click="$router.push('/')">去逛逛</el-button>
    </el-empty>

    <el-card v-else class="cart-card">
      <el-table
        ref="tableRef"
        :data="cartItems"
        style="width: 100%"
        @selection-change="handleSelectionChange"
        class="cart-table"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column label="商品" min-width="350">
          <template #default="{ row }">
            <div class="product-info">
              <img :src="row.product?.image || defaultImage" class="thumb" @error="handleImageError" />
              <div class="info">
                <div class="name">{{ row.product?.name }}</div>
                <div class="price">¥{{ row.product?.price.toFixed(2) }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="数量" width="200">
          <template #default="{ row }">
            <div class="quantity-control">
              <el-input-number
                v-model="row.quantity"
                :min="1"
                :max="row.product?.stock || 999"
                @change="updateQuantity(row)"
                size="large"
                controls-position="right"
                class="quantity-input"
              />
            </div>
          </template>
        </el-table-column>
        <el-table-column label="小计" width="140">
          <template #default="{ row }">
            <span class="subtotal" v-if="row.product">¥{{ (row.product.price * row.quantity).toFixed(2) }}</span>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100">
          <template #default="{ row }">
            <el-button type="danger" size="small" link @click="removeItem(row)">
              <el-icon><Delete /></el-icon>
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <div v-if="cartItems.length > 0" class="footer">
      <div class="select-info">
        <el-button class="btn-select-all" @click="toggleSelectAll">
          {{ isAllSelected ? '取消全选' : '全选' }}
        </el-button>
        <span class="select-count">已选 <strong>{{ selectedItems.length }}</strong> 件商品</span>
      </div>
      <div class="footer-right">
        <div class="total-section">
          <span class="total-label">合计:</span>
          <span class="total">¥{{ selectedTotalPrice.toFixed(2) }}</span>
        </div>
        <el-button
          type="primary"
          size="large"
          class="btn-checkout"
          @click="checkout"
          :disabled="selectedItems.length === 0"
        >
          结算
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { getCart, updateCart, deleteCartItem } from '@/api/shopping'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const cartItems = ref([])
const currentUser = ref(null)
const selectedItems = ref([])
const tableRef = ref(null)

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZGIi8+CjxwYXRoIGQ9Ik02MCAxMjBMODUgODVMMTE1IDExMEwxNDUgNzVMMTcwIDEyMEg2MFoiIGZpbGw9IiNEOUQzREMvPgo8Y2lyY2xlIGN4PSI4NSIgY3k9IjgwIiByPSIxNSIgZmlsbD0iI0Q5RDNEQyIvPgo8L3N2Zz4K'

const totalPrice = computed(() => {
  return cartItems.value.reduce((sum, item) => {
    return sum + (item.product?.price || 0) * item.quantity
  }, 0)
})

const selectedTotalPrice = computed(() => {
  return selectedItems.value.reduce((sum, item) => {
    return sum + (item.product?.price || 0) * item.quantity
  }, 0)
})

const isAllSelected = computed(() => {
  return cartItems.value.length > 0 && selectedItems.value.length === cartItems.value.length
})

onMounted(() => {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
    loadCart()
  }
})

async function loadCart() {
  if (!currentUser.value) return
  const res = await getCart(currentUser.value.id)
  cartItems.value = res.data || []
  await nextTick()
  toggleSelectAll()
}

function handleSelectionChange(selection) {
  selectedItems.value = selection
}

function toggleSelectAll() {
  if (tableRef.value) {
    if (isAllSelected.value) {
      tableRef.value.clearSelection()
    } else {
      cartItems.value.forEach(row => {
        tableRef.value.toggleRowSelection(row, true)
      })
    }
  }
}

async function updateQuantity(item) {
  await updateCart(item.id, { quantity: item.quantity })
}

async function removeItem(item) {
  await ElMessageBox.confirm('确定要删除这件商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  await deleteCartItem(item.id)
  cartItems.value = cartItems.value.filter(i => i.id !== item.id)
  ElMessage.success('已删除')
}

function checkout() {
  if (selectedItems.value.length === 0) {
    ElMessage.warning('请选择要结算的商品')
    return
  }
  localStorage.setItem('checkoutItems', JSON.stringify(selectedItems.value))
  router.push('/orders?checkout=true')
}

function handleImageError(e) {
  e.target.src = defaultImage
}
</script>

<style scoped>
.cart {
  padding-bottom: 30px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
}

.title-icon {
  color: #409eff;
}

.cart-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.cart-table {
  border-radius: 8px;
}

.product-info {
  display: flex;
  gap: 16px;
  align-items: center;
}

.product-info .thumb {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
  background: #f5f7fa;
}

.product-info .info {
  flex: 1;
}

.product-info .name {
  font-weight: 600;
  font-size: 15px;
  color: #333;
  margin-bottom: 6px;
}

.product-info .price {
  color: #ff4d4f;
  font-size: 16px;
  font-weight: 600;
}

.quantity-control {
  display: flex;
  justify-content: center;
  padding: 4px 0;
}

.quantity-input {
  width: 140px;
}

.quantity-input :deep(.el-input__wrapper) {
  padding-right: 36px !important;
}

.subtotal {
  color: #ff4d4f;
  font-weight: bold;
  font-size: 18px;
}

.footer {
  margin-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 28px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.select-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.btn-select-all {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 500;
}

.btn-select-all:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  color: white;
}

.select-count {
  color: #666;
  font-size: 14px;
}

.select-count strong {
  color: #333;
  font-size: 18px;
  font-weight: 600;
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 24px;
}

.total-section {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.total-label {
  color: #666;
  font-size: 14px;
}

.total {
  font-size: 28px;
  font-weight: bold;
  color: #ff4d4f;
}

.btn-checkout {
  background: linear-gradient(135deg, #ff4d4f 0%, #ff7875 100%);
  border: none;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
  padding: 12px 40px;
}

.btn-checkout:hover {
  background: linear-gradient(135deg, #ff7875 0%, #ff4d4f 100%);
}

.btn-checkout:disabled {
  background: #d9d9d9;
}
</style>
