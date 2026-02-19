<template>
  <div class="p-6">
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-3xl font-bold">Purchasing & Vendors</h1>
      <div class="flex gap-2">
        <button
            @click="activeTab = 'vendors'"
            class="px-4 py-2 rounded"
            :class="activeTab === 'vendors' ? 'bg-blue-600 text-white' : 'bg-gray-200'"
        >
            Vendors
        </button>
        <button
            @click="activeTab = 'pos'"
            class="px-4 py-2 rounded"
            :class="activeTab === 'pos' ? 'bg-blue-600 text-white' : 'bg-gray-200'"
        >
            Purchase Orders
        </button>
      </div>
    </div>

    <!-- VENDORS TAB -->
    <div v-if="activeTab === 'vendors'">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- Add Vendor Card -->
        <div class="bg-gray-50 border border-dashed border-gray-300 rounded p-6 flex flex-col items-center justify-center cursor-pointer hover:bg-gray-100">
            <span class="text-4xl text-gray-400 mb-2">+</span>
            <span class="font-bold text-gray-500">Add Vendor</span>
        </div>

        <div v-for="vendor in vendors" :key="vendor.id" class="bg-white p-4 rounded shadow border">
            <div class="flex justify-between items-start">
                <h3 class="font-bold text-lg">{{ vendor.name }}</h3>
                <span class="text-xs bg-gray-100 px-2 py-1 rounded">{{ vendor.code }}</span>
            </div>
            <div class="mt-2 text-sm text-gray-600">
                <p>👤 {{ vendor.contact_name || 'No Contact' }}</p>
                <p>✉️ {{ vendor.email || 'No Email' }}</p>
                <p>💳 {{ vendor.payment_terms }}</p>
            </div>
        </div>
      </div>
    </div>

    <!-- PO TAB -->
    <div v-if="activeTab === 'pos'">
      <div class="mb-6 flex gap-4">
        <button class="bg-green-600 text-white px-4 py-2 rounded shadow flex items-center gap-2">
            <span>📷</span> Scan Receipt (AI)
        </button>
        <button class="bg-blue-600 text-white px-4 py-2 rounded shadow">
            + New PO
        </button>
      </div>

      <div class="bg-white rounded shadow overflow-hidden">
        <table class="w-full">
            <thead class="bg-gray-50 border-b">
                <tr>
                    <th class="text-left p-4">ID</th>
                    <th class="text-left p-4">Vendor</th>
                    <th class="text-left p-4">Date</th>
                    <th class="text-left p-4">Status</th>
                    <th class="text-right p-4">Total</th>
                    <th class="text-right p-4">Actions</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="po in purchaseOrders" :key="po.id" class="border-b hover:bg-gray-50">
                    <td class="p-4 font-mono">PO-{{ po.id }}</td>
                    <td class="p-4">{{ getVendorName(po.vendor_id) }}</td>
                    <td class="p-4">{{ po.order_date }}</td>
                    <td class="p-4">
                        <span class="px-2 py-1 rounded text-xs font-bold uppercase"
                            :class="{
                                'bg-yellow-100 text-yellow-700': po.status === 'draft',
                                'bg-green-100 text-green-700': po.status === 'received',
                                'bg-blue-100 text-blue-700': po.status === 'sent'
                            }"
                        >
                            {{ po.status }}
                        </span>
                    </td>
                    <td class="p-4 text-right font-bold">${{ po.total_amount.toFixed(2) }}</td>
                    <td class="p-4 text-right">
                        <button v-if="po.status !== 'received'" @click="receivePO(po.id)" class="text-sm bg-gray-100 px-2 py-1 rounded hover:bg-green-100 text-green-700">
                            Receive
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
        <div v-if="purchaseOrders.length === 0" class="p-8 text-center text-gray-500">
            No Purchase Orders found.
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const activeTab = ref('vendors')
const vendors = ref([])
const purchaseOrders = ref([])

const fetchData = async () => {
    try {
        const [vRes, poRes] = await Promise.all([
            axios.get('/api/v1/vendors/'),
            axios.get('/api/v1/purchase-orders/')
        ])
        vendors.value = vRes.data
        purchaseOrders.value = poRes.data
    } catch (e) {
        console.error(e)
    }
}

const getVendorName = (id) => {
    const v = vendors.value.find(v => v.id === id)
    return v ? v.name : 'Unknown'
}

const receivePO = async (id) => {
    try {
        await axios.post(`/api/v1/purchase-orders/${id}/receive`)
        fetchData() // Refresh
    } catch (e) {
        alert("Error receiving PO: " + (e.response?.data?.detail || e.message))
    }
}

onMounted(() => {
    fetchData()
})
</script>
