<template>
  <main class="ai-page">
    <section class="ai-hero">
      <div>
        <el-page-header content="交院 AI 助手" @back="$router.push('/')" />
        <p>{{ modeIntro }}</p>
      </div>
      <div class="status-panel">
        <span>{{ assistantMode === 'campus_life' ? '案例 A' : '模型' }}</span>
        <strong>{{ assistantMode === 'campus_life' ? '校园百事通' : 'Spark-X2' }}</strong>
        <small>{{ assistantMode === 'campus_life' ? 'RAG 规则库 + 工具调用' : '优先官方数据，不足时明确提示' }}</small>
      </div>
    </section>

    <section class="chat-shell">
      <aside class="assistant-panel">
        <h2>常用问题</h2>
        <el-segmented v-model="assistantMode" :options="modeOptions" class="mode-switch" />
        <button v-for="item in suggestions" :key="item" type="button" @click="useSuggestion(item)">
          {{ item }}
        </button>

        <div class="digital-human" :class="{ speaking: isSpeaking }">
          <div class="human-avatar" aria-hidden="true">
            <span class="eye left"></span>
            <span class="eye right"></span>
            <span class="mouth"></span>
          </div>
          <div>
            <h3>招生数字人</h3>
            <p>{{ isSpeaking ? '正在为你朗读回答' : '回答完成后自动朗读' }}</p>
          </div>
          <div class="voice-actions">
            <el-switch v-model="voiceEnabled" active-text="朗读" inactive-text="静音" />
            <el-button size="small" @click="replayLastAnswer">重播</el-button>
            <el-button size="small" @click="stopSpeech">停止</el-button>
          </div>
        </div>

        <div class="settings-box">
          <h3>回答模式</h3>
          <label>
            <span>模型平台</span>
            <el-select v-model="provider" size="small">
              <el-option label="讯飞星火 Spark-X2" value="spark" />
              <el-option label="智谱 GLM" value="zhipu" />
              <el-option label="DeepSeek" value="deepseek" />
              <el-option label="OpenAI 兼容" value="openai" />
            </el-select>
          </label>
          <label>
            <span>深度思考</span>
            <el-select v-model="thinking" size="small">
              <el-option label="自动判断" value="auto" />
              <el-option label="强制开启" value="enabled" />
              <el-option label="关闭" value="disabled" />
            </el-select>
          </label>
          <label>
            <span>联网搜索</span>
            <el-switch v-model="webSearch" />
          </label>
          <label v-if="webSearch">
            <span>搜索深度</span>
            <el-select v-model="searchMode" size="small">
              <el-option label="普通" value="normal" />
              <el-option label="深度" value="deep" />
            </el-select>
          </label>
        </div>
      </aside>

      <section class="chat-card">
        <div ref="messageBox" class="message-list">
          <article v-for="(msg, index) in messages" :key="index" :class="['message', msg.role]">
            <div class="avatar">{{ msg.role === 'user' ? '我' : 'AI' }}</div>
            <div class="bubble">
              <pre>{{ msg.content }}</pre>
              <small v-if="msg.confidence">可信度：{{ Math.round(msg.confidence * 100) }}%</small>
              <div v-if="msg.sources?.length" class="sources">
                <b>参考来源</b>
                <p v-for="(source, sIndex) in msg.sources" :key="sIndex">[{{ source.source }}] {{ source.preview }}</p>
              </div>
              <div v-if="msg.role === 'assistant' && msg.conversation_id" class="feedback">
                <el-button size="small" @click="sendFeedback(msg, 'like')">有帮助</el-button>
                <el-button size="small" @click="sendFeedback(msg, 'dislike')">需改进</el-button>
              </div>
            </div>
          </article>
        </div>

        <div class="composer">
          <el-input
            v-model="question"
            type="textarea"
            :rows="4"
            resize="none"
            placeholder="例如：安徽物理 430 分能报哪些专业？人工智能技术应用就业方向是什么？"
            @keydown.enter.exact.prevent="askStream"
          />
          <div class="composer-actions">
            <span>{{ loading ? `${providerLabel} 正在生成回答...` : 'Enter 发送，Shift + Enter 换行' }}</span>
            <div>
              <el-button :loading="loading" @click="ask">普通发送</el-button>
              <el-button type="primary" :loading="loading" @click="askStream">流式发送</el-button>
              <el-button @click="downloadLastReport">导出建议书</el-button>
            </div>
          </div>
        </div>
      </section>
    </section>
  </main>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import http from '../api/http'

const route = useRoute()
const question = ref('')
const loading = ref(false)
const assistantMode = ref('admissions')
const provider = ref('zhipu')
const thinking = ref('auto')
const webSearch = ref(false)
const searchMode = ref('normal')
const messageBox = ref(null)
const voiceEnabled = ref(true)
const isSpeaking = ref(false)
const lastSpokenAnswer = ref('')
const modeOptions = [
  { label: '招生咨询', value: 'admissions' },
  { label: '校园生活', value: 'campus_life' }
]
const admissionsSuggestions = [
  '安徽物理 430 分能报哪些专业？',
  '人工智能技术应用专业就业方向是什么？',
  '对比大数据技术和新能源汽车技术',
  '学校有哪些交通类特色专业？',
  '招生咨询电话和学校地址是什么？'
]
const campusLifeSuggestions = [
  '怎么请病假？',
  '奖学金要多少绩点？',
  '宿舍灯坏了找谁？',
  '一卡通丢了怎么办？',
  '选错了课能退吗？',
  '现在第几周？',
  '绩点计算 85,90,78'
]
const suggestions = computed(() => (assistantMode.value === 'campus_life' ? campusLifeSuggestions : admissionsSuggestions))
const providerLabel = computed(() => {
  const map = {
    spark: '讯飞星火',
    zhipu: '智谱 GLM',
    deepseek: 'DeepSeek',
    openai: 'OpenAI 兼容模型'
  }
  return map[provider.value] || 'AI'
})
const modeIntro = computed(() =>
  assistantMode.value === 'campus_life'
    ? '案例 A：校园生活百事通助手。支持请假、奖学金、报修、一卡通、选课等校园生活 RAG 问答，并提供教学周查询和绩点计算工具。'
    : '接入讯飞星火 Spark-X2，结合本地招生、专业、官网采集数据，为考生、家长和师生提供咨询服务。'
)
const messages = ref([
  {
    role: 'assistant',
    content: '你好，我是安徽交通职业技术学院 AI 助手。你可以问专业、分数、就业方向、招生政策、官网新闻和办事入口。'
  }
])

function payload(q, history) {
  return {
    question: q,
    assistant_mode: assistantMode.value,
    provider: provider.value,
    thinking: thinking.value,
    web_search: webSearch.value,
    search_mode: searchMode.value,
    history
  }
}

function recentHistory() {
  return messages.value.slice(-10).map((m) => ({
    role: m.role === 'user' ? 'user' : 'assistant',
    content: m.content
  }))
}

function scrollBottom() {
  nextTick(() => {
    if (messageBox.value) messageBox.value.scrollTop = messageBox.value.scrollHeight
  })
}

function useSuggestion(text) {
  stopSpeech()
  question.value = text
}

function cleanSpeechText(text) {
  return String(text || '')
    .replace(/\[[^\]]+\]/g, '')
    .replace(/https?:\/\/\S+/g, '')
    .replace(/[#*_`>-]/g, '')
    .replace(/\s+/g, ' ')
    .trim()
}

function speakAnswer(text) {
  const content = cleanSpeechText(text)
  if (!voiceEnabled.value || !content || !('speechSynthesis' in window)) return
  stopSpeech()
  lastSpokenAnswer.value = content
  const utterance = new SpeechSynthesisUtterance(content)
  utterance.lang = 'zh-CN'
  utterance.rate = 1
  utterance.pitch = 1.05
  utterance.volume = 1
  const voices = window.speechSynthesis.getVoices()
  const zhVoice = voices.find((item) => item.lang?.toLowerCase().startsWith('zh')) || voices[0]
  if (zhVoice) utterance.voice = zhVoice
  utterance.onstart = () => {
    isSpeaking.value = true
  }
  utterance.onend = () => {
    isSpeaking.value = false
  }
  utterance.onerror = () => {
    isSpeaking.value = false
  }
  window.speechSynthesis.speak(utterance)
}

function stopSpeech() {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel()
  isSpeaking.value = false
}

function replayLastAnswer() {
  if (lastSpokenAnswer.value) speakAnswer(lastSpokenAnswer.value)
}

async function ask() {
  if (!question.value.trim() || loading.value) return
  const q = question.value.trim()
  const history = recentHistory()
  messages.value.push({ role: 'user', content: q })
  question.value = ''
  loading.value = true
  scrollBottom()
  try {
    const { data } = await http.post('/chat', payload(q, history))
    messages.value.push({
      role: 'assistant',
      content: data.answer,
      confidence: data.confidence,
      sources: data.sources,
      conversation_id: data.conversation_id,
      question: q
    })
    speakAnswer(data.answer)
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || 'AI 助手暂时无法回复，请检查后端和模型配置')
  } finally {
    loading.value = false
    scrollBottom()
  }
}

async function askStream() {
  if (!question.value.trim() || loading.value) return
  const q = question.value.trim()
  const history = recentHistory()
  messages.value.push({ role: 'user', content: q })
  const assistant = { role: 'assistant', content: '', confidence: null, sources: [], conversation_id: null, question: q }
  messages.value.push(assistant)
  question.value = ''
  loading.value = true
  scrollBottom()
  try {
    const res = await fetch('/api/chat/stream', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload(q, history))
    })
    if (!res.ok || !res.body) throw new Error('请求失败')
    const reader = res.body.getReader()
    const decoder = new TextDecoder('utf-8')
    let buffer = ''
    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const parts = buffer.split('\n\n')
      buffer = parts.pop()
      for (const part of parts) {
        const line = part.replace(/^data:\s*/, '')
        if (!line || line === '[DONE]') continue
        const event = JSON.parse(line)
        if (event.type === 'meta') Object.assign(assistant, event.data)
        if (event.type === 'chunk') {
          assistant.content += event.content
          scrollBottom()
        }
      }
    }
    speakAnswer(assistant.content)
  } catch (error) {
    assistant.content = `AI 助手暂时无法回复：${error.message || '请求异常'}`
  } finally {
    loading.value = false
    scrollBottom()
  }
}

async function sendFeedback(msg, sentiment) {
  await http.post('/chat/feedback', {
    conversation_id: msg.conversation_id,
    question: msg.question,
    answer: msg.content,
    sentiment
  })
  ElMessage.success('反馈已提交')
}

async function downloadLastReport() {
  const last = [...messages.value].reverse().find((m) => m.role === 'assistant' && m.content)
  if (!last) return
  const res = await http.post('/admissions/report', { question: last.question || '招生咨询', answer: last.content }, { responseType: 'blob' })
  const url = URL.createObjectURL(res.data)
  const a = document.createElement('a')
  a.href = url
  a.download = '报考建议书.pdf'
  a.click()
  URL.revokeObjectURL(url)
}

onMounted(() => {
  if ('speechSynthesis' in window) window.speechSynthesis.getVoices()
  if (route.query.q) question.value = String(route.query.q)
})

onBeforeUnmount(() => stopSpeech())
</script>

<style scoped>
.ai-page {
  min-height: 100vh;
  padding: 28px min(4vw, 48px) 40px;
  background: #eef4f8;
}
.ai-hero {
  display: grid;
  grid-template-columns: 1fr 260px;
  gap: 20px;
  align-items: stretch;
  margin-bottom: 20px;
}
.ai-hero > div,
.status-panel,
.chat-card,
.assistant-panel {
  background: #ffffff;
  border: 1px solid #dbe6ef;
  box-shadow: 0 18px 42px rgba(0, 54, 96, .08);
}
.ai-hero > div:first-child {
  padding: 24px;
}
.ai-hero p {
  margin: 18px 0 0;
  color: #51616f;
  line-height: 1.8;
}
.status-panel {
  display: grid;
  align-content: center;
  padding: 24px;
  border-left: 5px solid #2e7d32;
}
.status-panel span,
.settings-box h3 {
  color: #c41e3a;
  font-size: 13px;
  font-weight: 900;
}
.status-panel strong {
  margin: 8px 0;
  color: #003b70;
  font-size: 30px;
}
.status-panel small {
  color: #607080;
}
.chat-shell {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 20px;
}
.assistant-panel {
  padding: 22px;
}
.assistant-panel h2 {
  margin: 0 0 16px;
  color: #003b70;
}
.mode-switch {
  width: 100%;
  margin-bottom: 16px;
}
.assistant-panel button {
  width: 100%;
  margin-bottom: 10px;
  padding: 12px;
  border: 1px solid #d7e2ec;
  background: #f8fbfd;
  color: #263747;
  cursor: pointer;
  text-align: left;
  line-height: 1.5;
}
.assistant-panel button:hover {
  border-color: #0066b3;
  color: #0066b3;
}
.digital-human {
  display: grid;
  grid-template-columns: 64px 1fr;
  gap: 12px;
  align-items: center;
  margin: 18px 0 4px;
  padding: 14px;
  border: 1px solid #d7e2ec;
  background:
    radial-gradient(circle at 18% 12%, rgba(216, 255, 79, .28), transparent 34%),
    linear-gradient(135deg, #f7fbff, #f3fff7);
}
.human-avatar {
  position: relative;
  width: 58px;
  height: 58px;
  border-radius: 18px;
  background: linear-gradient(145deg, #0066b3, #2e7d32);
  box-shadow: inset 0 -10px 18px rgba(0, 0, 0, .16), 0 10px 24px rgba(0, 73, 130, .16);
}
.human-avatar::before {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  top: -7px;
  height: 12px;
  border-radius: 999px;
  background: #c41e3a;
}
.eye {
  position: absolute;
  top: 22px;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #ffffff;
}
.eye.left {
  left: 17px;
}
.eye.right {
  right: 17px;
}
.mouth {
  position: absolute;
  left: 22px;
  bottom: 15px;
  width: 14px;
  height: 5px;
  border-radius: 999px;
  background: #ffffff;
  transition: height .18s ease, bottom .18s ease;
}
.digital-human.speaking {
  border-color: rgba(0, 102, 179, .48);
  box-shadow: 0 18px 36px rgba(0, 92, 165, .12);
}
.digital-human.speaking .human-avatar {
  animation: humanPulse 1.1s ease-in-out infinite;
}
.digital-human.speaking .mouth {
  bottom: 12px;
  height: 12px;
  animation: mouthTalk .34s ease-in-out infinite alternate;
}
.digital-human h3 {
  margin: 0;
  color: #003b70;
  font-size: 16px;
}
.digital-human p {
  margin: 4px 0 0;
  color: #607080;
  font-size: 12px;
}
.voice-actions {
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}
.settings-box {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid #e1e9f0;
}
.settings-box label {
  display: grid;
  gap: 8px;
  margin-top: 14px;
  color: #536271;
  font-weight: 700;
}
.chat-card {
  min-height: 680px;
  display: grid;
  grid-template-rows: 1fr auto;
  overflow: hidden;
}
.message-list {
  max-height: calc(100vh - 290px);
  min-height: 470px;
  overflow-y: auto;
  padding: 24px;
}
.message {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr);
  gap: 12px;
  margin-bottom: 18px;
}
.message.user {
  grid-template-columns: minmax(0, 1fr) 42px;
}
.message.user .avatar {
  grid-column: 2;
}
.message.user .bubble {
  grid-column: 1;
  grid-row: 1;
  justify-self: end;
  color: #ffffff;
  background: linear-gradient(135deg, #0066b3, #2e7d32);
}
.avatar {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  color: #ffffff;
  background: #003b70;
  font-weight: 900;
}
.bubble {
  width: min(820px, 100%);
  padding: 16px 18px;
  background: #f7fafc;
  border: 1px solid #dfe9f1;
}
.bubble pre {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: inherit;
  line-height: 1.75;
}
.bubble small {
  display: block;
  margin-top: 10px;
  opacity: .72;
  font-weight: 800;
}
.sources {
  margin-top: 12px;
  padding: 12px;
  background: #eef6ef;
  color: #304050;
}
.sources p {
  margin: 8px 0 0;
  line-height: 1.6;
}
.feedback {
  margin-top: 12px;
}
.composer {
  padding: 18px;
  border-top: 1px solid #dfe9f1;
  background: #ffffff;
}
.composer-actions {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-top: 12px;
  color: #667788;
}
.composer-actions > div {
  display: flex;
  gap: 8px;
}
@media (max-width: 980px) {
  .ai-hero,
  .chat-shell {
    grid-template-columns: 1fr;
  }
  .composer-actions {
    align-items: stretch;
    flex-direction: column;
  }
  .composer-actions > div {
    flex-wrap: wrap;
  }
}
@keyframes humanPulse {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-3px);
  }
}
@keyframes mouthTalk {
  from {
    transform: scaleX(.72);
  }
  to {
    transform: scaleX(1.18);
  }
}
</style>
