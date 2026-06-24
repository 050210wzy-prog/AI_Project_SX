import { createRouter, createWebHistory } from 'vue-router'
import PortalView from '../views/PortalView.vue'
import ChatView from '../views/ChatView.vue'
import LoginView from '../views/LoginView.vue'
import ChannelView from '../views/ChannelView.vue'
import ArticleDetailView from '../views/ArticleDetailView.vue'
import CollegeDetailView from '../views/CollegeDetailView.vue'
import ServiceDetailView from '../views/ServiceDetailView.vue'
import EnglishView from '../views/EnglishView.vue'
import InnovationView from '../views/InnovationView.vue'
import StudentScheduleView from '../views/StudentScheduleView.vue'
import AdminLayout from '../layouts/AdminLayout.vue'
import DashboardView from '../views/admin/DashboardView.vue'
import AdmissionsView from '../views/admin/AdmissionsView.vue'
import WebsiteAdminView from '../views/admin/WebsiteAdminView.vue'
import InnovationAdminView from '../views/admin/InnovationAdminView.vue'
import CrawlerAdminView from '../views/admin/CrawlerAdminView.vue'
import TicketsView from '../views/admin/TicketsView.vue'
import StudentsView from '../views/admin/StudentsView.vue'
import StudentDetailView from '../views/admin/StudentDetailView.vue'
import AcademicView from '../views/admin/AcademicView.vue'
import SettingsView from '../views/admin/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: PortalView },
    { path: '/english', component: EnglishView },
    { path: '/en', component: EnglishView },
    { path: '/innovation', component: InnovationView },
    { path: '/schedule', component: StudentScheduleView },
    { path: '/channel/:name', component: ChannelView },
    { path: '/article/:id', component: ArticleDetailView },
    { path: '/college/:name', component: CollegeDetailView },
    { path: '/service/:name', component: ServiceDetailView },
    { path: '/admissions/:name', component: ServiceDetailView },
    { path: '/chat', component: ChatView },
    { path: '/login', component: LoginView },
    {
      path: '/admin',
      component: AdminLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', component: DashboardView },
        { path: 'admissions', component: AdmissionsView },
        { path: 'website', component: WebsiteAdminView },
        { path: 'crawler', component: CrawlerAdminView },
        { path: 'innovation', component: InnovationAdminView },
        { path: 'tickets', component: TicketsView },
        { path: 'students', component: StudentsView },
        { path: 'students/:id', component: StudentDetailView },
        { path: 'academic', component: AcademicView },
        { path: 'settings', component: SettingsView }
      ]
    }
  ]
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) return '/login'
  return true
})

export default router
