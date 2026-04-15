<template>
  <div class="cart">
    <h2>购物车</h2>
    <el-empty v-if="cartItems.length === 0" description="购物车是空的" />
    <el-table v-else :data="cartItems" style="width: 100%" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="55" />
      <el-table-column label="商品" width="400">
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
          <el-input-number v-model="row.quantity" :min="1" @change="updateQuantity(row)" />
        </template>
      </el-table-column>
      <el-table-column label="小计">
        <template #default="{ row }">
          <span class="subtotal" v-if="row.product">¥{{ (row.product.price * row.quantity).toFixed(2) }}</span>
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button type="danger" size="small" link @click="removeItem(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <div v-if="cartItems.length > 0" class="footer">
      <div class="select-info">
        <el-button link @click="toggleSelectAll">{{ isAllSelected ? '取消全选' : '全选' }}</el-button>
        <span>已选 {{ selectedItems.length }} 件商品</span>
      </div>
      <div class="footer-right">
        <span class="total">合计: ¥{{ selectedTotalPrice.toFixed(2) }}</span>
        <el-button type="primary" size="large" @click="checkout" :disabled="selectedItems.length === 0">结算</el-button>
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
  // 默认全选
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
  ElMessage.success('已更新')
}

async function removeItem(item) {
  await ElMessageBox.confirm('确定删除此商品？')
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
.cart h2 {
  margin-bottom: 20px;
}
.product-info {
  display: flex;
  gap: 10px;
  align-items: center;
}
.product-info .thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
  background: #f5f7fa;
}
.product-info .name {
  font-weight: bold;
}
.product-info .price {
  color: #f56c6c;
}
.subtotal {
  color: #f56c6c;
  font-weight: bold;
  font-size: 16px;
}
.footer {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.select-info {
  display: flex;
  align-items: center;
  gap: 15px;
}
.select-info span {
  color: #666;
}
.footer-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.total {
  font-size: 20px;
  font-weight: bold;
  color: #f56c6c;
}
</style>
