<template>
  <div class="h-[calc(100vh-64px)] flex overflow-hidden bg-gray-100">

    <!-- LEFT: CATEGORIES & NAVIGATION (ICON BAR) -->
    <div class="w-20 bg-white border-r flex flex-col items-center py-4 space-y-4">
      <button
        @click="selectedCategory = null"
        :class="{'bg-blue-100 text-blue-600': selectedCategory === null}"
        class="p-3 rounded-xl hover:bg-gray-100 transition"
        title="All Products"
      >
        <div class="text-2xl">🏪</div>
      </button>

      <button
        v-for="cat in categories"
        :key="cat.id"
        @click="selectedCategory = cat.id"
        :class="{'bg-blue-100 text-blue-600': selectedCategory === cat.id}"
        class="p-3 rounded-xl hover:bg-gray-100 transition relative group"
        :title="cat.name"
      >
        <img v-if="cat.image_url" :src="cat.image_url" class="w-8 h-8 rounded object-cover" />
        <div v-else class="text-2xl">📦</div>
      </button>
    </div>

    <!-- CENTER: PRODUCT GRID -->
    <div class="flex-1 flex flex-col min-w-0">
      <!-- Search Bar -->
      <div class="p-4 bg-white border-b flex gap-4">
        <div class="relative flex-1">
          <span class="absolute left-3 top-2.5 text-gray-400">🔍</span>
          <input
            v-model="searchQuery"
            ref="searchInput"
            class="w-full pl-10 pr-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="Search products or scan barcode..."
          />
        </div>
      </div>

      <!-- Grid -->
      <div class="flex-1 p-4 overflow-y-auto">
        <div v-if="loading" class="text-center mt-10 text-gray-500">Loading products...</div>

        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          <div
            v-for="product in filteredProducts"
            :key="product.id"
            @click="addToCart(product)"
            class="bg-white rounded-xl shadow-sm border p-3 cursor-pointer hover:shadow-md transition active:scale-95 flex flex-col h-full"
          >
            <div class="h-32 bg-gray-100 rounded-lg mb-3 overflow-hidden">
               <img v-if="product.image_url" :src="product.image_url" class="w-full h-full object-cover" />
               <div v-else class="w-full h-full flex items-center justify-center text-4xl">🍎</div>
            </div>
            <div class="font-bold text-gray-800 leading-tight mb-1">{{ product.name }}</div>
            <div class="text-xs text-gray-500 mb-auto">{{ product.stock_quantity }} in stock</div>
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
        <div v-for="(item, index) in cart" :key="index" class="flex justify-between items-center bg-gray-50 p-2 rounded">
            <div class="flex-1">
                <div class="font-medium text-sm">{{ item.name }}</div>
                <div class="text-xs text-gray-500">${{ item.price.toFixed(2) }} x {{ item.quantity }}</div>
            </div>
            <div class="flex items-center gap-2">
                <button @click="updateQty(index, -1)" class="w-6 h-6 bg-gray-200 rounded text-gray-600 hover:bg-gray-300">-</button>
                <span class="w-4 text-center text-sm font-bold">{{ item.quantity }}</span>
                <button @click="updateQty(index, 1)" class="w-6 h-6 bg-gray-200 rounded text-gray-600 hover:bg-gray-300">+</button>
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
            class="w-full py-4 rounded-xl font-bold text-lg text-white shadow-lg transition transform active:scale-95"
            :class="cart.length > 0 ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-400 cursor-not-allowed'"
        >
            {{ processing ? 'Processing...' : 'Pay Now' }}
        </button>
      </div>
    </div>

    <!-- New Customer Modal -->
    <div v-if="showNewCustomerModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div class="bg-white p-6 rounded-lg w-96 shadow-xl">
            <h3 class="font-bold text-lg mb-4">Add Customer</h3>
            <input v-model="newCustomer.name" class="w-full border p-2 mb-2 rounded" placeholder="Name" />
            <input v-model="newCustomer.phone" class="w-full border p-2 mb-4 rounded" placeholder="Phone" />
            <div class="flex justify-end gap-2">
                <button @click="showNewCustomerModal=false" class="px-4 py-2 text-gray-600">Cancel</button>
                <button @click="createCustomer" class="px-4 py-2 bg-blue-600 text-white rounded">Save</button>
            </div>
        </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
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
            axios.get('/api/v1/categories/'),
            axios.get('/api/v1/products/')
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
    const existing = cart.value.find(i => i.id === product.id)
    if (existing) {
        existing.quantity++
    } else {
        cart.value.push({ ...product, quantity: 1 })
    }
    // Clear search if it was a barcode scan
    if (searchQuery.value && product.barcode === searchQuery.value) {
        searchQuery.value = ""
    }
}

const updateQty = (index, change) => {
    const item = cart.value[index]
    const newQty = item.quantity + change
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
        const res = await axios.get(`/api/v1/customers/?search=${customerSearch.value}`)
        if (res.data.length > 0) {
            selectedCustomer.value = res.data[0] // Select first match
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
        const res = await axios.post('/api/v1/customers/', newCustomer.value)
        selectedCustomer.value = res.data
        showNewCustomerModal.value = false
        newCustomer.value = { name: "", phone: "" }
    } catch (e) {
        alert("Error creating customer")
    }
}

const processPayment = async () => {
    processing.value = true
    try {
        const orderData = {
            user_id: 1, // Hardcoded staff ID for POS
            customer_id: selectedCustomer.value?.id,
            items: cart.value.map(i => ({ product_id: i.id, quantity: i.quantity })),
            is_takeout: false,
            notes: orderNotes.value
        }

        await axios.post('/api/v1/orders/', orderData)

        alert(`Payment Successful! Total: $${cartTotal.value.toFixed(2)}`)
        cart.value = []
        selectedCustomer.value = null
        orderNotes.value = ""

        // Refresh stock
        fetchData()

    } catch (e) {
        alert("Payment Failed: " + (e.response?.data?.detail || e.message))
    } finally {
        processing.value = false
    }
}

// Global Barcode Listener
const handleGlobalKeydown = (e) => {
    // If user is typing in an input, don't interfere
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) return

    // Focus search input on keypress to catch barcode scanner input (which usually acts as keyboard)
    if (e.key.length === 1 && !e.ctrlKey && !e.metaKey) {
        searchInput.value.focus()
    }
}

onMounted(() => {
    fetchData()
    window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
    window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>
