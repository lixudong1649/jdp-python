<script setup lang="ts">
import { computed, ref } from 'vue'
import CodeEditor from './CodeEditor.vue'
import RunOutput from './RunOutput.vue'
import { b64decode, runPython, warmup, status, runtimeInfo, type RunResult } from '../pyodide-client'

const props = defineProps<{ code: string; raises?: string }>()
const original = b64decode(props.code)
const source = ref(original)
const editing = ref(false)
const running = ref(false)
const result = ref<RunResult | null>(null)
const modified = computed(() => source.value !== original)

async function run() {
  running.value = true
  result.value = await runPython(source.value)
  running.value = false
}
function reset() {
  source.value = original
  result.value = null
  editing.value = false
}
</script>

<template>
  <div class="py-runner" data-py-runner>
    <div class="py-toolbar">
      <span class="py-badge">Python · 可运行</span>
      <span v-if="raises" class="py-badge py-badge-warn" :title="'本例预期抛出 ' + raises">演示报错</span>
      <span class="py-spacer" />
      <span v-if="status === 'loading'" class="py-status">正在加载 Python 运行时…</span>
      <button class="py-btn" @click="editing = !editing">{{ editing ? '收起编辑器' : '编辑' }}</button>
      <button class="py-btn" :disabled="!modified && !result" @click="reset">重置</button>
      <button class="py-btn py-btn-primary" :disabled="running" @pointerenter="warmup" @click="run">▶ 运行</button>
    </div>
    <CodeEditor v-if="editing" v-model="source" :min-lines="3" @run="run" @focus="warmup" />
    <div v-else class="py-static"><slot /></div>
    <RunOutput :result="result" :running="running" :expected="raises" />
    <div v-if="status === 'error'" class="py-output is-error"><pre class="py-stderr">{{ runtimeInfo }}</pre></div>
  </div>
</template>
