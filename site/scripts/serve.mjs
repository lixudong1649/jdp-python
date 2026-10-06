// 零依赖静态服务器：托管构建产物 .vitepress/dist，默认只监听本机 127.0.0.1:5180。
// （vitepress preview 会忽略 --host、监听所有网卡，故用此脚本替代。）
// 用法：node scripts/serve.mjs [--port 5180] [--host 127.0.0.1]
import http from 'node:http'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const args = process.argv.slice(2)
const opt = (name, def) => {
  const i = args.indexOf(`--${name}`)
  return i >= 0 && args[i + 1] ? args[i + 1] : def
}
const host = opt('host', process.env.HOST || '127.0.0.1')
const port = Number(opt('port', process.env.PORT || 5180))
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../.vitepress/dist')

const MIME = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.mjs': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8', '.json': 'application/json; charset=utf-8', '.svg': 'image/svg+xml',
  '.png': 'image/png', '.ico': 'image/x-icon', '.woff2': 'font/woff2', '.wasm': 'application/wasm',
  '.zip': 'application/zip', '.py': 'text/plain; charset=utf-8', '.txt': 'text/plain; charset=utf-8',
  '.md': 'text/plain; charset=utf-8', '.toml': 'text/plain; charset=utf-8',
}

function resolveFile(urlPath) {
  let rel
  try { rel = decodeURIComponent(urlPath.split('?')[0].split('#')[0]) } catch { return null }
  const abs = path.resolve(root, '.' + rel)
  if (abs !== root && !abs.startsWith(root + path.sep)) return null
  for (const cand of [abs, path.join(abs, 'index.html'), abs + '.html']) {
    try { if (fs.statSync(cand).isFile()) return cand } catch {}
  }
  return null
}

if (!fs.existsSync(path.join(root, 'index.html'))) {
  console.error('未找到构建产物，请先运行 npm run build')
  process.exit(1)
}

http.createServer((req, res) => {
  if (req.method !== 'GET' && req.method !== 'HEAD') { res.writeHead(405).end(); return }
  let file = resolveFile(req.url || '/')
  let status = 200
  if (!file) { file = path.join(root, '404.html'); status = 404 }
  const ext = path.extname(file)
  res.writeHead(status, {
    'Content-Type': MIME[ext] || 'application/octet-stream',
    'Content-Length': fs.statSync(file).size,
    'Cache-Control': /[/\\]assets[/\\]/.test(file) ? 'public, max-age=31536000, immutable' : 'no-cache',
    'X-Content-Type-Options': 'nosniff',
  })
  if (req.method === 'HEAD') { res.end(); return }
  fs.createReadStream(file).pipe(res)
}).listen(port, host, () => {
  console.log(`课程站点：http://${host}:${port}/  （目录 ${path.relative(process.cwd(), root) || '.'}）`)
})
