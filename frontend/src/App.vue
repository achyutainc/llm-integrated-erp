<script setup>
import { computed, ref, onMounted } from 'vue'
import Dashboard from './views/Dashboard.vue'
import Shop from './views/Shop.vue'
import POS from './views/POS.vue'
import Purchasing from './views/Purchasing.vue'
import Inventory from './views/Inventory.vue'

const routes = {
  '/': Dashboard,
  '/shop': Shop,
  '/pos': POS,
  '/purchasing': Purchasing,
  '/inventory': Inventory
}

const currentPath = ref(window.location.hash)

onMounted(() => {
    window.addEventListener('hashchange', () => {
        currentPath.value = window.location.hash
    })
})

const currentView = computed(() => {
  return routes[currentPath.value.slice(1) || '/'] || Dashboard
})
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <nav class="bg-blue-600 text-white px-4 py-3 shadow-md">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-2xl font-bold flex items-center gap-2">
            🏪 Local ERP AI
        </h1>
        <div class="flex items-center gap-6">
          <a href="#/" class="hover:text-blue-100 transition" :class="{'font-bold underline': currentPath === '' || currentPath === '#/'}">
            Dashboard
          </a>
          <a href="#/inventory" class="hover:text-blue-100 transition" :class="{'font-bold underline': currentPath === '#/inventory'}">
            Inventory
          </a>
          <a href="#/pos" class="hover:text-blue-100 transition" :class="{'font-bold underline': currentPath === '#/pos'}">
            Point of Sale
          </a>
          <a href="#/purchasing" class="hover:text-blue-100 transition" :class="{'font-bold underline': currentPath === '#/purchasing'}">
            Purchasing
          </a>
          <a href="#/shop" class="hover:text-blue-100 transition" :class="{'font-bold underline': currentPath === '#/shop'}">
            Online Shop
          </a>
          <button class="bg-blue-700 px-3 py-1 rounded hover:bg-blue-800 transition">Logout</button>
        </div>
      </div>
    </nav>
    <main class="container mx-auto py-6">
      <component :is="currentView" />
    </main>
  </div>
</template>
