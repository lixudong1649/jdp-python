<script setup lang="ts">
import type { RunResult } from '../pyodide-client'
defineProps<{ result: RunResult | null; running: boolean; expected?: string }>()
</script>

<template>
  <div v-if="running || result" class="py-output" :class="{ 'is-error': result && !result.ok && !(expected && result.errType === expected) }">
    <div v-if="running" class="py-output-running">运行中…</div>
    <template v-else-if="result">
      <pre v-if="result.out" class="py-stdout">{{ result.out }}</pre>
      <pre v-if="result.err" class="py-stderr">{{ result.err }}</pre>
      <div v-if="!result.out && !result.err" class="py-output-empty">（无输出）</div>
      <div v-if="expected && result.errType === expected" class="py-output-note">✔ 这是本例要演示的预期错误：{{ expected }}</div>
      <div class="py-output-meta" v-if="result.ms !== undefined">耗时 {{ result.ms }} ms<span v-if="result.python"> · Python {{ result.python }}</span></div>
    </template>
  </div>
</template>
