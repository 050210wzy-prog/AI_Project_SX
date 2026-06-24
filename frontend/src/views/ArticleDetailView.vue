<template>
  <main class="page">
    <el-page-header content="文章详情" @back="$router.back()" />
    <article v-if="article" class="glass-card detail">
      <el-tag>{{ article.channel }}</el-tag>
      <h1>{{ article.title }}</h1>
      <div class="meta">
        来源：{{ article.source || '学校官网' }}　
        作者：{{ article.author || '管理员' }}　
        日期：{{ article.publish_date || '2026-05-14' }}
      </div>
      <p class="summary">{{ article.summary }}</p>
      <div class="body" v-html="article.content"></div>
      <section v-if="attachments.length" class="attachments">
        <h3>附件下载</h3>
        <el-button v-for="file in attachments" :key="file.id" round @click="download(file)">{{ file.file_name }}</el-button>
      </section>
      <div class="actions">
        <el-button @click="$router.push(`/channel/${encodeURIComponent(article.channel || '学校新闻')}`)">返回栏目</el-button>
        <el-button type="primary" @click="$router.push('/chat')">继续咨询</el-button>
      </div>
    </article>
    <el-empty v-else description="文章加载中或不存在" />
  </main>
</template>

<script setup>
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import http from '../api/http'

const route = useRoute()
const article = ref(null)
const attachments = ref([])

function download(file) {
  if (file.file_url) window.open(file.file_url, '_blank')
  else ElMessage.info('该附件暂无下载地址')
}

onMounted(async () => {
  const { data } = await http.get(`/website/articles/${route.params.id}`)
  article.value = data.article
  attachments.value = data.attachments || []
})
</script>

<style scoped>
.page {
  width: min(980px, calc(100vw - 40px));
  margin: 0 auto;
  padding: 26px 0 60px;
}
.detail {
  margin-top: 24px;
  padding: 34px;
  border-radius: 30px;
}
.detail h1 {
  margin: 18px 0;
  font-size: clamp(36px, 6vw, 72px);
  line-height: 1;
}
.meta {
  color: #667085;
}
.summary {
  margin: 22px 0;
  padding: 16px 18px;
  border-radius: 18px;
  background: #f6f9ef;
  font-weight: 800;
  line-height: 1.8;
}
.body {
  line-height: 2;
  font-size: 16px;
}
.attachments,
.actions {
  margin-top: 28px;
}
.actions {
  display: flex;
  gap: 10px;
}
</style>
