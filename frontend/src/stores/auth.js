import { defineStore } from 'pinia'
import http from '../api/http'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    username: localStorage.getItem('username') || '',
    role: localStorage.getItem('role') || '',
    permissions: []
  }),
  actions: {
    async login(username, password) {
      const { data } = await http.post('/auth/login', { username, password })
      this.token = data.access_token
      this.username = data.username
      this.role = data.role
      this.permissions = data.permissions || []
      localStorage.setItem('token', this.token)
      localStorage.setItem('username', this.username)
      localStorage.setItem('role', this.role)
    },
    logout() {
      this.token = ''
      this.username = ''
      this.role = ''
      localStorage.clear()
    },
    async fetchMe() {
      if (!this.token) return null
      const { data } = await http.get('/auth/me')
      this.username = data.username
      this.role = data.role
      this.permissions = data.permissions || []
      return data
    }
  }
})
