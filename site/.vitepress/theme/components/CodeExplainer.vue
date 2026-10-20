<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { withBase } from 'vitepress'
import CodeEditor from './CodeEditor.vue'
import { explainPython, warmup, status, runtimeInfo, type ExplainResult } from '../pyodide-client'
import { loadExplainCode } from '../explain-storage'

const REPO_EXAMPLES = [
  'examples/agent/minimal_agent.py',
  'examples/项目/12-自定义容器类/ring_buffer.py',
  'examples/项目/12-自定义容器类/test_ring_buffer.py',
  'examples/项目/13-计时重试装饰器/timing.py',
  'examples/项目/13-计时重试装饰器/test_timing.py',
  'examples/项目/14-日志统计CLI/logstats.py',
  'examples/项目/14-日志统计CLI/test_logstats.py',
  'examples/项目/15-CLI测试/test_cli_logstats.py',
  'examples/项目/16-项目模板/greeter/__init__.py',
  'examples/项目/16-项目模板/greeter/core.py',
  'examples/项目/16-项目模板/test_greeter.py',
  'examples/项目/17-CLI打包/logstats_pkg/__init__.py',
  'examples/项目/17-CLI打包/logstats_pkg/cli.py',
  'examples/项目/17-CLI打包/test_package.py',
  'examples/项目/18-并发下载模拟/downloader.py',
  'examples/项目/18-并发下载模拟/test_downloader.py',
  'examples/项目/19-异步minimal_agent/async_agent.py',
  'examples/项目/19-异步minimal_agent/test_async_agent.py',
  'examples/项目/20-优化慢函数/slow_math.py',
  'examples/项目/20-优化慢函数/test_slow_math.py',
  'examples/项目/21-CSV分析报告/analyze.py',
  'examples/项目/21-CSV分析报告/test_analyze.py',
  'examples/项目/22-天气工具API/app.py',
  'examples/项目/22-天气工具API/test_app.py',
  'examples/项目/23-mini-agent包/mini_agent/__init__.py',
  'examples/项目/23-mini-agent包/mini_agent/runner.py',
  'examples/项目/23-mini-agent包/mini_agent/tools.py',
  'examples/项目/23-mini-agent包/test_mini_agent.py',
  'examples/项目/conftest.py',
]

type ConceptRow = {
  id: string
  name: string
  meaning: string
  course_links: string[]
  glossary_links: string[]
}

const source = ref('print("hello")\n')
const selectedExample = ref('')
const filename = ref('<paste>')
const analyzing = ref(false)
const result = ref<ExplainResult | null>(null)
const conceptIndex = ref<ConceptRow[]>([])
const fileInput = ref<HTMLInputElement | null>(null)
const llmReady = ref(false)
const llmBusy = ref(false)
const llmText = ref('')

const conceptById = computed(() => {
  const m = new Map<string, ConceptRow>()
  for (const row of conceptIndex.value) m.set(row.id, row)
  return m
})

function fixLink(href: string) {
  if (!href || href.startsWith('http')) return href
  if (href.startsWith('../')) return withBase('/' + href.replace(/^\.\.\//, ''))
  return withBase(href.startsWith('/') ? href : '/' + href)
}

async function loadConceptIndex() {
  try {
    const res = await fetch(withBase('/concept-index.json'))
    if (!res.ok) return
    const data = await res.json()
    conceptIndex.value = data.rows || []
  } catch {
    /* offline */
  }
}

async function probeLlm() {
  if (typeof window === 'undefined') return
  const host = window.location.hostname
  if (host !== '127.0.0.1' && host !== 'localhost') return
  const port = (window as unknown as { __JDP_EXPLAIN_PORT?: string }).__JDP_EXPLAIN_PORT || '8031'
  try {
    const res = await fetch(`http://127.0.0.1:${port}/v1/health`, { method: 'GET' })
    llmReady.value = res.ok
  } catch {
    llmReady.value = false
  }
}

async function analyze() {
  analyzing.value = true
  result.value = null
  llmText.value = ''
  warmup()
  result.value = await explainPython(source.value, filename.value)
  analyzing.value = false
}

async function loadExample() {
  if (!selectedExample.value) return
  const url = withBase(`/repo/${encodeURI(selectedExample.value)}.txt`)
  const res = await fetch(url)
  if (!res.ok) return
  source.value = await res.text()
  filename.value = selectedExample.value.split('/').pop() || 'example.py'
  await analyze()
}

function onFilePick(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    source.value = String(reader.result || '')
    filename.value = file.name
    void analyze()
  }
  reader.readAsText(file)
  input.value = ''
}

function sessionKeyFromUrl(): string {
  if (typeof window === 'undefined') return ''
  return new URLSearchParams(window.location.search).get('k') || ''
}

function applySessionKey() {
  const k = sessionKeyFromUrl()
  const code = loadExplainCode(k)
  if (code) {
    source.value = code
    filename.value = '<lesson>'
    void analyze()
  }
}

async function requestLlm() {
  if (!result.value?.ok || !llmReady.value) return
  llmBusy.value = true
  llmText.value = ''
  const port = (window as unknown as { __JDP_EXPLAIN_PORT?: string }).__JDP_EXPLAIN_PORT || '8031'
  try {
    const res = await fetch(`http://127.0.0.1:${port}/v1/explain`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ code: source.value, analysis: result.value, filename: filename.value }),
    })
    const data = await res.json()
    if (!res.ok) {
      llmText.value = data.message || data.error || `请求失败 (${res.status})`
    } else {
      const parts = (data.sections || []).map((s: { title: string; body: string }) => `## ${s.title}\n${s.body}`)
      llmText.value = [data.intent && `**意图：** ${data.intent}`, ...parts].filter(Boolean).join('\n\n')
    }
  } catch (e) {
    llmText.value = String(e)
  } finally {
    llmBusy.value = false
  }
}

onMounted(() => {
  void loadConceptIndex()
  void probeLlm()
  applySessionKey()
})

</script>

<template>
  <div class="code-explainer">
    <p class="py-hint">
      在浏览器内用标准库 <code>ast</code> 分析代码，不执行你的程序。粘贴、选示例、打开本机文件，或从课程代码块点「解读」跳转。
    </p>

    <div class="ce-inputs">
      <div class="ce-field">
        <label for="ce-paste">粘贴 Python 代码</label>
        <CodeEditor v-model="source" :min-lines="8" @focus="warmup" />
      </div>
      <div class="ce-row">
        <div class="ce-field ce-grow">
          <label for="ce-example">仓库示例（{{ REPO_EXAMPLES.length }} 个）</label>
          <select id="ce-example" v-model="selectedExample" class="ce-select" @change="loadExample">
            <option value="">— 选择 —</option>
            <option v-for="p in REPO_EXAMPLES" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
        <div class="ce-field">
          <label for="ce-file">本机文件</label>
          <input id="ce-file" ref="fileInput" type="file" accept=".py,text/plain" @change="onFilePick" />
        </div>
      </div>
      <div class="ce-actions">
        <span v-if="status === 'loading'" class="py-status">正在加载 Pyodide…</span>
        <span v-else-if="status === 'ready'" class="py-status">{{ runtimeInfo }}</span>
        <span class="py-spacer" />
        <button type="button" class="py-btn py-btn-primary" :disabled="analyzing" @click="analyze">
          {{ analyzing ? '分析中…' : '开始解读' }}
        </button>
        <button
          v-if="llmReady"
          type="button"
          class="py-btn ce-llm"
          :disabled="llmBusy || !result?.ok"
          @click="requestLlm"
        >
          {{ llmBusy ? '讲解中…' : 'AI 讲解' }}
        </button>
      </div>
    </div>

    <div v-if="result && !result.ok" class="ce-error" role="alert">
      第 {{ result.error?.line }} 行，第 {{ result.error?.column }} 列：{{ result.error?.message }}
    </div>

    <template v-if="result?.ok">
      <section class="ce-section" aria-labelledby="ce-overview">
        <h2 id="ce-overview">概览</h2>
        <ul class="ce-list">
          <li>共 {{ result.overview?.line_count }} 行</li>
          <li v-if="result.overview?.docstring">模块文档字符串已识别</li>
          <li v-if="result.overview?.top_level_summary">{{ result.overview.top_level_summary }}</li>
          <li v-if="result.overview?.has_main_guard">含 <code>if __name__ == "__main__"</code> 入口</li>
          <li v-for="fn in result.overview?.functions || []" :key="'f' + fn.name">
            函数 <code>{{ fn.name }}</code>（第 {{ fn.line }} 行<span v-if="fn.is_async">，async</span>）
          </li>
          <li v-for="cl in result.overview?.classes || []" :key="'c' + cl.name">
            类 <code>{{ cl.name }}</code>（第 {{ cl.line }} 行）
          </li>
        </ul>
      </section>

      <section class="ce-section" aria-labelledby="ce-syntax">
        <h2 id="ce-syntax">语法点</h2>
        <table class="ce-table">
          <thead><tr><th>行号</th><th>语法</th><th>含义</th><th>课程</th></tr></thead>
          <tbody>
            <tr v-for="(p, i) in result.syntax_points || []" :key="i">
              <td>{{ (p.lines || []).join(', ') }}</td>
              <td><code>{{ p.syntax }}</code></td>
              <td>{{ p.meaning }}</td>
              <td>
                <a
                  v-for="(lnk, j) in p.course_links || []"
                  :key="j"
                  :href="fixLink(lnk)"
                >课</a>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <section class="ce-section" aria-labelledby="ce-structure">
        <h2 id="ce-structure">结构</h2>
        <ul v-if="(result.structure || []).length" class="ce-list">
          <li v-for="(s, i) in result.structure" :key="i">
            <strong>{{ s.kind }} {{ s.name }}</strong>（{{ s.line }}–{{ s.end_line }}）
            <span v-if="s.params?.length">参数：{{ s.params.join(', ') }}</span>
            <span v-if="s.calls?.length">调用：{{ s.calls.join(', ') }}</span>
          </li>
        </ul>
        <p v-else class="py-hint">无函数/类结构块（可能只有顶层语句）。</p>
      </section>

      <section class="ce-section" aria-labelledby="ce-concepts">
        <h2 id="ce-concepts">概念</h2>
        <ul class="ce-list">
          <li v-for="c in result.concepts || []" :key="c.id">
            <strong>{{ c.name || conceptById.get(c.id)?.name || c.id }}</strong>
            <span v-if="conceptById.get(c.id)?.meaning"> — {{ conceptById.get(c.id)?.meaning }}</span>
            <span class="ce-links">
              <a
                v-for="(lnk, j) in c.course_links?.length ? c.course_links : conceptById.get(c.id)?.course_links || []"
                :key="'c' + j"
                :href="fixLink(lnk)"
              >课程</a>
              <a
                v-for="(lnk, j) in c.glossary_links?.length ? c.glossary_links : conceptById.get(c.id)?.glossary_links || []"
                :key="'g' + j"
                :href="fixLink(lnk)"
              >术语</a>
            </span>
          </li>
        </ul>
      </section>

      <section class="ce-section" aria-labelledby="ce-run">
        <h2 id="ce-run">怎么运行</h2>
        <p v-if="result.run_info?.can_run_in_browser">可在课程页 Pyodide 中直接运行（仅标准库）。</p>
        <p v-else>浏览器内可能无法运行：第三方/未知模块 {{ (result.run_info?.blocked_imports || []).join(', ') }}</p>
        <p v-if="result.run_info?.suggested_command"><code>{{ result.run_info.suggested_command }}</code></p>
        <p v-if="result.run_info?.uv_add_hint" class="py-hint">{{ result.run_info.uv_add_hint }}</p>
      </section>

      <section class="ce-section" aria-labelledby="ce-pitfalls">
        <h2 id="ce-pitfalls">易错点</h2>
        <ul v-if="(result.pitfalls || []).length" class="ce-list">
          <li v-for="(p, i) in result.pitfalls" :key="i">
            <strong>{{ p.title }}</strong>（第 {{ (p.lines || []).join(', ') }} 行）
            {{ p.message }}
            <a v-if="p.course_link" :href="fixLink(p.course_link)">相关课</a>
          </li>
        </ul>
        <p v-else class="py-hint">未命中规则型易错点（不代表代码无问题）。</p>
      </section>

      <section v-if="llmText" class="ce-section ce-llm-out" aria-labelledby="ce-llm">
        <h2 id="ce-llm">AI 讲解（本机生成，可能有误）</h2>
        <pre class="ce-llm-pre">{{ llmText }}</pre>
      </section>
    </template>
  </div>
</template>
