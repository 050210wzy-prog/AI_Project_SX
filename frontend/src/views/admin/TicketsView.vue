<template>
  <div>
    <section class="page-head">
      <div>
        <p class="eyebrow">SERVICE DESK</p>
        <h1>咨询工单</h1>
        <p>集中处理招生 AI 低置信度问题、考生咨询、人工答复与知识库反哺。</p>
      </div>
      <el-button type="primary" @click="load">刷新工单</el-button>
    </section>

    <el-row :gutter="16" class="stats">
      <el-col :xs="12" :md="6" v-for="item in statCards" :key="item.label">
        <el-card shadow="never" class="stat-card">
          <span>{{ item.label }}</span>
          <b>{{ item.value }}</b>
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="panel">
      <div class="toolbar">
        <el-input v-model="keyword" clearable placeholder="搜索标题、问题、联系方式" />
        <el-select v-model="status" clearable placeholder="工单状态">
          <el-option label="待处理" value="待处理" />
          <el-option label="已处理" value="已处理" />
        </el-select>
      </div>
      <el-table :data="filteredTickets" stripe>
        <el-table-column prop="title" label="标题" min-width="220" />
        <el-table-column prop="category" label="类型" width="120" />
        <el-table-column label="优先级" width="100">
          <template #default="{ row }">
            <el-tag :type="row.priority === '高' ? 'danger' : 'info'">{{ row.priority || '普通' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '已处理' ? 'success' : 'warning'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="contact" label="联系方式" width="150" />
        <el-table-column prop="created_at" label="创建时间" width="190" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="openReply(row)">回复</el-button>
            <el-button size="small" @click="preview(row)">查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="工单回复" width="760px">
      <el-descriptions :column="1" border>
        <el-descriptions-item label="标题">{{ current?.title }}</el-descriptions-item>
        <el-descriptions-item label="问题">{{ current?.question }}</el-descriptions-item>
        <el-descriptions-item label="联系方式">{{ current?.contact || '未填写' }}</el-descriptions-item>
      </el-descriptions>
      <el-input v-model="answer" class="reply-box" type="textarea" :rows="7" placeholder="填写人工回复，提交后可反哺知识库" />
      <el-checkbox v-model="feedKnowledge">将回复内容反哺知识库，提升 AI 下次回答质量</el-checkbox>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReply">提交回复</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const tickets = ref([])
const dialogVisible = ref(false)
const current = ref(null)
const answer = ref('')
const feedKnowledge = ref(true)
const keyword = ref('')
const status = ref('')

const filteredTickets = computed(() => {
  const key = keyword.value.trim()
  return tickets.value.filter((item) => {
    const hitKey = !key || [item.title, item.question, item.contact].some((value) => (value || '').includes(key))
    const hitStatus = !status.value || item.status === status.value
    return hitKey && hitStatus
  })
})
const statCards = computed(() => [
  { label: '全部工单', value: tickets.value.length },
  { label: '待处理', value: tickets.value.filter((item) => item.status === '待处理').length },
  { label: '已处理', value: tickets.value.filter((item) => item.status === '已处理').length },
  { label: '知识库反哺', value: tickets.value.filter((item) => item.answer).length }
])

async function load() {
  tickets.value = (await http.get('/admin/tickets')).data
}
function openReply(row) {
  current.value = row
  answer.value = row.answer || ''
  dialogVisible.value = true
}
function preview(row) {
  ElMessageBox.alert(row.question, row.title)
}
async function submitReply() {
  await http.post(`/admin/tickets/${current.value.id}/reply`, { answer: answer.value, feed_knowledge: feedKnowledge.value })
  ElMessage.success('已回复，知识库已更新')
  dialogVisible.value = false
  await load()
}

onMounted(load)
</script>

<style scoped>
.page-head,
.panel,
.stat-card {
  border-radius: 24px;
  border: 1px solid rgba(16, 23, 19, .1);
  background: rgba(255,255,255,.78);
}
.page-head {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  padding: 26px;
  margin-bottom: 18px;
}
.eyebrow {
  font-weight: 900;
  letter-spacing: .08em;
  font-size: 12px;
  margin: 0 0 8px;
}
h1 {
  margin: 0;
  font-size: 34px;
}
.page-head p {
  color: #66716d;
}
.stats {
  margin-bottom: 18px;
}
.stat-card span {
  color: #66716d;
}
.stat-card b {
  display: block;
  font-size: 34px;
  margin-top: 8px;
}
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 14px;
}
.toolbar .el-input {
  max-width: 380px;
}
.reply-box {
  margin: 16px 0 8px;
}
</style>
