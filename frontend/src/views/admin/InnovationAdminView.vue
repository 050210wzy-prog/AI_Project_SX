<template>
  <div>
    <section class="page-head">
      <div>
        <p class="eyebrow">INNOVATION OPS</p>
        <h1>创新中心管理</h1>
        <p>管理 8 项创新功能开关、排序、说明，以及真实系统对接地址和运行检查。</p>
      </div>
      <div class="head-actions">
        <el-button @click="loadAll">刷新</el-button>
        <el-button type="primary" @click="saveAll">保存全部</el-button>
      </div>
    </section>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="15">
        <el-card shadow="never" class="panel">
          <h3>8 项创新功能</h3>
          <el-table :data="features" stripe>
            <el-table-column prop="sort_order" label="排序" width="80">
              <template #default="{ row }">
                <el-input-number v-model="row.sort_order" :min="1" :max="99" size="small" />
              </template>
            </el-table-column>
            <el-table-column prop="title" label="功能名称" min-width="170">
              <template #default="{ row }">
                <el-input v-model="row.title" />
              </template>
            </el-table-column>
            <el-table-column prop="description" label="说明" min-width="260">
              <template #default="{ row }">
                <el-input v-model="row.description" />
              </template>
            </el-table-column>
            <el-table-column label="启用" width="90">
              <template #default="{ row }">
                <el-switch v-model="row.enabled" />
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :xs="24" :lg="9">
        <el-card shadow="never" class="panel">
          <h3>运行检查</h3>
          <div class="health-grid">
            <article v-for="(value, key) in health" :key="key">
              <span>{{ key }}</span>
              <b>{{ value }}</b>
            </article>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="18">
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="panel">
          <h3>真实系统对接</h3>
          <div v-for="item in systemConfigs" :key="item.key" class="config-row">
            <label>{{ item.description || item.key }}</label>
            <el-input v-model="item.value" :placeholder="item.key" />
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :lg="12">
        <el-card shadow="never" class="panel">
          <h3>操作日志</h3>
          <el-timeline>
            <el-timeline-item v-for="item in logs" :key="item.id" :timestamp="item.created_at">
              {{ item.username }} {{ item.action }} {{ item.target }}
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import http from '../../api/http'

const features = ref([])
const systemConfigs = ref([])
const logs = ref([])
const health = ref({})

async function loadAll() {
  const [featureRes, configRes, logRes, healthRes] = await Promise.all([
    http.get('/admin/innovation-configs'),
    http.get('/admin/system-configs'),
    http.get('/admin/operation-logs'),
    http.get('/admin/health-check')
  ])
  features.value = featureRes.data
  systemConfigs.value = configRes.data
  logs.value = logRes.data
  health.value = healthRes.data
}

async function saveAll() {
  await Promise.all([
    ...features.value.map((item) => http.put(`/admin/innovation-configs/${item.feature_key}`, item)),
    ...systemConfigs.value.map((item) => http.put(`/admin/system-configs/${item.key}`, item))
  ])
  ElMessage.success('创新配置已保存')
  await loadAll()
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
.page-head p {
  color: #66716d;
}
.head-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}
.panel {
  margin-bottom: 18px;
}
.health-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}
.health-grid article {
  padding: 16px;
  border: 1px solid #dce5ee;
  background: #f7fafc;
}
.health-grid span {
  display: block;
  color: #66716d;
}
.health-grid b {
  color: #003b70;
  font-size: 24px;
}
.config-row {
  display: grid;
  gap: 8px;
  margin-bottom: 14px;
}
.config-row label {
  color: #003b70;
  font-weight: 800;
}
@media (max-width: 760px) {
  .page-head,
  .head-actions {
    display: grid;
  }
}
</style>
