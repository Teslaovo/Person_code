<template>
  <div class="dashboard">
    <div class="page-header">
      <h2>数据统计</h2>
      <el-button type="primary" @click="loadData">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <el-row :gutter="20" class="stats-cards">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card sales-card">
          <div class="stat-icon">
            <el-icon :size="40"><Wallet /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">¥{{ totalSales.toFixed(2) }}</div>
            <div class="stat-label">总销售额</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card orders-card">
          <div class="stat-icon">
            <el-icon :size="40"><DocumentCopy /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalOrders }}</div>
            <div class="stat-label">总订单数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card products-card">
          <div class="stat-icon">
            <el-icon :size="40"><Goods /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ totalProducts }}</div>
            <div class="stat-label">商品数量</div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card conversion-card">
          <div class="stat-icon">
            <el-icon :size="40"><DataLine /></el-icon>
          </div>
          <div class="stat-content">
            <div class="stat-value">{{ conversionRate.toFixed(2) }}%</div>
            <div class="stat-label">转化率</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-section">
      <el-col :xs="24" :lg="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>销售趋势</span>
              <el-radio-group v-model="salesPeriod" size="small" @change="loadSalesStats">
                <el-radio-button label="daily">日</el-radio-button>
                <el-radio-button label="weekly">周</el-radio-button>
                <el-radio-button label="monthly">月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-placeholder">
            <div v-if="salesStats.length > 0" class="sales-stats-list">
              <div v-for="stat in salesStats" :key="stat.period" class="sales-stat-item">
                <div class="stat-date">{{ stat.period }}</div>
                <div class="stat-data">
                  <div class="stat-orders">订单: {{ stat.total_orders }}</div>
                  <div class="stat-sales">销售额: ¥{{ stat.total_sales?.toFixed(2) }}</div>
                  <div class="stat-products">商品: {{ stat.total_products }}</div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无销售数据" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card class="chart-card">
          <template #header>
            <span>商品销售排行</span>
          </template>
          <div class="rank-list">
            <div
              v-for="(item, index) in salesRank"
              :key="item.product_id"
              class="rank-item"
            >
              <div class="rank-number" :class="'rank-' + (index + 1)">{{ index + 1 }}</div>
              <div class="rank-info">
                <div class="rank-name">{{ item.product_name }}</div>
                <div class="rank-stats">
                  销量 {{ item.sales_count }} | 销售额 ¥{{ item.sales_amount?.toFixed(2) }}
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="alerts-section">
      <el-col :xs="24" :lg="12">
        <el-card class="alert-card">
          <template #header>
            <div class="card-header">
              <span>低库存预警</span>
              <el-badge :value="lowStockProducts.length" :hidden="lowStockProducts.length === 0" />
            </div>
          </template>
          <div class="alert-list">
            <div
              v-for="product in lowStockProducts"
              :key="product.id"
              class="alert-item"
            >
              <div class="alert-info">
                <div class="alert-name">{{ product.name }}</div>
                <div class="alert-stock">库存 {{ product.stock }} / 预警线 {{ product.low_stock_threshold }}</div>
              </div>
              <el-progress
                :percentage="Math.min(100, (product.stock / product.low_stock_threshold) * 100)"
                :color="product.stock <= 5 ? '#ff4d4f' : '#faad14'"
                :stroke-width="8"
              />
            </div>
            <el-empty v-if="lowStockProducts.length === 0" description="暂无低库存商品" :image-size="60" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card class="alert-card">
          <template #header>
            <div class="card-header">
              <span>售罄商品</span>
              <el-badge :value="outOfStockProducts.length" :hidden="outOfStockProducts.length === 0" />
            </div>
          </template>
          <div class="alert-list">
            <div
              v-for="product in outOfStockProducts"
              :key="product.id"
              class="alert-item out-of-stock"
            >
              <div class="alert-info">
                <div class="alert-name">{{ product.name }}</div>
                <div class="alert-stock danger">已售罄</div>
              </div>
              <el-tag type="danger">缺货</el-tag>
            </div>
            <el-empty v-if="outOfStockProducts.length === 0" description="暂无售罄商品" :image-size="60" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  getSalesStats,
  getProductSalesRank,
  getLowStockProducts,
  getOutOfStockProducts,
  getProducts,
  getSummaryStats,
  getOrderConversionStats
} from '@/api/shopping'

const salesPeriod = ref('daily')
const salesStats = ref([])
const salesRank = ref([])
const lowStockProducts = ref([])
const outOfStockProducts = ref([])
const allProducts = ref([])

const totalSales = ref(0)
const totalOrders = ref(0)
const totalProducts = ref(0)
const conversionRate = ref(0)

async function loadData() {
  await Promise.all([
    loadSalesStats(),
    loadSalesRank(),
    loadLowStockProducts(),
    loadOutOfStockProducts(),
    loadProducts(),
    loadConversionStats()
  ])
}

async function loadConversionStats() {
  try {
    const res = await getOrderConversionStats()
    if (res.data) {
      conversionRate.value = res.data.conversion_rate || 0
    }
  } catch (e) {
    console.error('Load conversion stats failed', e)
  }
}

async function loadSalesStats() {
  try {
    const [statsRes, summaryRes] = await Promise.all([
      getSalesStats(salesPeriod.value),
      getSummaryStats()
    ])
    salesStats.value = statsRes.data || []
    if (summaryRes.data) {
      totalSales.value = summaryRes.data.total_sales || 0
      totalOrders.value = summaryRes.data.total_orders || 0
      totalProducts.value = summaryRes.data.total_products || 0
    }
  } catch (e) {
    console.error('Load sales stats failed', e)
  }
}

async function loadSalesRank() {
  try {
    const res = await getProductSalesRank(10)
    salesRank.value = res.data || []
  } catch (e) {
    console.error('Load sales rank failed', e)
  }
}

async function loadLowStockProducts() {
  try {
    const res = await getLowStockProducts()
    console.log('Low stock products response:', res)
    lowStockProducts.value = res.data || []
    console.log('Low stock products array:', lowStockProducts.value)
  } catch (e) {
    console.error('Load low stock products failed', e)
  }
}

async function loadOutOfStockProducts() {
  try {
    const res = await getOutOfStockProducts()
    outOfStockProducts.value = res.data || []
  } catch (e) {
    console.error('Load out of stock products failed', e)
  }
}

async function loadProducts() {
  try {
    const res = await getProducts()
    allProducts.value = res.data || []
  } catch (e) {
    console.error('Load products failed', e)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
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

.stats-cards {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.stat-card :deep(.el-card__body) {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
}

.stat-icon {
  width: 72px;
  height: 72px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sales-card .stat-icon {
  background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
  color: #667eea;
}

.orders-card .stat-icon {
  background: linear-gradient(135deg, #409eff20 0%, #66b1ff20 100%);
  color: #409eff;
}

.products-card .stat-icon {
  background: linear-gradient(135deg, #52c41a20 0%, #95de6420 100%);
  color: #52c41a;
}

.conversion-card .stat-icon {
  background: linear-gradient(135deg, #fa8c1620 0%, #ffc53d20 100%);
  color: #fa8c16;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #333;
  line-height: 1.2;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-placeholder {
  min-height: 300px;
}

.sales-stats-list {
  max-height: 300px;
  overflow-y: auto;
}

.sales-stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.sales-stat-item:last-child {
  border-bottom: none;
}

.stat-date {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  min-width: 100px;
}

.stat-data {
  display: flex;
  gap: 20px;
  font-size: 13px;
  color: #666;
}

.stat-orders {
  color: #409eff;
}

.stat-sales {
  color: #67c23a;
  font-weight: 500;
}

.stat-products {
  color: #e6a23c;
}

.rank-list {
  max-height: 400px;
  overflow-y: auto;
}

.rank-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.rank-item:last-child {
  border-bottom: none;
}

.rank-number {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  background: #f5f7fa;
  color: #666;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #fff;
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e8e8e8 100%);
  color: #fff;
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #daa06d 100%);
  color: #fff;
}

.rank-info {
  flex: 1;
  min-width: 0;
}

.rank-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.rank-stats {
  font-size: 12px;
  color: #999;
}

.alerts-section {
  margin-bottom: 24px;
}

.alert-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  margin-bottom: 20px;
}

.alert-list {
  max-height: 350px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.alert-item:last-child {
  border-bottom: none;
}

.alert-info {
  flex: 1;
}

.alert-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 6px;
}

.alert-stock {
  font-size: 13px;
  color: #999;
}

.alert-stock.danger {
  color: #ff4d4f;
  font-weight: 500;
}
</style>
