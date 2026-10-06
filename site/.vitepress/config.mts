import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitepress'
import { coursePlugin } from './lib/markdown.mjs'
import { loadCourse, buildSidebar } from './lib/course.mjs'

const here = path.dirname(fileURLToPath(import.meta.url))
const siteRoot = path.resolve(here, '..')
const projectRoot = path.resolve(siteRoot, '..')
const srcDir = path.join(projectRoot, 'docs')
const stages = loadCourse(srcDir)

// 中文分词：拉丁词按单词，CJK 连续文本按字的二元组（bigram）切分；索引与查询使用同一函数。
// 注意：VitePress 会把该函数序列化到浏览器端，因此函数体必须自包含（不能引用外部变量）。
const tokenize = (text: string) => {
  const out: string[] = []
  const re = /[A-Za-z0-9_]+|[\u3400-\u9fff\uf900-\ufaff]+/g
  let m: RegExpExecArray | null
  while ((m = re.exec(text))) {
    const w = m[0]
    if (/^[A-Za-z0-9_]/.test(w)) { out.push(w); continue }
    if (w.length === 1) { out.push(w); continue }
    for (let i = 0; i < w.length - 1; i++) out.push(w.slice(i, i + 2))
  }
  return out
}

export default defineConfig({
  lang: 'zh-CN',
  title: 'Python 读码实战课',
  description: '面向开发者的系统化 Python 课程：浏览器内可运行示例、自动判题练习、读真实代码，终点是读懂 minimal_agent.py',
  srcDir,
  srcExclude: ['**/README.md'],
  outDir: path.join(siteRoot, '.vitepress/dist'),
  cacheDir: path.join(siteRoot, '.vitepress/cache'),
  lastUpdated: false,
  head: [
    ['meta', { name: 'theme-color', content: '#3776ab' }],
    ['link', { rel: 'icon', type: 'image/svg+xml', href: '/logo.svg' }],
  ],
  markdown: {
    lineNumbers: false,
    languageAlias: { pycon: 'python' },
    config: (md) => coursePlugin(md, { srcDir, projectRoot }),
  },
  vite: {
    publicDir: path.join(siteRoot, 'public'),
    server: { fs: { allow: [projectRoot] } },
    // 内容在 ../docs（site 之外），其编译产物中的裸导入需要显式指向 site/node_modules
    resolve: {
      alias: [
        { find: /^vue$/, replacement: path.join(siteRoot, 'node_modules/vue') },
        { find: /^vue\/server-renderer$/, replacement: path.join(siteRoot, 'node_modules/vue/server-renderer') },
      ],
    },
    optimizeDeps: { include: ['codemirror', '@codemirror/lang-python', '@codemirror/theme-one-dark'] },
  },
  themeConfig: {
    logo: { light: '/logo.svg', dark: '/logo.svg' },
    nav: [
      { text: '首页', link: '/' },
      { text: '课程大纲', link: '/课程大纲' },
      { text: '开始学习', link: stages[0]?.lessons[0]?.link || '/' },
      { text: '速查表', link: '/课程/附录/速查表' },
      { text: '术语表', link: '/课程/附录/术语表' },
    ],
    sidebar: buildSidebar(stages, srcDir),
    // 自定义字段：课程元数据，供首页路线图与进度统计使用
    course: stages,
    outline: { level: [2, 3], label: '本页目录' },
    docFooter: { prev: '上一篇', next: '下一篇' },
    darkModeSwitchLabel: '外观',
    lightModeSwitchTitle: '切换到浅色模式',
    darkModeSwitchTitle: '切换到深色模式',
    sidebarMenuLabel: '目录',
    returnToTopLabel: '回到顶部',
    externalLinkIcon: true,
    footer: { message: '内容源：docs/ 下的 Markdown（单一事实来源）。示例在浏览器内由 Pyodide 运行。', copyright: '核对日期 2026-10-06' },
    search: {
      provider: 'local',
      options: {
        translations: {
          button: { buttonText: '搜索课程', buttonAriaLabel: '搜索课程' },
          modal: {
            displayDetails: '显示详情',
            resetButtonTitle: '清除',
            backButtonTitle: '关闭',
            noResultsText: '没有找到结果',
            footer: { selectText: '选择', navigateText: '切换', closeText: '关闭' },
          },
        },
        miniSearch: {
          options: { tokenize },
          searchOptions: { combineWith: 'AND', prefix: true, fuzzy: 0.1, tokenize },
        },
      },
    },
  } as any,
})
