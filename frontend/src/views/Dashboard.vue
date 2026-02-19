<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">Store Dashboard</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div class="bg-white p-4 rounded shadow">
        <h2 class="text-xl font-semibold mb-2">Inventory Overview</h2>
        <div v-if="loading" class="text-gray-500">Loading products...</div>
        <ul v-else class="space-y-2">
          <li v-for="product in products" :key="product.id" class="flex justify-between border-b pb-1">
            <span>{{ product.name }}</span>
            <span class="font-mono">{{ product.stock_quantity }} units</span>
          </li>
        </ul>
        <div v-if="error" class="text-red-500 mt-2">{{ error }}</div>
      </div>

      <div class="bg-white p-4 rounded shadow col-span-2">
        <!-- Chat Interface Component -->
        <ChatInterface />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ChatInterface from '../components/ChatInterface.vue'

const products = ref([])
const loading = ref(true)
const error = ref(null)

const fetchProducts = async () => {
  try {
    const response = await axios.get('/api/v1/products/')
    products.value = response.data
  } catch (err) {
    error.value = 'Failed to load products: ' + (err.response?.data?.detail || err.message)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProducts()
})
</script>
