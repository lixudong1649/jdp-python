<script setup lang="ts">
// 文档页底部的版权与许可行（默认主题页脚在有侧边栏的页面不显示）。
import { useData, withBase } from 'vitepress'
const { theme } = useData()
const repo = theme.value.siteMeta?.repo
const author = theme.value.siteMeta?.author
</script>

<template>
  <div class="site-copyright">
    © 2026 <a :href="author" target="_blank" rel="noopener">lixudong1649</a>
    · 代码 <a :href="`${repo}/blob/main/LICENSE`" target="_blank" rel="noopener">MIT</a>
    · 课程内容 <a :href="`${repo}/blob/main/LICENSE-CONTENT.md`" target="_blank" rel="noopener">CC BY-NC-SA 4.0</a>
    · <a :href="withBase('/关于')">关于与声明</a>
    · <a :href="`${repo}/issues`" target="_blank" rel="noopener">反馈问题</a>
  </div>
</template>
