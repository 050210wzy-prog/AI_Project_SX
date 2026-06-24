<template>
  <main class="portal">
    <header class="utility-bar">
      <div class="container utility-inner">
        <span>安徽交通职业技术学院官网</span>
        <div>
          <button v-for="item in utilityLinks" :key="item.title" type="button" @click="goService(item.title)">
            <component :is="item.icon" />
            {{ item.title }}
          </button>
        </div>
      </div>
    </header>

    <section class="site-header">
      <div class="container brand-row">
        <button class="brand" type="button" @click="router.push('/')">
          <img src="https://www.acvtc.edu.cn/images/logo.png" alt="安徽交通职业技术学院校徽" />
          <span>
            <b>安徽交通职业技术学院</b>
            <small>Anhui Communications Vocational & Technical College</small>
          </span>
        </button>
        <div class="header-tools">
          <el-input v-model="keyword" placeholder="搜索新闻、通知、招生、专业" clearable @keyup.enter="search(keyword)">
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button class="menu-button" :icon="Menu" @click="mobileOpen = !mobileOpen" />
        </div>
      </div>

      <nav class="container primary-nav" :class="{ open: mobileOpen }">
        <button v-for="item in navs" :key="item" type="button" @click="goChannel(item)">
          {{ item }}
        </button>
        <el-dropdown trigger="click">
          <button class="role-nav" type="button">
            角色导航
            <el-icon><ArrowDown /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item v-for="role in roles" :key="role.name" @click="goService(role.name)">
                {{ role.name }}：{{ role.items.join(' / ') }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </nav>
    </section>

    <section class="hero" :style="heroStyle">
      <div class="hero-overlay"></div>
      <div class="container hero-inner">
        <div class="hero-copy">
          <p>{{ activeBanner.kicker }}</p>
          <h1>{{ activeBanner.title }}</h1>
          <span>{{ activeBanner.subtitle }}</span>
          <div class="hero-actions">
            <el-button type="primary" size="large" @click="router.push('/chat')">招生咨询</el-button>
            <el-button size="large" @click="goChannel('招生就业')">招生就业</el-button>
          </div>
        </div>
        <div class="hero-panel">
          <strong>快捷入口</strong>
          <button v-for="item in heroServices" :key="item" type="button" @click="goService(item)">
            {{ item }}
          </button>
        </div>
      </div>
      <div class="container hero-pager">
        <button type="button" aria-label="上一张" @click="prev"><el-icon><ArrowLeft /></el-icon></button>
        <span>{{ current + 1 }} / {{ heroBanners.length }}</span>
        <button type="button" aria-label="下一张" @click="next"><el-icon><ArrowRight /></el-icon></button>
      </div>
      <div class="container hero-thumbs">
        <button v-for="(item, index) in heroBanners" :key="item.title" type="button" :class="{ active: index === current }" @click="current = index">
          <img :src="item.image" :alt="item.title" />
          <span>{{ item.thumb }}</span>
        </button>
      </div>
    </section>

    <section v-if="keyword" class="container page-section">
      <section-heading en="Search" title="站内搜索" />
      <div class="simple-list">
        <article v-for="item in searchResults" :key="item.title" @click="openArticle(item)">
          <time>{{ item.publish_date }}</time>
          <h3>{{ item.title }}</h3>
          <p>{{ item.summary }}</p>
        </article>
      </div>
    </section>

    <section class="container innovation-strip">
      <div>
        <span>Smart Campus Web</span>
        <h2>智慧官网创新中心</h2>
        <p>招生推荐、专业画像、内容同步、数据大屏、AI 引用问答、校园导览、英文映射等能力集中展示。</p>
      </div>
      <el-button type="primary" size="large" @click="router.push('/innovation')">进入创新中心</el-button>
    </section>

    <section class="container page-section news-section">
      <section-heading en="News & Notice" title="学校要闻与通知公告" />
      <div class="news-layout">
        <article class="lead-news" @click="openArticle(leadStory)">
          <img :src="leadStory.image" alt="学校要闻图片" />
          <div>
            <time>{{ leadStory.publish_date }}</time>
            <h3>{{ leadStory.title }}</h3>
            <p>{{ leadStory.summary }}</p>
          </div>
        </article>
        <div class="simple-list">
          <article v-for="item in news" :key="item.title" @click="openArticle(item)">
            <time>{{ item.publish_date }}</time>
            <h3>{{ item.title }}</h3>
            <p>{{ item.summary }}</p>
          </article>
        </div>
        <aside class="notice-board">
          <div>
            <h3>通知公告</h3>
            <button v-for="item in notices" :key="item.title" type="button" @click="openArticle(item)">
              <time>{{ item.publish_date }}</time>
              <span>{{ item.title }}</span>
            </button>
          </div>
          <div>
            <h3>媒体聚焦</h3>
            <button v-for="item in mediaReports" :key="item.title" type="button" @click="openArticle(item)">
              <time>{{ item.publish_date }}</time>
              <span>{{ item.title }}</span>
            </button>
          </div>
        </aside>
      </div>
    </section>

    <section class="data-section">
      <div class="container">
        <section-heading en="Data" title="数字交院" inverse />
        <div class="stats-grid">
          <article v-for="stat in stats" :key="stat.label">
            <b>{{ stat.value }}</b>
            <span>{{ stat.label }}</span>
          </article>
        </div>
      </div>
    </section>

    <section class="container page-section">
      <section-heading en="Disciplines" title="专业集群展示" />
      <div class="cluster-layout">
        <article v-for="cluster in clusters" :key="cluster.code" @click="goCollege(cluster.link)">
          <div class="cluster-media" :style="{ '--cluster-fallback': cluster.fallback }">
            <img :src="cluster.image" :alt="cluster.title" loading="lazy" @error="handleImageFallback" />
            <span>{{ cluster.code }}</span>
          </div>
          <div>
            <strong>{{ cluster.code }}</strong>
            <h3>{{ cluster.title }}</h3>
            <p>{{ cluster.desc }}</p>
          </div>
        </article>
      </div>
    </section>

    <section class="industry-section">
      <div class="container industry-inner">
        <div class="industry-text">
          <span>Integration</span>
          <h2>校企合作·产教融合</h2>
          <p>学院依托交通行业，深度融合产业发展，与行业领军企业共建冠名班、订单班、现代学徒制班，实现入学即入职、毕业即就业的精准培养。</p>
          <b>毕业生以“基础厚、上手快、留得住、后劲足”的优势广受用人单位青睐。</b>
        </div>
        <div class="partner-area"><button v-for="partner in partners" :key="partner" type="button" @click="goService(partner)">{{ partner }}</button></div>
        <div class="employment-area"><button v-for="item in employmentLinks" :key="item" type="button" @click="goService(item)">{{ item }}</button></div>
      </div>
    </section>

    <section class="container page-section culture-section">
      <section-heading en="Culture" title="校园文化与新媒体矩阵" />
      <div class="culture-layout">
        <div class="motto-card"><b>勤奋、通达、敬业、乐群</b><p>经世致用、实学报国</p><span>立足交通、服务行业、面向社会</span></div>
        <div class="culture-grid">
          <article v-for="item in cultureItems" :key="item.title" @click="goService(item.title)"><component :is="item.icon" /><h3>{{ item.title }}</h3><p>{{ item.desc }}</p></article>
        </div>
        <div class="media-card"><h3>融媒体平台</h3><div><span v-for="item in mediaMatrix" :key="item">{{ item }}</span></div><button type="button" @click="goService('校园宣传片')">校园宣传片</button></div>
      </div>
    </section>

    <footer class="footer">
      <div class="container footer-main">
        <div>
          <img src="https://www.acvtc.edu.cn/images/ftlogo.png" alt="安徽交通职业技术学院页脚标识" />
          <h2>安徽交通职业技术学院</h2>
          <p>新桥校区：安徽新桥国际产业园寿州大道16号</p>
          <p>包河校区：合肥市包河区合巢路114号</p>
          <p>招生咨询电话：0551-63444228　官网：www.acvtc.edu.cn</p>
        </div>
        <div class="footer-links"><button v-for="item in footerServices" :key="item" type="button" @click="goService(item)">{{ item }}</button></div>
      </div>
      <div class="container copyright">© 安徽交通职业技术学院 版权所有 皖ICP备xxxxxx号</div>
    </footer>
  </main>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, ArrowLeft, ArrowRight, Calendar, Connection, DataBoard, Location, Menu, Message, Monitor, Reading, School, Search, Service, User } from '@element-plus/icons-vue'
import http from '../api/http'

const router = useRouter()
const keyword = ref('')
const current = ref(0)
const mobileOpen = ref(false)
const apiArticles = ref([])
let carouselTimer = null

const utilityLinks = [
  { title: '学生课表', icon: Calendar },
  { title: '在线服务大厅', icon: Service },
  { title: 'WebVPN', icon: Connection },
  { title: '电子邮箱', icon: Message },
  { title: '信息门户', icon: Monitor },
  { title: '后台登录', icon: User },
  { title: 'English', icon: User }
]
const navs = ['首页', '学校概况', '院系设置', '招生就业', '教学科研', '校园文化', '国际交流', '信息服务', '智慧创新']
const roles = [
  { name: '在校学生', items: ['课表', '成绩查询', '图书馆'] },
  { name: '教职员工', items: ['办公系统', '科研申报', '工资查询'] },
  { name: '考生/家长', items: ['招生简章', '专业介绍', '历年分数'] },
  { name: '校友', items: ['校友活动', '返校预约', '校友捐赠'] },
  { name: '访客', items: ['校园地图', '联系方式', '办事指南'] }
]
const heroServices = ['学生课表/成绩', '后台登录', '招生咨询AI', '办事大厅', '招生管理系统', '图书馆资源']
const heroBanners = [
  { kicker: '蓝绿交织 通达未来', title: '勤奋、通达、敬业、乐群', subtitle: '安徽交通职业技术学院欢迎您。', thumb: '校园全景', image: 'https://www.acvtc.edu.cn/__local/2/7B/BA/1991E6320170386EEE706FD2F53_0528A760_1481E.jpg' },
  { kicker: '现代综合交通专业集群', title: '路·海·空·轨·车·邮', subtitle: '构建现代综合交通专业集群。', thumb: '专业集群', image: 'https://www.acvtc.edu.cn/__local/E/E9/35/4C4B4F751452708C9DC0758C59D_5BDAA9C0_17CC1.jpg' },
  { kicker: '高素质技术技能人才培养', title: '基础厚·上手快·留得住·后劲足', subtitle: '为交通强国培养高素质技术技能人才。', thumb: '实训教学', image: 'https://www.acvtc.edu.cn/__local/1/57/6C/D1CCD8E88FC99DAB8D3287DC5F4_0769FA99_14EFC.jpg' },
  { kicker: '校企合作 产教融合', title: '订单班·冠名班·现代学徒制班', subtitle: '让产业需求走进课堂，让职业成长抵达未来。', thumb: '产教融合', image: 'https://www.acvtc.edu.cn/__local/4/D8/C6/BAD0D1360D5C810E0A7A1F55F57_C2DD0CCE_1517E.jpg' },
  { kicker: '青春逐梦 技能报国', title: '遇见交院·成就未来', subtitle: '在技能竞赛、社团活动和志愿服务中书写青春答卷。', thumb: '校园生活', image: 'https://www.acvtc.edu.cn/__local/2/40/F2/EE54DCF56B0362EC3CCCEB10385_0D2D27FE_27717.jpg' },
  { kicker: '安徽交通黄埔', title: '服务安徽经济发展·融通综合交通行业', subtitle: '赓续办学传统，建设技能型高水平大学。', thumb: '交院传承', image: 'https://www.acvtc.edu.cn/__local/0/98/89/2FD3BF6455AC8EA5A4D555A529A_71B0703A_1F722.jpg' }
]
const activeBanner = computed(() => heroBanners[current.value])
const heroStyle = computed(() => ({ backgroundImage: `url('${activeBanner.value.image}')` }))
const defaultImage = 'https://www.acvtc.edu.cn/images/nybanner_new.jpg'
const leadStory = { title: '学院在2025年全国职业院校技能大赛中荣获佳绩', summary: '学校持续推进以赛促教、以赛促学，服务学生在真实项目与技能竞赛中提升综合素养。', publish_date: '2025-11-15', channel: '学校要闻', image: defaultImage }
const localNews = [
  { title: '安徽交通职业技术学院与安徽交通广播举行战略合作签约仪式', summary: '双方围绕交通文化传播、产教融合和实践育人开展深度合作。', publish_date: '2025-11-08', channel: '学校要闻' },
  { title: '我院与安徽工业大学举办联合培养本科生毕业典礼', summary: '联合培养项目持续拓展学生成长通道，提升技术技能人才培养层次。', publish_date: '2025-06-20', channel: '学校要闻' },
  { title: '学院推进新桥校区实训基地建设', summary: '围绕路桥、轨道、航海、航空、新能源汽车等专业方向完善实践教学条件。', publish_date: '2025-05-18', channel: '学校要闻' }
]
const notices = [
  { title: '关于2025-2026学年第二学期选课工作的通知', publish_date: '2025-12-01', summary: '发布选课时间、流程和注意事项。', channel: '通知公告' },
  { title: '安徽交通职业技术学院2026届毕业生秋季校园招聘会邀请函', publish_date: '2025-09-22', summary: '邀请用人单位参加校园招聘活动。', channel: '通知公告' },
  { title: '2025年“双师型”教师认定工作通知', publish_date: '2025-10-10', summary: '组织开展教师职业能力认定工作。', channel: '通知公告' }
]
const mediaReports = [
  { title: '《中国教育报》报道我院产教融合实践经验', publish_date: '2025-10-25', summary: '聚焦学院服务交通行业的人才培养路径。', channel: '媒体聚焦' },
  { title: '安徽新闻联播聚焦我院轨道交通人才培养', publish_date: '2025-11-02', summary: '展示轨道交通专业群实践教学成果。', channel: '媒体聚焦' }
]
const stats = [
  { value: '1956', label: '创办于' }, { value: '1200+亩', label: '校园占地面积' }, { value: '14000+人', label: '在校生规模' }, { value: '540+人', label: '教职工' }, { value: '41个', label: '特色专业' }, { value: '10个', label: '国家级重点专业' }, { value: '17个', label: '省级重点专业' }, { value: '236+个', label: '校外实习实训基地' }, { value: '11万名', label: '累计培养人才' }, { value: '98%+', label: '毕业生就业率' }
]
const clusters = [
  { code: '路', title: '交通土建施工群', desc: '道路与桥梁工程技术、建筑工程技术、土木工程检测技术等', link: '土木建筑学院', image: heroBanners[0].image, fallback: 'linear-gradient(135deg, #0066b3, #2e7d32)' },
  { code: '车', title: '新能源汽车与装备群', desc: '新能源汽车技术、汽车检测与维修、智能网联汽车技术等', link: '汽车工程学院', image: heroBanners[1].image, fallback: 'linear-gradient(135deg, #005e9f, #7aa34b)' },
  { code: '轨', title: '城市轨道交通群', desc: '城市轨道车辆应用技术、城市轨道交通运营管理等', link: '轨道交通学院', image: heroBanners[2].image, fallback: 'linear-gradient(135deg, #003b70, #00a1a7)' },
  { code: '海', title: '航海技术群', desc: '航海技术、轮机工程技术等特色专业方向', link: '航运工程学院', image: heroBanners[3].image, fallback: 'linear-gradient(135deg, #0066b3, #1f8a70)' },
  { code: '空', title: '航空维修与服务群', desc: '民航运输服务、飞机机电设备维修、通用航空器维修等', link: '航空与低空经济学院', image: heroBanners[4].image, fallback: 'linear-gradient(135deg, #2f6f9f, #7abf66)' },
  { code: '邮', title: '邮政物流服务群', desc: '现代物流管理、邮政快递运营管理等', link: '经济管理学院', image: heroBanners[5].image, fallback: 'linear-gradient(135deg, #2e7d32, #c41e3a)' },
  { code: '智', title: '交通信息技术群', desc: '人工智能技术应用、大数据技术、智能交通技术等', link: '人工智能学院', image: defaultImage, fallback: 'linear-gradient(135deg, #003b70, #5b8cba)' }
]
const partners = ['中铁大桥局', '通用汽车', '中国远洋', '合肥轨道交通集团', '安徽民航机场集团']
const employmentLinks = ['校园招聘会', '就业指导中心', '校友企业招聘平台']
const cultureItems = [
  { title: '我们的校史馆', desc: '以时间轴呈现1956年至今的发展脉络。', icon: Calendar },
  { title: 'VR全景校园', desc: '线上浏览新桥校区和包河校区。', icon: Location },
  { title: '荣誉交院', desc: '集中展示国家骨干高职院校等荣誉。', icon: School },
  { title: '校友风采', desc: '杰出校友图文故事。', icon: Reading },
  { title: '交院人物', desc: '优秀师生人物专访。', icon: DataBoard }
]
const mediaMatrix = ['官方微信', '官方微博', '抖音号', '视频号', 'B站']
const footerServices = ['办事大厅', '图书馆资源', '招生管理系统', '电子邮箱登录', 'VPN校外访问', '信息公开平台', '智慧校园', '院长信箱']
const news = computed(() => {
  const remote = apiArticles.value.filter((item) => item.channel === '学校要闻').slice(0, 3)
  return [...remote, ...localNews].slice(0, 5)
})
const searchResults = computed(() => {
  const key = keyword.value.trim().toLowerCase()
  if (!key) return []
  const all = [...apiArticles.value, leadStory, ...localNews, ...notices, ...mediaReports]
  return all.filter((item) => `${item.title}${item.summary || ''}${item.channel || ''}`.toLowerCase().includes(key)).slice(0, 8)
})
function goService(name) {
  if (name === '学生课表' || name === '学生课表/成绩' || name === '在校学生') return router.push('/schedule')
  if (name === '招生咨询AI') return router.push('/chat')
  if (name === '后台登录') return router.push('/admin')
  if (name === 'English') return router.push('/english')
  if (name === '在线服务大厅') return window.open('https://ehall.acvtc.edu.cn/', '_blank')
  router.push(`/service/${encodeURIComponent(name)}`)
}
function goCollege(name) { router.push(`/college/${encodeURIComponent(name)}`) }
function goChannel(name) {
  if (name === '首页') router.push('/')
  else if (name === '智慧创新') router.push('/innovation')
  else router.push(`/channel/${encodeURIComponent(name)}`)
}
function openArticle(item) {
  if (item.id) router.push(`/article/${item.id}`)
  else router.push(`/channel/${encodeURIComponent(item.channel || '学校要闻')}`)
}
function search(value) { keyword.value = String(value || '').trim(); loadArticles() }
function prev() { current.value = (current.value - 1 + heroBanners.length) % heroBanners.length }
function next() { current.value = (current.value + 1) % heroBanners.length }
function handleImageFallback(event) {
  const image = event.target
  const media = image.closest('.cluster-media')
  if (image.dataset.fallbackApplied) { image.remove(); media?.classList.add('is-fallback'); return }
  image.dataset.fallbackApplied = '1'
  image.src = defaultImage
}
async function loadArticles() {
  try {
    const { data } = await http.get('/website/articles', { params: keyword.value ? { keyword: keyword.value } : {} })
    apiArticles.value = Array.isArray(data) ? data : []
  } catch { apiArticles.value = [] }
}
const SectionHeading = defineComponent({
  props: { en: String, title: String, inverse: Boolean },
  setup(props) {
    return () => h('div', { class: ['section-heading', props.inverse ? 'inverse' : ''] }, [h('span', props.en), h('h2', props.title)])
  }
})
onMounted(() => { loadArticles(); carouselTimer = window.setInterval(next, 5200) })
onUnmounted(() => { if (carouselTimer) window.clearInterval(carouselTimer) })
</script>
<style scoped>
.portal {
  min-height: 100vh;
  color: #27313d;
  background: #f5f7fa;
}
.container {
  width: min(1180px, calc(100vw - 40px));
  margin: 0 auto;
}
button {
  font: inherit;
}
.utility-bar {
  background: #003b70;
  color: #dceaf6;
  font-size: 13px;
}
.utility-inner {
  min-height: 38px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
}
.utility-inner div {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.utility-inner button {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  border: 0;
  color: #f7fbff;
  background: transparent;
  padding: 7px 9px;
  cursor: pointer;
}
.utility-inner svg {
  width: 14px;
  height: 14px;
}
.site-header {
  position: sticky;
  top: 0;
  z-index: 20;
  background: rgba(255, 255, 255, .98);
  border-bottom: 1px solid #dce5ee;
}
.brand-row {
  min-height: 92px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 32px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 14px;
  border: 0;
  background: transparent;
  cursor: pointer;
  text-align: left;
}
.brand img {
  width: 58px;
  height: 58px;
  object-fit: contain;
}
.brand b {
  display: block;
  color: #003b70;
  font-size: 29px;
  line-height: 1.15;
  letter-spacing: .03em;
}
.brand small {
  display: block;
  margin-top: 5px;
  color: #2e7d32;
  font-size: 13px;
  font-weight: 700;
}
.header-tools {
  width: min(420px, 100%);
  display: flex;
  gap: 8px;
}
.menu-button {
  display: none;
}
.primary-nav {
  min-height: 50px;
  display: grid;
  grid-template-columns: repeat(8, 1fr) 112px;
}
.primary-nav button,
.role-nav {
  border: 0;
  border-top: 3px solid transparent;
  background: transparent;
  color: #1d2b39;
  cursor: pointer;
  font-weight: 700;
}
.primary-nav button:hover,
.role-nav:hover {
  color: #0066b3;
  border-top-color: #2e7d32;
}
.role-nav {
  width: 100%;
  height: 100%;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}
.hero {
  position: relative;
  min-height: calc(100vh - 180px);
  background-color: #003b70;
  background-image:
    linear-gradient(120deg, #003b70, #0066b3 52%, #2e7d32);
  background-size: cover;
  background-position: center;
  overflow: hidden;
}
.hero-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(90deg, rgba(0, 36, 68, .86), rgba(0, 78, 132, .5) 48%, rgba(46, 125, 50, .08)),
    linear-gradient(0deg, rgba(0, 0, 0, .35), transparent 35%);
}
.hero-inner {
  position: relative;
  min-height: calc(100vh - 180px);
  display: grid;
  grid-template-columns: 1fr 300px;
  align-items: end;
  gap: 48px;
  padding: 82px 0 86px;
  color: #ffffff;
}
.hero-copy p,
.industry-text span,
.section-heading span {
  margin: 0 0 14px;
  color: #2e7d32;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
}
.hero-copy p {
  color: #d9f0de;
}
.hero-copy h1 {
  width: min(820px, 100%);
  margin: 0 0 18px;
  font-size: clamp(42px, 6vw, 76px);
  line-height: 1.08;
  letter-spacing: .02em;
}
.hero-copy > span {
  display: block;
  width: min(620px, 100%);
  font-size: 21px;
  line-height: 1.75;
}
.hero-actions {
  display: flex;
  gap: 12px;
  margin-top: 28px;
}
.hero-panel {
  background: rgba(255, 255, 255, .94);
  border-top: 4px solid #2e7d32;
  padding: 22px;
  color: #1d2b39;
}
.hero-panel strong {
  display: block;
  margin-bottom: 12px;
  color: #003b70;
  font-size: 18px;
}
.hero-panel button {
  width: 100%;
  border: 0;
  border-bottom: 1px solid #dce5ee;
  background: transparent;
  padding: 13px 0;
  color: #27313d;
  text-align: left;
  cursor: pointer;
  font-weight: 700;
}
.hero-panel button:hover {
  color: #0066b3;
}
.hero-pager {
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: -62px;
  padding-bottom: 24px;
  color: #ffffff;
}
.hero-pager button {
  width: 38px;
  height: 38px;
  border: 1px solid rgba(255, 255, 255, .65);
  color: #ffffff;
  background: rgba(0, 0, 0, .18);
  cursor: pointer;
}
.hero-thumbs {
  position: relative;
  z-index: 2;
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 10px;
  margin-top: -4px;
  padding-bottom: 26px;
}
.hero-thumbs button {
  display: grid;
  grid-template-columns: 58px 1fr;
  align-items: center;
  gap: 10px;
  min-height: 58px;
  border: 1px solid rgba(255, 255, 255, .3);
  background: rgba(0, 34, 64, .52);
  color: #ffffff;
  cursor: pointer;
  text-align: left;
  font-weight: 800;
  overflow: hidden;
}
.hero-thumbs button.active,
.hero-thumbs button:hover {
  border-color: rgba(255, 255, 255, .82);
  background: rgba(255, 255, 255, .92);
  color: #003b70;
  transform: translateY(-2px);
}
.hero-thumbs img {
  width: 58px;
  height: 58px;
  object-fit: cover;
}
.page-section {
  padding: 72px 0;
}
.innovation-strip {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 28px;
  align-items: center;
  margin-top: 46px;
  padding: 30px 34px;
  border-left: 5px solid #2e7d32;
  background:
    linear-gradient(120deg, #ffffff, #f0f7fb);
  box-shadow: 0 18px 42px rgba(0, 54, 96, .08);
}
.innovation-strip span {
  color: #c41e3a;
  font-size: 13px;
  font-weight: 900;
  letter-spacing: .12em;
  text-transform: uppercase;
}
.innovation-strip h2 {
  margin: 8px 0;
  color: #003b70;
  font-size: 34px;
}
.innovation-strip p {
  margin: 0;
  color: #5f6c78;
  line-height: 1.8;
}
.section-heading {
  display: flex;
  justify-content: space-between;
  align-items: end;
  gap: 22px;
  margin-bottom: 28px;
  padding-bottom: 14px;
  border-bottom: 1px solid #dce5ee;
}
.section-heading h2 {
  margin: 0;
  color: #003b70;
  font-size: clamp(30px, 4vw, 44px);
  line-height: 1.15;
  letter-spacing: .02em;
}
.section-heading.inverse {
  border-bottom-color: rgba(255, 255, 255, .22);
}
.section-heading.inverse h2,
.section-heading.inverse span {
  color: #ffffff;
}
.news-layout {
  display: grid;
  grid-template-columns: 1.08fr 1fr .86fr;
  gap: 28px;
}
.lead-news,
.simple-list article,
.cluster-layout article,
.culture-grid article,
.motto-card,
.media-card {
  background: #ffffff;
  border: 1px solid #dce5ee;
}
.lead-news,
.simple-list article,
.cluster-layout article,
.culture-grid article {
  cursor: pointer;
  transition: transform .16s ease, border-color .16s ease, box-shadow .16s ease;
}
.lead-news:hover,
.simple-list article:hover,
.cluster-layout article:hover,
.culture-grid article:hover {
  transform: translateY(-3px);
  border-color: #9cc4df;
  box-shadow: 0 16px 34px rgba(0, 52, 91, .1);
}
.lead-news {
  overflow: hidden;
}
.lead-news img {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
}
.lead-news div {
  padding: 22px;
}
.lead-news time,
.simple-list time,
.notice-board time {
  color: #c41e3a;
  font-weight: 900;
  font-size: 13px;
}
.lead-news h3,
.simple-list h3,
.notice-board h3,
.cluster-layout h3,
.culture-grid h3,
.media-card h3 {
  margin: 9px 0;
  color: #1d2b39;
}
.lead-news p,
.simple-list p,
.cluster-layout p,
.culture-grid p,
.industry-text p,
.industry-text b {
  color: #5f6c78;
  line-height: 1.8;
}
.simple-list {
  display: grid;
  gap: 12px;
}
.simple-list article {
  padding: 18px 20px;
}
.simple-list p {
  margin: 0;
}
.notice-board {
  display: grid;
  gap: 18px;
}
.notice-board > div {
  border-left: 4px solid #0066b3;
  background: #ffffff;
  padding: 18px;
}
.notice-board button {
  width: 100%;
  display: grid;
  grid-template-columns: 92px 1fr;
  gap: 10px;
  border: 0;
  border-bottom: 1px solid #edf1f5;
  background: transparent;
  padding: 12px 0;
  text-align: left;
  cursor: pointer;
}
.data-section {
  padding: 72px 0;
  background: #003b70;
}
.stats-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 14px;
}
.stats-grid article {
  min-height: 126px;
  padding: 24px 16px;
  background: rgba(255, 255, 255, .08);
  border: 1px solid rgba(255, 255, 255, .16);
}
.stats-grid b {
  display: block;
  color: #ffffff;
  font-size: 34px;
  line-height: 1;
}
.stats-grid span {
  display: block;
  margin-top: 14px;
  color: #d9e9f5;
  font-weight: 700;
}
.cluster-layout {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}
.cluster-layout article {
  overflow: hidden;
}
.cluster-media {
  position: relative;
  display: grid;
  place-items: center;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background:
    linear-gradient(0deg, rgba(0, 34, 64, .2), rgba(0, 34, 64, .2)),
    var(--cluster-fallback, linear-gradient(135deg, #0066b3, #2e7d32));
}
.cluster-media::after {
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: 46%;
  background: linear-gradient(0deg, rgba(0, 34, 64, .72), transparent);
}
.cluster-media span {
  position: absolute;
  right: 16px;
  bottom: 12px;
  z-index: 2;
  color: rgba(255, 255, 255, .9);
  font-size: 54px;
  font-weight: 900;
  line-height: 1;
}
.cluster-layout img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  display: block;
  background:
    linear-gradient(0deg, rgba(0, 34, 64, .16), rgba(0, 34, 64, .16)),
    var(--cluster-fallback, linear-gradient(135deg, #0066b3, #2e7d32));
}
.cluster-layout div {
  padding: 18px;
}
.cluster-layout .cluster-media {
  padding: 0;
}
.cluster-layout strong {
  display: inline-grid;
  place-items: center;
  width: 42px;
  height: 42px;
  margin-bottom: 8px;
  border-radius: 50%;
  color: #ffffff;
  background: #0066b3;
  font-size: 22px;
}
.industry-section {
  background: #edf4f8;
}
.industry-inner {
  display: grid;
  grid-template-columns: 1.1fr .9fr;
  gap: 28px;
  align-items: center;
  padding: 72px 0;
}
.industry-text h2 {
  margin: 0 0 16px;
  color: #003b70;
  font-size: clamp(34px, 5vw, 54px);
  line-height: 1.1;
}
.partner-area,
.employment-area {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}
.partner-area button,
.employment-area button,
.media-card button,
.footer-links button {
  border: 1px solid #bfd0de;
  background: #ffffff;
  color: #0066b3;
  padding: 11px 14px;
  cursor: pointer;
  font-weight: 800;
}
.employment-area {
  grid-column: 1 / -1;
}
.culture-layout {
  display: grid;
  grid-template-columns: .88fr 1.42fr .8fr;
  gap: 22px;
}
.motto-card,
.media-card {
  padding: 24px;
}
.motto-card b {
  display: block;
  color: #003b70;
  font-size: 28px;
  line-height: 1.32;
}
.motto-card p {
  color: #c41e3a;
  font-size: 20px;
  font-weight: 900;
}
.culture-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.culture-grid article {
  padding: 20px;
}
.culture-grid svg {
  width: 30px;
  height: 30px;
  color: #2e7d32;
}
.media-card div {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin: 16px 0;
}
.media-card span {
  min-height: 78px;
  display: grid;
  place-items: center;
  border: 1px dashed #9fb2c3;
  color: #0066b3;
  background: #f5f7fa;
  font-weight: 900;
}
.footer {
  padding: 42px 0 24px;
  border-top: 4px solid #0066b3;
  background: #ffffff;
}
.footer-main {
  display: grid;
  grid-template-columns: 1.1fr .9fr;
  gap: 28px;
}
.footer-main img {
  width: 220px;
  max-width: 100%;
}
.footer-main h2 {
  color: #003b70;
}
.footer-main p {
  color: #5f6c78;
  margin: 8px 0;
}
.footer-links {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}
.copyright {
  margin-top: 26px;
  color: #6d7783;
  font-size: 14px;
}
@media (max-width: 1020px) {
  .brand-row,
  .industry-inner,
  .footer-main {
    display: grid;
    grid-template-columns: 1fr;
  }
  .primary-nav,
  .news-layout,
  .innovation-strip,
  .culture-layout {
    grid-template-columns: 1fr 1fr;
  }
  .hero-inner {
    grid-template-columns: 1fr;
    align-items: end;
  }
  .hero-panel {
    width: min(420px, 100%);
  }
  .notice-board,
  .employment-area {
    grid-column: 1 / -1;
  }
  .cluster-layout,
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 720px) {
  .container {
    width: min(100vw - 22px, 1180px);
  }
  .utility-inner,
  .brand-row {
    align-items: flex-start;
  }
  .utility-inner {
    display: grid;
  }
  .brand b {
    font-size: 22px;
  }
  .header-tools {
    width: 100%;
  }
  .menu-button {
    display: inline-flex;
  }
  .primary-nav {
    display: none;
    grid-template-columns: 1fr;
    padding-bottom: 10px;
  }
  .primary-nav.open {
    display: grid;
  }
  .primary-nav button,
  .role-nav {
    min-height: 44px;
    text-align: left;
    border-top: 0;
    border-bottom: 1px solid #edf1f5;
  }
  .hero,
  .hero-inner {
    min-height: 640px;
  }
  .hero-thumbs {
    grid-template-columns: 1fr 1fr;
  }
  .news-layout,
  .innovation-strip,
  .culture-layout,
  .culture-grid,
  .cluster-layout,
  .stats-grid,
  .footer-links {
    grid-template-columns: 1fr;
  }
  .section-heading {
    display: block;
  }
}

.portal {
  background:
    linear-gradient(180deg, #f7fafc 0, #eef3f7 560px, #eef3f7 100%);
}
.site-header {
  box-shadow: 0 10px 30px rgba(0, 54, 96, .06);
}
.hero {
  min-height: calc(100vh - 164px);
}
.hero-overlay {
  background:
    linear-gradient(90deg, rgba(0, 36, 68, .9), rgba(0, 78, 132, .56) 46%, rgba(46, 125, 50, .12)),
    linear-gradient(0deg, rgba(0, 0, 0, .46), transparent 44%);
}
.hero-copy h1 {
  text-shadow: 0 12px 34px rgba(0, 0, 0, .28);
}
.hero-panel {
  border: 1px solid rgba(255, 255, 255, .7);
  box-shadow: 0 24px 70px rgba(0, 30, 60, .22);
}
.hero-panel button:hover {
  padding-left: 8px;
}
.section-heading {
  border-bottom: 0;
  position: relative;
}
.section-heading::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -12px;
  width: 82px;
  height: 4px;
  background: linear-gradient(90deg, #0066b3, #2e7d32);
}
.lead-news,
.simple-list article,
.cluster-layout article,
.culture-grid article,
.motto-card,
.media-card {
  box-shadow: 0 18px 42px rgba(0, 54, 96, .08);
}
.lead-news,
.cluster-layout article {
  border-radius: 2px;
}
.simple-list article {
  border-left: 4px solid #0066b3;
}
.notice-board > div {
  box-shadow: 0 18px 42px rgba(0, 54, 96, .08);
}
.stats-grid article {
  backdrop-filter: blur(8px);
}
.cluster-layout article:hover img {
  transform: scale(1.035);
}
.cluster-layout img {
  transition: transform .32s ease;
}
.industry-section {
  border-top: 1px solid #d7e2ec;
  border-bottom: 1px solid #d7e2ec;
}
.partner-area button:hover,
.employment-area button:hover,
.media-card button:hover {
  color: #ffffff;
  background: #0066b3;
  border-color: #0066b3;
  transform: translateY(-2px);
}
.culture-grid article {
  border-top: 4px solid #2e7d32;
}
.motto-card {
  background:
    linear-gradient(160deg, #ffffff, #eef8f1);
}
</style>

