import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import TestSuites from '../views/TestSuites.vue'
import TestCases from '../views/TestCases.vue'
import TestRuns from '../views/TestRuns.vue'
import TestRunDetail from '../views/TestRunDetail.vue'
import TestRunTemplates from '../views/TestRunTemplates.vue'
import DirectTestRun from '../views/DirectTestRun.vue'
import Reports from '../views/Reports.vue'
import Schema from '../views/Schema.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/test-suites',
    name: 'TestSuites',
    component: TestSuites
  },
  {
    path: '/test-cases',
    name: 'TestCases',
    component: TestCases
  },
  {
    path: '/test-runs',
    name: 'TestRuns',
    component: TestRuns
  },
  {
    path: '/test-runs/:id',
    name: 'TestRunDetail',
    component: TestRunDetail
  },
  {
    path: '/test-run-templates',
    name: 'TestRunTemplates',
    component: TestRunTemplates
  },
  {
    path: '/direct-test-run/:id',
    name: 'DirectTestRun',
    component: DirectTestRun
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports
  },
  {
    path: '/schema',
    name: 'Schema',
    component: Schema
  }
]

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

export default router
