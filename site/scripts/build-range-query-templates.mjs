// Reads the tagged templates in ../templates/range-queries and generates:
//   - lib/generated/range-query-templates.ts  (typed manifest; tsc rejects unknown operations or data structure types)
//   - public/range-query-templates/<folder>/{template,sparse}.{py,cpp}  (static copies the picker fetches on click)
//
// A folder may also hold sparse.py / sparse.cpp: the same operations on a dynamic tree over any index range
// [lo, hi] where every position starts at 0. Their header has the same format, with layout "sparse" and memory
// sizes counted per update (e.g. node: sum[1*log(U)]); U there is the size of the index range [lo, hi].
// Run with: npm run gen:range-queries
//
// Header format (Python shown; C++ uses //):
//   # @operations: pointAssign rangeMin
//   # @data-structure-type: seg-tree
//   # @complexities:
//   #   pointAssign: log(N)
//   #   rangeMin: log(N)
//   #   build: N
//   # @memory:
//   #   layout: pow2-iterative
//   #   node: tree[4*N]
//   #   tags: none
//   #   other: none
//   #   note: optional free text
//   # @original-file-url: https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/segment-trees/normal/MinSeg.py

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const siteDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const srcDir = path.resolve(siteDir, "../templates/range-queries");
const publicDir = path.join(siteDir, "public/range-query-templates");
const manifestPath = path.join(siteDir, "lib/generated/range-query-templates.ts");

const LANGS = { ".py": "py", ".cpp": "cpp" };
// @original-file-url is optional: templates written fresh in this folder have no original.
const TAGS = ["operations", "data-structure-type", "complexities", "memory", "original-file-url"];
const OPTIONAL_TAGS = ["original-file-url"];
const TAG_RE = /^\s*(?:#|\/\/) @([a-z-]+):\s*(.*?)\s*$/;
const ENTRY_RE = /^\s*(?:#|\/\/)\s+([A-Za-z]\w*):\s*(.+?)\s*$/;

// N = number of elements, U = largest value (gcd, bit ops, floor div/sqrt depend on it); in sparse files U is the
// size of the index range instead.
const FACTORS = new Set(["1", "N", "log(N)", "log^2(N)", "sqrt(N)", "log(U)", "log(log(U))"]);

// A cost is terms joined by "+", each term factors joined by "*" (a factor may be a positive integer
// constant, e.g. 36*N), optionally followed by " amortized", then optionally " ?" (a bound we are not sure is
// tight or right, e.g. anything paying for gcd work).
const isValidFactor = (f) => FACTORS.has(f) || /^[1-9]\d*$/.test(f);
function isValidCost(cost) {
  const body = cost.replace(/ \?$/, "").replace(/ amortized$/, "");
  return body.split("+").every((term) => term.split("*").every(isValidFactor));
}

// Reads the header block: "@tag: value" lines; "@complexities:" and "@memory:" are followed by indented "key: value" lines.
const BLOCK_TAGS = ["complexities", "memory"];
function parseHeader(text) {
  const tags = {};
  const blocks = { complexities: {}, memory: {} };
  let block = null;
  for (const line of text.split("\n")) {
    const tag = line.match(TAG_RE);
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

const LAYOUTS = ["2n-iterative", "pow2-iterative", "4n-recursive", "sparse", "none"];
const MEMORY_GROUPS = ["node", "tags", "other"];
const ARRAY_RE = /^([A-Za-z_]\w*)\[([^\]]+)\]$/;

// "a[4*N] b[1*N*log(N)]" -> [{ name, size }], or null if malformed
function parseArrays(value) {
  if (value === "none") return [];
  const out = [];
  for (const item of value.split(/\s+/)) {
    const m = item.match(ARRAY_RE);
    if (!m || !isValidCost(m[2]) || m[2].endsWith(" amortized") || m[2].endsWith(" ?")) return null;
    out.push({ name: m[1], size: m[2] });
  }
  return out;
}

// Sums sizes like 4*N + 4*N + 1*N*log(N) into "8*N+1*N*log(N)", largest terms first.
const TERM_ORDER = ["N*log(N)", "N", "sqrt(N)", ""];
function sumSizes(sizes) {
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

const errors = [];
const entries = [];

// Parses and validates one language file's header. `where` prefixes error messages.
function readTemplateFile(where, filePath) {
  const { tags, complexities, memory } = parseHeader(fs.readFileSync(filePath, "utf8"));
  const errs = [];
  for (const t of TAGS) if (!(t in tags) && !OPTIONAL_TAGS.includes(t)) errs.push(`${where}: missing @${t}`);
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
      ...(tags["original-file-url"] ? { originalFileUrl: tags["original-file-url"] } : {}),
    },
  };
}

// Each template is a folder holding template.py and/or template.cpp. The folder is named by its operations
// (alphabetical, "-" joined), with a __<data-structure-type> suffix when two templates share operations.
// Both language files carry the same header; the C++ one may differ only in the original-file-url.
for (const folder of fs.readdirSync(srcDir).sort()) {
  const folderPath = path.join(srcDir, folder);
  if (!fs.statSync(folderPath).isDirectory()) {
    errors.push(`${folder}: expected a folder per template`);
    continue;
  }
  // reads one variant ("template" or "sparse") in every language it exists in; both languages must agree
  const readVariant = (stem) => {
    const langs = [];
    let data = null;
    for (const [ext, lang] of Object.entries(LANGS)) {
      const filePath = path.join(folderPath, `${stem}${ext}`);
      if (!fs.existsSync(filePath)) continue;
      const { errs, data: d } = readTemplateFile(`${folder}/${stem}${ext}`, filePath);
      errors.push(...errs);
      langs.push(lang);
      if (!data) {
        data = d;
      } else {
        const strip = (x) => JSON.stringify({ ...x, originalFileUrl: undefined });
        if (strip(data) !== strip(d)) errors.push(`${folder}: ${stem}${ext} header disagrees with the other language's`);
      }
    }
    return { langs, data };
  };
  const { langs, data } = readVariant("template");
  const sparse = readVariant("sparse");
  const STEMS = ["template", "sparse"];
  for (const f of fs.readdirSync(folderPath))
    if (!STEMS.some((stem) => Object.keys(LANGS).some((ext) => f === `${stem}${ext}`))) errors.push(`${folder}: unexpected file ${f}`);
  if (!data) {
    errors.push(`${folder}: no template.py or template.cpp`);
    continue;
  }
  const base = data.operations.join("-");
  const allowed = [base, `${base}__${data.dataStructureType}`];
  if (!allowed.includes(folder)) errors.push(`${folder}: folder should be ${allowed[0]} (or ${allowed[1]} if it collides)`);
  if (data.memory.layout === "sparse") errors.push(`${folder}: template files can't use the sparse layout; put it in sparse.py / sparse.cpp`);
  const entry = { folder, langs, ...data };
  if (sparse.data) {
    const s = sparse.data;
    if (s.operations.join(" ") !== data.operations.join(" ")) errors.push(`${folder}: sparse @operations must match the template's`);
    if (s.memory.layout !== "sparse") errors.push(`${folder}: sparse files must use layout "sparse"`);
    entry.sparse = { langs: sparse.langs, complexities: s.complexities, build: s.build, memory: s.memory };
  }
  entries.push(entry);
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

fs.rmSync(publicDir, { recursive: true, force: true });
fs.mkdirSync(publicDir, { recursive: true });
for (const { folder, langs, sparse } of entries) {
  fs.mkdirSync(path.join(publicDir, folder), { recursive: true });
  const files = [...langs.map((l) => `template.${l}`), ...(sparse?.langs ?? []).map((l) => `sparse.${l}`)];
  for (const name of files) fs.copyFileSync(path.join(srcDir, folder, name), path.join(publicDir, folder, name));
}

const manifest = `// Generated by scripts/build-range-query-templates.mjs from templates/range-queries. Do not edit.
import type { RangeQueryTemplate } from "../range-query-picker";

export const RANGE_QUERY_TEMPLATES: RangeQueryTemplate[] = ${JSON.stringify(entries, null, 2)};
`;
fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
fs.writeFileSync(manifestPath, manifest);

const sparseCount = entries.filter((e) => e.sparse).length;
console.log(`${entries.length} templates (${sparseCount} with a sparse version) -> ${path.relative(siteDir, manifestPath)} + ${path.relative(siteDir, publicDir)}/`);
