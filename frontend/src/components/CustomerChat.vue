<template>
  <div class="p-4 border rounded shadow-md bg-orange-50">
    <div class="flex items-center gap-2 mb-4">
      <div class="bg-orange-500 text-white rounded-full p-2 w-10 h-10 flex items-center justify-center font-bold">
        👨‍🍳
      </div>
      <h2 class="text-xl font-bold text-orange-800">Chef AI: Indian Cuisine Expert</h2>
    </div>

    <div class="h-64 overflow-y-auto mb-4 p-2 bg-white rounded border border-orange-200">
      <div v-if="messages.length === 0" class="text-center text-gray-500 mt-4 text-sm">
        Ask me for recipes or ingredients! (e.g. "How to make Biryani?")
      </div>
      <div v-for="(msg, index) in messages" :key="index" class="mb-2">
        <span v-if="msg.role === 'user'" class="font-bold text-gray-700">You: </span>
        <span v-else class="font-bold text-orange-600">Chef: </span>
        <span class="whitespace-pre-wrap">{{ msg.content }}</span>
      </div>
      <div v-if="loading" class="italic text-gray-500">Chef is looking for ingredients...</div>
    </div>

    <div class="flex gap-2">
      <input
        v-model="userInput"
        @keyup.enter="sendMessage"
        class="flex-1 p-2 border border-orange-200 rounded focus:outline-none focus:ring-2 focus:ring-orange-300"
        placeholder="What do you want to cook today?"
      />
      <button
        @click="sendMessage"
        class="bg-orange-500 text-white px-4 py-2 rounded hover:bg-orange-600"
        :disabled="loading"
      >
        Ask Chef
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
    const response = await axios.post('/ai/ask', { prompt: text, mode: 'customer' })
    messages.value.push({ role: 'ai', content: response.data.response })
  } catch (error) {
    messages.value.push({ role: 'ai', content: 'Sorry, I am having trouble checking the pantry right now.' })
  } finally {
    loading.value = false
  }
}
</script>
