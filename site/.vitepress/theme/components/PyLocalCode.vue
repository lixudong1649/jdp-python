<script setup lang="ts">
defineProps<{ raises?: string }>()
</script>

<template>
  <div class="py-runner py-local" data-py-local>
    <div class="py-toolbar">
      <span class="py-badge py-badge-warn">Python · 需在本地运行</span>
      <span v-if="raises" class="py-badge" :title="'本地运行时应抛出 ' + raises">演示报错</span>
      <span class="py-spacer" />
      <span class="py-hint">在仓库根目录用 <code>uv run python tests/check_course.py</code> 或复制到本地脚本执行</span>
    </div>
    <div class="py-static"><slot /></div>
  </div>
</template>
