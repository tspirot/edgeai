<?php
/**
 * GitHub webhook пријемник за deploy на Virtualmin.
 * Постави ван document root-а и мапирај Apache alias-ом на /webhook, или у
 * public_html ако друкчије не може. Дозволи PHP execute за овај фајл.
 *
 * GitHub → Settings → Webhooks:
 *   Payload URL: https://edgeai.tsp.edu.rs/webhook.php
 *   Content type: application/json
 *   Secret: иста вредност као WEBHOOK_SECRET у deploy/.env
 *   Events: само "push"
 */

header('Content-Type: text/plain; charset=utf-8');

$envFile = __DIR__ . '/.env';
if (!is_readable($envFile)) { http_response_code(500); exit("no .env\n"); }
$cfg = parse_ini_file($envFile);
$secret = $cfg['WEBHOOK_SECRET'] ?? '';
if ($secret === '' || $secret === 'promeni-me') { http_response_code(500); exit("set WEBHOOK_SECRET\n"); }

$body = file_get_contents('php://input');
$sig  = $_SERVER['HTTP_X_HUB_SIGNATURE_256'] ?? '';
$calc = 'sha256=' . hash_hmac('sha256', $body, $secret);
if (!hash_equals($calc, $sig)) { http_response_code(403); exit("bad signature\n"); }

$event = $_SERVER['HTTP_X_GITHUB_EVENT'] ?? '';
if ($event === 'ping') { echo "pong\n"; exit; }
if ($event !== 'push') { echo "ignored event: $event\n"; exit; }

$payload = json_decode($body, true);
if (($payload['ref'] ?? '') !== 'refs/heads/main') { echo "ignored ref\n"; exit; }

// deploy у позадини да webhook не истекне
$script = escapeshellarg(__DIR__ . '/deploy.sh');
$log    = escapeshellarg(__DIR__ . '/last-deploy.log');
shell_exec("nohup bash $script > $log 2>&1 &");

echo "deploy started\n";
