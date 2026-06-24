<template>
  <main class="english-site">
    <header class="en-top">
      <div class="container en-top-inner">
        <span>Official English Website</span>
        <button type="button" @click="router.push('/')">中文</button>
      </div>
    </header>

    <section class="en-header">
      <div class="container en-brand">
        <button type="button" @click="router.push('/english')">
          <img src="https://www.acvtc.edu.cn/images/logo.png" alt="ACVTC logo" />
          <span>
            <b>Anhui Communications Vocational & Technical College</b>
            <small>Developing skilled professionals for modern transportation</small>
          </span>
        </button>
        <nav>
          <a href="#about">About</a>
          <a href="#academics">Academics</a>
          <a href="#admissions">Admissions</a>
          <a href="#campus">Campus</a>
          <a href="#contact">Contact</a>
        </nav>
      </div>
    </section>

    <section class="en-hero">
      <div class="en-hero-shade"></div>
      <div class="container en-hero-inner">
        <p>Blue and Green, Connected to the Future</p>
        <h1>Anhui Communications Vocational & Technical College</h1>
        <span>
          ACVTC is a public vocational college with distinctive strengths in transportation-related education,
          serving regional development and the modern comprehensive transportation industry.
        </span>
        <div>
          <button type="button" @click="scrollTo('about')">Learn More</button>
          <button type="button" @click="scrollTo('admissions')">Admissions</button>
        </div>
      </div>
    </section>

    <section id="about" class="container en-section about-grid">
      <div>
        <span class="section-kicker">About ACVTC</span>
        <h2>Rooted in transportation education since 1956</h2>
        <p>
          Founded in 1956, Anhui Communications Vocational & Technical College has long served the transportation
          industry. The college is committed to practical education, industry collaboration, and high-quality technical
          talent development.
        </p>
        <p>
          Guided by the motto “Diligence, Accessibility, Dedication and Harmony”, ACVTC focuses on transportation,
          serves industry needs, and supports society through applied vocational education.
        </p>
      </div>
      <div class="fact-panel">
        <article v-for="item in facts" :key="item.label">
          <b>{{ item.value }}</b>
          <span>{{ item.label }}</span>
        </article>
      </div>
    </section>

    <section id="academics" class="en-band">
      <div class="container en-section">
        <span class="section-kicker">Academics</span>
        <h2>Transportation-focused academic clusters</h2>
        <div class="cluster-grid">
          <article v-for="item in clusters" :key="item.title">
            <strong>{{ item.code }}</strong>
            <h3>{{ item.title }}</h3>
            <p>{{ item.desc }}</p>
          </article>
        </div>
      </div>
    </section>

    <section id="admissions" class="container en-section admission-layout">
      <div>
        <span class="section-kicker">Admissions</span>
        <h2>Admissions and career development</h2>
        <p>
          ACVTC provides programs in civil engineering, automotive technology, rail transit, navigation, aviation,
          logistics, artificial intelligence and related fields. Students receive practical training and career-oriented
          support.
        </p>
      </div>
      <div class="admission-card">
        <h3>For Applicants</h3>
        <ul>
          <li>Program information and professional orientation</li>
          <li>Admissions policies and application guidance</li>
          <li>Campus life and student services</li>
          <li>Employment-oriented training pathways</li>
        </ul>
      </div>
    </section>

    <section id="campus" class="container en-section campus-section">
      <span class="section-kicker">Campus Life</span>
      <h2>Learning by doing, growing with the industry</h2>
      <div class="campus-grid">
        <article v-for="item in campus" :key="item.title">
          <img :src="item.image" :alt="item.title" />
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
        </article>
      </div>
    </section>

    <footer id="contact" class="en-footer">
      <div class="container footer-grid">
        <div>
          <h2>Anhui Communications Vocational & Technical College</h2>
          <p>XinQiao Campus: No.16 Shouzhou Avenue, Anhui Xinqiao International Industrial Park</p>
          <p>Baohe Campus: No.114 Hechao Road, Baohe District, Hefei, Anhui</p>
          <p>Admissions Hotline: 0551-63444228</p>
        </div>
        <div>
          <b>www.acvtc.edu.cn</b>
          <button type="button" @click="router.push('/')">中文官网</button>
        </div>
      </div>
    </footer>
  </main>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const facts = [
  { value: '1956', label: 'Founded' },
  { value: '14,000+', label: 'Students' },
  { value: '41', label: 'Programs' },
  { value: '236+', label: 'Off-campus Training Bases' }
]
const clusters = [
  { code: 'Road', title: 'Civil and Transportation Engineering', desc: 'Road and bridge engineering, construction technology, civil engineering testing.' },
  { code: 'Auto', title: 'New Energy Vehicles', desc: 'Automotive inspection, maintenance, intelligent connected vehicle technology.' },
  { code: 'Rail', title: 'Urban Rail Transit', desc: 'Rail transit operation, vehicles, communication and signal technology.' },
  { code: 'Marine', title: 'Navigation and Marine Engineering', desc: 'Navigation technology, marine engineering and port logistics.' },
  { code: 'Aviation', title: 'Aviation and Low-altitude Economy', desc: 'Civil aviation services, aircraft maintenance and UAV applications.' },
  { code: 'AI', title: 'Digital and Intelligent Transportation', desc: 'Artificial intelligence, big data and smart transportation technology.' }
]
const campus = [
  {
    title: 'Practical Training',
    desc: 'Students learn through labs, workshops, simulation environments and industry projects.',
    image: 'https://www.acvtc.edu.cn/__local/1/57/6C/D1CCD8E88FC99DAB8D3287DC5F4_0769FA99_14EFC.jpg'
  },
  {
    title: 'Campus Activities',
    desc: 'Skill competitions, student clubs and volunteer services enrich campus life.',
    image: 'https://www.acvtc.edu.cn/__local/2/40/F2/EE54DCF56B0362EC3CCCEB10385_0D2D27FE_27717.jpg'
  },
  {
    title: 'Industry Collaboration',
    desc: 'The college works with enterprises to support modern apprenticeship and order-based classes.',
    image: 'https://www.acvtc.edu.cn/__local/4/D8/C6/BAD0D1360D5C810E0A7A1F55F57_C2DD0CCE_1517E.jpg'
  }
]

function scrollTo(id) {
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
}
</script>

<style scoped>
.english-site {
  min-height: 100vh;
  color: #1d2b39;
  background: #eef3f7;
}
.container {
  width: min(1180px, calc(100vw - 40px));
  margin: 0 auto;
}
button,
a {
  font: inherit;
}
.en-top {
  background: linear-gradient(90deg, #003b70, #005b9e);
  color: #ffffff;
}
.en-top-inner {
  min-height: 38px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.en-top button,
.en-hero button,
.en-footer button {
  border: 1px solid rgba(255, 255, 255, .46);
  background: transparent;
  color: #ffffff;
  padding: 8px 14px;
  cursor: pointer;
  font-weight: 800;
}
.en-header {
  background: #ffffff;
  border-bottom: 1px solid #d7e2ec;
  box-shadow: 0 10px 30px rgba(0, 54, 96, .06);
}
.en-brand {
  min-height: 108px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 30px;
}
.en-brand button {
  display: flex;
  align-items: center;
  gap: 14px;
  border: 0;
  background: transparent;
  text-align: left;
  cursor: pointer;
}
.en-brand img {
  width: 58px;
  height: 58px;
  object-fit: contain;
}
.en-brand b {
  display: block;
  color: #003b70;
  font-size: 26px;
}
.en-brand small {
  display: block;
  margin-top: 4px;
  color: #2e7d32;
  font-weight: 800;
}
.en-brand nav {
  display: flex;
  gap: 22px;
  flex-wrap: wrap;
}
.en-brand a {
  color: #1d2b39;
  text-decoration: none;
  font-weight: 900;
}
.en-brand a:hover {
  color: #0066b3;
}
.en-hero {
  position: relative;
  min-height: 620px;
  background: url("https://www.acvtc.edu.cn/__local/2/7B/BA/1991E6320170386EEE706FD2F53_0528A760_1481E.jpg") center / cover;
}
.en-hero-shade {
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, rgba(0, 36, 68, .9), rgba(0, 102, 179, .55), rgba(46, 125, 50, .12));
}
.en-hero-inner {
  position: relative;
  min-height: 620px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: #ffffff;
}
.en-hero p,
.section-kicker {
  color: #d9f0de;
  font-weight: 900;
  letter-spacing: .14em;
  text-transform: uppercase;
}
.en-hero h1 {
  width: min(880px, 100%);
  margin: 12px 0 18px;
  font-size: clamp(42px, 7vw, 78px);
  line-height: 1.08;
}
.en-hero span {
  width: min(720px, 100%);
  font-size: 20px;
  line-height: 1.8;
}
.en-hero div div {
  display: flex;
  gap: 12px;
  margin-top: 28px;
}
.en-section {
  padding: 76px 0;
}
.section-kicker {
  color: #2e7d32;
  font-size: 13px;
}
.en-section h2 {
  margin: 10px 0 18px;
  color: #003b70;
  font-size: clamp(32px, 5vw, 54px);
  line-height: 1.12;
}
.en-section p {
  color: #5f6c78;
  line-height: 1.85;
}
.about-grid,
.admission-layout {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 42px;
  align-items: center;
}
.fact-panel,
.admission-card,
.campus-grid article {
  background: #ffffff;
  border: 1px solid #d7e2ec;
  box-shadow: 0 18px 42px rgba(0, 54, 96, .08);
}
.fact-panel {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
}
.fact-panel article {
  padding: 28px;
  border: 1px solid #edf1f5;
}
.fact-panel b {
  display: block;
  color: #c41e3a;
  font-size: 34px;
}
.fact-panel span {
  color: #5f6c78;
  font-weight: 800;
}
.en-band {
  background: #003b70;
}
.en-band h2,
.en-band .section-kicker {
  color: #ffffff;
}
.cluster-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.cluster-grid article {
  min-height: 210px;
  padding: 24px;
  border: 1px solid rgba(255, 255, 255, .18);
  background: rgba(255, 255, 255, .08);
  color: #ffffff;
}
.cluster-grid strong {
  color: #b8e1c0;
}
.cluster-grid p {
  color: #d9e9f5;
}
.admission-card {
  padding: 28px;
  border-top: 4px solid #2e7d32;
}
.admission-card h3 {
  color: #003b70;
}
.admission-card li {
  margin: 12px 0;
  color: #5f6c78;
}
.campus-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 18px;
}
.campus-grid article {
  overflow: hidden;
}
.campus-grid img {
  width: 100%;
  aspect-ratio: 16 / 10;
  object-fit: cover;
}
.campus-grid h3,
.campus-grid p {
  margin-left: 20px;
  margin-right: 20px;
}
.en-footer {
  padding: 44px 0;
  background: #003b70;
  color: #ffffff;
}
.footer-grid {
  display: grid;
  grid-template-columns: 1fr 240px;
  gap: 32px;
}
.en-footer p {
  color: #d9e9f5;
}
.en-footer b {
  display: block;
  margin-bottom: 18px;
}
@media (max-width: 900px) {
  .en-brand,
  .about-grid,
  .admission-layout,
  .footer-grid {
    grid-template-columns: 1fr;
    display: grid;
  }
  .cluster-grid,
  .campus-grid {
    grid-template-columns: 1fr;
  }
}
</style>
