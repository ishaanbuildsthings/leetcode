// Reads the 2D / 3D range query templates in ../templates/ultimate-template-tool/range-queries-2d (written by the
// generators in range-query-2d-tests/generators) and generates:
//   - lib/generated/range-2d-templates.ts  (the manifest the 2D range queries tab's picker reads)
//   - public/range-2d-templates/<folder>/template.{py,cpp}  (the copies the picker's drawer fetches)
//
// Each folder holds template.py and template.cpp with the same header as the 1D range-query templates, plus
//   @input: grid | points | online | grid-3d   what the constructor is given (the picker's switch)
//   @empty-cells: yes                                  (optional) cells can be empty: a min / max over none is "nothing"
//   @model: area                                       (optional) rect adds are true area adds (tester only)
//   @values: non-negative                              (optional) what the values must be
// Costs use R, C (a grid's rows and columns), X, Y (distinct coordinates; a 3D grid's sides), N, U (a coordinate range), Z.
// Run with: npm run gen:range-queries-2d

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { LANGS, readHeaderFile, readUsage } from "./catalog-lib.mjs";

const siteDir = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const srcDir = path.resolve(siteDir, "../templates/ultimate-template-tool/range-queries-2d");
const publicDir = path.join(siteDir, "public/range-2d-templates");
const manifestPath = path.join(siteDir, "lib/generated/range-2d-templates.ts");

const TAGS = ["operations", "data-structure-type", "input", "empty-cells", "values", "model", "complexities", "memory"];
const OPTIONAL_TAGS = ["empty-cells", "values", "model"];
const INPUTS = ["grid", "points", "online", "grid-3d"];
// (kept in step with RANGE_2D_TYPES in lib/range-2d-picker.ts, which tsc checks the manifest against)
const TYPES = ["prefix-sum", "difference-array", "corner-table", "hash", "bit-counts", "sparse-table",
  "BIT", "seg-tree", "seg-tree-kept-tags", "rows-of-trees"];

const errors = [];
const entries = [];

for (const folder of fs.readdirSync(srcDir).sort()) {
  const folderPath = path.join(srcDir, folder);
  if (!fs.statSync(folderPath).isDirectory()) continue;
  const langs = [];
  let data = null;
  for (const [ext, lang] of Object.entries(LANGS)) {
    const filePath = path.join(folderPath, `template${ext}`);
    if (!fs.existsSync(filePath)) continue;
    const where = `${folder}/template${ext}`;
    const { errs, tags, data: d } = readHeaderFile(where, filePath, { tags: TAGS, optionalTags: OPTIONAL_TAGS });
    errors.push(...errs);
    if (!TYPES.includes(d.dataStructureType)) errors.push(`${where}: @data-structure-type must be one of ${TYPES.join(", ")}`);
    if (!INPUTS.includes(tags.input)) errors.push(`${where}: @input must be one of ${INPUTS.join(", ")}`);
    if (tags["empty-cells"] !== undefined && tags["empty-cells"] !== "yes") errors.push(`${where}: @empty-cells can only be "yes"`);
    if (tags.values !== undefined && tags.values !== "non-negative") errors.push(`${where}: @values can only be "non-negative"`);
    // (the drawer reads usage from the code itself; this only checks it can)
    if (!readUsage(fs.readFileSync(filePath, "utf8"), lang, d.operations)) errors.push(`${where}: no class implements every operation (needed for the usage panel)`);
    const full = { ...d, input: tags.input, flags: (tags["empty-cells"] ? "e" : "") + (tags.values ? "n" : "") };
    langs.push(lang);
    if (!data) data = full;
    else if (JSON.stringify(data) !== JSON.stringify(full)) errors.push(`${folder}: template${ext} header disagrees with the other language's`);
  }
  for (const f of fs.readdirSync(folderPath).filter((f) => f !== "__pycache__"))  // Python's cache from running tests
    if (!Object.keys(LANGS).some((ext) => f === `template${ext}`)) errors.push(`${folder}: unexpected file ${f}`);
  if (!data) {
    errors.push(`${folder}: no template.py or template.cpp`);
    continue;
  }
  entries.push({ folder, langs, ...data });
}

if (errors.length) {
  console.error(errors.join("\n"));
  process.exit(1);
}

fs.rmSync(publicDir, { recursive: true, force: true });
for (const { folder, langs } of entries) {
  fs.mkdirSync(path.join(publicDir, folder), { recursive: true });
  for (const l of langs) fs.copyFileSync(path.join(srcDir, folder, `template.${l}`), path.join(publicDir, folder, `template.${l}`));
}

// the generic rectangle / square sparse tables you fill in yourself (the toolbar's "Generic sparse tables" menu)
const genericDir = path.resolve(siteDir, "../templates/ultimate-template-tool/generic-2d");
fs.mkdirSync(path.join(publicDir, "_generic"));
for (const name of fs.readdirSync(genericDir)) fs.copyFileSync(path.join(genericDir, name), path.join(publicDir, "_generic", name));

// Hundreds of variants share a few op lists, cost strings and memory layouts: the manifest is those tables plus one
// short row per template, expanded in the browser by decodeRange2dTemplates (lib/range-2d-picker.ts).
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
const costs = table();
const opLists = table();
const memories = table();
const rows = entries.map((e) => [
  e.folder,
  e.langs.join(" "),
  e.dataStructureType,
  e.input,
  e.flags,
  opLists.id(e.operations.join(" "), e.operations),
  e.operations.map((op) => costs.id(e.complexities[op])),
  costs.id(e.build),
  memories.id(JSON.stringify(e.memory), e.memory),
]);

const manifest = `// Generated by scripts/build-range-2d-templates.mjs from templates/ultimate-template-tool/range-queries-2d. Do not edit.
import type { Range2dManifest } from "@/lib/range-2d-picker";

export const RANGE_2D_MANIFEST: Range2dManifest = {
  costs: ${JSON.stringify(costs.items)},
  opLists: ${JSON.stringify(opLists.items)},
  memories: ${JSON.stringify(memories.items)},
  rows: [
${rows.map((r) => `    ${JSON.stringify(r)},`).join("\n")}
  ],
};
`;
fs.mkdirSync(path.dirname(manifestPath), { recursive: true });
fs.writeFileSync(manifestPath, manifest);
console.log(`${entries.length} 2D range query templates -> ${path.relative(siteDir, manifestPath)} + ${path.relative(siteDir, publicDir)}/`);
