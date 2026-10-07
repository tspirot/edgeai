/* Мали бојач синтаксе без зависности: python, bash, json.
   Враћа низ { t: класа|null, s: текст } — рендерује га components/Kod.jsx.
   Правила се пробају редом; прво које се поклапа на тренутној позицији побеђује. */

const PY_KW = [
  'and', 'as', 'assert', 'break', 'class', 'continue', 'def', 'del', 'elif', 'else', 'except',
  'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda', 'nonlocal', 'not',
  'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield',
]
const PY_CONST = ['True', 'False', 'None', 'self']
const PY_BUILTIN = [
  'print', 'len', 'range', 'int', 'float', 'str', 'list', 'dict', 'tuple', 'set', 'min', 'max',
  'sum', 'abs', 'enumerate', 'zip', 'open', 'sorted', 'isinstance', 'super',
]
const BASH_KW = ['if', 'then', 'else', 'fi', 'for', 'do', 'done', 'while', 'case', 'esac', 'in', 'export']

const words = (list) => new RegExp(`\\b(?:${list.join('|')})\\b`)

const STR = /(?:[rbfRBF]{1,2})?(?:"""[\s\S]*?"""|'''[\s\S]*?'''|"(?:\\.|[^"\\\n])*"|'(?:\\.|[^'\\\n])*')/

const JEZICI = {
  python: [
    ['k-kom', /#.*/],
    ['k-str', STR],
    ['k-dek', /@[A-Za-z_][\w.]*/],
    ['k-br', /\b\d+(?:\.\d+)?(?:e[+-]?\d+)?\b|0x[0-9a-fA-F]+/],
    ['k-kw', words(PY_KW)],
    ['k-kon', words(PY_CONST)],
    ['k-ugr', words(PY_BUILTIN)],
    ['k-fn', /[A-Za-z_]\w*(?=\()/],
  ],
  bash: [
    ['k-kom', /#.*/],
    ['k-str', /"(?:\\.|[^"\\])*"|'[^']*'/],
    ['k-var', /\$\{?[A-Za-z_]\w*\}?|\$[0-9?@#]/],
    ['k-flag', /(?<=\s)--?[A-Za-z][\w-]*/],
    ['k-br', /\b\d+(?:\.\d+)?\b/],
    ['k-kw', words(BASH_KW)],
    // Прва реч у реду, или иза && ; | — име команде.
    ['k-fn', /(?:(?<=^)|(?<=\n)|(?<=&&\s)|(?<=\|\s)|(?<=;\s)|(?<=^\s+)|(?<=\n\s+))[A-Za-z_./~][\w./~-]*/],
  ],
  json: [
    ['k-kljuc', /"(?:\\.|[^"\\\n])*"(?=\s*:)/],
    ['k-str', /"(?:\\.|[^"\\\n])*"/],
    ['k-br', /-?\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b/],
    ['k-kon', /\b(?:true|false|null)\b/],
  ],
}
JEZICI.sh = JEZICI.bash
JEZICI.shell = JEZICI.bash
JEZICI.py = JEZICI.python

export function oboji(kod, jezik) {
  const pravila = JEZICI[jezik]
  if (!pravila) return [{ t: null, s: kod }]

  // Једна алтернација са по једном групом за свако правило; најлевље поклапање побеђује,
  // а при истој позицији — правило које је раније у листи.
  const re = new RegExp(pravila.map(([, r]) => `(${r.source})`).join('|'), 'g')
  const out = []
  let kraj = 0
  let m
  while ((m = re.exec(kod)) !== null) {
    if (m[0] === '') { re.lastIndex++; continue }
    if (m.index > kraj) out.push({ t: null, s: kod.slice(kraj, m.index) })
    const i = m.slice(1).findIndex((g) => g !== undefined)
    out.push({ t: pravila[i][0], s: m[0] })
    kraj = m.index + m[0].length
  }
  if (kraj < kod.length) out.push({ t: null, s: kod.slice(kraj) })
  return out
}
