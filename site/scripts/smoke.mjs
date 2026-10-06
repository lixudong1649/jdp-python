// 浏览器冒烟测试（playwright-core + 本机 Chrome/Chromium）。
// 用法：先启动站点（npm run preview），再执行 `npm run smoke`；
// 可选环境变量：SMOKE_URL（默认 http://127.0.0.1:5180）、CHROME_PATH（浏览器可执行文件）。
import fs from 'node:fs'
import { chromium } from 'playwright-core'

const BASE = process.env.SMOKE_URL || 'http://127.0.0.1:5180'
const candidates = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
  '/usr/bin/google-chrome',
  '/usr/bin/chromium',
  '/usr/bin/chromium-browser',
].filter(Boolean)
const executablePath = candidates.find((p) => fs.existsSync(p))
if (!executablePath) {
  console.error('未找到 Chrome/Chromium，请设置 CHROME_PATH')
  process.exit(2)
}

const results = []
const step = async (name, fn) => {
  const t = Date.now()
  try {
    await fn()
    results.push({ name, ok: true, ms: Date.now() - t })
    console.log(`  ✓ ${name} (${Date.now() - t} ms)`)
  } catch (e) {
    results.push({ name, ok: false, error: String(e.message || e) })
    console.log(`  ✗ ${name}: ${String(e.message || e).split('\n')[0]}`)
  }
}

const browser = await chromium.launch({ executablePath, headless: true })
const page = await browser.newPage()
const consoleErrors = []
page.on('console', (m) => { if (m.type() === 'error') consoleErrors.push(m.text()) })
page.on('pageerror', (e) => consoleErrors.push(String(e)))
const lesson = (p) => `${BASE}/${encodeURI(p)}`

console.log(`冒烟测试：${BASE}（${executablePath}）`)

await step('首页路线图渲染 11 个阶段', async () => {
  await page.goto(BASE + '/', { waitUntil: 'networkidle' })
  await page.waitForSelector('.roadmap-card')
  const n = await page.locator('.roadmap-card').count()
  if (n !== 11) throw new Error(`阶段卡片数 ${n}`)
})

await step('示例代码块在 Pyodide 中运行并输出', async () => {
  await page.goto(lesson('课程/01-环境与工具/01-运行Python代码.html'), { waitUntil: 'networkidle' })
  const runner = page.locator('.py-runner').first()
  await runner.getByRole('button', { name: '▶ 运行' }).click()
  await runner.locator('.py-stdout').waitFor({ timeout: 90_000 })
  const out = await runner.locator('.py-stdout').innerText()
  if (!out.includes('Hello, Python')) throw new Error('输出不符：' + out)
})

await step('预期报错示例显示错误与说明', async () => {
  const runner = page.locator('.py-runner:has(.py-badge-warn)').first()
  await runner.getByRole('button', { name: '▶ 运行' }).click()
  await runner.locator('.py-output-note').waitFor({ timeout: 30_000 })
  const err = await runner.locator('.py-stderr').innerText()
  if (!err.includes('IndentationError')) throw new Error('错误输出不符：' + err)
})

await step('编辑代码后运行（CodeMirror 编辑器）', async () => {
  const runner = page.locator('.py-runner').first()
  await runner.getByRole('button', { name: '编辑' }).click()
  const editor = runner.locator('.cm-content')
  await editor.waitFor()
  await editor.click()
  await page.keyboard.press('ControlOrMeta+A')
  await page.keyboard.type('print(6 * 7)')
  await runner.getByRole('button', { name: '▶ 运行' }).click()
  await page.waitForFunction((el) => el.querySelector('.py-stdout')?.textContent?.trim() === '42', await runner.elementHandle(), { timeout: 30_000 })
})

await step('练习：起始代码提交被判失败', async () => {
  const ex = page.locator('.py-exercise').first()
  await ex.getByRole('button', { name: '✓ 提交检查' }).click()
  await ex.locator('.py-verdict-fail').waitFor({ timeout: 30_000 })
})

await step('练习：载入参考答案后通过并记录进度', async () => {
  const ex = page.locator('.py-exercise').first()
  await ex.getByRole('button', { name: '查看参考答案' }).click()
  await ex.getByRole('button', { name: '载入到编辑器' }).click()
  await ex.getByRole('button', { name: '✓ 提交检查' }).click()
  await ex.locator('.py-verdict-pass').waitFor({ timeout: 30_000 })
  await page.reload({ waitUntil: 'networkidle' })
  await page.locator('.py-exercise[data-passed="1"]').first().waitFor({ timeout: 10_000 })
})

await step('标记本课完成并更新侧边栏进度', async () => {
  await page.getByRole('button', { name: '标记本课已完成' }).click()
  await page.getByRole('button', { name: '撤销完成' }).waitFor()
  const label = await page.locator('.sidebar-progress-label').innerText()
  if (!/学习进度 1\//.test(label)) throw new Error('侧边栏进度：' + label)
  const marked = await page.locator('.VPSidebar a.is-done').count()
  if (marked < 1) throw new Error('侧边栏未出现完成标记')
})

await step('死循环 10 秒超时终止，之后可继续运行', async () => {
  const runner = page.locator('.py-runner').nth(1)
  await runner.getByRole('button', { name: '编辑' }).click()
  const editor = runner.locator('.cm-content')
  await editor.waitFor()
  await editor.click()
  await page.keyboard.press('ControlOrMeta+A')
  await page.keyboard.type('while True: pass')
  await runner.getByRole('button', { name: '▶ 运行' }).click()
  await runner.locator('.py-stderr', { hasText: '已被终止' }).waitFor({ timeout: 30_000 })
  const first = page.locator('.py-runner').first()
  await first.getByRole('button', { name: '▶ 运行' }).click()
  await first.locator('.py-stdout', { hasText: 'Hello, Python' }).waitFor({ timeout: 90_000 })
})

await step('中文全文搜索有结果', async () => {
  await page.keyboard.press('Escape')
  await page.locator('.VPNavBarSearch button').click()
  const input = page.locator('.VPLocalSearchBox input')
  await input.fill('真值检测')
  await page.locator('.VPLocalSearchBox .result').first().waitFor({ timeout: 10_000 })
  const n = await page.locator('.VPLocalSearchBox .result').count()
  if (n < 1) throw new Error('无搜索结果')
  await page.keyboard.press('Escape')
})

await step('深色/浅色模式切换', async () => {
  const before = await page.evaluate(() => document.documentElement.classList.contains('dark'))
  await page.locator('.VPNavBarAppearance button, .VPSwitchAppearance').first().click()
  const after = await page.evaluate(() => document.documentElement.classList.contains('dark'))
  if (before === after) throw new Error('未切换')
})

await step('上一篇/下一篇导航存在', async () => {
  await page.goto(lesson('课程/02-基础语法与数据类型/02-数字布尔与None.html'), { waitUntil: 'networkidle' })
  await page.locator('.pager-link.prev').waitFor()
  await page.locator('.pager-link.next').waitFor()
})

await browser.close()
const failed = results.filter((r) => !r.ok)
const relevantErrors = consoleErrors.filter((e) => !/favicon/.test(e))
if (relevantErrors.length) console.log('浏览器控制台错误：\n  ' + relevantErrors.slice(0, 10).join('\n  '))
console.log(`\n冒烟测试：${results.length - failed.length}/${results.length} 通过`)
process.exit(failed.length ? 1 : 0)
