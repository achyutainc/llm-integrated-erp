<template>
  <div class="p-4 border rounded shadow-md bg-white">
    <h2 class="text-xl font-bold mb-4">AI Assistant</h2>
    <div class="h-64 overflow-y-auto mb-4 p-2 bg-gray-100 rounded">
      <div v-for="(msg, index) in messages" :key="index" class="mb-2">
        <span v-if="msg.role === 'user'" class="font-bold text-blue-600">You: </span>
        <span v-else class="font-bold text-green-600">AI: </span>
        <span>{{ msg.content }}</span>
      </div>
      <div v-if="loading" class="italic text-gray-500">AI is thinking...</div>
    </div>
    <div class="flex gap-2">
      <input
        v-model="userInput"
        @keyup.enter="sendMessage"
        class="flex-1 p-2 border rounded"
        placeholder="Ask something (e.g., 'Do we have milk?')"
      />
      <button
        @click="sendMessage"
        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        :disabled="loading"
      >
        Send
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const messages = ref([])
const userInput = ref('')
const loading = ref(false)

const sendMessage = async () => {
  if (!userInput.value.trim()) return

  const text = userInput.value
  messages.value.push({ role: 'user', content: text })
  userInput.value = ''
  loading.value = true

  try {
    // Assuming Vite proxy forwards /ai to the AI service
    const response = await axios.post('/ai/ask', { prompt: text })
    messages.value.push({ role: 'ai', content: response.data.response })
  } catch (error) {
    messages.value.push({ role: 'ai', content: 'Error: ' + (error.response?.data?.detail || error.message) })
  } finally {
    loading.value = false
  }
}
</script>
