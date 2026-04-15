<template>
  <el-card class="product-card" shadow="hover">
    <div class="image-wrapper">
      <img :src="product.image || defaultImage" class="product-image" @error="handleImageError" />
    </div>
    <h3>{{ product.name }}</h3>
    <p class="description">{{ product.description }}</p>
    <div class="price-row">
      <span class="price">¥{{ product.price.toFixed(2) }}</span>
      <span class="stock">库存: {{ product.stock }}</span>
    </div>
    <el-button type="primary" style="width: 100%" @click="$emit('add-to-cart', product)">
      加入购物车
    </el-button>
  </el-card>
</template>

<script setup>
import { ref } from 'vue'

defineProps(['product'])
defineEmits(['add-to-cart'])

const defaultImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDIwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIyMDAiIGhlaWdodD0iMjAwIiBmaWxsPSIjRjVGN0ZGIiLz4KPHBhdGggZD0iTTYwIDEyMEw4NSA4NUwxMTUgMTEwTDE0NSA3NUwxNzAgMTIwSDYwWiIgZmlsbD0iI0Q5RDNEQyIvPgo8Y2lyY2xlIGN4PSI4NSIgY3k9IjgwIiByPSIxNSIgZmlsbD0iI0Q5RDNEQyIvPgo8L3N2Zz4K'

function handleImageError(e) {
  e.target.src = defaultImage
}
</script>

<style scoped>
.product-card {
  margin-bottom: 20px;
}
.image-wrapper {
  width: 100%;
  height: 180px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
  background: #f5f7fa;
}
.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.product-card h3 {
  margin: 10px 0;
  font-size: 16px;
}
.description {
  color: #999;
  font-size: 12px;
  height: 36px;
  overflow: hidden;
}
.price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 10px 0;
}
.price {
  color: #f56c6c;
  font-size: 18px;
  font-weight: bold;
}
.stock {
  color: #999;
  font-size: 12px;
}
</style>
