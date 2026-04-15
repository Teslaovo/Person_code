<template>
  <div class="addresses">
    <div class="page-header">
      <h2>收货地址管理</h2>
      <el-button type="primary" @click="showAddDialog">新增地址</el-button>
    </div>

    <el-row :gutter="20">
      <el-col :span="8" v-for="addr in addresses" :key="addr.id">
        <el-card class="address-card">
          <div class="address-info">
            <div class="name-phone">
              <span class="name">{{ addr.name }}</span>
              <span class="phone">{{ addr.phone }}</span>
            </div>
            <div class="address-detail">
              {{ addr.province }}{{ addr.city }}{{ addr.district || '' }}{{ addr.detail }}
            </div>
            <el-tag v-if="addr.is_default === 1" type="success" size="small">默认</el-tag>
          </div>
          <div class="address-actions">
            <el-button link type="primary" @click="showEditDialog(addr)">编辑</el-button>
            <el-button link type="danger" @click="handleDelete(addr.id)">删除</el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="addresses.length === 0" description="暂无收货地址" />

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑地址' : '新增地址'" width="500px">
      <el-form :model="addressForm" :rules="addressRules" ref="addressFormRef" label-width="80px">
        <el-form-item label="收货人" prop="name">
          <el-input v-model="addressForm.name" placeholder="请输入收货人姓名" />
        </el-form-item>
        <el-form-item label="手机号" prop="phone">
          <el-input v-model="addressForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="省份" prop="province">
          <el-input v-model="addressForm.province" placeholder="请输入省份" />
        </el-form-item>
        <el-form-item label="城市" prop="city">
          <el-input v-model="addressForm.city" placeholder="请输入城市" />
        </el-form-item>
        <el-form-item label="区县" prop="district">
          <el-input v-model="addressForm.district" placeholder="请输入区县（可选）" />
        </el-form-item>
        <el-form-item label="详细地址" prop="detail">
          <el-input v-model="addressForm.detail" type="textarea" placeholder="请输入详细地址" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="addressForm.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getAddresses, createAddress, updateAddress, deleteAddress } from '@/api/user'

const addresses = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const addressFormRef = ref(null)
const editingId = ref(null)

const addressForm = reactive({
  name: '',
  phone: '',
  province: '',
  city: '',
  district: '',
  detail: '',
  is_default: false
})

const addressRules = {
  name: [{ required: true, message: '请输入收货人姓名', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入手机号', trigger: 'blur' }],
  province: [{ required: true, message: '请输入省份', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }],
  detail: [{ required: true, message: '请输入详细地址', trigger: 'blur' }]
}

onMounted(() => {
  loadAddresses()
})

async function loadAddresses() {
  const res = await getAddresses()
  addresses.value = res.data || []
}

function showAddDialog() {
  isEdit.value = false
  editingId.value = null
  Object.assign(addressForm, {
    name: '',
    phone: '',
    province: '',
    city: '',
    district: '',
    detail: '',
    is_default: false
  })
  dialogVisible.value = true
}

function showEditDialog(addr) {
  isEdit.value = true
  editingId.value = addr.id
  Object.assign(addressForm, {
    name: addr.name,
    phone: addr.phone,
    province: addr.province,
    city: addr.city,
    district: addr.district || '',
    detail: addr.detail,
    is_default: addr.is_default === 1
  })
  dialogVisible.value = true
}

async function handleSave() {
  await addressFormRef.value?.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await updateAddress(editingId.value, {
        ...addressForm,
        is_default: addressForm.is_default ? 1 : 0
      })
      ElMessage.success('更新成功')
    } else {
      await createAddress({
        ...addressForm,
        is_default: addressForm.is_default ? 1 : 0
      })
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadAddresses()
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定要删除这个地址吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await deleteAddress(id)
    ElMessage.success('删除成功')
    loadAddresses()
  } catch (e) {
    ElMessage.error(e.message || '删除失败')
  }
}
</script>

<style scoped>
.addresses .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.addresses h2 {
  margin: 0;
}

.address-card {
  margin-bottom: 20px;
}

.address-info .name-phone {
  margin-bottom: 8px;
}

.address-info .name {
  font-weight: bold;
  margin-right: 15px;
}

.address-info .phone {
  color: #666;
}

.address-info .address-detail {
  color: #666;
  line-height: 1.6;
  margin-bottom: 10px;
}

.address-actions {
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
  text-align: right;
}
</style>
