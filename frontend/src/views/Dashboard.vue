<template>
  <div class="p-6">
    <h1 class="text-3xl font-bold mb-6">Store Dashboard (Staff)</h1>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">

      <!-- Inventory Overview -->
      <div class="bg-white p-4 rounded shadow col-span-1">
        <h2 class="text-xl font-semibold mb-2">Inventory Overview</h2>
        <div v-if="loading" class="text-gray-500">Loading products...</div>
        <ul v-else class="space-y-2 max-h-64 overflow-y-auto">
          <li v-for="product in products" :key="product.id" class="flex justify-between border-b pb-1">
            <span>{{ product.name }}</span>
            <span class="font-mono" :class="{'text-red-500 font-bold': product.stock_quantity < 20}">
              {{ product.stock_quantity }} units
            </span>
          </li>
        </ul>
        <div v-if="error" class="text-red-500 mt-2">{{ error }}</div>
      </div>

      <!-- Expiry Alert (Dynamic) -->
      <div class="bg-red-50 p-4 rounded border border-red-200 col-span-1">
        <h2 class="text-xl font-semibold mb-2 text-red-700">⚠️ Expiry Alerts</h2>
        <div v-if="loadingAlerts" class="text-xs text-red-400">Checking dates...</div>
        <ul v-else-if="alerts.length > 0" class="text-sm space-y-1">
          <li v-for="batch in alerts" :key="batch.id" class="text-red-800">
            • <span class="font-bold">{{ getProductName(batch.product_id) }}</span> ({{ batch.quantity }} units)
            <div class="text-xs ml-2 text-red-600">Expires: {{ batch.expiry_date }}</div>
          </li>
        </ul>
        <div v-else class="text-green-700 text-sm">✅ No items expiring soon.</div>

        <button
          @click="sendPrompt('Check for expiring products')"
          class="mt-4 text-xs bg-white border border-red-300 px-3 py-1 rounded text-red-800 hover:bg-red-50"
        >
          🔍 Analyze with AI
        </button>
      </div>

      <!-- Marketing Summary -->
      <div class="bg-blue-50 p-4 rounded border border-blue-200 col-span-1">
        <h2 class="text-xl font-semibold mb-2 text-blue-700">📣 Marketing</h2>
        <div class="text-sm text-blue-800 mb-2">Upcoming Posts:</div>
        <ul class="text-xs space-y-2 mb-4">
           <li class="bg-white p-2 rounded shadow-sm">
             <span class="font-bold">Instagram</span>: Butter Chicken Special (Tomorrow)
           </li>
        </ul>
        <button
          @click="sendPrompt('Draft a Facebook post about our fresh Ontario Apples')"
          class="text-xs bg-white border border-blue-300 px-3 py-1 rounded text-blue-800 hover:bg-blue-50"
        >
          ✍️ Draft New Post
        </button>
      </div>

      <!-- Staff Guide -->
      <div class="col-span-1 md:col-span-2 lg:col-span-3">
        <StaffGuide @send-prompt="sendPrompt" />
      </div>

      <!-- Chat Interface -->
      <div class="bg-white p-4 rounded shadow col-span-1 md:col-span-2 lg:col-span-3">
        <ChatInterface ref="chatRef" />
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import ChatInterface from '../components/ChatInterface.vue'
import StaffGuide from '../components/StaffGuide.vue'

const products = ref([])
const alerts = ref([])
const loading = ref(true)
const loadingAlerts = ref(true)
const error = ref(null)
const chatRef = ref(null)

const fetchProducts = async () => {
  try {
    const response = await axios.get('/api/v1/products/')
    products.value = response.data
    // After products loaded, check alerts so we can map names
    fetchAlerts()
  } catch (err) {
    error.value = 'Failed to load products: ' + (err.response?.data?.detail || err.message)
    loading.value = false
  }
}

const fetchAlerts = async () => {
    try {
        const response = await axios.get('/api/v1/inventory/alerts?days=7')
        alerts.value = response.data
    } catch (err) {
        console.error("Failed to load alerts", err)
    } finally {
        loadingAlerts.value = false
        loading.value = false
    }
}

const getProductName = (id) => {
    const p = products.value.find(p => p.id === id)
    return p ? p.name : `Product #${id}`
}

const sendPrompt = (text) => {
  if (chatRef.value) {
    chatRef.value.userInput = text
    chatRef.value.sendMessage()
  }
}

onMounted(() => {
  fetchProducts()
})
</script>
