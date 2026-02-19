<template>
  <div class="bg-gray-100 p-4 rounded shadow mt-6">
    <h3 class="font-bold mb-2">💡 Quick Staff Actions</h3>
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
      <button
        v-for="(prompt, idx) in staffPrompts"
        :key="idx"
        @click="$emit('send-prompt', prompt.text)"
        class="text-left text-sm p-3 bg-white border border-gray-200 hover:bg-blue-50 hover:border-blue-300 rounded transition-colors shadow-sm"
      >
        <div class="font-semibold text-gray-800">{{ prompt.label }}</div>
        <div class="text-xs text-gray-500 mt-1">{{ prompt.desc }}</div>
      </button>
    </div>
  </div>
</template>

<script setup>
const staffPrompts = [
  { label: "🔍 Check Expiry", desc: "Show items expiring this week", text: "Check for expiring products" },
  { label: "✍️ Draft FB Post", desc: "Create a Facebook post about Apples", text: "Draft a Facebook post about our fresh Ontario Apples" },
  { label: "🥛 Check Milk Stock", desc: "Verify milk quantity", text: "Do we have milk in stock?" },
  { label: "📦 Create Bread Order", desc: "Restock bread (Draft)", text: "Create an order for Bread (Whole Wheat)" }
]
</script>
