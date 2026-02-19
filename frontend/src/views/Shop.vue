<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h1 class="text-4xl font-bold text-orange-600">Taste of Ontario & India</h1>
        <p class="text-gray-600">Fresh local produce & authentic spices delivered to your door.</p>
      </div>
      <div class="text-right">
        <button class="bg-green-600 text-white px-4 py-2 rounded shadow hover:bg-green-700">🛒 Cart (0)</button>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">

      <!-- Product Grid -->
      <div class="lg:col-span-2">
        <h2 class="text-2xl font-bold mb-4 border-b pb-2">Featured Products</h2>
        <div v-if="loading" class="text-center p-8">Loading fresh items...</div>

        <div v-else class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
          <div v-for="product in products" :key="product.id" class="bg-white border rounded shadow-sm hover:shadow-md transition p-4">
            <div class="h-32 bg-gray-100 rounded mb-4 flex items-center justify-center text-4xl">
              🍎
            </div>
            <h3 class="font-bold text-lg">{{ product.name }}</h3>
            <p class="text-gray-500 text-sm mb-2 h-10 overflow-hidden">{{ product.description || 'Fresh item' }}</p>
            <div class="flex justify-between items-center mt-2">
              <span class="font-bold text-green-700">${{ product.price }}</span>
              <button class="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700">Add</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar: Chef AI -->
      <div class="lg:col-span-1">
        <div class="sticky top-4">
          <CustomerChat />

          <div class="mt-8 bg-yellow-50 p-4 rounded border border-yellow-200">
            <h3 class="font-bold text-yellow-800 mb-2">Today's Special</h3>
            <p class="text-sm text-yellow-700">
              Get <strong>Butter Chicken</strong> takeout for only $12.99! Order before 5 PM.
            </p>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import CustomerChat from '../components/CustomerChat.vue'

const products = ref([])
const loading = ref(true)

const fetchProducts = async () => {
  try {
    const response = await axios.get('/api/v1/products/')
    products.value = response.data
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchProducts()
})
</script>
