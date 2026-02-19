<script setup>
import Dashboard from './views/Dashboard.vue'
</script>

<template>
  <div class="min-h-screen bg-gray-50 text-gray-900">
    <nav class="bg-blue-600 text-white p-4 shadow-md">
      <div class="container mx-auto flex justify-between items-center">
        <h1 class="text-2xl font-bold">Local ERP AI</h1>
        <div>
          <span class="mr-4">Welcome, User</span>
          <button class="bg-blue-700 px-3 py-1 rounded hover:bg-blue-800">Logout</button>
        </div>
      </div>
    </nav>
    <main class="container mx-auto py-8">
      <Dashboard />
    </main>
  </div>
</template>

<style>
/* Global styles if needed */
</style>
