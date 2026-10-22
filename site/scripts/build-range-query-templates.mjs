// Reads the tagged templates in ../templates/range-queries and generates:
//   - lib/generated/range-query-templates.ts  (typed manifest; tsc rejects unknown operations or data structure types)
//   - public/range-query-templates/<folder>/{template,sparse}.{py,cpp}  (static copies the picker fetches on click)
//
// A folder may also hold sparse.py / sparse.cpp: the same operations over any index range [lo, hi]. Their header
// has the same format, with layout "sparse". For a template with updates every position starts at 0, memory sizes
// are counted per update (e.g. node: sum[1*log(U)]) and U is the size of the index range; a static template's
// sparse version is built from N given values ((index, value) pairs; every other index 0), with costs and memory in N.
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
const TAGS = ["operations", "data-structure-type", "fractional-cascading", "complexities", "memory", "original-file-url"];
const OPTIONAL_TAGS = ["original-file-url", "fractional-cascading"];

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
  return {
    errs,
    data: {
      ...data,
      ...(fc !== undefined ? { fractionalCascading: fc === "yes" } : {}),
      ...(tags["original-file-url"] ? { originalFileUrl: tags["original-file-url"] } : {}),
    },
  };
}

// Each template is a folder holding template.py and/or template.cpp. The folder is named by its operations
// (alphabetical, "-" joined), with a __<data-structure-type> suffix when two templates share operations.
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
  const { langs, data, usage } = readVariant("template");
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
  const entry = { folder, langs, ...data, usage };
  if (sparse.data) {
    const s = sparse.data;
    if (s.operations.join(" ") !== data.operations.join(" ")) errors.push(`${folder}: sparse @operations must match the template's`);
    if (s.memory.layout !== "sparse") errors.push(`${folder}: sparse files must use layout "sparse"`);
    entry.sparse = { langs: sparse.langs, complexities: s.complexities, build: s.build, memory: s.memory, usage: sparse.usage };
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
