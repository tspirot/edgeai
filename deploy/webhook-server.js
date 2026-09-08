#!/usr/bin/env node
/**
 * GitHub webhook пријемник за edgeai.tsp.edu.rs
 * Исти приступ као код tsp портала: Node сервис на 127.0.0.1, PM2 га држи,
 * Apache (Virtualmin) проксира /webhook на овај порт. Без SSH.
 *
 * ENV (поставља се преко deploy/ecosystem.config.js):
 *   WEBHOOK_SECRET  — исти као у GitHub webhook подешавањима
 *   WEBHOOK_PORT    — подразумевано 9008
 *   REPO_DIR        — путања до клонираног репоа
 *   PUBLIC_HTML     — document root поддомена
 */

const http = require('http');
const crypto = require('crypto');
const { execFile } = require('child_process');
const path = require('path');
const fs = require('fs');

const SECRET = process.env.WEBHOOK_SECRET || '';
const PORT = process.env.WEBHOOK_PORT || 9008;
const BRANCH = process.env.DEPLOY_BRANCH || 'main';
const DEPLOY_SCRIPT = path.join(__dirname, 'deploy.sh');
const LOG_FILE = path.join(__dirname, 'logs', 'webhook.log');

try {
  fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
} catch (err) {
  console.error('Не могу да направим logs/:', err.message);
}

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  process.stdout.write(line);
  try { fs.appendFileSync(LOG_FILE, line); } catch { /* ignore */ }
}

function verifySignature(payload, signature) {
  if (!SECRET) return true;
  const digest = 'sha256=' + crypto.createHmac('sha256', SECRET).update(payload).digest('hex');
  try {
    return crypto.timingSafeEqual(Buffer.from(digest), Buffer.from(signature || ''));
  } catch {
    return false;
  }
}

let deploying = false;

function runDeploy(reason) {
  if (deploying) {
    log(`DEPLOY: већ у току, прескачем (${reason})`);
    return;
  }
  deploying = true;
  log(`DEPLOY: покрећем deploy.sh (${reason})`);
  const env = {
    ...process.env,
    GIT_TERMINAL_PROMPT: '0',
    REPO_DIR: process.env.REPO_DIR || path.resolve(__dirname, '..'),
    PUBLIC_HTML: process.env.PUBLIC_HTML || '',
    DEPLOY_BRANCH: BRANCH,
  };
  execFile('bash', [DEPLOY_SCRIPT], { timeout: 900000, env }, (err, stdout, stderr) => {
    deploying = false;
    if (err) {
      log(`ГРЕШКА у deploy: ${err.message}`);
      if (stderr) log(`STDERR: ${stderr.trim()}`);
    } else {
      log('УСПЕШНО: deploy завршен');
      if (stdout) log(`STDOUT: ${stdout.trim().split('\n').slice(-3).join(' | ')}`);
    }
  });
}

const server = http.createServer((req, res) => {
  if (req.method === 'GET' && req.url === '/webhook/health') {
    res.writeHead(200);
    res.end('ok');
    return;
  }
  if (req.method !== 'POST' || !req.url.startsWith('/webhook')) {
    res.writeHead(404);
    res.end('Not found');
    return;
  }

  let body = '';
  req.on('data', (chunk) => { body += chunk.toString(); });
  req.on('end', () => {
    const signature = req.headers['x-hub-signature-256'];
    if (SECRET && !verifySignature(body, signature)) {
      log('ОДБИЈЕН: неважећи потпис');
      res.writeHead(401);
      res.end('Unauthorized');
      return;
    }

    const event = req.headers['x-github-event'] || 'push';
    if (event === 'ping') {
      log('GitHub PING — webhook активан');
      res.writeHead(200);
      res.end('PONG');
      return;
    }
    if (event !== 'push') {
      res.writeHead(200);
      res.end(`Event ${event} ignored`);
      return;
    }

    let payload;
    try {
      payload = JSON.parse(body);
    } catch {
      res.writeHead(400);
      res.end('Bad Request');
      return;
    }

    if ((payload.ref || '') !== `refs/heads/${BRANCH}`) {
      log(`ПРЕСКОЧЕН: push на ${payload.ref} (није ${BRANCH})`);
      res.writeHead(200);
      res.end('Skipped: other branch');
      return;
    }

    // сајт се мења само ако је дирнуто web/ (или сам deploy)
    const files = (payload.commits || []).flatMap((c) => [
      ...(c.added || []), ...(c.modified || []), ...(c.removed || []),
    ]);
    const touchesSite = files.length === 0 || files.some(
      (f) => f.startsWith('web/') || f.startsWith('deploy/'),
    );
    if (!touchesSite) {
      log('ПРЕСКОЧЕН: push не дира web/');
      res.writeHead(200);
      res.end('Skipped: no site changes');
      return;
    }

    const pusher = payload.pusher?.name || 'unknown';
    log(`ПРИМЉЕНО: push од ${pusher}, ${payload.commits?.length || 0} commit(s)`);
    res.writeHead(202);
    res.end('Deploy started');
    runDeploy(`push од ${pusher}`);
  });
});

server.listen(PORT, '127.0.0.1', () => log(`Webhook сервер на 127.0.0.1:${PORT}`));

process.on('SIGTERM', () => server.close(() => process.exit(0)));
