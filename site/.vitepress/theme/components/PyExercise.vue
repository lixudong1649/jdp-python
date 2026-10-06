<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import CodeEditor from './CodeEditor.vue'
import RunOutput from './RunOutput.vue'
import { b64decode, runPython, warmup, status, runtimeInfo, type RunResult } from '../pyodide-client'
import { initProgress, isExercisePassed, markExercisePassed } from '../progress'

const props = defineProps<{ exId: string; data: string }>()
const ex = JSON.parse(b64decode(props.data)) as { starter: string; solution: string; check: string }
const DRAFT_KEY = `jdp-python-course:draft:${props.exId}`

const source = ref(ex.starter)
const result = ref<RunResult | null>(null)
const verdict = ref<'pass' | 'fail' | null>(null)
const running = ref(false)
const showSolution = ref(false)
const showCheck = ref(false)
const mounted = ref(false)
const passed = computed(() => mounted.value && isExercisePassed(props.exId))

onMounted(() => {
  initProgress()
  const draft = localStorage.getItem(DRAFT_KEY)
  if (draft !== null) source.value = draft
  mounted.value = true
})
watch(source, (v) => {
  if (!mounted.value) return
  if (v === ex.starter) localStorage.removeItem(DRAFT_KEY)
  else localStorage.setItem(DRAFT_KEY, v)
})

async function run() {
  running.value = true
  verdict.value = null
  result.value = await runPython(source.value)
  running.value = false
}
async function check() {
  running.value = true
  verdict.value = null
  const r = await runPython(source.value, ex.check)
  running.value = false
  result.value = r
  verdict.value = r.ok ? 'pass' : 'fail'
  if (r.ok) markExercisePassed(props.exId)
}
function reset() {
  source.value = ex.starter
  result.value = null
  verdict.value = null
}
function loadSolution() {
  source.value = ex.solution
  verdict.value = null
  result.value = null
}
</script>

<template>
  <div class="py-exercise" :data-exercise-id="exId" :data-passed="passed ? '1' : '0'">
    <div class="py-toolbar">
      <span class="py-badge py-badge-ex">练习</span>
      <span v-if="passed" class="py-badge py-badge-ok">✓ 已通过</span>
      <span class="py-spacer" />
      <span v-if="status === 'loading'" class="py-status">正在加载 Python 运行时…</span>
      <button class="py-btn" @click="reset">重置</button>
      <button class="py-btn" :disabled="running" @pointerenter="warmup" @click="run">▶ 运行</button>
      <button class="py-btn py-btn-primary" :disabled="running" @pointerenter="warmup" @click="check">✓ 提交检查</button>
    </div>
    <CodeEditor v-model="source" :min-lines="6" @run="check" @focus="warmup" />
    <div v-if="verdict === 'pass'" class="py-verdict py-verdict-pass">✅ 全部检查通过</div>
    <div v-else-if="verdict === 'fail'" class="py-verdict py-verdict-fail">
      ❌ {{ result?.phase === 'check' ? '检查未通过，看看下面的提示' : result?.phase === 'timeout' ? '运行超时' : '代码运行出错' }}
    </div>
    <RunOutput :result="result" :running="running" />
    <div v-if="status === 'error'" class="py-output is-error"><pre class="py-stderr">{{ runtimeInfo }}</pre></div>
    <div class="py-ex-footer">
      <button class="py-link" @click="showSolution = !showSolution">{{ showSolution ? '隐藏参考答案' : '查看参考答案' }}</button>
      <button class="py-link" @click="showCheck = !showCheck">{{ showCheck ? '隐藏检查代码' : '查看检查代码' }}</button>
      <span class="py-hint">快捷键：⌘/Ctrl + Enter 提交检查</span>
    </div>
    <div v-if="showSolution" class="py-reveal">
      <div class="py-reveal-head">参考答案 <button class="py-link" @click="loadSolution">载入到编辑器</button></div>
      <pre><code>{{ ex.solution }}</code></pre>
    </div>
    <div v-if="showCheck" class="py-reveal">
      <div class="py-reveal-head">检查代码（在你的代码之后、同一命名空间中执行）</div>
      <pre><code>{{ ex.check }}</code></pre>
    </div>
  </div>
</template>
