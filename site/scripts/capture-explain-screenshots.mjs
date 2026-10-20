// Goal v2.4 D9：导出 6 张解读页截图（需站点已启动，默认 5180）。
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { chromium } from 'playwright-core'

const siteRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const outDir = path.resolve(siteRoot, '..', 'docs/规划/证据/v2.4-screenshots')
const sitePort = process.env.SERVER_PORT || process.env.PORT || process.env.JDP_PYTHON_SITE_PORT || 5180
const BASE = process.env.SMOKE_URL || `http://127.0.0.1:${sitePort}`
const explainUrl = `${BASE}/${encodeURI('代码解读/')}`
const lessonUrl = `${BASE}/${encodeURI('课程/01-环境与工具/01-运行Python代码.html')}`

const candidates = [
  process.env.CHROME_PATH,
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/Applications/Chromium.app/Contents/MacOS/Chromium',
  '/usr/bin/google-chrome',
].filter(Boolean)
const executablePath = candidates.find((p) => fs.existsSync(p))
if (!executablePath) {
  console.error('未找到 Chrome，请设置 CHROME_PATH')
  process.exit(2)
}

fs.mkdirSync(outDir, { recursive: true })

const browser = await chromium.launch({ executablePath, headless: true })
const page = await browser.newPage()

async function shot(name) {
  const file = path.join(outDir, name)
  await page.screenshot({ path: file, fullPage: true })
  console.log('wrote', file)
}

await page.goto(explainUrl, { waitUntil: 'networkidle' })
await shot('01-empty-page.png')

await page.getByRole('button', { name: '开始解读' }).click()
await page.locator('#ce-overview').waitFor({ timeout: 120_000 })
await shot('02-result-six-panels.png')

await page.goto(explainUrl, { waitUntil: 'networkidle' })
await page.locator('textarea, .cm-content').first().click()
await page.keyboard.press('ControlOrMeta+A')
await page.keyboard.type('def broken(\n')
await page.getByRole('button', { name: '开始解读' }).click()
await page.locator('.ce-error, .explain-error, #ce-overview').first().waitFor({ timeout: 60_000 })
await shot('03-syntax-error.png')

await page.goto(lessonUrl, { waitUntil: 'networkidle' })
const runner = page.locator('.py-runner').first()
await runner.getByRole('button', { name: '解读' }).scrollIntoViewIfNeeded()
await shot('04-lesson-explain-button.png')

await page.goto(explainUrl, { waitUntil: 'networkidle' })
await page.locator('.VPNavBarAppearance button, .VPSwitchAppearance').first().click()
await page.waitForFunction(() => document.documentElement.classList.contains('dark'))
await shot('05-dark-mode.png')

await page.setViewportSize({ width: 390, height: 844 })
await page.goto(explainUrl, { waitUntil: 'networkidle' })
await shot('06-viewport-390w.png')

await browser.close()
console.log('D9 截图完成')
