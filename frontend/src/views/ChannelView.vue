<template>
  <site-shell :breadcrumbs="breadcrumbs">
    <section class="container channel-hero">
      <span>{{ channel.en }}</span>
      <h1>{{ channel.title }}</h1>
      <p>{{ channel.intro }}</p>
      <div class="subnav">
        <button v-for="item in channel.children" :key="item" type="button" @click="jump(item)">
          {{ item }}
        </button>
      </div>
    </section>

    <section class="container content-layout">
      <aside class="side-nav">
        <h2>{{ channel.title }}</h2>
        <button v-for="item in channel.children" :key="item" type="button" @click="jump(item)">
          {{ item }}
        </button>
      </aside>

      <div class="main-content">
        <template v-if="channelName === '学校概况'">
          <section-card title="学校简介">
            <p>安徽交通职业技术学院始建于1956年，围绕交通强国、交通强省建设需求，长期服务综合交通运输行业和区域经济社会发展。</p>
            <p>学校坚持“立足交通、服务行业、面向社会”的办学定位，突出“路、海、空、轨、车、邮、智”现代综合交通专业集群建设，培养高素质技术技能人才。</p>
          </section-card>
          <section-card title="历史沿革">
            <ol class="timeline">
              <li v-for="item in history" :key="item.year"><b>{{ item.year }}</b><span>{{ item.text }}</span></li>
            </ol>
          </section-card>
          <section-card title="现任领导">
            <div class="leader-grid">
              <article v-for="item in leaders" :key="item.name">
                <b>{{ item.name }}</b>
                <span>{{ item.role }}</span>
                <p>{{ item.desc }}</p>
              </article>
            </div>
          </section-card>
        </template>

        <template v-else-if="channelName === '院系设置'">
          <section-card title="院系设置">
            <div class="college-grid">
              <article v-for="college in colleges" :key="college.name" @click="router.push(`/college/${encodeURIComponent(college.name)}`)">
                <h3>{{ college.name }}</h3>
                <p>{{ college.desc }}</p>
                <span>{{ college.majors }}</span>
              </article>
            </div>
          </section-card>
        </template>

        <template v-else-if="channelName === '招生就业'">
          <section-card title="招生信息">
            <div class="admission-grid">
              <article v-for="item in admissionBlocks" :key="item.title" @click="router.push(`/service/${encodeURIComponent(item.title)}`)">
                <h3>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
              </article>
            </div>
          </section-card>
          <section-card title="报考参考">
            <table class="info-table">
              <tbody>
                <tr><th>普通高考招生</th><td>招生简章、专业目录、招生计划、录取规则</td></tr>
                <tr><th>定向军士招生</th><td>提前批次政策、体检政审、报考流程</td></tr>
                <tr><th>联合培养本科</th><td>专升本联合培养政策、培养方案、毕业要求</td></tr>
                <tr><th>历年分数线</th><td>按年份、专业、科类查询最低分、最高分和位次参考</td></tr>
              </tbody>
            </table>
          </section-card>
        </template>

        <template v-else>
          <section-card :title="channel.title">
            <p>{{ channel.intro }}</p>
            <div class="feature-list">
              <article v-for="item in channel.children" :key="item" @click="jump(item)">
                <h3>{{ item }}</h3>
                <p>{{ item }}相关内容可由后台持续发布和维护。</p>
              </article>
            </div>
          </section-card>
        </template>

        <section-card title="最新发布">
          <el-input v-model="keyword" placeholder="在本栏目搜索标题、摘要和正文" clearable @change="load" />
          <div v-if="articles.length" class="article-list">
            <article v-for="item in articles" :key="item.id || item.title" @click="openArticle(item)">
              <time>{{ item.publish_date || '2026-05-20' }}</time>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
            </article>
          </div>
          <el-empty v-else description="本栏目暂无后台发布内容，已展示内置栏目资料" />
        </section-card>
      </div>
    </section>
  </site-shell>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SiteShell from '../components/SiteShell.vue'
import http from '../api/http'

const route = useRoute()
const router = useRouter()
const keyword = ref(String(route.query.keyword || ''))
const remoteArticles = ref([])
const channelName = computed(() => String(route.params.name || '学校概况'))
const breadcrumbs = computed(() => [{ label: channelName.value }])

const channels = {
  学校概况: {
    title: '学校概况',
    en: 'About ACVTC',
    intro: '集中展示学校简介、历史沿革、现任领导、机构设置、校园地图和学校标识。',
    children: ['学校简介', '历史沿革', '现任领导', '机构设置', '校园地图', '学校标识']
  },
  院系设置: {
    title: '院系设置',
    en: 'Schools',
    intro: '展示二级学院、专业设置、师资队伍、实训条件和学院动态。',
    children: ['土木建筑学院', '汽车工程学院', '轨道交通学院', '航运工程学院', '航空与低空经济学院', '人工智能学院', '经济管理学院', '人文社科学院']
  },
  招生就业: {
    title: '招生就业',
    en: 'Admissions',
    intro: '发布招生简章、专业目录、历年分数、报考指南、就业服务和校企招聘信息。',
    children: ['招生信息', '就业信息网', '专业目录', '历年分数', '助学政策', '征兵（定向军士）专栏']
  },
  教学科研: {
    title: '教学科研',
    en: 'Teaching & Research',
    intro: '展示专业建设、课程建设、实训基地、科研成果、技能竞赛和教学名师。',
    children: ['专业建设', '课程建设', '实训基地', '科研成果', '技能竞赛', '教学名师']
  },
  校园文化: {
    title: '校园文化',
    en: 'Culture',
    intro: '展示校训校风、校史馆、校园活动、社团风采、志愿者服务和交院人物。',
    children: ['校训校风', '校史馆', '校园活动', '社团风采', '志愿者服务', '交院人物']
  },
  国际交流: {
    title: '国际交流',
    en: 'International',
    intro: '发布国际合作项目、留学生教育、境外交流学习和外事新闻。',
    children: ['国际合作项目', '留学生教育', '境外交流学习', '外事新闻']
  },
  信息服务: {
    title: '信息服务',
    en: 'Services',
    intro: '提供通知公告、办事指南、信息公开、校历、常用系统导航和网络服务。',
    children: ['通知公告', '办事指南', '信息公开', '校历', '常用系统导航', '网络服务']
  }
}
const channel = computed(() => channels[channelName.value] || channels.信息服务)

const history = [
  { year: '1956', text: '安徽交通学校创立。' },
  { year: '1958', text: '升格为安徽交通学院（本科）。' },
  { year: '1988', text: '安徽大学交通分校设立。' },
  { year: '2001', text: '合并组建安徽交通职业技术学院。' },
  { year: '2008', text: '成为省级示范高职院校。' },
  { year: '2014', text: '建成国家骨干高职院校。' },
  { year: '2019', text: '立项安徽省技能型高水平大学建设单位。' }
]
const leaders = [
  { name: '杨菲铃', role: '党委书记', desc: '主持学校党委全面工作。' },
  { name: '孙晓雷', role: '党委副书记、校长', desc: '主持学校行政全面工作。' }
]
const colleges = [
  { name: '土木建筑学院', desc: '聚焦道桥、建筑、检测等专业方向。', majors: '道路与桥梁工程技术 / 建筑工程技术 / 土木工程检测技术' },
  { name: '汽车工程学院', desc: '服务新能源汽车和智能网联汽车产业链。', majors: '新能源汽车技术 / 汽车检测与维修 / 智能网联汽车技术' },
  { name: '轨道交通学院', desc: '面向城市轨道车辆运用、运营管理和通信信号。', majors: '城市轨道车辆应用技术 / 城市轨道交通运营管理' },
  { name: '航运工程学院', desc: '建设航海技术、轮机工程技术等特色专业。', majors: '航海技术 / 轮机工程技术' },
  { name: '航空与低空经济学院', desc: '面向民航服务、飞机维修和无人机应用。', majors: '民航运输服务 / 飞机机电设备维修 / 无人机应用技术' },
  { name: '人工智能学院', desc: '聚焦大数据、人工智能和智能交通技术。', majors: '人工智能技术应用 / 大数据技术 / 智能交通技术' },
  { name: '经济管理学院', desc: '服务现代物流、邮政快递和财经管理。', majors: '现代物流管理 / 邮政快递运营管理 / 大数据与会计' },
  { name: '人文社科学院', desc: '支撑通识教育、人文素养和社会服务。', majors: '公共基础课程 / 人文素质教育' }
]
const admissionBlocks = [
  { title: '招生信息', desc: '普通高考、分类考试、提前批次和联合培养招生信息。' },
  { title: '历年分数', desc: '查询近年录取分数线、位次参考和专业热度。' },
  { title: '招生简章', desc: '查看招生章程、录取规则、收费标准和联系方式。' },
  { title: '报考指南', desc: '面向考生和家长提供报考流程、专业选择和志愿填报建议。' }
]
const articles = computed(() => remoteArticles.value)

function jump(item) {
  const college = colleges.find((row) => row.name === item)
  if (college) router.push(`/college/${encodeURIComponent(item)}`)
  else router.push(`/service/${encodeURIComponent(item)}`)
}
function openArticle(item) {
  if (item.id) router.push(`/article/${item.id}`)
  else router.push(`/service/${encodeURIComponent(item.title)}`)
}
async function load() {
  try {
    const { data } = await http.get('/website/articles', { params: { channel: channelName.value, keyword: keyword.value } })
    remoteArticles.value = Array.isArray(data) ? data : []
  } catch {
    remoteArticles.value = []
  }
}

const SectionCard = defineComponent({
  props: { title: String },
  setup(props, { slots }) {
    return () => h('section', { class: 'section-card' }, [h('h2', props.title), h('div', slots.default?.())])
  }
})

onMounted(load)
watch(() => [route.params.name, route.query.keyword], () => {
  keyword.value = String(route.query.keyword || '')
  load()
})
</script>

<style scoped>
.container {
  width: min(1180px, calc(100vw - 40px));
  margin: 0 auto;
}
.channel-hero {
  margin-top: 22px;
  padding: 48px 0 36px;
  border-bottom: 1px solid #dce5ee;
}
.channel-hero span,
.section-card > h2::before {
  color: #2e7d32;
}
.channel-hero h1 {
  margin: 10px 0 12px;
  color: #003b70;
  font-size: clamp(38px, 6vw, 64px);
}
.channel-hero p {
  width: min(820px, 100%);
  color: #5f6c78;
  line-height: 1.8;
}
.subnav {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 20px;
}
.subnav button,
.side-nav button {
  border: 1px solid #bfd0de;
  background: #ffffff;
  color: #0066b3;
  padding: 10px 13px;
  cursor: pointer;
  font-weight: 800;
}
.content-layout {
  display: grid;
  grid-template-columns: 240px 1fr;
  gap: 34px;
  padding: 36px 0 72px;
}
.side-nav {
  align-self: start;
  position: sticky;
  top: 18px;
  background: #ffffff;
  border-left: 4px solid #0066b3;
  padding: 18px;
}
.side-nav h2 {
  margin: 0 0 12px;
  color: #003b70;
}
.side-nav button {
  width: 100%;
  display: block;
  text-align: left;
  margin-top: 8px;
}
.main-content {
  display: grid;
  gap: 22px;
}
.section-card {
  background: #ffffff;
  border: 1px solid #dce5ee;
  padding: 26px;
}
.section-card > h2 {
  margin: 0 0 18px;
  color: #003b70;
  font-size: 28px;
}
.section-card > h2::before {
  content: "";
  display: inline-block;
  width: 5px;
  height: 24px;
  margin-right: 10px;
  vertical-align: -4px;
  background: #2e7d32;
}
.section-card p {
  color: #5f6c78;
  line-height: 1.9;
}
.timeline {
  margin: 0;
  padding: 0;
  list-style: none;
}
.timeline li {
  display: grid;
  grid-template-columns: 96px 1fr;
  gap: 18px;
  padding: 14px 0;
  border-bottom: 1px solid #edf1f5;
}
.timeline b {
  color: #c41e3a;
}
.leader-grid,
.college-grid,
.admission-grid,
.feature-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.leader-grid article,
.college-grid article,
.admission-grid article,
.feature-list article,
.article-list article {
  border: 1px solid #dce5ee;
  padding: 18px;
  cursor: pointer;
}
.leader-grid article {
  cursor: default;
}
.college-grid h3,
.admission-grid h3,
.feature-list h3,
.article-list h3 {
  margin: 0 0 8px;
  color: #1d2b39;
}
.college-grid span {
  color: #0066b3;
  font-weight: 800;
}
.info-table {
  width: 100%;
  border-collapse: collapse;
}
.info-table th,
.info-table td {
  border: 1px solid #dce5ee;
  padding: 14px;
  text-align: left;
}
.info-table th {
  width: 180px;
  color: #003b70;
  background: #f5f7fa;
}
.article-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}
.article-list time {
  color: #c41e3a;
  font-weight: 900;
}
@media (max-width: 820px) {
  .content-layout,
  .leader-grid,
  .college-grid,
  .admission-grid,
  .feature-list {
    grid-template-columns: 1fr;
  }
  .side-nav {
    position: static;
  }
}

.channel-hero {
  position: relative;
  margin-top: 24px;
  padding: 62px 52px 46px;
  overflow: hidden;
  border: 1px solid #dce5ee;
  border-bottom: 4px solid #0066b3;
  background:
    linear-gradient(110deg, rgba(0, 59, 112, .94), rgba(0, 102, 179, .78) 46%, rgba(46, 125, 50, .72)),
    url("https://www.acvtc.edu.cn/images/nybanner_new.jpg") center / cover;
  color: #ffffff;
}
.channel-hero::after {
  content: "";
  position: absolute;
  right: -90px;
  bottom: -120px;
  width: 360px;
  height: 360px;
  border: 54px solid rgba(255, 255, 255, .12);
  border-radius: 50%;
}
.channel-hero > * {
  position: relative;
  z-index: 1;
}
.channel-hero span {
  color: #d9f0de;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
}
.channel-hero h1 {
  color: #ffffff;
}
.channel-hero p {
  color: rgba(255, 255, 255, .88);
  font-size: 18px;
}
.subnav button {
  border-color: rgba(255, 255, 255, .42);
  background: rgba(255, 255, 255, .12);
  color: #ffffff;
}
.subnav button:hover {
  background: #ffffff;
  color: #0066b3;
}
.content-layout {
  gap: 38px;
}
.side-nav,
.section-card {
  box-shadow: 0 18px 44px rgba(0, 54, 96, .07);
}
.side-nav {
  border: 1px solid #dce5ee;
  border-top: 5px solid #0066b3;
  border-left: 1px solid #dce5ee;
}
.side-nav button {
  border-color: transparent;
  border-bottom: 1px solid #edf1f5;
}
.side-nav button:hover {
  background: #edf4f8;
  border-color: #cbddea;
}
.section-card {
  position: relative;
  overflow: hidden;
}
.section-card::after {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 4px;
  background: linear-gradient(90deg, #0066b3, #2e7d32);
}
.leader-grid article,
.college-grid article,
.admission-grid article,
.feature-list article,
.article-list article {
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.leader-grid article:hover,
.college-grid article:hover,
.admission-grid article:hover,
.feature-list article:hover,
.article-list article:hover {
  transform: translateY(-4px);
  border-color: #9cc4df;
  box-shadow: 0 16px 34px rgba(0, 52, 91, .1);
}
.timeline li {
  position: relative;
  padding-left: 12px;
}
.timeline li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 20px;
  width: 6px;
  height: 6px;
  background: #2e7d32;
}
.info-table th {
  border-left: 4px solid #0066b3;
}
@media (max-width: 820px) {
  .channel-hero {
    padding: 42px 24px 34px;
  }
}

.channel-hero {
  box-shadow: 0 24px 70px rgba(0, 54, 96, .14);
}
.channel-hero h1 {
  text-shadow: 0 10px 28px rgba(0, 0, 0, .18);
}
.content-layout {
  align-items: start;
}
.side-nav {
  border-radius: 2px;
}
.side-nav h2 {
  border-bottom: 1px solid #edf1f5;
  padding-bottom: 12px;
}
.side-nav button {
  position: relative;
  padding-left: 18px;
}
.side-nav button::before {
  content: "";
  position: absolute;
  left: 3px;
  top: 50%;
  width: 6px;
  height: 6px;
  background: #2e7d32;
  transform: translateY(-50%);
}
.section-card {
  border-radius: 2px;
}
.section-card > h2 {
  letter-spacing: .03em;
}
.leader-grid article,
.college-grid article,
.admission-grid article,
.feature-list article,
.article-list article {
  border-radius: 2px;
}
.college-grid article {
  min-height: 152px;
}
.college-grid article::after,
.admission-grid article::after,
.feature-list article::after {
  content: "查看详情";
  display: inline-block;
  margin-top: 12px;
  color: #0066b3;
  font-weight: 900;
}
.article-list article {
  border-left: 4px solid #0066b3;
}
</style>
