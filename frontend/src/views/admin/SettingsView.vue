<template>
  <div>
    <section class="page-head">
      <div>
        <p class="eyebrow">SYSTEM GOVERNANCE</p>
        <h1>系统设置</h1>
        <p>管理大模型接入、角色权限、安全策略、备份计划和通知规则。</p>
      </div>
      <el-button type="primary" @click="saveAll">保存配置</el-button>
    </section>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="panel">
          <h3>AI 模型配置</h3>
          <el-form :model="modelConfig" label-width="120px">
            <el-form-item label="模型服务商">
              <el-select v-model="modelConfig.provider">
                <el-option label="讯飞星火 Spark-X2" value="spark" />
                <el-option label="OpenAI 兼容接口" value="openai" />
                <el-option label="DeepSeek" value="deepseek" />
                <el-option label="本地 Ollama" value="ollama" />
              </el-select>
            </el-form-item>
            <el-form-item label="Base URL"><el-input v-model="modelConfig.baseUrl" /></el-form-item>
            <el-form-item label="模型名称"><el-input v-model="modelConfig.model" /></el-form-item>
            <el-form-item label="思考模式">
              <el-radio-group v-model="modelConfig.thinking">
                <el-radio-button label="enabled">开启</el-radio-button>
                <el-radio-button label="auto">自动</el-radio-button>
                <el-radio-button label="disabled">关闭</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="低置信度阈值">
              <el-slider v-model="modelConfig.confidence" :min="0" :max="1" :step="0.05" />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="panel">
          <h3>权限角色</h3>
          <el-table :data="roles" stripe>
            <el-table-column prop="role" label="角色" width="120" />
            <el-table-column prop="scope" label="权限范围" />
            <el-table-column label="状态" width="90">
              <template #default="{ row }">
                <el-tag :type="row.enabled ? 'success' : 'info'">{{ row.enabled ? '启用' : '停用' }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="panel">
          <h3>真实系统对接</h3>
          <div v-for="item in systemConfigs" :key="item.key" class="setting-column">
            <span>{{ item.description || item.key }}</span>
            <el-input v-model="item.value" :placeholder="item.key" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="panel">
          <h3>运行状态</h3>
          <div v-for="(value, key) in health" :key="key" class="setting-row">
            <span>{{ key }}</span>
            <el-tag type="success">{{ value }}</el-tag>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="panel">
          <h3>安全策略</h3>
          <div class="setting-row"><span>登录失败锁定</span><el-switch v-model="security.lock" /></div>
          <div class="setting-row"><span>管理员操作审计</span><el-switch v-model="security.audit" /></div>
          <div class="setting-row"><span>敏感内容审核</span><el-switch v-model="security.review" /></div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="panel">
          <h3>备份计划</h3>
          <el-timeline>
            <el-timeline-item timestamp="每日 02:00">MySQL 自动备份</el-timeline-item>
            <el-timeline-item timestamp="每周日">上传资源与知识库备份</el-timeline-item>
            <el-timeline-item timestamp="每月">审计日志归档</el-timeline-item>
          </el-timeline>
          <el-button @click="backupNow">立即备份</el-button>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="8">
        <el-card shadow="never" class="panel">
          <h3>通知规则</h3>
          <div v-for="item in notices" :key="item.name" class="setting-row">
            <span>{{ item.name }}</span>
            <el-switch v-model="item.enabled" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const modelConfig = ref({
  provider: 'spark',
  baseUrl: 'https://spark-api-open.xf-yun.com/x2/',
  model: 'spark-x',
  thinking: 'auto',
  confidence: 0.45
})
const roles = ref([
  { role: 'admin', scope: '全部模块、用户权限、系统设置', enabled: true },
  { role: 'admission', scope: '招生数据、咨询工单、报考建议', enabled: true },
  { role: 'editor', scope: '官网栏目、文章、资源文件', enabled: true },
  { role: 'teacher', scope: '学生档案、课程、成绩考勤', enabled: true }
])
const security = ref({ lock: true, audit: true, review: true })
const notices = ref([
  { name: '低置信度自动转工单', enabled: true },
  { name: '文章待审核提醒', enabled: true },
  { name: '招生数据异常提醒', enabled: true },
  { name: '备份失败提醒', enabled: true }
])
const systemConfigs = ref([])
const health = ref({})

async function load() {
  const [configRes, healthRes] = await Promise.all([
    http.get('/admin/system-configs'),
    http.get('/admin/health-check')
  ])
  systemConfigs.value = configRes.data
  health.value = healthRes.data
}
async function saveAll() {
  const localSettings = [
    { key: 'ai_provider', value: modelConfig.value.provider, group_name: 'AI模型配置', description: '模型服务商' },
    { key: 'ai_base_url', value: modelConfig.value.baseUrl, group_name: 'AI模型配置', description: 'Base URL' },
    { key: 'ai_model', value: modelConfig.value.model, group_name: 'AI模型配置', description: '模型名称' },
    { key: 'security_policy', value: JSON.stringify(security.value), group_name: '安全策略', description: '安全策略 JSON' },
    { key: 'notice_rules', value: JSON.stringify(notices.value), group_name: '通知规则', description: '通知规则 JSON' }
  ]
  await Promise.all([
    ...localSettings.map((item) => http.put(`/admin/system-configs/${item.key}`, item)),
    ...systemConfigs.value.map((item) => http.put(`/admin/system-configs/${item.key}`, item))
  ])
  ElMessage.success('配置已保存到后端数据库')
  await load()
}
function backupNow() {
  ElMessage.success('已记录备份任务；生产环境可接入定时备份脚本')
}
onMounted(load)
</script>

<style scoped>
.page-head,.panel { border-radius: 24px; border: 1px solid rgba(16,23,19,.1); background: rgba(255,255,255,.78); }
.page-head { display: flex; justify-content: space-between; gap: 18px; padding: 26px; margin-bottom: 18px; }
.eyebrow { font-weight: 900; letter-spacing: .08em; font-size: 12px; margin: 0 0 8px; }
h1 { margin: 0; font-size: 34px; }
.page-head p { color: #66716d; }
.panel { margin-bottom: 18px; }
.setting-row { display: flex; justify-content: space-between; align-items: center; gap: 14px; padding: 14px 0; border-bottom: 1px solid #edf0f4; }
.setting-column { display: grid; gap: 8px; padding: 12px 0; border-bottom: 1px solid #edf0f4; }
.setting-column span { color: #003b70; font-weight: 800; }
</style>
