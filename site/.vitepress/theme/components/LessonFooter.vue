<script setup lang="ts">
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vitepress'
import { initProgress, isLessonDone, setLessonDone, progress, normPath } from '../progress'
import { LESSON_RE, useCourse } from '../course-data'

const route = useRoute()
const mounted = ref(false)
const exIds = ref<string[]>([])
const path = computed(() => normPath(route.path))
const isLesson = computed(() => LESSON_RE.test(path.value))
const done = computed(() => mounted.value && isLessonDone(path.value))
const passedCount = computed(() => exIds.value.filter((id) => progress.exercises[id]).length)
const { doneCount, allLessons } = useCourse()

function scan() {
  exIds.value = Array.from(document.querySelectorAll<HTMLElement>('[data-exercise-id]')).map((e) => e.dataset.exerciseId!)
}
onMounted(() => {
  initProgress()
  mounted.value = true
  scan()
})
watch(() => route.path, () => nextTick(scan))
</script>

<template>
  <div v-if="isLesson && mounted" class="lesson-footer" :class="{ done }">
    <div class="lesson-footer-text">
      <strong>{{ done ? '本课已完成 ✓' : '学完了吗？' }}</strong>
      <span v-if="exIds.length"> · 本课练习通过 {{ passedCount }}/{{ exIds.length }}</span>
      <span> · 总进度 {{ doneCount }}/{{ allLessons.length }} 课</span>
    </div>
    <button class="py-btn" :class="{ 'py-btn-primary': !done }" @click="setLessonDone(path, !done)">
      {{ done ? '撤销完成' : '标记本课已完成' }}
    </button>
  </div>
</template>
