<template>
  <div class="messages">
    <div class="page-header">
      <h2>消息管理</h2>
      <div class="header-actions">
        <el-badge :value="totalUnreadCount" :hidden="totalUnreadCount === 0" class="unread-badge">
          <el-button @click="refresh">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </el-badge>
      </div>
    </div>

    <div class="messages-container">
      <div class="user-list">
        <div class="list-header">对话用户</div>
        <div
          v-for="userId in conversationUsers"
          :key="userId"
          class="user-item"
          :class="{ active: selectedUserId === userId }"
          @click="selectUser(userId)"
        >
          <div class="user-avatar">{{ (userNames[userId]?.nickname || userNames[userId]?.username || 'U').charAt(0) }}</div>
          <div class="user-info">
            <div class="user-name">用户：{{ userNames[userId]?.nickname || userNames[userId]?.username || userId }}</div>
          </div>
          <el-badge v-if="unreadCounts[userId] > 0" :value="unreadCounts[userId]" class="unread-count" />
        </div>
        <el-empty v-if="conversationUsers.length === 0" description="暂无对话" :image-size="80" />
      </div>

      <div class="chat-area" v-if="selectedUserId">
        <div class="chat-header">
          <span>与用户：{{ userNames[selectedUserId]?.nickname || userNames[selectedUserId]?.username || selectedUserId }} 的对话</span>
        </div>
        <div class="chat-messages" ref="messagesRef">
          <div v-for="msg in messages" :key="msg.id" class="message" :class="msg.from_user_id === currentUser.id ? 'sent' : 'received'">
            <div class="message-content">{{ msg.content }}</div>
            <div class="message-time">{{ formatTime(msg.created_at) }}</div>
          </div>
        </div>
        <div class="chat-input">
          <el-input v-model="inputMessage" placeholder="输入消息..." @keyup.enter="handleSend" />
          <el-button type="primary" @click="handleSend">发送</el-button>
        </div>
      </div>
      <div class="chat-area empty" v-else>
        <el-empty description="请选择一个对话" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { getMessages, sendMessage as sendMessageApi, getConversations, getUnreadCount, markConversationRead } from '@/api/shopping'
import { getUserInfo } from '@/api/user'

const messages = ref([])
const conversationUsers = ref([])
const selectedUserId = ref(null)
const inputMessage = ref('')
const currentUser = ref(null)
const messagesRef = ref(null)
const userNames = ref({})
const unreadCounts = ref({})
let refreshTimer = null

const totalUnreadCount = computed(() => {
  return Object.values(unreadCounts.value).reduce((sum, count) => sum + count, 0)
})

function loadUser() {
  const saved = localStorage.getItem('currentUser')
  if (saved) {
    currentUser.value = JSON.parse(saved)
  }
}

async function loadUserInfo(userId) {
  if (userNames.value[userId]) return
  try {
    const res = await getUserInfo(userId)
    userNames.value[userId] = res.data
  } catch (e) {
    console.error('Load user info failed', e)
  }
}

async function loadUnreadCounts() {
  if (!currentUser.value) return
  try {
    const res = await getUnreadCount(currentUser.value.id)
    // 这里需要后端返回每个用户的未读数量，先简化处理
    // 如果后端只返回总数，我们需要为每个对话加载未读
    if (conversationUsers.value.length > 0) {
      for (const userId of conversationUsers.value) {
        await loadUserUnreadCount(userId)
      }
    }
  } catch (e) {
    console.error('Load unread counts failed', e)
  }
}

async function loadUserUnreadCount(userId) {
  if (!currentUser.value) return
  try {
    const res = await getMessages(currentUser.value.id, userId)
    const msgs = res.data || []
    unreadCounts.value[userId] = msgs.filter(m => m.to_user_id === currentUser.value.id && m.is_read === 0).length
  } catch (e) {
    console.error('Load user unread count failed', e)
  }
}

async function refresh() {
  await loadConversations()
  await loadUnreadCounts()
  if (selectedUserId.value) {
    await loadMessages()
  }
}

async function loadConversations() {
  if (!currentUser.value) return
  try {
    const res = await getConversations(currentUser.value.id)
    conversationUsers.value = res.data || []
    for (const userId of conversationUsers.value) {
      await loadUserInfo(userId)
    }
  } catch (e) {
    console.error('Load conversations failed', e)
  }
}

async function selectUser(userId) {
  selectedUserId.value = userId
  await loadUserInfo(userId)
  await loadMessages()
  // 标记对话为已读
  if (currentUser.value && userId) {
    try {
      await markConversationRead(currentUser.value.id, userId)
      unreadCounts.value[userId] = 0
    } catch (e) {
      console.error('Mark conversation read failed', e)
    }
  }
}

async function loadMessages() {
  if (!currentUser.value || !selectedUserId.value) return
  try {
    const res = await getMessages(currentUser.value.id, selectedUserId.value)
    messages.value = res.data || []
    await nextTick()
    scrollToBottom()
  } catch (e) {
    ElMessage.error('加载消息失败')
  }
}

async function handleSend() {
  if (!inputMessage.value.trim() || !currentUser.value || !selectedUserId.value) return
  try {
    await sendMessageApi({
      from_user_id: currentUser.value.id,
      to_user_id: selectedUserId.value,
      content: inputMessage.value.trim()
    })
    inputMessage.value = ''
    await loadMessages()
  } catch (e) {
    ElMessage.error('发送失败')
  }
}

function scrollToBottom() {
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

function formatTime(time) {
  const date = new Date(time)
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadUser()
  loadConversations()
  // 每3秒自动刷新一次
  refreshTimer = setInterval(() => {
    refresh()
  }, 3000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.messages {
  padding: 20px;
  height: calc(100vh - 140px);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.page-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.unread-badge :deep(.el-badge__content) {
  top: 2px;
  right: 2px;
}

.messages-container {
  display: flex;
  height: 100%;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.user-list {
  width: 260px;
  border-right: 1px solid #eee;
  display: flex;
  flex-direction: column;
}

.list-header {
  padding: 16px 20px;
  font-weight: 600;
  border-bottom: 1px solid #eee;
  background: #fafafa;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  cursor: pointer;
  transition: background 0.3s;
  border-bottom: 1px solid #f5f5f5;
}

.user-item:hover {
  background: #f5f7fa;
}

.user-item.active {
  background: #e6f7ff;
}

.user-avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
  font-weight: 600;
}

.user-info {
  flex: 1;
  min-width: 0;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.unread-count {
  margin-left: auto;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-area.empty {
  justify-content: center;
  align-items: center;
}

.chat-header {
  padding: 16px 20px;
  background: #f5f7fa;
  border-bottom: 1px solid #eee;
  font-size: 15px;
  font-weight: 600;
}

.chat-messages {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
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
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.6;
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
  margin-top: 4px;
}

.message.sent .message-time {
  text-align: right;
}

.chat-input {
  padding: 16px 20px;
  border-top: 1px solid #eee;
  display: flex;
  gap: 12px;
}

.chat-input .el-input {
  flex: 1;
}
</style>
