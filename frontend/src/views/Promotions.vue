<template>
  <div class="promotions">
    <div class="page-header">
      <h2>营销活动管理</h2>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        创建活动
      </el-button>
    </div>

    <el-card class="promotions-card">
      <el-tabs v-model="activeTab">
        <el-tab-pane label="全部" name="" />
        <el-tab-pane label="限时秒杀" name="flashsale" />
        <el-tab-pane label="满减活动" name="fullreduce" />
        <el-tab-pane label="拼团" name="groupon" />
        <el-tab-pane label="新人专享" name="newuser" />
      </el-tabs>

      <el-table :data="filteredPromotions" style="width: 100%">
        <el-table-column prop="name" label="活动名称" min-width="200" />
        <el-table-column prop="type" label="活动类型" width="120">
          <template #default="{ row }">
            <el-tag :type="getTypeTagType(row.type)">{{ getTypeName(row.type) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">
              {{ row.status === 'active' ? '进行中' : '已结束' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="活动时间" width="320">
          <template #default="{ row }">
            <div v-if="row.start_time && row.end_time">
              <div>{{ formatDate(row.start_time) }}</div>
              <div class="time-arrow">↓</div>
              <div>{{ formatDate(row.end_time) }}</div>
            </div>
            <div v-else>永久有效</div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" link @click="editPromotion(row)">编辑</el-button>
            <el-button type="danger" size="small" link @click="deletePromotion(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="editingPromotion ? '编辑活动' : '创建活动'"
      width="600px"
    >
      <el-form :model="form" label-width="100px">
        <el-form-item label="活动名称">
          <el-input v-model="form.name" placeholder="请输入活动名称" />
        </el-form-item>
        <el-form-item label="活动类型">
          <el-select v-model="form.type" placeholder="请选择活动类型" @change="handleTypeChange">
            <el-option label="限时秒杀" value="flashsale" />
            <el-option label="满减活动" value="fullreduce" />
            <el-option label="拼团" value="groupon" />
            <el-option label="新人专享" value="newuser" />
          </el-select>
        </el-form-item>
        <el-form-item label="活动状态">
          <el-select v-model="form.status" placeholder="请选择状态">
            <el-option label="进行中" value="active" />
            <el-option label="未开始" value="inactive" />
            <el-option label="已结束" value="ended" />
          </el-select>
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="form.start_time"
            type="datetime"
            placeholder="选择开始时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="form.end_time"
            type="datetime"
            placeholder="选择结束时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DDTHH:mm:ss"
          />
        </el-form-item>

        <!-- 限时秒杀配置 -->
        <template v-if="form.type === 'flashsale'">
          <el-form-item label="秒杀价格">
            <el-input-number v-model="formConfig.flash_price" :min="0" :precision="2" placeholder="秒杀价格" style="width: 100%;" />
          </el-form-item>
        </template>

        <!-- 满减活动配置 -->
        <template v-if="form.type === 'fullreduce'">
          <el-form-item label="满减金额">
            <div style="display: flex; gap: 10px; align-items: center;">
              <span>满</span>
              <el-input-number v-model="formConfig.min_amount" :min="0" :precision="2" placeholder="最低金额" />
              <span>减</span>
              <el-input-number v-model="formConfig.discount" :min="0" :precision="2" placeholder="优惠金额" />
            </div>
          </el-form-item>
        </template>

        <!-- 拼团配置 -->
        <template v-if="form.type === 'groupon'">
          <el-form-item label="拼团配置">
            <div style="display: flex; gap: 10px; align-items: center;">
              <span>拼团人数:</span>
              <el-input-number v-model="formConfig.group_size" :min="2" placeholder="拼团人数" />
              <span>折扣:</span>
              <el-input-number v-model="formConfig.discount_rate" :min="0.1" :max="1" :step="0.1" placeholder="折扣率" />
            </div>
          </el-form-item>
        </template>

        <!-- 新人专享配置 -->
        <template v-if="form.type === 'newuser'">
          <el-form-item label="新人专享价">
            <el-input-number v-model="formConfig.new_user_price" :min="0" :precision="2" placeholder="新人专享价格" style="width: 100%;" />
          </el-form-item>
        </template>

        <el-form-item label="关联分类">
          <el-input v-model="form.category" placeholder="限定分类，为空表示不限" />
        </el-form-item>
        <el-form-item label="关联商品">
          <el-select v-model="selectedProductIds" multiple placeholder="选择商品，为空表示不限" style="width: 100%;">
            <el-option
              v-for="product in products"
              :key="product.id"
              :label="product.name"
              :value="product.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="savePromotion">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getPromotions, createPromotion, updatePromotion, deletePromotion as deletePromotionApi, getProducts } from '@/api/shopping'

const activeTab = ref('')
const promotions = ref([])
const products = ref([])
const dialogVisible = ref(false)
const editingPromotion = ref(null)
const selectedProductIds = ref([])
const formConfig = ref({
  flash_price: 0,
  min_amount: 0,
  discount: 0,
  group_size: 2,
  discount_rate: 0.8,
  new_user_price: 0
})

const form = ref({
  name: '',
  type: 'flashsale',
  status: 'active',
  start_time: null,
  end_time: null,
  config: '',
  category: '',
  product_ids: ''
})

const filteredPromotions = computed(() => {
  if (!activeTab.value) return promotions.value
  return promotions.value.filter(p => p.type === activeTab.value)
})

async function loadPromotions() {
  try {
    const res = await getPromotions()
    promotions.value = res.data || []
  } catch (e) {
    console.error('Load promotions failed', e)
  }
}

async function loadProducts() {
  try {
    const res = await getProducts()
    products.value = res.data || []
  } catch (e) {
    console.error('Load products failed', e)
  }
}

function handleTypeChange() {
  formConfig.value = {
    flash_price: 0,
    min_amount: 0,
    discount: 0,
    group_size: 2,
    discount_rate: 0.8,
    new_user_price: 0
  }
}

function parseConfig(configStr) {
  if (!configStr) return {}
  try {
    return JSON.parse(configStr)
  } catch (e) {
    return {}
  }
}

function showCreateDialog() {
  editingPromotion.value = null
  form.value = {
    name: '',
    type: 'flashsale',
    status: 'active',
    start_time: null,
    end_time: null,
    config: '',
    category: '',
    product_ids: ''
  }
  formConfig.value = {
    flash_price: 0,
    min_amount: 0,
    discount: 0,
    group_size: 2,
    discount_rate: 0.8,
    new_user_price: 0
  }
  selectedProductIds.value = []
  dialogVisible.value = true
}

function editPromotion(promotion) {
  editingPromotion.value = promotion
  const config = parseConfig(promotion.config)
  form.value = {
    name: promotion.name,
    type: promotion.type,
    status: promotion.status,
    start_time: promotion.start_time,
    end_time: promotion.end_time,
    config: promotion.config,
    category: promotion.category,
    product_ids: promotion.product_ids
  }
  formConfig.value = {
    flash_price: config.flash_price || 0,
    min_amount: config.min_amount || 0,
    discount: config.discount || 0,
    group_size: config.group_size || 2,
    discount_rate: config.discount_rate || 0.8,
    new_user_price: config.new_user_price || 0
  }
  selectedProductIds.value = promotion.product_ids
    ? promotion.product_ids.split(',').map(id => parseInt(id)).filter(id => !isNaN(id))
    : []
  dialogVisible.value = true
}

async function savePromotion() {
  if (!form.value.name) {
    ElMessage.warning('请输入活动名称')
    return
  }
  try {
    const data = { ...form.value }
    data.product_ids = selectedProductIds.value.join(',')

    let config = {}
    switch (form.value.type) {
      case 'flashsale':
        config = { flash_price: Number(formConfig.value.flash_price) || 0 }
        break
      case 'fullreduce':
        config = {
          min_amount: Number(formConfig.value.min_amount) || 0,
          discount: Number(formConfig.value.discount) || 0
        }
        break
      case 'groupon':
        config = {
          group_size: Number(formConfig.value.group_size) || 2,
          discount_rate: Number(formConfig.value.discount_rate) || 0.8
        }
        break
      case 'newuser':
        config = { new_user_price: Number(formConfig.value.new_user_price) || 0 }
        break
    }
    data.config = JSON.stringify(config)
    console.log('Saving promotion with config:', data.config)

    if (editingPromotion.value) {
      await updatePromotion(editingPromotion.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await createPromotion(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadPromotions()
  } catch (e) {
    console.error('Save promotion error:', e)
    ElMessage.error('保存失败')
  }
}

async function deletePromotion(promotion) {
  await ElMessageBox.confirm('确定要删除这个活动吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await deletePromotionApi(promotion.id)
    ElMessage.success('删除成功')
    loadPromotions()
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

function getTypeName(type) {
  const names = {
    flashsale: '限时秒杀',
    fullreduce: '满减活动',
    groupon: '拼团',
    newuser: '新人专享'
  }
  return names[type] || type
}

function getTypeTagType(type) {
  const types = {
    flashsale: 'danger',
    fullreduce: 'success',
    groupon: 'warning',
    newuser: 'primary'
  }
  return types[type] || ''
}

function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

onMounted(() => {
  loadPromotions()
  loadProducts()
})
</script>

<style scoped>
.promotions {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h2 {
  margin: 0;
}

.promotions-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.time-arrow {
  text-align: center;
  color: #999;
  line-height: 1.2;
}
</style>
