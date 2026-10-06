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

// 部署路径：本机为 '/'；GitHub Pages 项目页构建时设 SITE_BASE=/jdp-python/。SITE_OUT 可改输出目录（便于本机并行验证）。
const base = process.env.SITE_BASE || '/'
const outDir = process.env.SITE_OUT ? path.resolve(siteRoot, process.env.SITE_OUT) : path.join(siteRoot, '.vitepress/dist')
const REPO = 'https://github.com/lixudong1649/jdp-python'
const AUTHOR = 'https://github.com/lixudong1649'

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
  base,
  srcDir,
  srcExclude: ['**/README.md'],
  outDir,
  cacheDir: path.join(siteRoot, '.vitepress/cache'),
  lastUpdated: false,
  head: [
    ['meta', { name: 'theme-color', content: '#3776ab' }],
    ['link', { rel: 'icon', type: 'image/svg+xml', href: `${base}logo.svg` }],
  ],
  markdown: {
    lineNumbers: false,
    languageAlias: { pycon: 'python' },
    config: (md) => coursePlugin(md, { srcDir, projectRoot, base }),
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
      { text: '项目', items: [
        { text: '项目架构与技术栈', link: '/项目架构与技术栈' },
        { text: '关于与声明', link: '/关于' },
        { text: '更新记录', link: `${REPO}/blob/main/CHANGELOG.md` },
      ] },
    ],
    socialLinks: [{ icon: 'github', link: REPO, ariaLabel: 'GitHub 仓库' }],
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
    footer: {
      message: `代码 <a href="${REPO}/blob/main/LICENSE">MIT</a> · 课程内容 <a href="${REPO}/blob/main/LICENSE-CONTENT.md">CC BY-NC-SA 4.0</a> · <a href="${base}关于">关于与声明</a> · <a href="${REPO}/issues">反馈问题</a>`,
      copyright: `© 2026 <a href="${AUTHOR}">lixudong1649</a> · 核对日期 2026-10-06`,
    },
    // 自定义字段：文档页底部版权行（默认页脚仅在无侧边栏页面显示）
    siteMeta: { repo: REPO, author: AUTHOR },
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
