<template>
  <main class="site-shell">
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
          <el-input v-model="keyword" placeholder="搜索新闻、通知、招生、专业" clearable @keyup.enter="search" />
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

    <section class="container breadcrumb-row">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item v-for="item in breadcrumbs" :key="item.path || item.label" :to="item.path ? { path: item.path } : undefined">
          {{ item.label }}
        </el-breadcrumb-item>
      </el-breadcrumb>
    </section>

    <slot />

    <footer class="footer">
      <div class="container footer-main">
        <div>
          <img src="https://www.acvtc.edu.cn/images/ftlogo.png" alt="安徽交通职业技术学院页脚标识" />
          <h2>安徽交通职业技术学院</h2>
          <p>新桥校区：安徽新桥国际产业园寿州大道16号</p>
          <p>包河校区：合肥市包河区合巢路114号</p>
          <p>招生咨询电话：0551-63444228　官网：www.acvtc.edu.cn</p>
        </div>
        <div class="footer-links">
          <button v-for="item in footerServices" :key="item" type="button" @click="goService(item)">
            {{ item }}
          </button>
        </div>
      </div>
      <div class="container copyright">© 安徽交通职业技术学院 版权所有　皖ICP备xxxxxx号</div>
    </footer>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ArrowDown, Connection, Menu, Message, Monitor, Service, User } from '@element-plus/icons-vue'

defineProps({
  breadcrumbs: {
    type: Array,
    default: () => []
  }
})

const router = useRouter()
const keyword = ref('')
const mobileOpen = ref(false)

const utilityLinks = [
  { title: '在线服务大厅', icon: Service },
  { title: 'WebVPN', icon: Connection },
  { title: '电子邮箱', icon: Message },
  { title: '信息门户', icon: Monitor },
  { title: 'English', icon: User }
]
const navs = ['首页', '学校概况', '院系设置', '招生就业', '教学科研', '校园文化', '国际交流', '信息服务', '智慧创新']
const roles = [
  { name: '在校学生', items: ['课表', '选课', '成绩查询', '图书馆'] },
  { name: '教职员工', items: ['办公系统', '科研申报', '工资查询'] },
  { name: '考生/家长', items: ['招生简章', '专业介绍', '历年分数'] },
  { name: '校友', items: ['校友活动', '返校预约', '校友捐赠'] },
  { name: '访客', items: ['校园地图', '联系方式', '办事指南'] }
]
const footerServices = ['办事大厅', '图书馆资源', '招生管理系统', '电子邮箱登录', 'VPN校外访问', '信息公开平台', '智慧校园', '院长信箱']

function goChannel(name) {
  mobileOpen.value = false
  if (name === '首页') router.push('/')
  else if (name === '智慧创新') router.push('/innovation')
  else router.push(`/channel/${encodeURIComponent(name)}`)
}
function goService(name) {
  mobileOpen.value = false
  if (name === 'English') {
    router.push('/english')
    return
  }
  if (name === '在线服务大厅') {
    window.open('https://ehall.acvtc.edu.cn/', '_blank')
    return
  }
  router.push(`/service/${encodeURIComponent(name)}`)
}
function search() {
  const key = keyword.value.trim()
  if (key) router.push(`/channel/${encodeURIComponent('信息服务')}?keyword=${encodeURIComponent(key)}`)
}
</script>

<style scoped>
.site-shell {
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
.breadcrumb-row {
  padding: 18px 0 0;
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
.footer-links button {
  border: 1px solid #bfd0de;
  background: #ffffff;
  color: #0066b3;
  padding: 11px 14px;
  cursor: pointer;
  font-weight: 800;
}
.copyright {
  margin-top: 26px;
  color: #6d7783;
  font-size: 14px;
}

.utility-bar {
  background: linear-gradient(90deg, #003b70, #005b9e);
}
.site-header {
  box-shadow: 0 10px 30px rgba(0, 54, 96, .06);
}
.brand-row {
  position: relative;
}
.brand-row::after {
  content: "";
  position: absolute;
  left: 72px;
  bottom: 12px;
  width: 180px;
  height: 2px;
  background: linear-gradient(90deg, #0066b3, #2e7d32);
}
.brand img {
  filter: drop-shadow(0 8px 14px rgba(0, 59, 112, .16));
}
.primary-nav {
  border-top: 1px solid #edf2f6;
}
.primary-nav button,
.role-nav {
  position: relative;
}
.primary-nav button::after,
.role-nav::after {
  content: "";
  position: absolute;
  left: 18px;
  right: 18px;
  bottom: 0;
  height: 3px;
  background: linear-gradient(90deg, #0066b3, #2e7d32);
  transform: scaleX(0);
  transform-origin: center;
  transition: transform .18s ease;
}
.primary-nav button:hover::after,
.role-nav:hover::after {
  transform: scaleX(1);
}
.breadcrumb-row {
  padding-top: 22px;
}
.footer {
  background:
    linear-gradient(180deg, #ffffff, #f7fafc);
}
.footer-links button:hover {
  color: #ffffff;
  background: #0066b3;
  border-color: #0066b3;
  transform: translateY(-2px);
}
@media (max-width: 920px) {
  .brand-row,
  .footer-main {
    display: grid;
    grid-template-columns: 1fr;
  }
  .primary-nav {
    grid-template-columns: repeat(3, 1fr);
  }
}
@media (max-width: 720px) {
  .container {
    width: min(100vw - 22px, 1180px);
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
  .footer-links {
    grid-template-columns: 1fr;
  }
}
</style>
