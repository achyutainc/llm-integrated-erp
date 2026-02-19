<script setup>
import { computed, ref, onMounted } from 'vue'
import Dashboard from './views/Dashboard.vue'
import Shop from './views/Shop.vue'

const routes = {
  '/': Dashboard,
  '/shop': Shop
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
    <nav class="bg-blue-600 text-white p-4 shadow-md">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-2xl font-bold">Local ERP AI</h1>
        <div>
          <a href="#/" class="mr-4 hover:underline">Staff Dashboard</a>
          <a href="#/shop" class="mr-4 hover:underline">Customer Shop</a>
          <button class="bg-blue-700 px-3 py-1 rounded hover:bg-blue-800">Logout</button>
        </div>
      </div>
    </nav>
    <main class="container mx-auto py-8">
      <component :is="currentView" />
    </main>
  </div>
</template>
