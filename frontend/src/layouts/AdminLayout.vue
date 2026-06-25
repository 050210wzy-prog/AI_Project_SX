<template>
  <el-container class="admin-shell">
    <el-aside width="280px" class="admin-aside">
      <div class="brand">
        <div class="brand-mark">A</div>
        <div>
          <h2>ACVTC 管理后台</h2>
          <p>官网 / 招生 / 学工 / 教务</p>
        </div>
      </div>

      <div class="profile-card">
        <span class="avatar">{{ auth.username?.slice(0, 1)?.toUpperCase() || 'A' }}</span>
        <div>
          <strong>{{ auth.username || '未登录' }}</strong>
          <p>{{ roleText }}</p>
        </div>
      </div>
      <el-button class="direct-btn" type="primary" @click="router.push('/admin/dashboard')">直接进入后台首页</el-button>

      <el-menu router :default-active="route.path" class="admin-menu">
        <el-menu-item v-if="can('dashboard')" index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据看板</span>
        </el-menu-item>
        <el-menu-item v-if="can('admissions')" index="/admin/admissions">
          <el-icon><School /></el-icon>
          <span>招生管理</span>
        </el-menu-item>
        <el-menu-item v-if="can('website')" index="/admin/website">
          <el-icon><Monitor /></el-icon>
          <span>官网管理</span>
        </el-menu-item>
        <el-menu-item v-if="can('crawler')" index="/admin/crawler">
          <el-icon><Download /></el-icon>
          <span>官网采集</span>
        </el-menu-item>
        <el-menu-item v-if="can('innovation')" index="/admin/innovation">
          <el-icon><MagicStick /></el-icon>
          <span>创新中心</span>
        </el-menu-item>
        <el-menu-item v-if="can('tickets')" index="/admin/tickets">
          <el-icon><Service /></el-icon>
          <span>咨询工单</span>
        </el-menu-item>

        <div class="menu-label">学校业务</div>
        <el-menu-item v-if="can('students')" index="/admin/students">
          <el-icon><UserFilled /></el-icon>
          <span>学生管理</span>
        </el-menu-item>
        <el-menu-item v-if="can('academic')" index="/admin/academic">
          <el-icon><Notebook /></el-icon>
          <span>教务管理</span>
        </el-menu-item>
        <el-menu-item v-if="can('settings')" index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>

      <div class="aside-footer">
        <el-button class="portal-btn" @click="router.push('/')">返回官网首页</el-button>
        <el-button text class="logout-btn" @click="logout">退出登录</el-button>
      </div>
    </el-aside>

    <el-container>
      <el-header class="admin-header">
        <div>
          <strong>{{ pageTitle }}</strong>
          <span>安徽交通职业技术学院一体化管理中心</span>
        </div>
        <div class="header-actions">
          <el-tag type="success" effect="light">运行正常</el-tag>
          <el-button @click="router.push('/chat')">招生 AI 助手</el-button>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { DataAnalysis, Download, MagicStick, Monitor, Notebook, School, Service, Setting, UserFilled } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const can = (perm) => auth.role === 'admin' || auth.permissions.includes(perm)

const roleText = computed(() => {
  const map = {
    admin: '超级管理员',
    admission: '招生管理员',
    editor: '官网编辑',
    reviewer: '内容审核员',
    teacher: '教务教师',
    operator: '运营管理员'
  }
  return map[auth.role] || '普通用户'
})

const pageTitle = computed(() => {
  const map = {
    '/admin/dashboard': '数据看板',
    '/admin/admissions': '招生管理',
    '/admin/website': '官网管理',
    '/admin/crawler': '官网采集',
    '/admin/innovation': '创新中心',
    '/admin/tickets': '咨询工单',
    '/admin/students': '学生管理',
    '/admin/academic': '教务管理',
    '/admin/settings': '系统设置'
  }
  return map[route.path] || '管理后台'
})

function logout() {
  auth.logout()
  router.push('/login')
}

onMounted(() => auth.fetchMe())
</script>

<style scoped>
.admin-shell {
  min-height: 100vh;
  background:
    radial-gradient(circle at 76% 8%, rgba(205, 255, 72, .42), transparent 26%),
    radial-gradient(circle at 58% 38%, rgba(157, 224, 255, .36), transparent 28%),
    linear-gradient(135deg, #fbfaf5 0%, #eef8f7 100%);
}
.admin-aside {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 22px 16px;
  border-right: 1px solid rgba(20, 35, 32, .1);
  background: rgba(255, 255, 251, .86);
  backdrop-filter: blur(18px);
  box-shadow: 18px 0 45px rgba(20, 35, 32, .06);
}
.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}
.brand-mark {
  width: 42px;
  height: 42px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  font-weight: 900;
  color: #101713;
  background: linear-gradient(135deg, #d8ff4f, #b5e4ff);
}
.brand h2 {
  margin: 0;
  font-size: 22px;
}
.brand p,
.profile-card p,
.admin-header span {
  margin: 4px 0 0;
  color: #66716d;
  font-size: 13px;
}
.profile-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  border: 1px solid rgba(20, 35, 32, .1);
  border-radius: 8px;
  background: rgba(255,255,255,.72);
}
.avatar {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-weight: 800;
  background: #111;
  color: #fff;
}
.admin-menu {
  margin-top: 22px;
  border: 0;
  background: transparent;
}
.direct-btn {
  width: 100%;
  margin-top: 12px;
  border-radius: 8px;
}
.admin-menu :deep(.el-menu-item) {
  height: 46px;
  margin: 6px 0;
  border-radius: 8px;
  color: #24302c;
}
.admin-menu :deep(.el-menu-item.is-active) {
  color: #111;
  background: linear-gradient(90deg, rgba(216,255,79,.9), rgba(181,228,255,.55));
  font-weight: 800;
}
.menu-label {
  margin: 20px 12px 8px;
  color: #8a938f;
  font-size: 12px;
  letter-spacing: .08em;
}
.aside-footer {
  position: absolute;
  left: 16px;
  right: 16px;
  bottom: 20px;
}
.portal-btn {
  width: 100%;
  border-radius: 8px;
}
.logout-btn {
  width: 100%;
  margin: 8px 0 0;
}
.admin-header {
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 28px;
  background: rgba(255,255,255,.62);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(20, 35, 32, .08);
}
.admin-header strong {
  display: block;
  font-size: 20px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}
.el-main {
  padding: 28px;
}
@media (max-width: 900px) {
  .admin-aside {
    width: 220px !important;
  }
  .brand h2 {
    font-size: 18px;
  }
}
</style>
