<template>
  <div class="products">
    <div class="page-header">
      <h2>商品管理</h2>
      <el-button type="primary" @click="showAddDialog">添加商品</el-button>
    </div>

    <el-table :data="products" stripe>
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column label="图片" width="100">
        <template #default="{ row }">
          <img v-if="row.image" :src="row.image" class="product-thumb" />
        </template>
      </el-table-column>
      <el-table-column prop="name" label="商品名称" />
      <el-table-column prop="description" label="描述" show-overflow-tooltip />
      <el-table-column prop="price" label="价格" width="120">
        <template #default="{ row }">¥{{ row.price.toFixed(2) }}</template>
      </el-table-column>
      <el-table-column prop="stock" label="库存" width="100" />
      <el-table-column label="操作" width="200">
        <template #default="{ row }">
          <el-button link type="primary" @click="showEditDialog(row)">编辑</el-button>
          <el-button link type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑商品' : '添加商品'" width="600px">
      <el-form :model="productForm" :rules="productRules" ref="productFormRef" label-width="100px">
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="productForm.name" placeholder="请输入商品名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="productForm.description" type="textarea" placeholder="请输入商品描述" />
        </el-form-item>
        <el-form-item label="价格" prop="price">
          <el-input-number v-model="productForm.price" :min="0" :precision="2" placeholder="价格" style="width: 100%" />
        </el-form-item>
        <el-form-item label="图片">
          <el-tabs v-model="imageTab">
            <el-tab-pane label="输入URL" name="url">
              <el-input v-model="productForm.image" placeholder="请输入图片URL" />
            </el-tab-pane>
            <el-tab-pane label="上传图片" name="upload">
              <el-upload
                class="image-uploader"
                :show-file-list="false"
                :before-upload="beforeUpload"
                :http-request="handleUpload"
                accept="image/*"
              >
                <img v-if="productForm.image" :src="productForm.image" class="image-preview" />
                <el-icon v-else class="image-uploader-icon"><Plus /></el-icon>
              </el-upload>
              <div class="upload-tip">支持 jpg、png、gif 格式，建议尺寸 400x400</div>
            </el-tab-pane>
          </el-tabs>
        </el-form-item>
        <el-form-item label="库存" prop="stock">
          <el-input-number v-model="productForm.stock" :min="0" placeholder="库存" style="width: 100%" />
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
import { Plus } from '@element-plus/icons-vue'
import { getProducts, createProduct, updateProduct, deleteProduct, uploadProductImage } from '@/api/shopping'

const products = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const saving = ref(false)
const uploading = ref(false)
const productFormRef = ref(null)
const editingId = ref(null)
const imageTab = ref('url')

const productForm = reactive({
  name: '',
  description: '',
  price: 0,
  image: '',
  stock: 0
})

const productRules = {
  name: [{ required: true, message: '请输入商品名称', trigger: 'blur' }],
  price: [{ required: true, message: '请输入价格', trigger: 'blur' }],
  stock: [{ required: true, message: '请输入库存', trigger: 'blur' }]
}

onMounted(() => {
  loadProducts()
})

async function loadProducts() {
  const res = await getProducts()
  products.value = res.data || []
}

function showAddDialog() {
  isEdit.value = false
  editingId.value = null
  imageTab.value = 'url'
  Object.assign(productForm, {
    name: '',
    description: '',
    price: 0,
    image: '',
    stock: 0
  })
  dialogVisible.value = true
}

function showEditDialog(product) {
  isEdit.value = true
  editingId.value = product.id
  imageTab.value = product.image ? 'url' : 'upload'
  Object.assign(productForm, {
    name: product.name,
    description: product.description || '',
    price: product.price,
    image: product.image || '',
    stock: product.stock
  })
  dialogVisible.value = true
}

function beforeUpload(file) {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

async function handleUpload({ file }) {
  uploading.value = true
  try {
    const res = await uploadProductImage(file)
    productForm.image = res.data.url
    ElMessage.success('图片上传成功')
  } catch (e) {
    ElMessage.error(e.message || '图片上传失败')
  } finally {
    uploading.value = false
  }
}

async function handleSave() {
  await productFormRef.value?.validate()
  saving.value = true
  try {
    if (isEdit.value) {
      await updateProduct(editingId.value, productForm)
      ElMessage.success('更新成功')
    } else {
      await createProduct(productForm)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    loadProducts()
  } catch (e) {
    ElMessage.error(e.message || '操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(id) {
  await ElMessageBox.confirm('确定要删除这个商品吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
  try {
    await deleteProduct(id)
    ElMessage.success('删除成功')
    loadProducts()
  } catch (e) {
    ElMessage.error(e.message || '删除失败')
  }
}
</script>

<style scoped>
.products .page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.products h2 {
  margin: 0;
}

.product-thumb {
  width: 60px;
  height: 60px;
  object-fit: cover;
  border-radius: 4px;
}

.image-uploader {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  transition: border-color 0.3s;
  width: 178px;
  height: 178px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.image-uploader:hover {
  border-color: #409eff;
}

.image-uploader-icon {
  font-size: 28px;
  color: #8c939d;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.upload-tip {
  margin-top: 8px;
  font-size: 12px;
  color: #999;
}
</style>
