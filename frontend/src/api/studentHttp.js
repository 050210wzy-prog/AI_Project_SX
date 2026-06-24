import axios from 'axios'
import { axiosBaseUrl } from './base'

const studentHttp = axios.create({
  baseURL: axiosBaseUrl,
  timeout: 30000
})

studentHttp.interceptors.request.use((config) => {
  const token = localStorage.getItem('student_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

studentHttp.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem('student_token')
    }
    return Promise.reject(error)
  }
)

export default studentHttp
