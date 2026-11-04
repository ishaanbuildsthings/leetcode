// Reads the tagged templates in ../templates/range-queries and generates:
//   - lib/generated/range-query-templates.ts  (typed manifest; tsc rejects unknown operations or data structure types)
//   - public/range-query-templates/<folder>/{template,sparse}.{py,cpp}  (static copies the picker fetches on click)
//
// A folder may also hold sparse.py / sparse.cpp: the same operations (getAll may be left out) over any index range
// [lo, hi]. Their header has the same format, with layout "sparse". For a template with updates every position
// starts at 0, memory sizes are counted per update (e.g. node: sum[1*log(U)]) and U is the size of the index range;
// a static template's sparse version is built from N given values ((index, value) pairs; every other index 0), with
// costs and memory in N.
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
import { LANGS, readHeaderFile, readUsage } from "./catalog-lib.mjs";

const siteDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const srcDir = path.resolve(siteDir, "../templates/range-queries");
const publicDir = path.join(siteDir, "public/range-query-templates");
const manifestPath = path.join(siteDir, "lib/generated/range-query-templates.ts");

// @original-file-url is optional: templates written fresh in this folder have no original.
// @fractional-cascading (yes / no) is required on, and only allowed on, merge sort trees.
// @values: offline (optional) = the constructor needs every value that will ever be added (e.g. by append) up front.
// @letters: same (optional) = the very same file takes a list of characters for its character ops (see gen_letters.py);
// a template that needs a different file for that has letters.py / letters.cpp instead.
const TAGS = ["operations", "data-structure-type", "fractional-cascading", "values", "letters", "complexities", "memory", "original-file-url"];
const OPTIONAL_TAGS = ["original-file-url", "fractional-cascading", "values", "letters"];

const errors = [];
const entries = [];

// Parses and validates one language file's header: the shared checks, plus the range-query tags.
function readTemplateFile(where, filePath) {
  const { errs, tags, data } = readHeaderFile(where, filePath, { tags: TAGS, optionalTags: OPTIONAL_TAGS });
  const fc = tags["fractional-cascading"];
  if (tags["data-structure-type"] === "merge-sort-tree" && !["yes", "no"].includes(fc))
    errs.push(`${where}: a merge sort tree needs "@fractional-cascading: yes" or "no"`);
  if (tags["data-structure-type"] !== "merge-sort-tree" && fc !== undefined)
    errs.push(`${where}: @fractional-cascading is only for merge sort trees`);
  if (tags.values !== undefined && tags.values !== "offline") errs.push(`${where}: @values can only be "offline"`);
  if (tags.letters !== undefined && tags.letters !== "same") errs.push(`${where}: @letters can only be "same"`);
  return {
    errs,
    data: {
      ...data,
      ...(fc !== undefined ? { fractionalCascading: fc === "yes" } : {}),
      ...(tags.values === "offline" ? { valuesOffline: true } : {}),
      ...(tags.letters === "same" ? { lettersSame: true } : {}),
      ...(tags["original-file-url"] ? { originalFileUrl: tags["original-file-url"] } : {}),
    },
  };
}

// Each template is a folder holding template.py and/or template.cpp. The folder is named by its operations
// (alphabetical, "-" joined, leaving out getAll and size: nearly every structure with updates has getAll, and every one
// whose length changes has size), with a __<data-structure-type> suffix when two templates share operations; any folder
// may instead be named "<data-structure-type>-<anything>" (long op lists, or variants of one structure sharing an op list).
// Both language files carry the same header; they may differ only in the original-file-url and the @memory note
// (each language's note describes its own implementation).
for (const folder of fs.readdirSync(srcDir).sort()) {
  const folderPath = path.join(srcDir, folder);
  if (!fs.statSync(folderPath).isDirectory()) {
    errors.push(`${folder}: expected a folder per template`);
    continue;
  }
  // reads one variant ("template" or "sparse") in every language it exists in; both languages must agree
  const readVariant = (stem) => {
    const langs = [];
    const notes = {};
    const usage = {};
    let data = null;
    for (const [ext, lang] of Object.entries(LANGS)) {
      const filePath = path.join(folderPath, `${stem}${ext}`);
      if (!fs.existsSync(filePath)) continue;
      const { errs, data: d } = readTemplateFile(`${folder}/${stem}${ext}`, filePath);
      errors.push(...errs);
      langs.push(lang);
      // the @memory note may differ: each language's file describes its own implementation
      if (d.memory.note) notes[lang] = d.memory.note;
      const u = readUsage(fs.readFileSync(filePath, "utf8"), lang, d.operations);
      if (u) usage[lang] = u;
      else errors.push(`${folder}/${stem}${ext}: no class implements every operation (needed for the usage panel)`);
      if (!data) {
        data = d;
      } else {
        const strip = (x) => JSON.stringify({ ...x, originalFileUrl: undefined, memory: { ...x.memory, note: undefined } });
        if (strip(data) !== strip(d)) errors.push(`${folder}: ${stem}${ext} header disagrees with the other language's`);
      }
    }
    if (data && Object.keys(notes).length) data.memory.notes = notes;
    return { langs, data, usage };
  };
  const { langs, data } = readVariant("template");
  const sparse = readVariant("sparse");
  const letters = readVariant("letters");
  const STEMS = ["template", "sparse", "letters"];
  for (const f of fs.readdirSync(folderPath))
    if (!STEMS.some((stem) => Object.keys(LANGS).some((ext) => f === `${stem}${ext}`))) errors.push(`${folder}: unexpected file ${f}`);
  if (!data) {
    errors.push(`${folder}: no template.py or template.cpp`);
    continue;
  }
  const base = data.operations.filter((op) => op !== "getAll" && op !== "size").join("-");
  const allowed = [base, `${base}__${data.dataStructureType}`];
  // a folder may name the structure instead of the op list: "<type>-..." (needed when the list is too long for a
  // filename, or when two variants of one structure share an op list, like the online / offline persistent trees)
  const named = folder.startsWith(`${data.dataStructureType}-`);
  if (!allowed.includes(folder) && !named)
    errors.push(`${folder}: folder should be ${allowed[0]} (or ${allowed[1]} if it collides, or ${data.dataStructureType}-<name>)`);
  if (data.memory.layout === "sparse") errors.push(`${folder}: template files can't use the sparse layout; put it in sparse.py / sparse.cpp`);
  const entry = { folder, langs, ...data };
  if (sparse.data) {
    const s = sparse.data;
    // a sparse tree may leave out getAll (its index range can be huge) and ops it has no version of (beats searches)
    const dense = data.operations.join(" ");
    if (s.operations.some((op) => !data.operations.includes(op)))
      errors.push(`${folder}: sparse @operations must be some of the template's`);
    if (s.memory.layout !== "sparse") errors.push(`${folder}: sparse files must use layout "sparse"`);
    entry.sparse = {
      langs: sparse.langs,
      ...(s.operations.join(" ") !== dense ? { operations: s.operations } : {}),
      complexities: s.complexities,
      build: s.build,
      memory: s.memory,
    };
  }
  if (letters.data) {
    const v = letters.data;
    // the letters version: the template's character ops only, and the same structure
    if (v.operations.some((op) => !data.operations.includes(op))) errors.push(`${folder}: letters @operations must be some of the template's`);
    if (data.lettersSame) errors.push(`${folder}: a template marked "@letters: same" needs no letters files`);
    entry.letters = { langs: letters.langs, operations: v.operations, complexities: v.complexities, build: v.build, memory: v.memory };
  }
  entries.push(entry);
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

fs.rmSync(publicDir, { recursive: true, force: true });
fs.mkdirSync(publicDir, { recursive: true });
for (const { folder, langs, sparse, letters } of entries) {
  fs.mkdirSync(path.join(publicDir, folder), { recursive: true });
  const files = [
    ...langs.map((l) => `template.${l}`),
    ...(sparse?.langs ?? []).map((l) => `sparse.${l}`),
    ...(letters?.langs ?? []).map((l) => `letters.${l}`),
  ];
  for (const name of files) fs.copyFileSync(path.join(srcDir, folder, name), path.join(publicDir, folder, name));
}
// the generic seg trees you fill in yourself (the picker's buttons above the op grid): copied as they are
const genericDir = path.resolve(siteDir, "../templates/segment-trees/generic");
fs.mkdirSync(path.join(publicDir, "_generic"));
for (const name of fs.readdirSync(genericDir)) fs.copyFileSync(path.join(genericDir, name), path.join(publicDir, "_generic", name));

// Thousands of templates share a few op lists, cost lists and memory layouts: the manifest is those tables plus one
// short row per template, expanded in the browser by decodeRangeTemplates (lib/range-query-picker.ts). The usage panel
// isn't in it either: the drawer reads it from the code it fetches (this script only checks that it can).
const table = () => {
  const items = [];
  const index = new Map();
  return {
    items,
    id(key, item = key) {
      if (!index.has(key)) index.set(key, items.push(item) - 1);
      return index.get(key);
    },
  };
};
const opNames = [...new Set(entries.flatMap((e) => [...e.operations, ...(e.sparse?.operations ?? []), ...(e.letters?.operations ?? [])]))].sort();
const opIndex = new Map(opNames.map((op, i) => [op, i]));
const costs = table();
const opLists = table();
const costLists = table();
const memories = table();
const pack = (operations, complexities, build, memory) => {
  const list = opLists.id(operations.join(" "), operations.map((op) => opIndex.get(op)));
  const cl = operations.map((op) => costs.id(complexities[op]));
  return [list, costLists.id(cl.join(" "), cl), costs.id(build), memories.id(JSON.stringify(memory), memory)];
};
const rows = entries.map((e) => {
  const flags = (e.fractionalCascading === true ? "f" : e.fractionalCascading === false ? "F" : "") + (e.valuesOffline ? "o" : "") + (e.lettersSame ? "s" : "");
  const row = [e.folder, e.langs.join(" "), e.dataStructureType, flags, e.originalFileUrl ?? "", ...pack(e.operations, e.complexities, e.build, e.memory)];
  const variant = (v) => (v ? [v.langs.join(" "), ...pack(v.operations ?? e.operations, v.complexities, v.build, v.memory), v.operations ? 1 : 0] : 0);
  row.push(variant(e.sparse), variant(e.letters));
  return row;
});

const manifest = `// Generated by scripts/build-range-query-templates.mjs from templates/range-queries. Do not edit.
import type { OpId, RangeTemplateRow } from "../range-query-picker";
import type { MemoryBreakdown } from "../template-picker";

export const RANGE_OP_NAMES: readonly OpId[] = ${JSON.stringify(opNames)};
export const RANGE_COSTS: readonly string[] = ${JSON.stringify(costs.items)};
export const RANGE_OP_LISTS: readonly (readonly number[])[] = ${JSON.stringify(opLists.items)};
export const RANGE_COST_LISTS: readonly (readonly number[])[] = ${JSON.stringify(costLists.items)};
export const RANGE_MEMORIES: readonly MemoryBreakdown[] = ${JSON.stringify(memories.items)};
// [folder, langs, type, flags (f / F fractional cascading yes / no, o values offline, s letters same), original url,
//  op list, cost list, build, memory, sparse (0 or [langs, op list, cost list, build, memory, own ops]), letters (same)]
export const RANGE_TEMPLATE_ROWS: readonly RangeTemplateRow[] = [
${rows.map((r) => "  " + JSON.stringify(r)).join(",\n")},
];
`;
fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
fs.writeFileSync(manifestPath, manifest);

const sparseCount = entries.filter((e) => e.sparse).length;
console.log(`${entries.length} templates (${sparseCount} with a sparse version) -> ${path.relative(siteDir, manifestPath)} + ${path.relative(siteDir, publicDir)}/`);
