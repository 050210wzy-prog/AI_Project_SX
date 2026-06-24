<template>
  <site-shell :breadcrumbs="breadcrumbs">
    <section class="container detail-hero">
      <div>
        <span>{{ page.tag }}</span>
        <h1>{{ page.title }}</h1>
        <p>{{ page.summary }}</p>
        <div class="hero-actions">
          <el-button v-for="action in page.actions" :key="action.text" type="primary" plain @click="runAction(action)">
            {{ action.text }}
          </el-button>
        </div>
      </div>
      <aside>
        <b>{{ page.parent }}</b>
        <small>独立子页面</small>
        <p>内容支持后台文章实时更新，当前页面同时提供完整内置资料兜底。</p>
      </aside>
    </section>

    <section class="container detail-layout">
      <main>
        <section-card v-if="page.system" :title="page.system.title">
          <div class="system-panel">
            <div class="login-box">
              <h3>{{ page.system.loginTitle }}</h3>
              <template v-if="!systemAuthed">
                <el-input v-model="loginForm.username" placeholder="请输入统一身份认证账号" />
                <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
              </template>
              <div v-else class="login-status">
                <b>{{ auth.username || localUsername }}</b>
                <span>已通过统一身份认证</span>
              </div>
              <el-button type="primary" :loading="systemLoading" @click="systemLogin(page.system.name)">
                {{ systemAuthed ? '刷新数据' : '登录' }}
              </el-button>
              <p v-if="systemError" class="system-error">{{ systemError }}</p>
              <p>{{ page.system.note }}</p>
            </div>
            <div class="system-apps">
              <article v-for="item in page.system.apps" :key="item.title" @click="openSystemApp(item)">
                <h3>{{ item.title }}</h3>
                <p>{{ item.desc }}</p>
              </article>
            </div>
          </div>
          <div v-if="systemAuthed" class="real-system">
            <template v-if="page.title === '信息门户'">
              <h3>我的门户</h3>
              <p>当前用户：{{ portalData.user?.username }}　日期：{{ portalData.today }}</p>
              <div class="real-grid">
                <article v-for="item in portalData.schedule || []" :key="item.time" class="system-result">
                  <b>{{ item.time }}</b>
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.location }}</p>
                </article>
              </div>
              <h3>最新通知</h3>
              <div class="real-grid">
                <article v-for="item in portalData.notices || []" :key="item.id" class="system-result" @click="openArticle(item)">
                  <b>{{ item.date }}</b>
                  <h4>{{ item.title }}</h4>
                  <p>来自官网后台发布内容，进入后可查看正文和附件。</p>
                </article>
              </div>
            </template>
            <template v-else-if="page.title === 'WebVPN'">
              <h3>受保护资源</h3>
              <div class="real-grid">
                <article v-for="item in vpnResources" :key="item.title" @click="openResource(item)">
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.desc }}</p>
                </article>
              </div>
            </template>
            <template v-else-if="page.title === '电子邮箱'">
              <h3>站内邮箱：{{ mailbox }}</h3>
              <div class="mail-compose">
                <el-input v-model="mailForm.recipient" placeholder="收件人用户名或邮箱" />
                <el-input v-model="mailForm.subject" placeholder="邮件主题" />
                <el-input v-model="mailForm.body" type="textarea" :rows="4" placeholder="邮件正文" />
                <el-button type="primary" @click="sendMail">发送邮件</el-button>
              </div>
              <div class="mail-list">
                <article v-for="item in messages" :key="item.id" @click="markRead(item)">
                  <b>{{ item.subject }}</b>
                  <span>{{ item.sender }} → {{ item.recipient }}</span>
                  <p>{{ item.body }}</p>
                </article>
                <div v-if="!messages.length" class="empty-mail">
                  <b>暂无邮件</b>
                  <p>可以先给 admin 或 admin@example.com 发送一封测试邮件，发送后会立即出现在这里。</p>
                </div>
              </div>
            </template>
          </div>
        </section-card>

        <section-card v-for="section in page.sections" :key="section.title" :title="section.title">
          <p v-if="section.text" class="section-text">{{ section.text }}</p>
          <div v-if="section.items" class="info-grid">
            <article v-for="item in section.items" :key="item.title">
              <h3>{{ item.title }}</h3>
              <p>{{ item.desc }}</p>
            </article>
          </div>
          <ol v-if="section.timeline" class="timeline">
            <li v-for="item in section.timeline" :key="item.year">
              <b>{{ item.year }}</b>
              <span>{{ item.text }}</span>
            </li>
          </ol>
          <table v-if="section.table" class="data-table">
            <thead>
              <tr>
                <th v-for="head in section.table.headers" :key="head">{{ head }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, index) in section.table.rows" :key="index">
                <td v-for="cell in row" :key="cell">{{ cell }}</td>
              </tr>
            </tbody>
          </table>
        </section-card>

        <section-card title="官网实时更新">
          <div v-if="articles.length" class="article-list">
            <article v-for="item in articles" :key="item.id || item.title" @click="openArticle(item)">
              <time>{{ item.publish_date || '2026-05-20' }}</time>
              <h3>{{ item.title }}</h3>
              <p>{{ item.summary }}</p>
            </article>
          </div>
          <div v-else class="empty-updates">
            <h3>暂无后台发布的关联文章</h3>
            <p>后台在“官网管理”发布标题、摘要或正文包含“{{ page.title }}”的文章后，会自动出现在这里。</p>
          </div>
        </section-card>

        <section-card v-if="!page.system" title="在线办理">
          <div class="ticket-panel">
            <el-input v-model="ticketForm.title" placeholder="事项标题" />
            <el-input v-model="ticketForm.contact" placeholder="联系方式" />
            <el-input v-model="ticketForm.question" type="textarea" :rows="4" placeholder="请填写要咨询或办理的具体内容" />
            <el-button type="primary" @click="submitTicket">提交工单</el-button>
          </div>
        </section-card>
      </main>

      <aside class="side-panel">
        <section>
          <h2>本页导航</h2>
          <a v-for="section in page.sections" :key="section.title" href="#" @click.prevent>{{ section.title }}</a>
        </section>
        <section>
          <h2>办理说明</h2>
          <ol>
            <li v-for="item in page.steps" :key="item">{{ item }}</li>
          </ol>
        </section>
        <section>
          <h2>联系方式</h2>
          <p v-for="item in page.contacts" :key="item">{{ item }}</p>
        </section>
      </aside>
    </section>
  </site-shell>
</template>

<script setup>
import { computed, defineComponent, h, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'
import SiteShell from '../components/SiteShell.vue'
import http from '../api/http'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const articles = ref([])
const loginForm = reactive({ username: '', password: '' })
const mailForm = reactive({ recipient: '', subject: '', body: '' })
const ticketForm = reactive({ title: '', contact: '', question: '' })
const systemLoading = ref(false)
const systemAuthed = ref(Boolean(localStorage.getItem('token')))
const systemError = ref('')
const localUsername = ref(localStorage.getItem('username') || '')
const portalData = ref({})
const vpnResources = ref([])
const messages = ref([])
const mailbox = ref('')
const pageName = computed(() => String(route.params.name || '信息服务'))
const breadcrumbs = computed(() => [
  { label: page.value.parent || '信息服务', path: `/channel/${encodeURIComponent(page.value.parent || '信息服务')}` },
  { label: page.value.title }
])

const commonContacts = ['学校办公室：0551-63416906', '招生咨询电话：0551-63444228']
const commonActions = [{ text: '返回首页' }]

function pageConfig(parent, title, tag, summary, sections, extra = {}) {
  return {
    parent,
    title,
    tag,
    summary,
    sections,
    steps: extra.steps || ['查看页面说明', '阅读相关资料', '通过官网后台查看最新发布内容'],
    contacts: extra.contacts || commonContacts,
    actions: extra.actions || commonActions
  }
}

const pages = {
  学校简介: pageConfig('学校概况', '学校简介', 'About ACVTC', '系统展示学院办学历史、办学定位、专业特色和发展成效。', [
    {
      title: '学院概况',
      text: '安徽交通职业技术学院始建于1956年，长期扎根交通运输行业办学，面向综合交通运输、现代物流、智能交通和区域产业发展培养高素质技术技能人才。学校坚持“立足交通、服务行业、面向社会”的办学定位，形成了鲜明的交通职业教育特色。'
    },
    {
      title: '办学特色',
      items: [
        { title: '交通行业底色鲜明', desc: '围绕路、海、空、轨、车、邮、智建设现代综合交通专业集群。' },
        { title: '实践教学体系完善', desc: '依托校内外实训基地和行业企业项目，强化工学结合、岗课赛证融通。' },
        { title: '服务区域发展', desc: '持续为安徽综合交通运输体系和地方经济社会发展提供人才支撑。' },
        { title: '就业导向明确', desc: '以“基础厚、上手快、留得住、后劲足”为培养目标，提升毕业生岗位适应能力。' }
      ]
    },
    {
      title: '办学数据',
      table: {
        headers: ['项目', '数据'],
        rows: [
          ['创办时间', '1956年'],
          ['校园面积', '1200+亩'],
          ['在校生规模', '14000+人'],
          ['特色专业', '41个'],
          ['校外实习实训基地', '236+个']
        ]
      }
    }
  ]),
  历史沿革: pageConfig('学校概况', '历史沿革', 'History', '以时间轴呈现学院从交通学校到现代高职院校的发展脉络。', [
    {
      title: '发展时间轴',
      timeline: [
        { year: '1956', text: '安徽交通学校创立。' },
        { year: '1958', text: '升格为安徽交通学院（本科）。' },
        { year: '1988', text: '安徽大学交通分校设立。' },
        { year: '2001', text: '合并组建安徽交通职业技术学院。' },
        { year: '2008', text: '成为省级示范高职院校。' },
        { year: '2014', text: '建成国家骨干高职院校。' },
        { year: '2019', text: '立项安徽省技能型高水平大学建设单位。' }
      ]
    },
    {
      title: '历史文脉',
      text: '学校在长期办学历程中始终与交通行业同频共振，围绕行业技术变革和岗位需求优化专业结构，逐步形成服务综合交通运输体系的职业教育品牌。'
    }
  ]),
  现任领导: pageConfig('学校概况', '现任领导', 'Leadership', '展示学校领导班子成员及主要工作分工。', [
    {
      title: '领导班子',
      items: [
        { title: '杨菲铃', desc: '党委书记，主持学校党委全面工作。' },
        { title: '孙晓雷', desc: '党委副书记、校长，主持学校行政全面工作。' }
      ]
    },
    {
      title: '工作机制',
      text: '学校坚持党委领导下的校长负责制，围绕党的建设、人才培养、专业建设、学生发展、社会服务和校园治理持续推进高质量发展。'
    }
  ]),
  机构设置: pageConfig('学校概况', '机构设置', 'Organization', '展示党政管理机构、教学机构、教辅机构和服务机构。', [
    {
      title: '机构分类',
      items: [
        { title: '党政管理机构', desc: '办公室、组织人事、教务、学生、财务、总务等职能部门。' },
        { title: '教学机构', desc: '土木建筑、汽车工程、轨道交通、航运工程、航空与低空经济、人工智能、经济管理等二级学院。' },
        { title: '教辅机构', desc: '图书馆、信息中心、实训中心等教学支撑单位。' },
        { title: '服务机构', desc: '后勤服务、就业服务、心理健康、校园安全等服务体系。' }
      ]
    }
  ]),
  校园地图: pageConfig('学校概况', '校园地图', 'Campus Map', '提供新桥校区、包河校区地址和交通指引。', [
    {
      title: '校区地址',
      table: {
        headers: ['校区', '地址', '主要功能'],
        rows: [
          ['新桥校区', '安徽新桥国际产业园寿州大道16号', '教学、实训、学生生活和综合服务'],
          ['包河校区', '合肥市包河区合巢路114号', '继续教育、培训和部分管理服务']
        ]
      }
    },
    {
      title: '交通指引',
      items: [
        { title: '访客入校', desc: '建议提前联系对接部门，按校园访客管理要求办理入校手续。' },
        { title: '考生来校', desc: '招生咨询、校园开放日和报到期间，以学校最新通知中的交通安排为准。' }
      ]
    }
  ]),
  学校标识: pageConfig('学校概况', '学校标识', 'Visual Identity', '展示校徽、校名、校训和学校视觉识别基础规范。', [
    {
      title: '校训与精神',
      items: [
        { title: '校训', desc: '勤奋、通达、敬业、乐群。' },
        { title: '办学理念', desc: '经世致用、实学报国。' },
        { title: '办学定位', desc: '立足交通、服务行业、面向社会。' },
        { title: '主题色彩', desc: '交通蓝象征通达，生机绿象征职业教育活力。' }
      ]
    }
  ]),
  招生信息: pageConfig('招生就业', '招生信息', 'Admissions', '集中发布普通高考、分类考试、定向军士、联合培养本科等招生信息。', [
    {
      title: '招生类别',
      items: [
        { title: '普通高考招生', desc: '发布招生计划、专业目录、录取规则和报到须知。' },
        { title: '分类考试招生', desc: '提供分类考试报名、测试安排和录取查询。' },
        { title: '定向军士招生', desc: '展示提前批次报考流程、体检政审和培养说明。' },
        { title: '联合培养本科', desc: '发布联合培养本科项目政策和培养安排。' }
      ]
    },
    {
      title: '考生服务',
      items: [
        { title: '专业查询', desc: '按学院和专业群查看培养目标、核心课程和就业方向。' },
        { title: '录取查询', desc: '按考生信息查询录取结果和报到提示。' },
        { title: '智能咨询', desc: '通过招生问答入口了解政策、专业和分数建议。' }
      ]
    }
  ], { actions: [{ text: '智能招生咨询' }, { text: '查看历年分数' }] }),
  历年分数: pageConfig('招生就业', '历年分数', 'Admission Score', '按年份、专业、科类展示录取分数线和报考参考。', [
    {
      title: '录取分数参考',
      table: {
        headers: ['年份', '专业', '科类', '最低分', '最高分'],
        rows: [
          ['2025', '道路与桥梁工程技术', '物理类', '389', '421'],
          ['2025', '新能源汽车技术', '物理类', '402', '438'],
          ['2025', '城市轨道交通运营管理', '历史类', '374', '416'],
          ['2025', '人工智能技术应用', '物理类', '396', '432']
        ]
      }
    },
    {
      title: '使用说明',
      text: '历年分数仅供报考参考，正式录取结果以省级招生考试机构和学校最终发布信息为准。建议结合位次、专业热度和个人兴趣综合判断。'
    }
  ], { actions: [{ text: '智能招生咨询' }, { text: '进入招生管理' }] }),
  招生简章: pageConfig('招生就业', '招生简章', 'Brochure', '展示招生章程、招生计划、录取规则、收费标准和联系方式。', [
    {
      title: '简章内容',
      items: [
        { title: '招生章程', desc: '包含学校概况、招生计划、录取原则、收费标准和监督机制。' },
        { title: '专业目录', desc: '展示各专业培养目标、核心课程、就业方向和所属学院。' },
        { title: '助学政策', desc: '说明奖助贷补免勤等学生资助体系。' },
        { title: '联系方式', desc: '提供招生咨询电话、官网入口和常见问题说明。' }
      ]
    }
  ]),
  报考指南: pageConfig('招生就业', '报考指南', 'Guide', '面向考生和家长提供报考流程、专业选择、志愿填报建议和常见问题。', [
    {
      title: '报考流程',
      items: [
        { title: '了解学校', desc: '查看学校概况、专业集群、校园环境和就业质量。' },
        { title: '查阅专业', desc: '结合兴趣、职业方向和交通行业趋势选择专业。' },
        { title: '参考分数', desc: '结合历年分数线和位次，形成稳妥的志愿梯度。' },
        { title: '咨询确认', desc: '通过招生咨询入口确认政策、计划和录取规则。' }
      ]
    }
  ], { actions: [{ text: '查看历年分数' }, { text: '智能招生咨询' }] }),
  专业目录: pageConfig('招生就业', '专业目录', 'Majors', '集中展示各专业培养方向、所属学院和就业面向。', [
    {
      title: '专业群',
      items: [
        { title: '路', desc: '交通土建施工群：道路与桥梁工程技术、建筑工程技术、土木工程检测技术等。' },
        { title: '车', desc: '新能源汽车与装备群：新能源汽车技术、汽车检测与维修、智能网联汽车技术等。' },
        { title: '轨', desc: '城市轨道交通群：城市轨道车辆应用技术、城市轨道交通运营管理等。' },
        { title: '智', desc: '交通信息技术群：人工智能技术应用、大数据技术、智能交通技术等。' }
      ]
    }
  ]),
  就业信息网: pageConfig('招生就业', '就业信息网', 'Employment', '整合校园招聘、就业指导、校友企业招聘和就业政策。', [
    {
      title: '就业服务',
      items: [
        { title: '校园招聘会', desc: '发布招聘会邀请函、参会企业和岗位信息。' },
        { title: '就业指导', desc: '提供简历制作、面试辅导、政策解读和职业规划服务。' },
        { title: '校友企业招聘', desc: '汇聚校友企业和行业合作单位招聘需求。' }
      ]
    }
  ]),
  助学政策: pageConfig('招生就业', '助学政策', 'Student Aid', '展示奖学金、助学金、助学贷款、勤工助学和困难帮扶政策。', [
    {
      title: '资助体系',
      items: [
        { title: '奖学金', desc: '奖励品学兼优和技能竞赛表现突出的学生。' },
        { title: '助学金', desc: '帮助家庭经济困难学生顺利完成学业。' },
        { title: '助学贷款', desc: '按国家政策提供生源地信用助学贷款指导。' },
        { title: '勤工助学', desc: '提供校内勤工助学岗位和实践机会。' }
      ]
    }
  ]),
  '征兵（定向军士）专栏': pageConfig('招生就业', '征兵（定向军士）专栏', 'Sergeant Program', '发布定向军士、征兵政策、报名条件和培养说明。', [
    {
      title: '专栏内容',
      items: [
        { title: '政策解读', desc: '说明定向培养军士招生政策和培养要求。' },
        { title: '报考流程', desc: '展示报名、体检、政审、录取等关键环节。' },
        { title: '培养管理', desc: '介绍在校培养、军事素养训练和就业去向。' }
      ]
    }
  ]),
  校历: pageConfig('信息服务', '校历', 'Calendar', '查看教学周、节假日、考试周、报到注册和重要校园活动。', [
    {
      title: '本学期关键安排',
      items: [
        { title: '2026-05-01 至 2026-05-05', desc: '劳动节放假，调休和值班安排以学校通知为准。' },
        { title: '2026-06-18 至 2026-06-20', desc: '期末考试周，各学院按教务安排组织考试。' },
        { title: '2026-09-01', desc: '新生报到，按录取通知书和迎新系统提示办理。' }
      ]
    }
  ]),
  图书馆资源: pageConfig('信息服务', '图书馆资源', 'Library', '提供馆藏检索、电子资源、座位预约、借阅规则和读者培训服务。', [
    {
      title: '图书馆服务',
      items: [
        { title: '馆藏检索', desc: '查询纸质图书、期刊和馆藏位置。' },
        { title: '电子资源', desc: '访问电子图书、数据库和学习平台。' },
        { title: '座位预约', desc: '预约阅览座位和研讨空间。' },
        { title: '读者培训', desc: '提供信息检索、论文写作和资源使用培训。' }
      ]
    }
  ]),
  办事大厅: pageConfig('信息服务', '办事大厅', 'Online Service', '面向师生提供证明申请、成绩单、报修、报销、场地借用等一站式服务。', [
    {
      title: '常用办理事项',
      items: [
        { title: '学生证明申请', desc: '办理在读证明、成绩证明等事项。' },
        { title: '后勤报修', desc: '提交宿舍、教室、公共区域维修需求。' },
        { title: '财务报销', desc: '面向教职工提供报销流程和进度查询。' },
        { title: '场地借用', desc: '提交会议室、报告厅、运动场地等使用申请。' }
      ]
    }
  ]),
  在线服务大厅: pageConfig('信息服务', '在线服务大厅', 'Online Service Hall', '面向师生提供证明申请、成绩单、后勤报修、财务报销、场地借用等一站式在线办理服务。', [
    {
      title: '常用事项',
      items: [
        { title: '学生事务', desc: '在读证明、成绩单、学籍异动、奖助申请等学生服务。' },
        { title: '教职工事务', desc: '财务报销、用印申请、会议室预约、办公用品申领。' },
        { title: '后勤服务', desc: '宿舍报修、教室设备维护、校园环境和物业服务。' },
        { title: '进度查询', desc: '按事项编号或个人账号查询办理进度和审核结果。' }
      ]
    },
    {
      title: '办理流程',
      timeline: [
        { year: '01', text: '选择需要办理的事项。' },
        { year: '02', text: '填写申请信息并上传材料。' },
        { year: '03', text: '等待相关部门审核办理。' },
        { year: '04', text: '在线查看结果或下载证明材料。' }
      ]
    }
  ], { actions: [{ text: '进入办事大厅' }, { text: '查看办理进度' }] }),
  WebVPN: {
    ...pageConfig('信息服务', 'WebVPN', 'Remote Access', '为师生在校外访问校内资源、数据库和业务系统提供安全通道。', [
    {
      title: '可访问资源',
      items: [
        { title: '校内业务系统', desc: '在校外访问部分教务、办公、科研和信息服务系统。' },
        { title: '图书馆数据库', desc: '访问学校订购的电子资源、数据库和学习平台。' },
        { title: '信息门户', desc: '通过统一身份认证进入个人信息和常用应用。' },
        { title: '安全提醒', desc: '请妥善保管账号密码，离开公共电脑时及时退出登录。' }
      ]
    },
    {
      title: '使用说明',
      text: 'WebVPN 入口通常需要使用学校统一身份认证账号登录。若无法访问，请确认账号状态、浏览器兼容性和网络环境，或联系信息中心。'
    }
  ], { actions: [{ text: '打开 WebVPN' }, { text: '网络服务支持' }], contacts: ['信息中心：0551-63416906', '服务时间：工作日 8:30-17:00'] }),
    system: {
      name: 'WebVPN',
      title: 'WebVPN 校内资源入口',
      loginTitle: '统一身份认证登录',
      note: '使用统一身份认证登录后访问校内资源。当前入口已接入后端鉴权，公开可确认的系统将打开学校真实地址。',
      apps: [
        { title: '教务系统', url: '/service/常用系统导航', desc: '校外访问课表、成绩、选课等教务服务。' },
        { title: '图书馆数据库', url: 'https://www.acvtc.edu.cn/tsg/', desc: '访问图书馆主页、电子资源和学习服务。' },
        { title: '协同办公系统', url: 'https://jyoa.acvtc.edu.cn/', desc: '进入公文流转、会议和流程审批。' },
        { title: '网上办事大厅', url: 'https://ehall.acvtc.edu.cn/', desc: '进入学校一站式线上办事服务。' }
      ]
    }
  },
  电子邮箱: {
    ...pageConfig('信息服务', '电子邮箱', 'Email Service', '提供学校电子邮箱登录、账号维护、密码找回和邮箱使用帮助。', [
    {
      title: '邮箱服务',
      items: [
        { title: '邮箱登录', desc: '使用学校邮箱账号收发邮件，支持教学、办公和对外联系。' },
        { title: '密码维护', desc: '提供密码修改、找回和账号安全提醒。' },
        { title: '客户端配置', desc: '支持在常用邮件客户端中配置收发服务器。' },
        { title: '常见问题', desc: '处理登录失败、容量不足、邮件退信和异常提醒。' }
      ]
    }
  ], { actions: [{ text: '进入邮箱' }, { text: '账号帮助' }], contacts: ['信息中心：0551-63416906'] }),
    system: {
      name: '电子邮箱',
      title: '电子邮箱',
      loginTitle: '邮箱账号登录',
      note: '使用统一身份认证登录后收发站内邮件。邮件会写入 MySQL 数据库，可真实保存、读取和标记已读。',
      apps: [
        { title: '收件箱', desc: '查看学校通知、课程信息和办公邮件。' },
        { title: '写邮件', desc: '撰写并发送教学、办公和对外联系邮件。' },
        { title: '通讯录', desc: '查找部门、教师和常用联系人。' },
        { title: '邮箱设置', desc: '维护签名、转发、自动回复和安全选项。' }
      ]
    }
  },
  信息门户: {
    ...pageConfig('信息服务', '信息门户', 'Information Portal', '汇聚个人信息、教务服务、办公系统、通知公告和常用应用入口。', [
    {
      title: '门户功能',
      items: [
        { title: '统一身份认证', desc: '一个账号访问多类校园信息系统。' },
        { title: '个人服务', desc: '查看课表、成绩、待办、通知和个人信息。' },
        { title: '业务应用', desc: '集成教务、办公、财务、资产、图书馆等应用入口。' },
        { title: '消息提醒', desc: '集中接收通知公告、流程待办和系统提醒。' }
      ]
    }
  ], { actions: [{ text: '进入信息门户' }, { text: '账号帮助' }], contacts: ['信息中心：0551-63416906'] }),
    system: {
      name: '信息门户',
      title: '信息门户',
      loginTitle: '统一身份认证登录',
      note: '使用统一身份认证登录后读取个人门户、待办课程和官网后台通知。',
      apps: [
        { title: '我的课表', desc: '查看本周课程、教学地点和任课教师。' },
        { title: '成绩查询', desc: '查看课程成绩、考试安排和学业进度。' },
        { title: '待办事项', desc: '查看审批、通知、报修和个人待办。' },
        { title: '常用应用', desc: '进入教务、办公、图书馆、缴费和服务系统。' }
      ]
    }
  },
  通知公告: pageConfig('信息服务', '通知公告', 'Notice', '集中展示学校重要通知、公告、公示和提醒事项。', [
    { title: '公告分类', items: [
      { title: '教学通知', desc: '课程、考试、选课和教务安排。' },
      { title: '行政公告', desc: '会议、值班、采购、公示等事项。' },
      { title: '学生通知', desc: '奖助、活动、安全和就业相关提醒。' }
    ] }
  ]),
  办事指南: pageConfig('信息服务', '办事指南', 'Guide', '提供师生常用事项办理流程、材料清单和联系方式。', [
    { title: '指南内容', items: [
      { title: '学生事务', desc: '学籍、证明、奖助、宿舍和心理健康服务。' },
      { title: '教师事务', desc: '科研、报销、场地、资产和办公系统服务。' },
      { title: '访客事务', desc: '校园地图、联系方式、入校预约和办事咨询。' }
    ] }
  ]),
  信息公开: pageConfig('信息服务', '信息公开', 'Disclosure', '依法公开学校基本情况、重大事项、招生就业、财务资产和质量报告。', [
    { title: '公开目录', items: [
      { title: '基本信息', desc: '学校章程、机构设置、办学规模等。' },
      { title: '招生就业', desc: '招生政策、录取信息和就业质量报告。' },
      { title: '财务资产', desc: '收费标准、采购公告和资产管理信息。' }
    ] }
  ]),
  常用系统导航: pageConfig('信息服务', '常用系统导航', 'Systems', '汇聚师生常用信息系统入口。', [
    { title: '系统入口', items: [
      { title: '信息门户', desc: '统一身份认证和个人信息服务入口。' },
      { title: '教务系统', desc: '课表、选课、成绩、考试和教学评价。' },
      { title: '办公系统', desc: '公文流转、通知发布、会议和流程审批。' },
      { title: 'WebVPN', desc: '校外访问校内资源和业务系统。' }
    ] }
  ]),
  网络服务: pageConfig('信息服务', '网络服务', 'Network', '提供校园网、VPN、邮箱、账号和信息化支持。', [
    { title: '服务内容', items: [
      { title: '校园网', desc: '网络接入、故障报修和使用说明。' },
      { title: '电子邮箱', desc: '学校邮箱登录、密码维护和使用帮助。' },
      { title: '账号服务', desc: '统一身份认证账号开通、找回和安全提醒。' }
    ] }
  ])
}

const fallback = computed(() =>
  pageConfig('信息服务', pageName.value, 'Service', `${pageName.value}相关内容在此集中展示，后台发布后可实时更新。`, [
    {
      title: '页面说明',
      items: [
        { title: pageName.value, desc: '这是独立子页面，支持展示栏目资料、服务说明、附件下载和后台实时发布内容。' },
        { title: '实时更新', desc: '后台在官网管理中发布关联文章后，会自动出现在“官网实时更新”区域。' }
      ]
    }
  ])
)
const page = computed(() => pages[pageName.value] || fallback.value)

function runAction(action) {
  if (action.text.includes('招生管理')) router.push('/admin/admissions')
  else if (action.text.includes('咨询')) router.push('/chat')
  else if (action.text.includes('历年分数')) router.push('/service/历年分数')
  else if (action.text.includes('返回首页')) router.push('/')
  else if (action.text.includes('办事大厅')) window.open('https://ehall.acvtc.edu.cn/', '_blank')
  else if (action.text.includes('OA') || action.text.includes('协同办公')) window.open('https://jyoa.acvtc.edu.cn/', '_blank')
  else if (action.text.includes('WebVPN')) router.push('/service/WebVPN')
  else if (action.text.includes('邮箱')) router.push('/service/电子邮箱')
  else if (action.text.includes('信息门户')) router.push('/service/信息门户')
  else if (action.text.includes('账号帮助')) router.push('/service/网络服务')
  else if (action.text.includes('网络服务支持')) router.push('/service/网络服务')
  else {
    ticketForm.title = action.text
    ticketForm.question = `申请办理：${action.text}`
    ElMessage.info('请在页面下方“在线办理”提交具体需求')
  }
}
async function systemLogin(name) {
  systemLoading.value = true
  systemError.value = ''
  try {
    if (!auth.token) {
      if (!loginForm.username || !loginForm.password) {
        ElMessage.warning('请输入账号和密码')
        return
      }
      await auth.login(loginForm.username, loginForm.password)
      localUsername.value = auth.username
    }
    systemAuthed.value = true
    await loadSystemData()
    ElMessage.success(`${name}登录成功`)
  } catch (error) {
    const message = error?.response?.data?.detail || '登录失败，请确认后端已启动，并检查账号密码'
    systemError.value = message
    ElMessage.error(message)
  } finally {
    systemLoading.value = false
  }
}
async function loadSystemData() {
  if (!systemAuthed.value) return
  try {
    if (page.value.title === '信息门户') {
      const { data } = await http.get('/systems/portal')
      portalData.value = data
    } else if (page.value.title === 'WebVPN') {
      const { data } = await http.get('/systems/vpn/resources')
      vpnResources.value = data.resources || []
    } else if (page.value.title === '电子邮箱') {
      const { data } = await http.get('/systems/mail/messages')
      mailbox.value = data.mailbox
      messages.value = data.messages || []
    }
  } catch (error) {
    if (error?.response?.status === 401) {
      systemAuthed.value = false
      systemError.value = '登录已失效，请重新输入账号密码'
    }
  }
}
function openSystemApp(item) {
  if (!systemAuthed.value) {
    ElMessage.warning('请先登录')
    return
  }
  if (item.url?.startsWith('http')) {
    window.open(item.url, '_blank')
    return
  }
  if (item.url) {
    router.push(item.url)
    return
  }
  ElMessage.success(`${item.title}已进入`)
}
function openResource(item) {
  if (!systemAuthed.value) {
    ElMessage.warning('请先登录 WebVPN')
    return
  }
  if (item.url?.startsWith('http')) window.open(item.url, '_blank')
  else router.push(item.url || '/')
}
async function sendMail() {
  if (!systemAuthed.value) {
    ElMessage.warning('请先登录邮箱')
    return
  }
  try {
    await http.post('/systems/mail/messages', mailForm)
    mailForm.recipient = ''
    mailForm.subject = ''
    mailForm.body = ''
    await loadSystemData()
    ElMessage.success('邮件发送成功')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '邮件发送失败')
  }
}
async function markRead(item) {
  await http.post(`/systems/mail/messages/${item.id}/read`)
  item.is_read = true
}
async function submitTicket() {
  if (!ticketForm.title || !ticketForm.question) {
    ElMessage.warning('请填写事项标题和具体内容')
    return
  }
  const { data } = await http.post('/chat/tickets', {
    title: ticketForm.title,
    category: page.value.title,
    question: ticketForm.question,
    contact: ticketForm.contact
  })
  ticketForm.title = ''
  ticketForm.contact = ''
  ticketForm.question = ''
  ElMessage.success(`工单已提交，编号：${data.id}`)
}
function openArticle(item) {
  if (item.id) router.push(`/article/${item.id}`)
}
async function loadArticles() {
  try {
    const { data } = await http.get('/website/articles', { params: { keyword: page.value.title } })
    articles.value = Array.isArray(data) ? data : []
  } catch {
    articles.value = []
  }
}

const SectionCard = defineComponent({
  props: { title: String },
  setup(props, { slots }) {
    return () => h('section', { class: 'section-card' }, [h('h2', props.title), h('div', slots.default?.())])
  }
})

onMounted(async () => {
  await loadArticles()
  await loadSystemData()
})
watch(() => route.params.name, async () => {
  await loadArticles()
  await loadSystemData()
})
</script>

<style scoped>
.container {
  width: min(1180px, calc(100vw - 40px));
  margin: 0 auto;
}
.detail-hero {
  position: relative;
  display: grid;
  grid-template-columns: 1fr 290px;
  gap: 36px;
  align-items: end;
  margin-top: 24px;
  padding: 62px 52px 46px;
  overflow: hidden;
  border: 1px solid #dce5ee;
  border-bottom: 4px solid #0066b3;
  background:
    linear-gradient(120deg, rgba(255, 255, 255, .97), rgba(238, 247, 242, .95)),
    radial-gradient(circle at 88% 22%, rgba(46, 125, 50, .22), transparent 28%),
    radial-gradient(circle at 76% 70%, rgba(0, 102, 179, .18), transparent 26%);
}
.detail-hero::after {
  content: "";
  position: absolute;
  right: -80px;
  top: -90px;
  width: 300px;
  height: 300px;
  border: 48px solid rgba(0, 102, 179, .08);
  border-radius: 50%;
}
.detail-hero > * {
  position: relative;
  z-index: 1;
}
.detail-hero span {
  color: #2e7d32;
  font-weight: 900;
  letter-spacing: .16em;
  text-transform: uppercase;
}
.detail-hero h1 {
  margin: 10px 0 12px;
  color: #003b70;
  font-size: clamp(42px, 6vw, 70px);
}
.detail-hero p {
  color: #5f6c78;
  font-size: 18px;
  line-height: 1.8;
}
.detail-hero aside {
  border-left: 4px solid #2e7d32;
  background: #ffffff;
  padding: 20px;
  box-shadow: 0 16px 34px rgba(0, 52, 91, .08);
}
.detail-hero aside b {
  display: block;
  color: #003b70;
  font-size: 24px;
}
.detail-hero aside small {
  color: #c41e3a;
  font-weight: 900;
}
.hero-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 18px;
}
.detail-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 38px;
  padding: 36px 0 72px;
}
main {
  display: grid;
  gap: 22px;
}
.section-card,
.side-panel section {
  position: relative;
  overflow: hidden;
  background: #ffffff;
  border: 1px solid #dce5ee;
  padding: 26px;
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
.section-card h2,
.side-panel h2 {
  margin: 0 0 18px;
  color: #003b70;
}
.section-text,
.empty-updates p,
.side-panel p,
.side-panel li {
  color: #5f6c78;
  line-height: 1.85;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.info-grid article,
.article-list article {
  border: 1px solid #dce5ee;
  border-left: 4px solid #2e7d32;
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  padding: 18px;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.info-grid article:hover,
.article-list article:hover {
  transform: translateY(-4px);
  border-color: #9cc4df;
  box-shadow: 0 16px 34px rgba(0, 52, 91, .1);
}
.info-grid h3,
.article-list h3,
.empty-updates h3 {
  margin: 0 0 8px;
  color: #1d2b39;
}
.info-grid p,
.article-list p {
  color: #5f6c78;
  line-height: 1.8;
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
  padding: 15px 0 15px 14px;
  border-bottom: 1px solid #edf1f5;
  position: relative;
}
.timeline li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 22px;
  width: 6px;
  height: 6px;
  background: #2e7d32;
}
.timeline b,
.article-list time {
  color: #c41e3a;
  font-weight: 900;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  background: #ffffff;
}
.data-table th,
.data-table td {
  border: 1px solid #dce5ee;
  padding: 13px;
  text-align: left;
}
.data-table th {
  color: #003b70;
  background: #f5f7fa;
}
.data-table tbody tr:hover {
  background: #f4f9fc;
}
.article-list {
  display: grid;
  gap: 12px;
}
.article-list article {
  cursor: pointer;
}
.empty-updates {
  border: 1px dashed #b8cad8;
  background: #f7fafc;
  padding: 20px;
}
.system-panel {
  display: grid;
  grid-template-columns: 320px 1fr;
  gap: 22px;
}
.login-box {
  display: grid;
  gap: 12px;
  align-content: start;
  padding: 22px;
  background:
    linear-gradient(160deg, #003b70, #0066b3 62%, #2e7d32);
  color: #ffffff;
  box-shadow: 0 18px 42px rgba(0, 54, 96, .18);
}
.login-box h3 {
  margin: 0 0 6px;
  color: #ffffff;
}
.login-box p {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, .82);
  line-height: 1.7;
  font-size: 13px;
}
.login-status {
  display: grid;
  gap: 6px;
  padding: 14px;
  border: 1px solid rgba(255, 255, 255, .26);
  background: rgba(255, 255, 255, .12);
}
.login-status b {
  color: #ffffff;
  font-size: 20px;
}
.login-status span {
  color: rgba(255, 255, 255, .86);
}
.login-box .system-error {
  padding: 10px 12px;
  background: rgba(196, 30, 58, .95);
  color: #ffffff;
  font-weight: 800;
}
.system-apps {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.system-apps article {
  border: 1px solid #dce5ee;
  border-top: 4px solid #0066b3;
  background: linear-gradient(180deg, #ffffff, #fbfdff);
  padding: 18px;
  cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.system-apps article:nth-child(2n) {
  border-top-color: #2e7d32;
}
.system-apps article:hover {
  transform: translateY(-4px);
  border-color: #9cc4df;
  box-shadow: 0 16px 34px rgba(0, 52, 91, .1);
}
.system-apps h3 {
  margin: 0 0 8px;
  color: #003b70;
}
.system-apps p {
  margin: 0;
  color: #5f6c78;
  line-height: 1.8;
}
.real-system {
  margin-top: 22px;
  padding: 22px;
  border: 1px solid #dce5ee;
  background:
    linear-gradient(180deg, #f8fbfe, #ffffff);
}
.real-system h3 {
  margin: 0 0 14px;
  color: #003b70;
}
.real-system h3:not(:first-child) {
  margin-top: 22px;
}
.real-system > p {
  margin: 0 0 16px;
  color: #5f6c78;
}
.real-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}
.real-grid article,
.mail-list article {
  border: 1px solid #dce5ee;
  border-left: 4px solid #0066b3;
  background: #ffffff;
  padding: 16px;
  cursor: pointer;
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
}
.real-grid article:nth-child(2n),
.mail-list article:nth-child(2n) {
  border-left-color: #2e7d32;
}
.real-grid article:hover,
.mail-list article:hover {
  transform: translateY(-3px);
  border-color: #9cc4df;
  box-shadow: 0 14px 30px rgba(0, 52, 91, .1);
}
.real-grid b,
.mail-list span {
  color: #c41e3a;
  font-size: 13px;
  font-weight: 900;
}
.real-grid h4,
.mail-list b {
  display: block;
  margin: 6px 0 8px;
  color: #1d2b39;
}
.real-grid p,
.mail-list p {
  margin: 0;
  color: #5f6c78;
  line-height: 1.7;
}
.mail-compose {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 16px;
}
.mail-compose :deep(.el-textarea),
.mail-compose .el-button {
  grid-column: 1 / -1;
}
.mail-list {
  display: grid;
  gap: 12px;
}
.ticket-panel {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.ticket-panel :deep(.el-textarea),
.ticket-panel .el-button {
  grid-column: 1 / -1;
}
.empty-mail {
  border: 1px dashed #b8cad8;
  background: #f7fafc;
  padding: 18px;
}
.empty-mail b {
  display: block;
  margin-bottom: 6px;
  color: #003b70;
}
.empty-mail p {
  margin: 0;
  color: #5f6c78;
  line-height: 1.7;
}
.side-panel {
  align-self: start;
  position: sticky;
  top: 18px;
  display: grid;
  gap: 16px;
}
.side-panel a {
  display: block;
  border-bottom: 1px solid #edf1f5;
  color: #0066b3;
  padding: 10px 0;
  text-decoration: none;
  font-weight: 800;
}
.side-panel ol {
  margin: 0;
  padding-left: 20px;
}
.side-panel li {
  margin: 8px 0;
}
@media (max-width: 900px) {
  .detail-hero,
  .detail-layout,
  .info-grid,
  .system-panel,
  .system-apps,
  .real-grid,
  .mail-compose,
  .ticket-panel {
    grid-template-columns: 1fr;
  }
  .detail-hero {
    padding: 42px 24px 34px;
  }
  .side-panel {
    position: static;
  }
}

.detail-hero {
  box-shadow: 0 24px 70px rgba(0, 54, 96, .11);
}
.detail-hero h1 {
  letter-spacing: .02em;
}
.detail-hero aside {
  border-radius: 2px;
}
.section-card,
.side-panel section {
  border-radius: 2px;
}
.section-card h2,
.side-panel h2 {
  letter-spacing: .03em;
}
.section-card h2::before,
.side-panel h2::before {
  content: "";
  display: inline-block;
  width: 5px;
  height: 22px;
  margin-right: 10px;
  vertical-align: -4px;
  background: #2e7d32;
}
.info-grid article {
  min-height: 132px;
}
.info-grid article:nth-child(2n) {
  border-left-color: #0066b3;
}
.data-table {
  box-shadow: inset 0 0 0 1px #dce5ee;
}
.data-table td:first-child {
  color: #003b70;
  font-weight: 900;
}
.empty-updates {
  border-left: 4px solid #0066b3;
}
.side-panel section:first-child {
  background:
    linear-gradient(160deg, #ffffff, #f3f8fc);
}
.side-panel a:hover {
  color: #2e7d32;
  padding-left: 6px;
}
</style>
