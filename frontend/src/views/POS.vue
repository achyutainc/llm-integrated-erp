<template>
  <div class="h-screen flex bg-gray-100 overflow-hidden">

    <!-- LEFT: PRODUCTS -->
    <div class="flex-1 flex flex-col p-4 overflow-hidden">
      <!-- Search & Filters -->
      <div class="flex gap-4 mb-4">
        <div class="relative flex-1">
          <input
            v-model="searchQuery"
            ref="searchInput"
            placeholder="Search or Scan Barcode..."
            class="w-full pl-10 pr-4 py-3 rounded-xl border shadow-sm focus:ring-2 focus:ring-blue-500 focus:outline-none"
            autofocus
          />
          <span class="absolute left-3 top-3.5 text-gray-400">🔍</span>
        </div>
        <select v-model="selectedCategory" class="p-3 rounded-xl border shadow-sm bg-white">
          <option :value="null">All Categories</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>

      <!-- Product Grid -->
      <div class="flex-1 overflow-y-auto">
        <div v-if="loading" class="text-center mt-10 text-gray-500">Loading products...</div>

        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          <div
            v-for="product in filteredProducts"
            :key="product.id"
            @click="addToCart(product)"
            class="bg-white rounded-xl shadow-sm border p-3 cursor-pointer hover:shadow-md transition active:scale-95 flex flex-col h-full relative"
            :class="{'opacity-50 pointer-events-none': product.stock_quantity <= 0}"
          >
            <div class="absolute top-2 right-2 bg-red-500 text-white text-xs px-2 py-1 rounded" v-if="product.stock_quantity <= 0">Out of Stock</div>
            <div class="h-32 bg-gray-100 rounded-lg mb-3 overflow-hidden">
               <img v-if="product.image_url" :src="product.image_url" class="w-full h-full object-cover" />
               <div v-else class="w-full h-full flex items-center justify-center text-4xl">🍎</div>
            </div>
            <div class="font-bold text-gray-800 leading-tight mb-1">{{ product.name }}</div>
            <div class="text-xs text-gray-500 mb-auto" :class="{'text-red-500 font-bold': product.stock_quantity < 5}">
                {{ product.stock_quantity }} in stock
            </div>
            <div class="mt-2 font-bold text-blue-600 text-lg">${{ product.price.toFixed(2) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- RIGHT: CART & CHECKOUT -->
    <div class="w-96 bg-white border-l flex flex-col shadow-xl z-10">

      <!-- Customer Selector -->
      <div class="p-4 border-b bg-gray-50">
        <div v-if="!selectedCustomer" class="flex gap-2">
            <input
                v-model="customerSearch"
                placeholder="Customer Phone/Name"
                class="flex-1 p-2 text-sm border rounded"
                @keyup.enter="findCustomer"
            />
            <button @click="findCustomer" class="bg-blue-600 text-white px-3 rounded text-sm">Find</button>
            <button @click="showNewCustomerModal=true" class="bg-green-600 text-white px-3 rounded text-sm">+</button>
        </div>
        <div v-else class="flex justify-between items-center bg-blue-100 p-2 rounded border border-blue-200">
            <div>
                <div class="font-bold text-sm text-blue-900">{{ selectedCustomer.name }}</div>
                <div class="text-xs text-blue-700">Points: {{ selectedCustomer.points }}</div>
            </div>
            <button @click="selectedCustomer = null" class="text-blue-500 hover:text-red-500">✕</button>
        </div>
      </div>

      <!-- Cart Items -->
      <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <div v-if="cart.length === 0" class="text-center text-gray-400 mt-10">
            Cart is empty
        </div>
        <div v-else v-for="(item, index) in cart" :key="index" class="flex justify-between items-center bg-gray-50 p-2 rounded">
            <div class="flex-1">
                <div class="font-medium text-sm">{{ item.name }}</div>
                <div class="text-xs text-gray-500">${{ item.price.toFixed(2) }}</div>
            </div>
            <div class="flex items-center gap-2">
                <button @click="updateQty(index, -1)" class="w-6 h-6 bg-gray-200 rounded text-gray-600 hover:bg-gray-300 flex items-center justify-center">-</button>
                <span class="w-6 text-center text-sm font-bold">{{ item.quantity }}</span>
                <button @click="updateQty(index, 1)" class="w-6 h-6 bg-gray-200 rounded text-gray-600 hover:bg-gray-300 flex items-center justify-center">+</button>
            </div>
            <div class="w-16 text-right font-bold text-sm">
                ${{ (item.price * item.quantity).toFixed(2) }}
            </div>
            <button @click="removeFromCart(index)" class="ml-2 text-red-400 hover:text-red-600">✕</button>
        </div>
      </div>

      <!-- Order Notes -->
      <div class="px-4 py-2 border-t">
        <textarea
            v-model="orderNotes"
            rows="2"
            class="w-full text-sm border rounded p-2 resize-none"
            placeholder="Order notes..."
        ></textarea>
      </div>

      <!-- Totals & Pay -->
      <div class="p-4 bg-gray-50 border-t">
        <div class="flex justify-between mb-2 text-sm text-gray-600">
            <span>Subtotal</span>
            <span>${{ cartTotal.toFixed(2) }}</span>
        </div>
        <div class="flex justify-between mb-4 text-xl font-bold text-gray-900">
            <span>Total</span>
            <span>${{ cartTotal.toFixed(2) }}</span>
        </div>

        <button
            @click="processPayment"
            :disabled="cart.length === 0 || processing"
            class="w-full py-4 rounded-xl font-bold text-lg text-white shadow-lg transition transform active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            :class="cart.length > 0 ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-400'"
        >
            {{ processing ? 'Processing...' : 'Pay Now' }}
        </button>
      </div>
    </div>

    <!-- New Customer Modal -->
    <div v-if="showNewCustomerModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
            <h3 class="font-bold text-lg mb-4">Add Customer</h3>
            <div class="mb-2">
                <label class="block text-sm text-gray-600">Name</label>
                <input v-model="newCustomer.name" class="w-full border p-2 rounded" />
            </div>
            <div class="mb-4">
                <label class="block text-sm text-gray-600">Phone</label>
                <input v-model="newCustomer.phone" class="w-full border p-2 rounded" />
            </div>
            <div class="flex justify-end gap-2">
                <button @click="showNewCustomerModal=false" class="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded">Cancel</button>
                <button @click="createCustomer" class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">Save</button>
            </div>
        </div>
    </div>

    <!-- Receipt Modal -->
    <div v-if="showReceiptModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white p-6 rounded-lg w-80 shadow-xl flex flex-col max-h-[90vh]">
            <div class="text-center mb-4">
                <h3 class="font-bold text-xl">✅ Payment Success</h3>
                <p class="text-sm text-gray-500">Order #{{ lastOrder?.id }}</p>
            </div>

            <div class="flex-1 overflow-y-auto border-t border-b py-2 my-2 text-sm font-mono">
                <div v-for="item in lastOrder?.items" :key="item.id" class="flex justify-between">
                    <span>{{ item.quantity }}x Product #{{ item.product_id }}</span>
                    <span>${{ (item.unit_price * item.quantity).toFixed(2) }}</span>
                </div>
                <div class="flex justify-between font-bold mt-2 pt-2 border-t border-dashed">
                    <span>TOTAL</span>
                    <span>${{ lastOrder?.total_amount.toFixed(2) }}</span>
                </div>
            </div>

            <div class="flex flex-col gap-2 mt-4">
                <button @click="printReceipt" class="bg-gray-200 text-gray-800 py-2 rounded hover:bg-gray-300">🖨️ Print Receipt</button>
                <button @click="closeReceipt" class="bg-blue-600 text-white py-2 rounded hover:bg-blue-700">New Order</button>
            </div>
        </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import axios from 'axios'

// State
const categories = ref([])
const products = ref([])
const cart = ref([])
const selectedCategory = ref(null)
const searchQuery = ref("")
const loading = ref(true)
const processing = ref(false)
const searchInput = ref(null)
const orderNotes = ref("")

// Customer State
const selectedCustomer = ref(null)
const customerSearch = ref("")
const showNewCustomerModal = ref(false)
const newCustomer = ref({ name: "", phone: "" })

// Receipt State
const showReceiptModal = ref(false)
const lastOrder = ref(null)

const API_PREFIX = '/api/v1'

// Computed
const filteredProducts = computed(() => {
    let result = products.value

    if (selectedCategory.value) {
        result = result.filter(p => p.category_id === selectedCategory.value)
    }

    if (searchQuery.value) {
        const q = searchQuery.value.toLowerCase()
        result = result.filter(p =>
            p.name.toLowerCase().includes(q) ||
            (p.barcode && p.barcode.includes(q))
        )
    }
    return result
})

const cartTotal = computed(() => {
    return cart.value.reduce((sum, item) => sum + (item.price * item.quantity), 0)
})

// Methods
const fetchData = async () => {
    try {
        const [catRes, prodRes] = await Promise.all([
            axios.get(`${API_PREFIX}/categories/`),
            axios.get(`${API_PREFIX}/products/`)
        ])
        categories.value = catRes.data
        products.value = prodRes.data
    } catch (e) {
        console.error(e)
    } finally {
        loading.value = false
    }
}

const addToCart = (product) => {
    if (product.stock_quantity <= 0) {
        alert("Item is out of stock!")
        return
    }

    const existingIndex = cart.value.findIndex(i => i.id === product.id)
    if (existingIndex !== -1) {
        // Check stock limit
        if (cart.value[existingIndex].quantity >= product.stock_quantity) {
             alert(`Cannot add more. Only ${product.stock_quantity} in stock.`)
             return
        }
        cart.value[existingIndex].quantity++
    } else {
        cart.value.push({ ...product, quantity: 1 })
    }

    // Clear search if it was a barcode scan match
    if (searchQuery.value && product.barcode === searchQuery.value) {
        searchQuery.value = ""
    }
}

const updateQty = (index, change) => {
    const item = cart.value[index]
    const product = products.value.find(p => p.id === item.id)
    const stock = product ? product.stock_quantity : 9999

    const newQty = item.quantity + change

    if (change > 0 && newQty > stock) {
        alert(`Cannot add more. Only ${stock} in stock.`)
        return
    }

    if (newQty <= 0) {
        cart.value.splice(index, 1)
    } else {
        item.quantity = newQty
    }
}

const removeFromCart = (index) => {
    cart.value.splice(index, 1)
}

const findCustomer = async () => {
    if (!customerSearch.value) return
    try {
        const res = await axios.get(`${API_PREFIX}/customers/?search=${customerSearch.value}`)
        if (res.data.length > 0) {
            selectedCustomer.value = res.data[0]
            customerSearch.value = ""
        } else {
            alert("Customer not found")
        }
    } catch (e) {
        alert("Error finding customer")
    }
}

const createCustomer = async () => {
    try {
        const res = await axios.post(`${API_PREFIX}/customers/`, newCustomer.value)
        selectedCustomer.value = res.data
        showNewCustomerModal.value = false
        newCustomer.value = { name: "", phone: "" }
    } catch (e) {
        alert("Error creating customer: " + e.message)
    }
}

const processPayment = async () => {
    processing.value = true
    try {
        const orderData = {
            user_id: 1,
            customer_id: selectedCustomer.value?.id,
            items: cart.value.map(i => ({ product_id: i.id, quantity: i.quantity })),
            is_takeout: false,
            notes: orderNotes.value
        }

        const res = await axios.post(`${API_PREFIX}/orders/`, orderData)
        lastOrder.value = res.data
        showReceiptModal.value = true

        // Refresh stock immediately
        await fetchData()

    } catch (e) {
        alert("Payment Failed: " + (e.response?.data?.detail || e.message))
    } finally {
        processing.value = false
    }
}

const closeReceipt = () => {
    showReceiptModal.value = false
    cart.value = []
    selectedCustomer.value = null
    orderNotes.value = ""
    lastOrder.value = null
}

const printReceipt = () => {
    window.print()
}

// Global Barcode Listener
const handleGlobalKeydown = (e) => {
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return

    if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
        if (searchInput.value) searchInput.value.focus()
    }
}

// Watch search query for exact barcode match
watch(searchQuery, (newVal) => {
    if (!newVal) return
    const match = products.value.find(p => p.barcode === newVal)
    if (match) {
        addToCart(match)
    }
})

onMounted(() => {
    fetchData()
    window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>
