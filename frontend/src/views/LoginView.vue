<template>
  <div class="page login-page">
    <el-card class="login-card" shadow="never">
      <h2>管理员登录</h2>
      <p>请输入管理员账号进入后台管理系统</p>
      <el-input v-model="username" placeholder="用户名" />
      <el-input v-model="password" placeholder="密码" type="password" show-password />
      <el-button type="primary" size="large" :loading="loading" @click="login">登录后台</el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const auth = useAuthStore()
const username = ref('')
const password = ref('')
const loading = ref(false)

async function login() {
  if (!username.value || !password.value) {
    ElMessage.warning('请输入用户名和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(username.value, password.value)
    ElMessage.success('登录成功')
    router.push('/admin')
  } catch (error) {
    ElMessage.error(error?.response?.data?.detail || '登录失败，请检查账号和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  background:
    linear-gradient(135deg, rgba(0, 102, 179, .12), rgba(46, 125, 50, .12)),
    #f5f7fa;
}
.login-card {
  width: min(420px, 92vw);
  border-radius: 8px;
}
.login-card h2 {
  margin: 0 0 8px;
  color: #003b70;
}
.login-card p {
  margin: 0 0 16px;
  color: #5f6c78;
}
.login-card :deep(.el-input), .login-card .el-button {
  margin-top: 14px;
  width: 100%;
}
</style>
