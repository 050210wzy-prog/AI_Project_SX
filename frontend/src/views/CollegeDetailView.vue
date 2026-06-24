<template>
  <site-shell :breadcrumbs="breadcrumbs">
    <section class="container college-hero">
      <span>School Detail</span>
      <h1>{{ college.name }}</h1>
      <p>{{ college.desc }}</p>
      <div>
        <el-button type="primary" @click="$router.push('/chat')">咨询该学院专业</el-button>
        <el-button @click="$router.push('/channel/院系设置')">返回院系设置</el-button>
      </div>
    </section>

    <section class="container college-layout">
      <main>
        <section-card title="学院简介">
          <p>{{ college.profile }}</p>
        </section-card>

        <section-card title="专业列表">
          <table class="major-table">
            <thead>
              <tr>
                <th>专业名称</th>
                <th>核心课程</th>
                <th>就业岗位</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="major in college.majors" :key="major.name">
                <td>{{ major.name }}</td>
                <td>{{ major.courses }}</td>
                <td>{{ major.jobs }}</td>
                <td>
                  <button type="button" @click="askMajor(major.name)">专业咨询</button>
                  <button type="button" @click="$router.push('/service/历年分数')">查分数</button>
                </td>
              </tr>
            </tbody>
          </table>
        </section-card>

        <section-card title="师资力量">
          <div class="faculty-grid">
            <article v-for="item in college.faculty" :key="item.label">
              <b>{{ item.value }}</b>
              <span>{{ item.label }}</span>
            </article>
          </div>
        </section-card>

        <section-card title="实训条件">
          <div class="training-grid">
            <article v-for="item in college.training" :key="item.title">
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </article>
          </div>
        </section-card>

        <section-card title="学院动态">
          <div class="news-list">
            <article v-for="item in college.news" :key="item.title" @click="$router.push('/channel/院系设置')">
              <time>{{ item.date }}</time>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
            </article>
          </div>
        </section-card>
      </main>

      <aside class="side-panel">
        <section>
          <h2>联系方式</h2>
          <p>教学秘书：{{ college.contact.teacher }}</p>
          <p>招生咨询：{{ college.contact.phone }}</p>
          <p>办公地点：{{ college.contact.address }}</p>
        </section>
        <section>
          <h2>学院服务</h2>
          <button v-for="item in college.services" :key="item" type="button" @click="$router.push(`/service/${encodeURIComponent(item)}`)">
            {{ item }}
          </button>
        </section>
      </aside>
    </section>
  </site-shell>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import SiteShell from '../components/SiteShell.vue'

const route = useRoute()
const router = useRouter()
const breadcrumbs = computed(() => [
  { label: '院系设置', path: '/channel/院系设置' },
  { label: college.value.name }
])

function makeCollege(name, desc, majors, extra = {}) {
  return {
    name,
    desc,
    profile: extra.profile || `${name}围绕学院专业群建设和行业岗位需求，推进岗课赛证融通，强化实践教学和校企协同育人。`,
    majors,
    faculty: extra.faculty || [
      { value: '40+人', label: '专兼职教师' },
      { value: '70%+', label: '双师型教师比例' },
      { value: '8项', label: '教科研与竞赛成果' }
    ],
    training: extra.training || [
      { title: '综合实训室', desc: '服务专业核心课程实训、技能竞赛训练和职业资格认证。' },
      { title: '校企合作基地', desc: '与行业企业共建实践教学基地，开展项目化教学和岗位实习。' }
    ],
    services: extra.services || ['历年分数', '招生信息', '图书馆资源', '办事大厅'],
    contact: extra.contact || { teacher: `${name}办公室`, phone: '0551-63444228', address: '新桥校区' },
    news: extra.news || [
      { date: '05-20', title: `${name}开展专业建设研讨`, summary: '围绕人才培养方案、课程建设和实训条件持续优化。' },
      { date: '05-12', title: `${name}推进校企合作项目`, summary: '对接行业企业需求，拓展学生实习和就业岗位。' }
    ]
  }
}

const colleges = {
  土木建筑学院: makeCollege('土木建筑学院', '聚焦道桥、建筑、检测等专业方向，服务交通基础设施建设。', [
    { name: '道路与桥梁工程技术', courses: '道路工程、桥梁工程、工程测量、施工组织', jobs: '道路桥梁施工、试验检测、工程管理' },
    { name: '建筑工程技术', courses: '建筑施工、结构识图、BIM技术', jobs: '建筑施工、质量管理、资料管理' },
    { name: '土木工程检测技术', courses: '材料检测、结构检测、工程试验', jobs: '工程检测、质量评价、试验员' }
  ]),
  汽车工程学院: makeCollege('汽车工程学院', '服务新能源汽车、智能网联汽车和汽车检测维修产业链。', [
    { name: '新能源汽车技术', courses: '动力电池、电机电控、整车维护', jobs: '新能源汽车检测、维修、售后服务' },
    { name: '汽车检测与维修技术', courses: '汽车检测、故障诊断、维修工艺', jobs: '汽车维修、检测诊断、服务顾问' },
    { name: '智能网联汽车技术', courses: '智能传感、车联网、自动驾驶基础', jobs: '智能网联测试、车联网运维' }
  ]),
  轨道交通学院: makeCollege('轨道交通学院', '面向城市轨道交通运营、车辆、通信信号和机电设备维护岗位培养人才。', [
    { name: '城市轨道交通运营管理', courses: '客运组织、行车组织、票务管理', jobs: '站务员、行车值班、运营调度' },
    { name: '城市轨道车辆应用技术', courses: '车辆构造、检修工艺、制动系统', jobs: '轨道车辆检修、车辆维护' },
    { name: '城市轨道交通通信信号技术', courses: '通信系统、信号控制、联锁设备', jobs: '通信信号维护、系统调试' }
  ]),
  航运工程学院: makeCollege('航运工程学院', '服务现代航运、港口物流、水上交通安全和船舶运维领域。', [
    { name: '航海技术', courses: '船舶驾驶、航海气象、海上安全', jobs: '船舶驾驶、航运管理' },
    { name: '轮机工程技术', courses: '船舶动力、轮机维护、机舱管理', jobs: '轮机管理、船舶设备维护' },
    { name: '港口与航运管理', courses: '港口业务、航运组织、物流管理', jobs: '港口调度、航运业务、物流运营' }
  ]),
  航空与低空经济学院: makeCollege('航空与低空经济学院', '面向民航服务、飞机维修、无人机应用和低空经济新兴领域。', [
    { name: '民航运输服务', courses: '民航服务、客舱安全、机场运营', jobs: '机场服务、民航客运、地面保障' },
    { name: '飞机机电设备维修', courses: '飞机结构、机电设备、维修规范', jobs: '飞机维修、航材管理' },
    { name: '无人机应用技术', courses: '无人机操控、航测、维护', jobs: '无人机飞手、航测数据处理、低空应用服务' }
  ]),
  人工智能学院: makeCollege('人工智能学院', '聚焦大数据、人工智能、智能交通技术和数字媒体应用。', [
    { name: '人工智能技术应用', courses: 'Python、机器学习、数据库、智能交通应用', jobs: 'AI应用开发、智能系统运维、数据标注与分析' },
    { name: '大数据技术', courses: '数据采集、数据分析、可视化', jobs: '数据分析、BI开发、数据处理' },
    { name: '智能交通技术', courses: '交通数据、感知设备、系统集成', jobs: '智能交通运维、项目实施' }
  ]),
  经济管理学院: makeCollege('经济管理学院', '服务现代物流、邮政快递、电子商务和财经管理。', [
    { name: '现代物流管理', courses: '仓储配送、供应链管理、运输组织', jobs: '物流运营、仓储管理、供应链专员' },
    { name: '邮政快递运营管理', courses: '快递运营、网点管理、物流信息技术', jobs: '快递运营、网点主管、客户服务' },
    { name: '大数据与会计', courses: '会计基础、财务管理、财务软件', jobs: '会计核算、财务助理、数据统计' }
  ])
}
const fallback = colleges.人工智能学院
const college = computed(() => colleges[String(route.params.name)] || fallback)

function askMajor(name) {
  router.push({ path: '/chat', query: { q: `请介绍${name}专业的就业方向和录取分数` } })
}

const SectionCard = defineComponent({
  props: { title: String },
  setup(props, { slots }) {
    return () => h('section', { class: 'section-card' }, [h('h2', props.title), h('div', slots.default?.())])
  }
})
</script>

<style scoped>
.container {
  width: min(1180px, calc(100vw - 40px));
  margin: 0 auto;
}
.college-hero {
  padding: 46px 0 34px;
  border-bottom: 1px solid #dce5ee;
}
.college-hero span {
  color: #2e7d32;
  font-weight: 900;
  text-transform: uppercase;
}
.college-hero h1 {
  margin: 10px 0 12px;
  color: #003b70;
  font-size: clamp(38px, 6vw, 64px);
}
.college-hero p {
  color: #5f6c78;
  line-height: 1.8;
}
.college-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 30px;
  padding: 36px 0 72px;
}
main {
  display: grid;
  gap: 20px;
}
.section-card,
.side-panel section {
  background: #ffffff;
  border: 1px solid #dce5ee;
  padding: 24px;
}
.section-card h2,
.side-panel h2 {
  margin: 0 0 18px;
  color: #003b70;
}
.section-card p,
.side-panel p {
  color: #5f6c78;
  line-height: 1.85;
}
.major-table {
  width: 100%;
  border-collapse: collapse;
}
.major-table th,
.major-table td {
  border: 1px solid #dce5ee;
  padding: 13px;
  text-align: left;
  vertical-align: top;
}
.major-table th {
  color: #003b70;
  background: #f5f7fa;
}
.major-table button,
.side-panel button {
  border: 1px solid #bfd0de;
  background: #ffffff;
  color: #0066b3;
  padding: 8px 10px;
  margin: 3px;
  cursor: pointer;
  font-weight: 800;
}
.faculty-grid,
.training-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
.faculty-grid article,
.training-grid article,
.news-list article {
  border: 1px solid #dce5ee;
  padding: 18px;
}
.faculty-grid b {
  display: block;
  color: #c41e3a;
  font-size: 28px;
}
.faculty-grid span {
  color: #5f6c78;
}
.training-grid h3,
.news-list h3 {
  margin: 0 0 8px;
  color: #1d2b39;
}
.news-list {
  display: grid;
  gap: 12px;
}
.news-list article {
  cursor: pointer;
}
.news-list time {
  color: #c41e3a;
  font-weight: 900;
}
.side-panel {
  align-self: start;
  position: sticky;
  top: 18px;
  display: grid;
  gap: 16px;
}
.side-panel button {
  width: 100%;
  display: block;
  text-align: left;
  margin: 8px 0 0;
}
@media (max-width: 920px) {
  .college-layout,
  .faculty-grid,
  .training-grid {
    grid-template-columns: 1fr;
  }
  .side-panel {
    position: static;
  }
}

.college-hero {
  position: relative;
  margin-top: 24px;
  padding: 62px 52px 46px;
  overflow: hidden;
  border: 1px solid #dce5ee;
  border-bottom: 4px solid #2e7d32;
  background:
    linear-gradient(110deg, rgba(0, 59, 112, .95), rgba(0, 102, 179, .74) 48%, rgba(46, 125, 50, .66)),
    url("https://www.acvtc.edu.cn/__local/2/7B/BA/1991E6320170386EEE706FD2F53_0528A760_1481E.jpg") center / cover;
  color: #ffffff;
}
.college-hero::after {
  content: "ACVTC";
  position: absolute;
  right: 42px;
  bottom: 22px;
  color: rgba(255, 255, 255, .12);
  font-size: 86px;
  font-weight: 900;
  letter-spacing: .08em;
}
.college-hero > * {
  position: relative;
  z-index: 1;
}
.college-hero span {
  color: #d9f0de;
  letter-spacing: .16em;
}
.college-hero h1,
.college-hero p {
  color: #ffffff;
}
.college-hero p {
  width: min(780px, 100%);
  font-size: 18px;
  color: rgba(255, 255, 255, .9);
}
.college-layout {
  gap: 38px;
}
.section-card,
.side-panel section {
  position: relative;
  overflow: hidden;
  box-shadow: 0 18px 44px rgba(0, 54, 96, .07);
}
.section-card::before,
.side-panel section::before {
  content: "";
  position: absolute;
  inset: 0 0 auto;
  height: 4px;
  background: linear-gradient(90deg, #0066b3, #2e7d32);
}
.major-table {
  background: #ffffff;
}
.major-table tbody tr {
  transition: background .16s ease;
}
.major-table tbody tr:hover {
  background: #f4f9fc;
}
.major-table button,
.side-panel button {
  transition: background .16s ease, color .16s ease, border-color .16s ease;
}
.major-table button:hover,
.side-panel button:hover {
  color: #ffffff;
  background: #0066b3;
  border-color: #0066b3;
}
.faculty-grid article,
.training-grid article,
.news-list article {
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.faculty-grid article:hover,
.training-grid article:hover,
.news-list article:hover {
  transform: translateY(-4px);
  border-color: #9cc4df;
  box-shadow: 0 16px 34px rgba(0, 52, 91, .1);
}
.faculty-grid article {
  border-top: 4px solid #2e7d32;
}
.training-grid article {
  border-left: 4px solid #0066b3;
}
.side-panel section {
  border-top: 0;
}
@media (max-width: 920px) {
  .college-hero {
    padding: 42px 24px 34px;
  }
  .college-hero::after {
    display: none;
  }
}

.college-hero {
  box-shadow: 0 24px 70px rgba(0, 54, 96, .14);
}
.college-hero h1 {
  text-shadow: 0 10px 28px rgba(0, 0, 0, .18);
}
.section-card,
.side-panel section {
  border-radius: 2px;
}
.section-card h2,
.side-panel h2 {
  letter-spacing: .03em;
}
.major-table {
  box-shadow: inset 0 0 0 1px #dce5ee;
}
.major-table th {
  font-size: 15px;
}
.major-table td:first-child {
  color: #003b70;
  font-weight: 900;
}
.faculty-grid article {
  background:
    linear-gradient(160deg, #ffffff, #f3faf5);
}
.training-grid article {
  min-height: 128px;
}
.news-list article {
  border-left: 4px solid #0066b3;
}
.side-panel section:first-child {
  background:
    linear-gradient(160deg, #ffffff, #f3f8fc);
}
.side-panel button:hover {
  transform: translateX(4px);
}
</style>
