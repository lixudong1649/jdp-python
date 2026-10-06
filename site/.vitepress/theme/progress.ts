import { reactive, watch } from 'vue'

const KEY = 'jdp-python-course:progress:v1'

interface State {
  lessons: Record<string, number> // 课程路径 -> 完成时间戳
  exercises: Record<string, number> // 练习 ID -> 通过时间戳
}

function load(): State {
  if (typeof localStorage === 'undefined') return { lessons: {}, exercises: {} }
  try {
    const s = JSON.parse(localStorage.getItem(KEY) || '{}')
    return { lessons: s.lessons || {}, exercises: s.exercises || {} }
  } catch {
    return { lessons: {}, exercises: {} }
  }
}

export const progress = reactive<State>({ lessons: {}, exercises: {} })
let started = false

/** 仅在浏览器端调用（onMounted 中），避免 SSR 与水合不一致。 */
export function initProgress() {
  if (started || typeof window === 'undefined') return
  started = true
  Object.assign(progress, load())
  watch(progress, (v) => localStorage.setItem(KEY, JSON.stringify(v)), { deep: true })
  window.addEventListener('storage', (e) => {
    if (e.key === KEY) Object.assign(progress, load())
  })
}

/** 统一路径格式：解码、去掉 .html 与末尾 index。 */
// 站点部署路径（本机 '/'，Pages 为 '/jdp-python/'）；进度键统一使用不含 base 的路径。
const BASE = decodeURI(import.meta.env.BASE_URL || '/')

export function normPath(p: string): string {
  let s = p.split('#')[0].split('?')[0]
  try { s = decodeURI(s) } catch {}
  if (BASE !== '/' && s.startsWith(BASE)) s = s.slice(BASE.length - 1)
  s = s.replace(/\.html$/, '').replace(/\/index$/, '/')
  return s
}

export const isLessonDone = (p: string) => !!progress.lessons[normPath(p)]
export function setLessonDone(p: string, done: boolean) {
  const k = normPath(p)
  if (done) progress.lessons[k] = Date.now()
  else delete progress.lessons[k]
}
export const isExercisePassed = (id: string) => !!progress.exercises[id]
export const markExercisePassed = (id: string) => { progress.exercises[id] = Date.now() }
export function resetProgress() {
  progress.lessons = {}
  progress.exercises = {}
}
