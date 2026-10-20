import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import PyRunner from './components/PyRunner.vue'
import PyLocalCode from './components/PyLocalCode.vue'
import PyExercise from './components/PyExercise.vue'
import CourseRoadmap from './components/CourseRoadmap.vue'
import LessonFooter from './components/LessonFooter.vue'
import SidebarProgress from './components/SidebarProgress.vue'
import SiteCopyright from './components/SiteCopyright.vue'
import CodeExplainer from './components/CodeExplainer.vue'
import './style.css'

export default {
  extends: DefaultTheme,
  Layout: () =>
    h(DefaultTheme.Layout, null, {
      'doc-footer-before': () => h(LessonFooter),
      'sidebar-nav-before': () => h(SidebarProgress),
      'doc-after': () => h(SiteCopyright),
    }),
  enhanceApp({ app }) {
    app.component('PyRunner', PyRunner)
    app.component('PyLocalCode', PyLocalCode)
    app.component('PyExercise', PyExercise)
    app.component('CourseRoadmap', CourseRoadmap)
    app.component('CodeExplainer', CodeExplainer)
  },
} satisfies Theme
