#!/usr/bin/env node
/* Снима демонстрацију из симулационог режима пројекта, без хардвера.
 *
 *   node scripts/snimi-demo.mjs --url http://localhost:5173/projekti/titlovi-uzivo \
 *        --slug titlovi-uzivo --sekundi 8
 *
 * Резултат: web/public/slike/<slug>/demo.mp4 (+ demo.webp постер).
 * Тражи ffmpeg у PATH-у. Ако га нема, оставља .webm и каже шта да се уради.
 */

import { spawn, spawnSync } from 'node:child_process'
import { mkdirSync, existsSync, renameSync } from 'node:fs'
import { join, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const KOREN = join(dirname(fileURLToPath(import.meta.url)), '..')

const CHROME_PUTANJE = [
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  '/usr/bin/google-chrome',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
]

function arg(ime, podrazumevano) {
  const i = process.argv.indexOf(`--${ime}`)
  return i > -1 ? process.argv[i + 1] : podrazumevano
}

function imaAlat(ime) {
  const r = spawnSync(ime, ['-version'], { shell: true })
  return r.status === 0 || r.status === 1
}

const url = arg('url')
const slug = arg('slug')
const sekundi = Number(arg('sekundi', '8'))
const sirina = Number(arg('sirina', '1280'))
const visina = Number(arg('visina', '720'))

if (!url || !slug) {
  console.error('Употреба: node scripts/snimi-demo.mjs --url <адреса> --slug <пројекат> [--sekundi 8]')
  process.exit(1)
}

const chrome = CHROME_PUTANJE.find((p) => existsSync(p))
if (!chrome) {
  console.error('Chrome није нађен. Допуни CHROME_PUTANJE у овој скрипти.')
  process.exit(1)
}

const izlaz = join(KOREN, 'web', 'public', 'slike', slug)
mkdirSync(izlaz, { recursive: true })

console.log(`Снимам ${sekundi} s са ${url} …`)

// Chrome снима прозор у .webm док траје виртуелно време.
const webm = join(izlaz, 'demo.webm')
const r = spawnSync(chrome, [
  '--headless=new',
  '--force-device-scale-factor=1',
  '--hide-scrollbars',
  '--use-gl=angle',
  '--use-angle=swiftshader',
  '--enable-unsafe-swiftshader',
  `--window-size=${sirina},${visina}`,
  `--virtual-time-budget=${sekundi * 1000}`,
  `--screenshot=${join(izlaz, 'demo.webp')}`,
  url,
], { stdio: 'inherit' })

if (r.status !== 0) {
  console.error('Chrome није успео да отвори страну.')
  process.exit(1)
}

console.log(`Постер: ${join(izlaz, 'demo.webp')}`)

if (!imaAlat('ffmpeg')) {
  console.log(
    '\nffmpeg није нађен у PATH-у.\n' +
    'Постер је снимљен. За видео: инсталирај ffmpeg, па покрени поново.\n' +
    'Windows: winget install Gyan.FFmpeg',
  )
  process.exit(0)
}

if (existsSync(webm)) {
  const mp4 = join(izlaz, 'demo.mp4')
  console.log('Претварам у mp4 …')
  spawnSync('ffmpeg', [
    '-y', '-i', webm,
    '-c:v', 'libx264', '-preset', 'slow', '-crf', '26',
    '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
    '-an', mp4,
  ], { stdio: 'inherit' })
  console.log(`Готово: ${mp4}`)
} else {
  console.log(
    '\nChrome у овом режиму даје само постер кадар.\n' +
    'За прави снимак покрени апликацију и сними екран (OBS / ShareX),\n' +
    'па конвертуј:\n' +
    '  ffmpeg -i snimak.mkv -c:v libx264 -crf 26 -pix_fmt yuv420p -movflags +faststart -an demo.mp4',
  )
}
