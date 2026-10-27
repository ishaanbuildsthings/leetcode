import fs from "node:fs";

// Shared by the template-catalog builds (scripts/build-range-query-templates.mjs, scripts/build-set-templates.mjs):
// header parsing, cost / memory validation, and the usage data the picker's code drawer shows.

export const LANGS = { ".py": "py", ".cpp": "cpp" };
export const TAG_RE = /^\s*(?:#|\/\/) @([a-z-]+):\s*(.*?)\s*$/;
const ENTRY_RE = /^\s*(?:#|\/\/)\s+([A-Za-z]\w*):\s*(.+?)\s*$/;

// N = number of elements, U = largest value (gcd, bit ops, floor div/sqrt depend on it); in sparse files U is the
// size of the index range instead (and in set templates, the size of the value range [lo, hi]).
// log64(U) = log base 64 of U (a 64-ary bit trie's depth).
// U/64 = U 64-bit words (a bitset over U values).
const FACTORS = new Set(["1", "N", "log(N)", "log^2(N)", "sqrt(N)", "U", "U/64", "log(U)", "log64(U)", "log(log(U))"]);

// A cost is terms joined by "+", each term factors joined by "*" (a factor may be a positive integer
// constant, e.g. 36*N), optionally followed by " amortized" or " expected", then optionally " ?" (a bound we are
// not sure is tight or right, e.g. anything paying for gcd work).
const isValidFactor = (f) => FACTORS.has(f) || /^[1-9]\d*$/.test(f);
export function isValidCost(cost) {
  const body = cost.replace(/ \?$/, "").replace(/ (amortized|expected)$/, "");
  return body.split("+").every((term) => term.split("*").every(isValidFactor));
}

// Reads the header block: "@tag: value" lines; "@complexities:" and "@memory:" are followed by indented "key: value" lines.
const BLOCK_TAGS = ["complexities", "memory"];
export function parseHeader(text) {
  const tags = {};
  const blocks = { complexities: {}, memory: {} };
  let block = null;
  let started = false; // lines before the first @tag (the "Template by ..." attribution) are skipped
  for (const line of text.split("\n")) {
    const tag = line.match(TAG_RE);
    if (!tag && !started) continue;
    started = true;
    if (tag) {
      tags[tag[1]] = tag[2];
      block = BLOCK_TAGS.includes(tag[1]) ? tag[1] : null;
      continue;
    }
    const entry = block && line.match(ENTRY_RE);
    if (!entry) break;
    blocks[block][entry[1]] = entry[2];
  }
  return { tags, complexities: blocks.complexities, memory: blocks.memory };
}

export const LAYOUTS = ["2n-iterative", "pow2-iterative", "4n-recursive", "sparse", "none"];
export const MEMORY_GROUPS = ["node", "tags", "other"];
const ARRAY_RE = /^([A-Za-z_]\w*)\[([^\]]+)\]$/;

// "a[4*N] b[1*N*log(N)]" -> [{ name, size }], or null if malformed
export function parseArrays(value) {
  if (value === "none") return [];
  const out = [];
  for (const item of value.split(/\s+/)) {
    const m = item.match(ARRAY_RE);
    if (!m || !isValidCost(m[2]) || / (amortized|expected|\?)$/.test(m[2])) return null;
    out.push({ name: m[1], size: m[2] });
  }
  return out;
}

// Sums sizes like 4*N + 4*N + 1*N*log(N) into "8*N+1*N*log(N)", largest terms first.
const TERM_ORDER = ["N*log(N)", "N", "sqrt(N)", ""];
export function sumSizes(sizes) {
  const byShape = new Map();
  for (const size of sizes) {
    for (const term of size.split("+")) {
      const factors = term.split("*");
      const coef = factors.filter((f) => /^\d+$/.test(f)).reduce((p, f) => p * Number(f), 1);
      const shape = factors.filter((f) => !/^\d+$/.test(f) && f !== "1").join("*");
      byShape.set(shape, (byShape.get(shape) ?? 0) + coef);
    }
  }
  const shapes = [...byShape.keys()].sort((a, b) => (TERM_ORDER.indexOf(a) + 99) % 99 - (TERM_ORDER.indexOf(b) + 99) % 99);
  return shapes.map((shape) => (shape ? `${byShape.get(shape)}*${shape}` : String(byShape.get(shape)))).join("+") || "0";
}

// ------------------------------------------------------------------------------------------------ usage
// The usage parser lives in lib/template-usage.ts: the set picker's drawer runs it in the browser on the code it
// fetches, and the builds run it here (Node strips its types) to fail early on a template it can't read.
export { readUsage } from "../lib/template-usage.ts";


// Parses and validates one language file's header against a catalog's tags. `where` prefixes error messages.
// Returns { errs, tags, data } with data = operations, data structure type, costs and memory.
export function readHeaderFile(where, filePath, { tags: TAGS, optionalTags = [] }) {
  const { tags, complexities, memory } = parseHeader(fs.readFileSync(filePath, "utf8"));
  const errs = [];
  for (const t of TAGS) if (!(t in tags) && !optionalTags.includes(t)) errs.push(`${where}: missing @${t}`);
  for (const t of Object.keys(tags)) if (!TAGS.includes(t)) errs.push(`${where}: unknown tag @${t}`);

  const operations = (tags.operations ?? "").split(/\s+/).filter(Boolean);
  if (!operations.length) errs.push(`${where}: @operations is empty`);
  if (operations.join(" ") !== [...operations].sort().join(" ")) errs.push(`${where}: @operations not alphabetical`);
  if (new Set(operations).size !== operations.length) errs.push(`${where}: duplicate in @operations`);

  if (!LAYOUTS.includes(memory.layout)) errs.push(`${where}: @memory layout must be one of ${LAYOUTS.join(", ")}`);
  for (const k of Object.keys(memory))
    if (![...MEMORY_GROUPS, "layout", "note"].includes(k)) errs.push(`${where}: unknown @memory key "${k}"`);
  const memoryGroups = {};
  for (const g of MEMORY_GROUPS) {
    const arrays = memory[g] === undefined ? null : parseArrays(memory[g]);
    if (!arrays) errs.push(`${where}: @memory ${g} must be "none" or name[size] entries`);
    memoryGroups[g] = { arrays: arrays ?? [], total: sumSizes((arrays ?? []).map((a) => a.size)) };
  }
  const allSizes = MEMORY_GROUPS.flatMap((g) => memoryGroups[g].arrays.map((a) => a.size));
  if (!allSizes.length) errs.push(`${where}: @memory lists no arrays`);

  for (const [name, cost] of Object.entries(complexities)) {
    if (name !== "build" && !operations.includes(name)) errs.push(`${where}: @complexities lists "${name}", not in @operations`);
    if (!isValidCost(cost)) errs.push(`${where}: bad cost "${cost}" for ${name}`);
  }
  for (const op of operations) if (!(op in complexities)) errs.push(`${where}: @complexities is missing ${op}`);
  if (!("build" in complexities)) errs.push(`${where}: @complexities is missing build`);

  const { build, ...perOperation } = complexities;
  return {
    errs,
    tags,
    data: {
      operations,
      dataStructureType: tags["data-structure-type"],
      complexities: perOperation,
      build,
      memory: {
        layout: memory.layout,
        ...memoryGroups,
        ...(memory.note ? { note: memory.note } : {}),
        total: sumSizes(allSizes),
      },
    },
  };
}
