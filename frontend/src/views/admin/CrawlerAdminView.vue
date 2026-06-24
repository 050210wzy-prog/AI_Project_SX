<template>
  <div>
    <section class="page-head">
      <div>
        <p class="eyebrow">REALTIME WEBSITE CRAWLER</p>
        <h1>官网实时采集</h1>
        <p>维护官网栏目采集源，查看最后采集状态、成功数量、失败原因，并将内容写入官网文章库。</p>
      </div>
      <div class="actions">
        <el-button @click="loadAll">刷新</el-button>
        <el-button type="primary" :loading="runningAll" @click="runAll">采集全部</el-button>
      </div>
    </section>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="16">
        <el-card shadow="never" class="panel">
          <div class="panel-head">
            <h3>采集源状态</h3>
            <el-button type="primary" @click="openSource()">新增采集源</el-button>
          </div>
          <el-table :data="sources" stripe>
            <el-table-column prop="name" label="名称" width="120" />
            <el-table-column prop="channel" label="写入栏目" width="120" />
            <el-table-column label="运行状态" width="120">
              <template #default="{ row }">
                <el-tag :type="sourceType(row)">{{ sourceText(row) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="last_count" label="上次新增" width="90" />
            <el-table-column prop="success_count" label="累计成功" width="90" />
            <el-table-column prop="failed_count" label="失败数" width="80" />
            <el-table-column prop="last_run_at" label="最后采集时间" width="170" />
            <el-table-column prop="latest_message" label="最近信息" min-width="220" show-overflow-tooltip />
            <el-table-column label="启用" width="80">
              <template #default="{ row }">
                <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '停用' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="220" fixed="right">
              <template #default="{ row }">
                <el-button size="small" type="primary" :loading="runningId === row.id" @click="runOne(row)">采集</el-button>
                <el-button size="small" @click="openSource(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="removeSource(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="panel">
          <h3>采集概览</h3>
          <div class="summary-grid">
            <span>采集源</span><b>{{ sources.length }}</b>
            <span>启用</span><b>{{ sources.filter((item) => item.enabled).length }}</b>
            <span>累计成功</span><b>{{ sources.reduce((sum, item) => sum + item.success_count, 0) }}</b>
            <span>失败记录</span><b>{{ sources.reduce((sum, item) => sum + item.failed_count, 0) }}</b>
          </div>
          <el-alert title="建议先用“待审核”状态采集，确认内容格式后再发布。" type="warning" show-icon />
        </el-card>
      </el-col>
    </el-row>

    <el-card shadow="never" class="panel">
      <div class="panel-head">
        <h3>采集记录</h3>
        <el-button @click="$router.push('/admin/website')">进入官网管理审核</el-button>
      </div>
      <el-table :data="records" stripe>
        <el-table-column prop="source_name" label="来源" width="120" />
        <el-table-column prop="title" label="标题" min-width="260" />
        <el-table-column label="状态" width="110">
          <template #default="{ row }">
            <el-tag :type="row.status === '采集失败' ? 'danger' : 'success'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="message" label="信息" min-width="220" show-overflow-tooltip />
        <el-table-column prop="created_at" label="时间" width="190" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button v-if="row.article_id" link type="primary" @click="$router.push(`/article/${row.article_id}`)">查看</el-button>
            <el-button link @click="openUrl(row.article_url)">原文</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑采集源' : '新增采集源'" width="680px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="写入栏目"><el-input v-model="form.channel" /></el-form-item>
        <el-form-item label="列表页"><el-input v-model="form.list_url" /></el-form-item>
        <el-form-item label="基础域名"><el-input v-model="form.base_url" /></el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.publish_status">
            <el-option label="待审核" value="待审核" />
            <el-option label="已发布" value="已发布" />
            <el-option label="草稿" value="草稿" />
          </el-select>
        </el-form-item>
        <el-form-item label="启用"><el-switch v-model="form.enabled" /></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSource">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const sources = ref([])
const records = ref([])
const dialogVisible = ref(false)
const runningAll = ref(false)
const runningId = ref(null)
const form = ref({})

const sourceType = (row) => {
  if (!row.enabled) return 'info'
  if (row.failed_count > 0 && row.latest_status === '采集失败') return 'danger'
  if (row.last_run_at) return 'success'
  return 'warning'
}
const sourceText = (row) => {
  if (!row.enabled) return '已停用'
  if (row.latest_status === '采集失败') return '采集失败'
  if (row.last_run_at) return '运行正常'
  return '未采集'
}

async function loadAll() {
  const [sourceRes, recordRes] = await Promise.all([
    http.get('/admin/crawl/sources'),
    http.get('/admin/crawl/records')
  ])
  sources.value = sourceRes.data
  records.value = recordRes.data
}
function openSource(row = null) {
  form.value = row
    ? { ...row }
    : { name: '', channel: '学校新闻', list_url: 'https://www.acvtc.edu.cn/', base_url: 'https://www.acvtc.edu.cn', enabled: true, publish_status: '待审核' }
  dialogVisible.value = true
}
async function saveSource() {
  if (form.value.id) await http.put(`/admin/crawl/sources/${form.value.id}`, form.value)
  else await http.post('/admin/crawl/sources', form.value)
  ElMessage.success('采集源已保存')
  dialogVisible.value = false
  await loadAll()
}
async function removeSource(row) {
  await ElMessageBox.confirm(`确认删除采集源“${row.name}”？`, '提示')
  await http.delete(`/admin/crawl/sources/${row.id}`)
  ElMessage.success('采集源已删除')
  await loadAll()
}
async function runOne(row) {
  runningId.value = row.id
  try {
    const { data } = await http.post(`/admin/crawl/run/${row.id}`, null, { params: { limit: 8 } })
    ElMessage.success(`${row.name} 采集完成：新增 ${data.created} 条，跳过 ${data.skipped} 条`)
    await loadAll()
  } finally {
    runningId.value = null
  }
}
async function runAll() {
  runningAll.value = true
  try {
    const { data } = await http.post('/admin/crawl/run-all', null, { params: { limit: 8 } })
    const count = data.results.reduce((sum, item) => sum + item.created, 0)
    const errors = data.results.reduce((sum, item) => sum + (item.errors?.length || 0), 0)
    ElMessage.success(`全部采集完成：新增 ${count} 条，失败 ${errors} 项`)
    await loadAll()
  } finally {
    runningAll.value = false
  }
}
function openUrl(url) {
  window.open(url, '_blank')
}

onMounted(loadAll)
</script>
<style scoped>

.page-head,
.panel {
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
.page-head p,
.panel p {
  color: #66716d;
  line-height: 1.8;
}
.actions,
.panel-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}
.panel {
  margin-bottom: 18px;
}
.summary-grid {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 14px;
  margin-bottom: 18px;
}
.summary-grid span {
  color: #66716d;
}
.summary-grid b {
  font-size: 22px;
}
@media (max-width: 760px) {
  .page-head,
  .actions,
  .panel-head {
    display: grid;
  }
}
</style>

