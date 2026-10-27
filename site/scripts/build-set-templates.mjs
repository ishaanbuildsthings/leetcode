// Reads the tagged ordered-multiset templates in ../templates/sets and generates:
//   - lib/generated/set-templates.ts  (typed manifest; tsc rejects unknown operations or data structure types)
//   - public/set-templates/<folder>/template.{py,cpp}  (local copies: in dev the picker's drawer fetches these, so it
//     works offline; this folder is gitignored, and prod fetches the same files from templates/sets on GitHub)
//
// Each template is a folder (named by its structure, e.g. treap-with-sums: the op list is too long for a folder
// name) holding template.py and/or template.cpp with the same header as range-query templates plus
//   # @values: offline | online-range | online-bits | online
// saying what the constructor needs up front: every value that will be added / a range [lo, hi] / nothing.
// Loose files in templates/sets (older originals) are ignored.
// Run with: npm run gen:sets

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { LANGS, readHeaderFile, readUsage } from "./catalog-lib.mjs";

const siteDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const srcDir = path.resolve(siteDir, "../templates/sets");
const publicDir = path.join(siteDir, "public/set-templates");
const manifestPath = path.join(siteDir, "lib/generated/set-templates.ts");

// @tracks: what the template keeps current on every update (cached min / max, medians, mex), or none
const TAGS = ["operations", "data-structure-type", "values", "keys", "tracks", "complexities", "memory"];
const VALUES = ["offline", "online-range", "online-bits", "online"];
// any: values only need to compare (tuples, pairs, ...); numbers: the template needs numeric values
const KEYS = ["any", "numbers"];

const errors = [];
const entries = [];

for (const folder of fs.readdirSync(srcDir).sort()) {
  const folderPath = path.join(srcDir, folder);
  if (!fs.statSync(folderPath).isDirectory()) continue;
  // reads template.* or distinct.* (FastSet's no-duplicates variant) in every language it exists in
  const readStem = (stem) => {
    const langs = [];
    const notes = {};
    let data = null;
    for (const [ext, lang] of Object.entries(LANGS)) {
      const filePath = path.join(folderPath, `${stem}${ext}`);
      if (!fs.existsSync(filePath)) continue;
      const where = `${folder}/${stem}${ext}`;
      const { errs, tags, data: d } = readHeaderFile(where, filePath, { tags: TAGS });
      errors.push(...errs);
      if (!VALUES.includes(tags.values)) errors.push(`${where}: @values must be one of ${VALUES.join(", ")}`);
      d.values = tags.values;
      if (!KEYS.includes(tags.keys)) errors.push(`${where}: @keys must be one of ${KEYS.join(", ")}`);
      d.keys = tags.keys;
      d.tracks = tags.tracks === "none" ? [] : (tags.tracks ?? "").split(/\s+/).filter(Boolean);
      langs.push(lang);
      if (d.memory.note) notes[lang] = d.memory.note;
      // (the drawer reads usage from the code itself; this only checks it can)
      if (!readUsage(fs.readFileSync(filePath, "utf8"), lang, d.operations)) errors.push(`${where}: no class implements every operation (needed for the usage panel)`);
      if (!data) data = d;
      else {
        const strip = (x) => JSON.stringify({ ...x, memory: { ...x.memory, note: undefined } });
        if (strip(data) !== strip(d)) errors.push(`${folder}: ${stem}${ext} header disagrees with the other language's`);
      }
    }
    if (data && Object.keys(notes).length) data.memory.notes = notes;
    return { langs, data };
  };
  const { langs, data } = readStem("template");
  const distinct = readStem("distinct");
  for (const f of fs.readdirSync(folderPath))
    if (!["template", "distinct"].some((stem) => Object.keys(LANGS).some((ext) => f === `${stem}${ext}`))) errors.push(`${folder}: unexpected file ${f}`);
  if (!data) {
    errors.push(`${folder}: no template.py or template.cpp`);
    continue;
  }
  const entry = { folder, langs, ...data };
  if (distinct.data) {
    const d = distinct.data;
    entry.distinct = { langs: distinct.langs, operations: d.operations, complexities: d.complexities, build: d.build, memory: d.memory };
  }
  entries.push(entry);
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

fs.rmSync(publicDir, { recursive: true, force: true });
fs.mkdirSync(publicDir, { recursive: true });
for (const { folder, langs, distinct } of entries) {
  fs.mkdirSync(path.join(publicDir, folder), { recursive: true });
  const files = [...langs.map((l) => `template.${l}`), ...(distinct?.langs ?? []).map((l) => `distinct.${l}`)];
  for (const f of files) fs.copyFileSync(path.join(srcDir, folder, f), path.join(publicDir, folder, f));
}

// Thousands of variants share a few op lists, cost strings and memory layouts: the manifest is those tables plus one
// short row per template (its costs one character per op, in its op list's order), expanded in the browser by
// decodeSetTemplates (lib/set-picker.ts). Op names are checked against SetOpId by tsc.
const CODE = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_";
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
const opNames = [...new Set(entries.flatMap((e) => [...e.operations, ...(e.distinct?.operations ?? [])]))].sort();
const opIndex = new Map(opNames.map((op, i) => [op, i]));
const costs = table();
const opLists = table();
const memories = table();
const pack = (operations, complexities, build, memory) => {
  const ops = opLists.id(operations.join(" "), operations.map((op) => opIndex.get(op)));
  const codes = operations.map((op) => CODE[costs.id(complexities[op])]).join("");
  return [ops, codes, costs.id(build), memories.id(JSON.stringify(memory), memory)];
};
const rows = entries.map((e) => {
  const row = [e.folder, e.langs.join(" "), e.dataStructureType, e.values, e.keys, e.tracks.join(" "),
    ...pack(e.operations, e.complexities, e.build, e.memory)];
  if (e.distinct) row.push([e.distinct.langs.join(" "), ...pack(e.distinct.operations, e.distinct.complexities, e.distinct.build, e.distinct.memory)]);
  return row;
});
if (costs.items.length > CODE.length) {
  console.error(`${costs.items.length} distinct costs: more than one character per op can index`);
  process.exit(1);
}

const manifest = `// Generated by scripts/build-set-templates.mjs from templates/sets. Do not edit.
import type { SetOpId, SetTemplateRow } from "../set-picker";
import type { MemoryBreakdown } from "../template-picker";

export const SET_OP_NAMES: readonly SetOpId[] = ${JSON.stringify(opNames)};
export const SET_COSTS: readonly string[] = ${JSON.stringify(costs.items)};
export const SET_OP_LISTS: readonly (readonly number[])[] = ${JSON.stringify(opLists.items)};
export const SET_MEMORIES: readonly MemoryBreakdown[] = ${JSON.stringify(memories.items)};
// [folder, langs, type, values, keys, tracks, op list, costs, build, memory, distinct?]
export const SET_TEMPLATE_ROWS: readonly SetTemplateRow[] = [
${rows.map((r) => "  " + JSON.stringify(r)).join(",\n")},
];
`;
fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
fs.writeFileSync(manifestPath, manifest);
console.log(`${entries.length} set templates -> ${path.relative(siteDir, manifestPath)} + ${path.relative(siteDir, publicDir)}/`);
