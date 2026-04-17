<template>
  <div class="customer-service" v-if="currentUser && !isAdmin">
    <div class="chat-window" v-if="showChat">
      <div class="chat-header">
        <span>在线客服</span>
        <el-icon class="close-icon" @click="showChat = false"><Close /></el-icon>
      </div>
      <div class="chat-messages" ref="messagesRef">
        <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.from_user_id === currentUser.id ? 'sent' : 'received'">
          <div class="message-content">{{ msg.content }}</div>
          <div class="message-time">{{ formatTime(msg.created_at) }}</div>
        </div>
      </div>
      <div class="chat-input">
        <el-input v-model="inputMessage" placeholder="输入消息..." @keyup.enter="sendMessage" />
        <el-button type="primary" @click="sendMessage">发送</el-button>
      </div>
    </div>
    <div class="floating-btn" @click="toggleChat" v-else>
      <el-icon :size="32"><Service /></el-icon>
      <div class="unread-badge" v-if="unreadCount > 0">{{ unreadCount }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, nextTick, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { getMessages, sendMessage as sendMessageApi, getUnreadCount, markConversationRead } from '@/api/shopping'

const showChat = ref(false)
const messages = ref([])
const inputMessage = ref('')
const currentUser = ref(null)
const unreadCount = ref(0)
const messagesRef = ref(null)
const adminId = ref(1)

const isAdmin = computed(() => currentUser.value?.role === 'admin')

function loadUser() {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
}

async function loadMessages() {
  if (!currentUser.value) return
  try {
    const res = await getMessages(currentUser.value.id, adminId.value)
    messages.value = res.data || []
    await nextTick()
    scrollToBottom()
    if (messages.value.length > 0) {
      await markConversationRead(currentUser.value.id, adminId.value)
      unreadCount.value = 0
    }
  } catch (e) {
    console.error('Load messages failed', e)
  }
}

async function loadUnreadCount() {
  if (!currentUser.value) return
  try {
    const res = await getUnreadCount(currentUser.value.id)
    unreadCount.value = res.data?.count || 0
  } catch (e) {
    console.error('Load unread count failed', e)
  }
}

async function sendMessage() {
  if (!inputMessage.value.trim() || !currentUser.value) return
  try {
    await sendMessageApi({
      from_user_id: currentUser.value.id,
      to_user_id: adminId.value,
      content: inputMessage.value.trim()
    })
    inputMessage.value = ''
    await loadMessages()
  } catch (e) {
    ElMessage.error('发送失败')
  }
}

function toggleChat() {
  showChat.value = !showChat.value
  if (showChat.value) {
    loadMessages()
  }
}

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

function formatTime(time) {
  const date = new Date(time)
  return date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
}

onMounted(() => {
  loadUser()
  loadUnreadCount()
  setInterval(loadUnreadCount, 10000)
})

watch(() => showChat.value, (val) => {
  if (val) {
    loadMessages()
  }
})
</script>

<style scoped>
.customer-service {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 9999;
}

.floating-btn {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  transition: all 0.3s ease;
  color: white;
  position: relative;
}

.floating-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.unread-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff4d4f;
  color: white;
  font-size: 12px;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 0 6px;
}

.chat-window {
  width: 380px;
  height: 500px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 16px 20px;
  font-size: 16px;
  font-weight: 600;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.close-icon {
  cursor: pointer;
  font-size: 20px;
}

.chat-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  max-width: 70%;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message.sent {
  align-self: flex-end;
}

.message.received {
  align-self: flex-start;
}

.message-content {
  padding: 10px 14px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
}

.message.sent .message-content {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-bottom-right-radius: 4px;
}

.message.received .message-content {
  background: #f5f7fa;
  color: #333;
  border-bottom-left-radius: 4px;
}

.message-time {
  font-size: 11px;
  color: #999;
  margin-top: 2px;
}

.message.sent .message-time {
  text-align: right;
}

.chat-input {
  padding: 12px 16px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
}

.chat-input .el-input {
  flex: 1;
}
</style>
