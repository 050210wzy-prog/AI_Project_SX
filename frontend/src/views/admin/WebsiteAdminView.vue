<template>
  <div>
    <section class="page-head">
      <div>
        <p class="eyebrow">OFFICIAL WEBSITE CMS</p>
        <h1>官网管理</h1>
        <p>维护栏目、文章、轮播图、知识库和资源文件，让官网内容真正可编辑、可审核、可回滚。</p>
      </div>
      <el-button type="primary" @click="openArticle()">新增文章</el-button>
    </section>

    <el-tabs v-model="tab" @tab-change="loadAll">
      <el-tab-pane label="文章管理" name="articles">
        <el-card shadow="never" class="panel">
          <el-table :data="articles" stripe>
            <el-table-column prop="title" label="标题" min-width="260" />
            <el-table-column prop="channel" label="栏目" width="120" />
            <el-table-column prop="publish_status" label="发布状态" width="100" />
            <el-table-column prop="review_status" label="审核状态" width="100" />
            <el-table-column prop="view_count" label="浏览" width="80" />
            <el-table-column label="操作" width="250" fixed="right">
              <template #default="{ row }">
                <el-button size="small" @click="openArticle(row)">编辑</el-button>
                <el-button size="small" @click="openVersions(row)">版本</el-button>
                <el-button size="small" type="danger" @click="remove('articles', row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="栏目管理" name="channels">
        <el-card shadow="never" class="panel">
          <el-button type="primary" @click="openChannel()">新增栏目</el-button>
          <el-table :data="channels" stripe class="top-table">
            <el-table-column prop="name" label="栏目名称" />
            <el-table-column prop="slug" label="标识" />
            <el-table-column prop="sort_order" label="排序" width="80" />
            <el-table-column label="主导航" width="90">
              <template #default="{ row }"><el-tag>{{ row.is_nav ? '是' : '否' }}</el-tag></template>
            </el-table-column>
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" @click="openChannel(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="remove('channels', row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="轮播图" name="banners">
        <el-card shadow="never" class="panel">
          <el-button type="primary" @click="openBanner()">新增轮播图</el-button>
          <el-table :data="banners" stripe class="top-table">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="image_url" label="图片 URL" min-width="260" />
            <el-table-column prop="sort_order" label="排序" width="80" />
            <el-table-column label="操作" width="180">
              <template #default="{ row }">
                <el-button size="small" @click="openBanner(row)">编辑</el-button>
                <el-button size="small" type="danger" @click="remove('banners', row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="内容审核" name="audit">
        <el-card shadow="never" class="panel">
          <el-table :data="auditArticles" stripe>
            <el-table-column prop="title" label="标题" min-width="260" />
            <el-table-column prop="channel" label="栏目" width="120" />
            <el-table-column prop="review_status" label="审核状态" width="120" />
            <el-table-column label="操作" width="230">
              <template #default="{ row }">
                <el-button size="small" type="success" @click="audit(row, '已发布')">通过发布</el-button>
                <el-button size="small" type="warning" @click="audit(row, '已退回')">退回</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="知识库" name="knowledge">
        <el-card shadow="never" class="panel">
          <el-upload :http-request="uploadKnowledge" :show-file-list="false">
            <el-button type="primary">上传 TXT/MD 知识文档</el-button>
          </el-upload>
          <el-table :data="knowledge" stripe class="top-table">
            <el-table-column prop="filename" label="文件名" />
            <el-table-column prop="category" label="分类" width="120" />
            <el-table-column prop="chunk_count" label="片段数" width="100" />
            <el-table-column prop="created_at" label="上传时间" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="资源库" name="resources">
        <el-card shadow="never" class="panel">
          <el-upload :http-request="uploadResource" :show-file-list="false">
            <el-button type="primary">上传资源文件</el-button>
          </el-upload>
          <el-table :data="resources" stripe class="top-table">
            <el-table-column prop="original_name" label="文件名" />
            <el-table-column prop="file_type" label="类型" width="90" />
            <el-table-column prop="file_size" label="大小" width="100" />
            <el-table-column prop="file_url" label="地址" min-width="240" />
            <el-table-column label="操作" width="160">
              <template #default="{ row }">
                <el-button size="small" @click="copyUrl(row.file_url)">复制</el-button>
                <el-button size="small" type="danger" @click="deleteResource(row.id)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <el-dialog v-model="dialog.visible" :title="dialog.title" width="760px">
      <el-form :model="form" label-width="100px">
        <template v-if="dialog.type === 'articles'">
          <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
          <el-form-item label="栏目"><el-input v-model="form.channel" /></el-form-item>
          <el-form-item label="摘要"><el-input v-model="form.summary" type="textarea" /></el-form-item>
          <el-form-item label="正文"><el-input v-model="form.content" type="textarea" :rows="8" /></el-form-item>
          <el-form-item label="封面图"><el-input v-model="form.cover_url" /></el-form-item>
          <el-form-item label="封面上传">
            <el-upload :http-request="uploadCover" :show-file-list="false">
              <el-button>上传图片</el-button>
            </el-upload>
          </el-form-item>
          <el-form-item label="发布状态">
            <el-select v-model="form.publish_status">
              <el-option label="已发布" value="已发布" />
              <el-option label="草稿" value="草稿" />
            </el-select>
          </el-form-item>
          <el-form-item label="审核状态">
            <el-select v-model="form.review_status">
              <el-option label="草稿" value="草稿" />
              <el-option label="待审核" value="待审核" />
              <el-option label="已发布" value="已发布" />
              <el-option label="已退回" value="已退回" />
            </el-select>
          </el-form-item>
          <el-form-item label="版本备注"><el-input v-model="form.version_note" /></el-form-item>
        </template>

        <template v-if="dialog.type === 'channels'">
          <el-form-item label="栏目名称"><el-input v-model="form.name" /></el-form-item>
          <el-form-item label="栏目标识"><el-input v-model="form.slug" /></el-form-item>
          <el-form-item label="排序"><el-input-number v-model="form.sort_order" /></el-form-item>
          <el-form-item label="主导航"><el-switch v-model="form.is_nav" /></el-form-item>
        </template>

        <template v-if="dialog.type === 'banners'">
          <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
          <el-form-item label="副标题"><el-input v-model="form.subtitle" type="textarea" /></el-form-item>
          <el-form-item label="图片地址"><el-input v-model="form.image_url" /></el-form-item>
          <el-form-item label="链接地址"><el-input v-model="form.link_url" /></el-form-item>
          <el-form-item label="排序"><el-input-number v-model="form.sort_order" /></el-form-item>
          <el-form-item label="启用"><el-switch v-model="form.is_active" /></el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="dialog.visible = false">取消</el-button>
        <el-button type="primary" @click="saveDialog">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="versionDialog" title="文章版本" width="700px">
      <el-table :data="versions" stripe>
        <el-table-column prop="version_note" label="备注" />
        <el-table-column prop="created_at" label="时间" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button size="small" @click="rollback(row)">回滚</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import http from '../../api/http'

const tab = ref('articles')
const articles = ref([])
const channels = ref([])
const banners = ref([])
const knowledge = ref([])
const resources = ref([])
const versions = ref([])
const versionDialog = ref(false)
const currentArticleId = ref(null)
const dialog = ref({ visible: false, title: '', type: '', id: null })
const form = ref({})

const auditArticles = computed(() => articles.value.filter((item) => item.review_status !== '已发布'))

async function loadAll() {
  articles.value = (await http.get('/admin/site/articles')).data
  channels.value = (await http.get('/admin/site/channels')).data
  banners.value = (await http.get('/admin/site/banners')).data
  knowledge.value = (await http.get('/admin/knowledge')).data
  resources.value = (await http.get('/admin/resources')).data
}
function openArticle(row = null) {
  dialog.value = { visible: true, title: row ? '编辑文章' : '新增文章', type: 'articles', id: row?.id }
  form.value = row ? { ...row, version_note: '后台编辑' } : { title: '', channel: '学校新闻', summary: '', content: '', cover_url: '', publish_status: '已发布', review_status: '已发布', source: '学校官网', author: '管理员', version_note: '新增文章' }
}
function openChannel(row = null) {
  dialog.value = { visible: true, title: row ? '编辑栏目' : '新增栏目', type: 'channels', id: row?.id }
  form.value = row ? { ...row } : { name: '', slug: '', sort_order: 20, is_nav: true, is_active: true, channel_type: 'list' }
}
function openBanner(row = null) {
  dialog.value = { visible: true, title: row ? '编辑轮播图' : '新增轮播图', type: 'banners', id: row?.id }
  form.value = row ? { ...row } : { title: '', subtitle: '', image_url: '', link_url: '', sort_order: 10, is_active: true }
}
async function saveDialog() {
  const type = dialog.value.type
  const id = dialog.value.id
  const url = `/admin/site/${type}${id ? `/${id}` : ''}`
  if (id) await http.put(url, form.value)
  else await http.post(url, form.value)
  ElMessage.success('保存成功')
  dialog.value.visible = false
  await loadAll()
}
async function remove(type, id) {
  await ElMessageBox.confirm('确认删除这条数据吗？', '提示')
  await http.delete(`/admin/site/${type}/${id}`)
  ElMessage.success('已删除')
  await loadAll()
}
async function openVersions(row) {
  currentArticleId.value = row.id
  versions.value = (await http.get(`/admin/site/articles/${row.id}/versions`)).data
  versionDialog.value = true
}
async function rollback(row) {
  await http.post(`/admin/site/articles/${currentArticleId.value}/rollback/${row.id}`)
  ElMessage.success('已回滚到选中版本')
  versionDialog.value = false
  await loadAll()
}
async function audit(row, status) {
  await http.post(`/website/articles/${row.id}/audit`, null, { params: { review_status: status } })
  ElMessage.success('审核状态已更新')
  await loadAll()
}
async function uploadKnowledge(options) {
  const data = new FormData()
  data.append('file', options.file)
  await http.post('/admin/knowledge/upload', data)
  ElMessage.success('知识文档已上传并切片')
  await loadAll()
}
async function uploadResource(options) {
  const data = new FormData()
  data.append('file', options.file)
  await http.post('/admin/upload', data)
  ElMessage.success('资源已上传')
  await loadAll()
}
async function uploadCover(options) {
  const data = new FormData()
  data.append('file', options.file)
  const res = await http.post('/admin/upload', data)
  form.value.cover_url = res.data.url
  ElMessage.success('封面已上传')
}
function copyUrl(url) {
  navigator.clipboard?.writeText(url)
  ElMessage.success('地址已复制')
}
async function deleteResource(id) {
  await http.delete(`/admin/resources/${id}`)
  ElMessage.success('资源已删除')
  await loadAll()
}

onMounted(loadAll)
</script>

<style scoped>
.page-head,
.panel {
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
.panel {
  margin-bottom: 18px;
}
.top-table {
  margin-top: 14px;
}
</style>
