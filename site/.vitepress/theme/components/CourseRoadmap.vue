<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import { initProgress, progress, normPath, resetProgress } from '../progress'
import { useCourse } from '../course-data'

const mounted = ref(false)
const { stages, allLessons, doneCount, nextLesson, stageDone } = useCourse()
onMounted(() => { initProgress(); mounted.value = true })
const isDone = (link: string) => mounted.value && !!progress.lessons[normPath(link)]
function confirmReset() {
  if (confirm('确定清空本机浏览器中的全部学习进度与练习记录吗？')) resetProgress()
}
</script>

<template>
  <section class="roadmap">
    <div class="roadmap-summary">
      <div>
        <div class="roadmap-title">学习路线 · 11 个阶段 · {{ allLessons.length }} 课</div>
        <div class="roadmap-sub" v-if="mounted">
          已完成 {{ doneCount }}/{{ allLessons.length }} 课 · 练习通过 {{ Object.keys(progress.exercises).length }} 道（进度仅保存在本机浏览器 localStorage）
        </div>
      </div>
      <div class="roadmap-actions" v-if="mounted">
        <a v-if="nextLesson" class="py-btn py-btn-primary" :href="withBase(nextLesson.link)">{{ doneCount ? '继续学习' : '开始学习' }}：{{ nextLesson.title }}</a>
        <span v-else class="py-badge py-badge-ok">全部完成 🎉</span>
        <button v-if="doneCount || Object.keys(progress.exercises).length" class="py-link" @click="confirmReset">重置进度</button>
      </div>
    </div>
    <div class="bar big" v-if="mounted"><div class="bar-fill" :style="{ width: (100 * doneCount) / Math.max(1, allLessons.length) + '%' }" /></div>
    <ol class="roadmap-grid">
      <li v-for="s in stages" :key="s.no" class="roadmap-card" :class="{ complete: mounted && stageDone(s) === s.lessons.length }">
        <div class="roadmap-card-head">
          <span class="roadmap-no">{{ String(s.no).padStart(2, '0') }}</span>
          <a class="roadmap-card-title" :href="withBase(s.link)">{{ s.short }}</a>
          <span class="roadmap-count" v-if="mounted">{{ stageDone(s) }}/{{ s.lessons.length }}</span>
        </div>
        <p class="roadmap-goal">{{ s.goal }}</p>
        <ul class="roadmap-lessons">
          <li v-for="l in s.lessons" :key="l.link" :class="{ done: isDone(l.link) }">
            <a :href="withBase(l.link)">{{ l.title }}</a>
          </li>
        </ul>
      </li>
    </ol>
  </section>
</template>
