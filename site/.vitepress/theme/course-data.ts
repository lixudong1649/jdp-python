import { computed } from 'vue'
import { useData } from 'vitepress'
import { progress, normPath } from './progress'

export interface Lesson { title: string; link: string }
export interface Stage { no: number; title: string; short: string; goal: string; link: string; lessons: Lesson[] }

export const LESSON_RE = /^\/课程\/\d\d-[^/]+\/\d\d-[^/]+$/

export function useCourse() {
  const { theme } = useData()
  const stages = computed<Stage[]>(() => theme.value.course || [])
  const allLessons = computed(() => stages.value.flatMap((s) => s.lessons))
  const doneCount = computed(() => allLessons.value.filter((l) => progress.lessons[normPath(l.link)]).length)
  const nextLesson = computed(() => allLessons.value.find((l) => !progress.lessons[normPath(l.link)]))
  const stageDone = (s: Stage) => s.lessons.filter((l) => progress.lessons[normPath(l.link)]).length
  return { stages, allLessons, doneCount, nextLesson, stageDone }
}
