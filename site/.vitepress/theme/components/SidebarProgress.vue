<script setup lang="ts">
import { onMounted, ref, watch, nextTick } from 'vue'
import { useRoute } from 'vitepress'
import { initProgress, progress, normPath } from '../progress'
import { useCourse } from '../course-data'

const mounted = ref(false)
const { doneCount, allLessons } = useCourse()
const route = useRoute()

// 给侧边栏中已完成的课程链接加上 is-done 标记（CSS 显示 ✓）
function mark() {
  document.querySelectorAll<HTMLAnchorElement>('.VPSidebar a[href]').forEach((a) => {
    const done = !!progress.lessons[normPath(new URL(a.href).pathname)]
    a.classList.toggle('is-done', done)
  })
}
onMounted(() => {
  initProgress()
  mounted.value = true
  nextTick(mark)
  new MutationObserver(() => mark()).observe(document.querySelector('.VPSidebar') || document.body, { childList: true, subtree: true })
})
watch(() => [route.path, { ...progress.lessons }], () => nextTick(mark), { deep: true })
</script>

<template>
  <div v-if="mounted && allLessons.length" class="sidebar-progress">
    <div class="sidebar-progress-label">学习进度 {{ doneCount }}/{{ allLessons.length }} 课</div>
    <div class="bar"><div class="bar-fill" :style="{ width: (100 * doneCount) / allLessons.length + '%' }" /></div>
  </div>
</template>
