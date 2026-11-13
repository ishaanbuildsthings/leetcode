// How to call a template, read from its source (Python or C++). Shared by the catalog builds (scripts/catalog-lib.mjs
// re-exports it; Node strips the types) and the set picker's drawer, which runs it on the code it just fetched. No
// imports but types, so Node can load this file directly.
import type { TemplateLang, Usage, UsageParam } from "./template-picker";

interface ParsedClass {
  name: string;
  doc: string;
  ctor: UsageParam[];
  ctorDoc: string;
  methods: Record<string, { params: string[]; returns?: string; doc: string }>;
  // C++: a plain struct, not a template <typename T> one (written without <T>)
  plain?: boolean;
}

// How to call a template, read from its source: the class that implements the most of the folder's operations (ties:
// the one defined last, as a wrapper follows the class it wraps), its constructor's parameters, and each operation's
// parameters (and, in C++, return type). The picker turns this into "construct, then one line per selected op".

// "a, b = 2, vector<pair<long long, T>> c" -> top-level comma-separated pieces
function splitTopLevel(s: string): string[] {
  const out: string[] = [];
  let depth = 0;
  let cur = "";
  let quote = ""; // inside a '(' or "," literal, brackets and commas are just characters
  for (const ch of s) {
    if (quote) {
      if (ch === quote) quote = "";
    } else if (ch === "'" || ch === '"') quote = ch;
    else if ("<([{".includes(ch)) depth++;
    else if (">)]}".includes(ch)) depth--;
    if (ch === "," && depth === 0 && !quote) {
      out.push(cur.trim());
      cur = "";
    } else cur += ch;
  }
  if (cur.trim()) out.push(cur.trim());
  return out;
}

function pyParams(s: string): UsageParam[] {
  return splitTopLevel(s).map((p) => {
    const [name, def] = p.split("=").map((x) => x.trim());
    return def === undefined ? { name } : { name, default: def };
  });
}

function cppParams(s: string): UsageParam[] {
  return splitTopLevel(s).map((p) => {
    const [decl, def] = p.split("=").map((x) => x.trim());
    const m = decl.match(/^(.*?)\s*\b(\w+)$/);
    const param: UsageParam = m
      ? { name: m[2], type: m[1].trim() }
      : { name: decl, type: "" };
    return def === undefined ? param : { ...param, default: def };
  });
}

// The comment block right above line i (comment marker cm), as one string with an "O(...) --" cost prefix dropped.
function docAbove(lines: string[], i: number, cm: string): string {
  const out: string[] = [];
  for (let j = i - 1; j >= 0; j--) {
    const t = lines[j].trim();
    if (
      !t.startsWith(cm) ||
      t.startsWith(`${cm} @`) ||
      /^(#|\/\/)\s*[=\-]{4,}/.test(t)
    )
      break;
    out.unshift(t.slice(cm.length).trim());
  }
  return out
    .join(" ")
    .trim()
    .replace(
      /^(?:amortized\s+)?O\((?:[^()]|\([^()]*\))*\)(?:\s*(?:expected|amortized))?\s*(?:--|—|$)\s*/,
      "",
    )
    .trim();
}

// Whether the comment block right above line i opens with its cost ("O(log N) -- ...").
function startsWithCost(lines: string[], i: number, cm: string): boolean {
  let first = "";
  for (let j = i - 1; j >= 0 && lines[j].trim().startsWith(cm); j--) first = lines[j].trim().slice(cm.length).trim();
  return /^(?:amortized\s+)?O\(/.test(first);
}

// Line i with its comment dropped; a signature broken over several lines comes back as one.
function joinedSignature(lines: string[], i: number, cm: string): string {
  const uncommented = (t: string) => t.replace(cm === "#" ? /#.*$/ : /\/\/.*$/, "").trimEnd();
  let whole = uncommented(lines[i]);
  if (!/^\s{4}(?!\s)/.test(whole) || (cm === "#" && !/^\s{4}def /.test(whole))) return whole;
  const open = () => {
    let depth = 0;
    let quote = "";
    for (const ch of whole) {
      if (quote) {
        if (ch === quote) quote = "";
      } else if (ch === "'" || ch === '"') quote = ch;
      else if (ch === "(") depth++;
      else if (ch === ")") depth--;
    }
    return depth > 0;
  };
  for (let j = i + 1; j < lines.length && j <= i + 8 && open(); j++) whole += ` ${uncommented(lines[j]).trim()}`;
  return whole;
}

// A long constructor comment is mostly implementation notes; its first sentence is the part worth showing.
const firstSentenceIfLong = (s: string) =>
  s.length > 180 ? s.split(/(?<=\.)\s/)[0] : s;

// The parameter list of the call / definition whose "(" is at or after index i: up to the matching ")".
function parenArgs(line: string, i: number): string {
  const open = line.indexOf("(", i);
  let depth = 0;
  for (let k = open; k < line.length; k++) {
    if (line[k] === "'" || line[k] === '"') { // a char or string literal, e.g. T openChar = T('(')
      const close = line.indexOf(line[k], k + 1);
      if (close !== -1) k = close;
    } else if (line[k] === "(") depth++;
    else if (line[k] === ")" && --depth === 0) return line.slice(open + 1, k);
  }
  return line.slice(open + 1);
}

// A Python class's description: the comment block above it (past blank lines and module constants), else the
// comment lines / docstring right inside it.
function pyClassDoc(lines: string[], i: number): string {
  let j = i - 1;
  while (
    j >= 0 &&
    (lines[j].trim() === "" || /^[A-Z_][A-Z0-9_]* = /.test(lines[j]))
  )
    j--;
  const above =
    j >= 0 && lines[j].trim().startsWith("#")
      ? docAbove(lines, j + 1, "#")
      : "";
  if (above) return above;
  const inside: string[] = [];
  for (let k = i + 1; k < lines.length; k++) {
    const t = lines[k].trim();
    if (t.startsWith("#")) inside.push(t.slice(1).trim());
    else if (/^"""/.test(t)) {
      let text = t.slice(3);
      while (!text.includes('"""') && k + 1 < lines.length)
        text += " " + lines[++k].trim();
      inside.push(text.replace(/"""[\s\S]*$/, "").trim());
      break;
    } else break;
  }
  return inside.join(" ").trim();
}

function pyClasses(text: string): ParsedClass[] {
  const classes: ParsedClass[] = [];
  const lines = text.split("\n");
  let cur: ParsedClass | null = null;
  lines.forEach((line, i) => {
    const c = line.match(/^class (\w+)/);
    if (c) {
      cur = {
        name: c[1],
        doc: pyClassDoc(lines, i),
        ctor: [],
        ctorDoc: "",
        methods: {},
      };
      classes.push(cur);
      return;
    }
    if (/^[^\s#]/.test(line)) cur = null; // any other top-level statement ends the class
    const m = joinedSignature(lines, i, "#").match(/^    def (\w+)\(self(?:,\s*)?(.*)\):/);
    if (!cur || !m) return;
    if (m[1] === "__init__") {
      cur.ctor = pyParams(m[2]);
      cur.ctorDoc = firstSentenceIfLong(docAbove(lines, i, "#"));
    } else
      cur.methods[m[1]] = {
        params: pyParams(m[2]).map((p) => p.name),
        doc: docAbove(lines, i, "#"),
      };
  });
  return classes;
}

function cppClasses(text: string): ParsedClass[] {
  const classes: ParsedClass[] = [];
  const lines = text.split("\n");
  for (let i = 0; i + 1 < lines.length; i++) {
    // a top-level struct, templated (template <typename T> on the line above) or not (union find: the ones with your
    // own merge, next free index); start: the struct's own line
    const templated = /^template <typename T>/.test(lines[i]);
    const start = templated ? i + 1 : i;
    const s = lines[start].match(/^struct (\w+) \{/);
    if (!s || (!templated && i > 0 && /^template </.test(lines[i - 1]))) continue;
    const cls: ParsedClass = {
      name: s[1],
      doc: docAbove(lines, templated ? i : start, "//"),
      ctor: [],
      ctorDoc: "",
      methods: {},
      ...(templated ? {} : { plain: true }),
    };
    const isPublic = new Set<string>(); // methods whose chosen overload is documented with its cost
    let depth = 0;
    for (let j = start; j < lines.length; j++) {
      const line = lines[j].replace(/\/\/.*$/, "");
      if (depth === 1) {
        const whole = joinedSignature(lines, j, "//");
        // (a constructor may be a template itself, e.g. the trees' "template <typename E = int> Tree(edges, root)")
        const ctor = whole.match(
          new RegExp(`^\\s{4}(?:template\\s*<[^>]*>\\s*)?(?:explicit\\s+)?${cls.name}\\(`),
        );
        const m = whole.match(
          /^\s{4}(?:(?:static|inline|constexpr|virtual|LEETCODE_NO_SANITIZE(?:_INLINE)?)\s+)*([\w:<>, *&]+?)\s+(\w+)\((.*)\)\s*(?:const\s*)?(?:\{|$)/,
        );
        if (ctor) {
          cls.ctor = cppParams(parenArgs(whole, ctor.index ?? 0));
          cls.ctorDoc = firstSentenceIfLong(docAbove(lines, j, "//"));
        } else if (m) {
          const doc = docAbove(lines, j, "//");
          const params = cppParams(m[3]).map((p) => p.name);
          // an overload keeps the public method (its comment starts with the cost) over an internal helper of the
          // same name (e.g. cut(l, r) over the cut(l, r, a, b, c) that hands back raw roots). A public no-argument
          // overload gives way to one with arguments: copy(l, r) is the op, copy() just the whole-array shorthand
          const pub = startsWithCost(lines, j, "//");
          const old = cls.methods[m[2]];
          const better = !old || (pub && !isPublic.has(m[2])) || (pub && !old.params.length && params.length > 0);
          if (better) {
            cls.methods[m[2]] = { params, returns: m[1].trim(), doc };
            if (pub) isPublic.add(m[2]);
          }
        }
      }
      depth +=
        (line.match(/\{/g) || []).length - (line.match(/\}/g) || []).length;
      if (depth === 0 && line.includes("}")) break;
    }
    classes.push(cls);
  }
  return classes;
}

// Each operation goes to the class implementing the most of the folder's operations (ties: the one defined last).
// Usually that is one class; a folder may split its operations over two (e.g. a count tree and a distinct tree).
export function readUsage(
  text: string,
  lang: TemplateLang,
  operations: string[],
): Usage | null {
  const classes = (lang === "py" ? pyClasses(text) : cppClasses(text)).map(
    (cls, order) => ({
      cls,
      order,
      n: operations.filter((op) => op in cls.methods).length,
    }),
  );
  const owner: Record<string, (typeof classes)[number]> = {};
  for (const op of operations) {
    const cands = classes.filter((c) => op in c.cls.methods);
    if (!cands.length) return null;
    owner[op] = cands.reduce((a, b) =>
      b.n > a.n || (b.n === a.n && b.order > a.order) ? b : a,
    );
  }
  const used = [...new Set(Object.values(owner))].sort(
    (a, b) => a.order - b.order,
  );
  return {
    classes: used.map(({ cls }) => ({
      className: cls.name,
      doc: cls.doc,
      ctor: cls.ctor,
      ctorDoc: cls.ctorDoc,
      ...(cls.plain ? { plain: true } : {}),
    })),
    methods: Object.fromEntries(
      operations.map((op) => [
        op,
        { ...owner[op].cls.methods[op], cls: used.indexOf(owner[op]) },
      ]),
    ),
  };
}
