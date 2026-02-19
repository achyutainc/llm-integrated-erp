<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const products = ref([])
const alerts = ref([])
const showAdjustModal = ref(false)
const showHistoryModal = ref(false)
const selectedProduct = ref(null)
const moves = ref([])

const adjustment = ref({
    quantity_change: 0,
    reason: ''
})

const API_PREFIX = '/api/v1'

const fetchProducts = async () => {
    try {
        const res = await axios.get(`${API_PREFIX}/products/`)
        products.value = res.data
    } catch (e) {
        console.error("Failed to load products", e)
    }
}

const fetchAlerts = async () => {
    try {
        const res = await axios.get(`${API_PREFIX}/inventory/alerts`)
        alerts.value = res.data
    } catch (e) {
        console.error("Failed to load alerts", e)
    }
}

const openAdjustModal = (product) => {
    selectedProduct.value = product
    adjustment.value = { quantity_change: 0, reason: '' }
    showAdjustModal.value = true
}

const submitAdjustment = async () => {
    if (!selectedProduct.value) return
    try {
        await axios.post(`${API_PREFIX}/inventory/adjust`, {
            product_id: selectedProduct.value.id,
            quantity_change: parseInt(adjustment.value.quantity_change),
            reason: adjustment.value.reason
        })
        showAdjustModal.value = false
        fetchProducts() // Refresh stock
    } catch (e) {
        alert("Adjustment failed: " + (e.response?.data?.detail || e.message))
    }
}

const viewHistory = async (product) => {
    selectedProduct.value = product
    try {
        const res = await axios.get(`${API_PREFIX}/inventory/moves?product_id=${product.id}`)
        moves.value = res.data
        showHistoryModal.value = true
    } catch (e) {
        console.error("Failed to load history", e)
    }
}

onMounted(() => {
    fetchProducts()
    fetchAlerts()
})
</script>

<template>
    <div class="p-6 bg-white rounded-lg shadow-md">
        <h2 class="text-2xl font-bold mb-6 flex justify-between items-center">
            <span>📦 Inventory Management</span>
            <button class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 text-sm">
                + New Product
            </button>
        </h2>

        <!-- Alerts Section -->
        <div v-if="alerts.length > 0" class="mb-8 bg-yellow-50 p-4 rounded-lg border border-yellow-200">
            <h3 class="text-lg font-semibold text-yellow-800 mb-2">⚠️ Expiry Alerts</h3>
            <ul class="list-disc list-inside text-yellow-700">
                <li v-for="batch in alerts" :key="batch.id">
                    Product #{{ batch.product_id }} (Qty: {{ batch.quantity }}) expires on {{ batch.expiry_date }}
                </li>
            </ul>
        </div>

        <!-- Product Table -->
        <div class="overflow-x-auto">
            <table class="w-full text-left border-collapse">
                <thead>
                    <tr class="bg-gray-100 text-gray-600 text-sm uppercase tracking-wider">
                        <th class="p-3 border-b">ID</th>
                        <th class="p-3 border-b">Product</th>
                        <th class="p-3 border-b text-right">Stock</th>
                        <th class="p-3 border-b text-right">Price</th>
                        <th class="p-3 border-b text-center">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="p in products" :key="p.id" class="hover:bg-gray-50 border-b last:border-0">
                        <td class="p-3 text-gray-500">#{{ p.id }}</td>
                        <td class="p-3 font-medium">{{ p.name }}</td>
                        <td class="p-3 text-right font-bold" :class="{'text-red-500': p.stock_quantity <= 5, 'text-green-600': p.stock_quantity > 5}">
                            {{ p.stock_quantity }}
                        </td>
                        <td class="p-3 text-right">${{ p.price.toFixed(2) }}</td>
                        <td class="p-3 flex justify-center gap-2">
                            <button @click="openAdjustModal(p)" class="text-blue-600 hover:text-blue-800 text-sm px-2 py-1 border border-blue-200 rounded hover:bg-blue-50">
                                Adjust
                            </button>
                            <button @click="viewHistory(p)" class="text-gray-600 hover:text-gray-800 text-sm px-2 py-1 border border-gray-200 rounded hover:bg-gray-50">
                                History
                            </button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>

        <!-- Adjustment Modal -->
        <div v-if="showAdjustModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-lg shadow-xl w-full max-w-md p-6">
                <h3 class="text-xl font-bold mb-4">Adjust Stock: {{ selectedProduct?.name }}</h3>
                <div class="space-y-4">
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Quantity Change</label>
                        <input type="number" v-model="adjustment.quantity_change" class="w-full border rounded p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none" placeholder="+10 or -5">
                        <p class="text-xs text-gray-500 mt-1">Use negative values to remove stock.</p>
                    </div>
                    <div>
                        <label class="block text-sm font-medium text-gray-700 mb-1">Reason</label>
                        <input type="text" v-model="adjustment.reason" class="w-full border rounded p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none" placeholder="e.g. Spoilage, Found, Correction">
                    </div>
                </div>
                <div class="mt-6 flex justify-end gap-3">
                    <button @click="showAdjustModal = false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">Cancel</button>
                    <button @click="submitAdjustment" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Save Adjustment</button>
                </div>
            </div>
        </div>

        <!-- History Modal -->
        <div v-if="showHistoryModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div class="bg-white rounded-lg shadow-xl w-full max-w-2xl p-6 h-3/4 flex flex-col">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold">Stock History: {{ selectedProduct?.name }}</h3>
                    <button @click="showHistoryModal = false" class="text-gray-400 hover:text-gray-600 text-2xl">&times;</button>
                </div>

                <div class="overflow-y-auto flex-1 border rounded">
                    <table class="w-full text-left text-sm">
                        <thead class="bg-gray-50 sticky top-0">
                            <tr>
                                <th class="p-2 border-b">Date</th>
                                <th class="p-2 border-b">Type</th>
                                <th class="p-2 border-b text-right">Change</th>
                                <th class="p-2 border-b">Reference</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="m in moves" :key="m.id" class="border-b last:border-0 hover:bg-gray-50">
                                <td class="p-2 text-gray-600">{{ new Date(m.date).toLocaleString() }}</td>
                                <td class="p-2 capitalize">
                                    <span :class="{
                                        'px-2 py-0.5 rounded text-xs font-semibold': true,
                                        'bg-green-100 text-green-800': m.quantity > 0,
                                        'bg-red-100 text-red-800': m.quantity < 0
                                    }">{{ m.move_type }}</span>
                                </td>
                                <td class="p-2 text-right font-mono font-bold" :class="{'text-green-600': m.quantity > 0, 'text-red-600': m.quantity < 0}">
                                    {{ m.quantity > 0 ? '+' : ''}}{{ m.quantity }}
                                </td>
                                <td class="p-2 text-gray-500 truncate max-w-xs" :title="m.reference">{{ m.reference }}</td>
                            </tr>
                            <tr v-if="moves.length === 0">
                                <td colspan="4" class="p-4 text-center text-gray-400">No history found.</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div class="mt-4 text-right">
                    <button @click="showHistoryModal = false" class="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300">Close</button>
                </div>
            </div>
        </div>
    </div>
</template>
