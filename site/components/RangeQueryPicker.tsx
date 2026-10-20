"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import {
  OP_GROUPS,
  DATA_STRUCTURE_TYPES,
  costValue,
  formatCost,
  formatMemoryOf,
  memoryValue,
  TREE_LAYOUT_LABELS,
  type Op,
  type OpId,
  type RangeQueryTemplate,
  type TemplateView,
  viewOf,
  templateKindLabel,
  isBuiltFromPoints,
  type TierKind,
  type TemplateLang,
  TEMPLATE_LANG_LABELS,
} from "@/lib/range-query-picker";
import { RANGE_QUERY_TEMPLATES } from "@/lib/generated/range-query-templates";

const ALL_OPS: Op[] = OP_GROUPS.flatMap((g) => g.tiers.flatMap((t) => t.ops));

// Ops from the "Mod p" tiers. A template with any of them does all its arithmetic mod p, so it is only offered
// once you pick one of them; otherwise a selection like pointGet + pointAdd could land on a mod template.
const MOD_P_OPS = new Set<OpId>(OP_GROUPS.flatMap((g) => g.tiers.filter((t) => t.kind === "mod").flatMap((t) => t.ops.map((o) => o.id))));
const isModP = (t: RangeQueryTemplate) => t.operations.some((op) => MOD_P_OPS.has(op));

const GITHUB_BASE = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/";

const opCost = (t: RangeQueryTemplate, op: OpId) => t.complexities[op] ?? "?";

// Templates covering every selected op, ranked by: slowest selected op, data structure type, total cost
// of selected ops, memory, then fewest extra ops. Type outranks total because amortized bounds on heavy
// structures (beats) hide large constants. Ops you didn't select don't count against a template.
// Which versions compete: dense only, dense and sparse (each sparse version with its own costs and memory), or
// sparse only.
type SparseMode = "none" | "include" | "only";
const SPARSE_MODES: { mode: SparseMode; label: string; title: string }[] = [
  { mode: "none", label: "No sparse", title: "Only the dense templates (indices 0..n-1)" },
  { mode: "include", label: "Include sparse", title: "Dense templates and their sparse versions together" },
  {
    mode: "only",
    label: "Only sparse",
    title:
      "Only sparse versions: any index range [lo, hi] (e.g. up to 1e18). Templates with updates become dynamic trees where every position starts at 0; static ones are built from (index, value) points, every other index 0.",
  },
];

function matchTemplates(selected: Set<OpId>, sparseMode: SparseMode) {
  if (selected.size === 0) return [];
  const picked = [...selected];
  const wantsMod = picked.some((op) => MOD_P_OPS.has(op));
  return RANGE_QUERY_TEMPLATES.flatMap((t) => [sparseMode !== "only" ? viewOf(t, false) : null, sparseMode !== "none" ? viewOf(t, true) : null])
    .filter((t): t is TemplateView => t !== null)
    .filter((t) => picked.every((op) => t.operations.includes(op)) && (wantsMod || !isModP(t)))
    .map((t) => {
      const costs = picked.map((op) => ({ op, cost: opCost(t, op), value: costValue(opCost(t, op)) }));
      const bottleneck = costs.reduce((a, b) => (b.value > a.value ? b : a));
      return {
        template: t,
        extra: t.operations.filter((op) => !selected.has(op)),
        costs,
        bottleneck,
        total: costs.reduce((sum, c) => sum + c.value, 0),
      };
    })
    .sort(
      (a, b) =>
        a.bottleneck.value - b.bottleneck.value ||
        DATA_STRUCTURE_TYPES.indexOf(a.template.dataStructureType) - DATA_STRUCTURE_TYPES.indexOf(b.template.dataStructureType) ||
        a.total - b.total ||
        memoryValue(a.template.memory) - memoryValue(b.template.memory) ||
        a.extra.length - b.extra.length ||
        a.template.folder.localeCompare(b.template.folder) ||
        a.template.file.localeCompare(b.template.file)
    );
}

type MemoryGroupId = "node" | "tags" | "other";

// The memory lines a template shows, named for its kind of structure: a sparse table has a table, not nodes,
// and only segment trees (and sqrt blocks) carry lazy tags. "other" is anything outside the main structure,
// like a copy of the input or prefix sums.
function memoryGroups(template: RangeQueryTemplate): { id: MemoryGroupId; label: string }[] {
  const { memory, dataStructureType: type } = template;
  const groups: { id: MemoryGroupId; label: string }[] = [
    { id: "node", label: type === "sparse-table" ? "Table" : type === "sqrt" ? "Blocks" : type === "positions" ? "Lists" : "Node data" },
  ];
  const tree = memory.layout !== "none" && (memory.layout !== "sparse" || ["seg-tree", "lazy-seg-tree", "beats"].includes(type));
  if (tree || memory.tags.arrays.length > 0) groups.push({ id: "tags", label: "Lazy tags" });
  if (memory.other.arrays.length > 0) groups.push({ id: "other", label: "Extra arrays" });
  return groups;
}

// The layout's label after "Memory <total>", if any. Sparse versions get none: the card's title ("Sparse seg tree",
// "Sparse table over points") already says what they are.
function layoutLabel(memory: RangeQueryTemplate["memory"]): string | null {
  return memory.layout === "none" || memory.layout === "sparse" ? null : TREE_LAYOUT_LABELS[memory.layout];
}

// "1 field" / "3 fields" / "none", for the card's memory lines.
function fieldCount(n: number): string {
  return n === 0 ? "none" : `${n} ${n === 1 ? "field" : "fields"}`;
}

function MemoryPanel({ template, lang }: { template: RangeQueryTemplate; lang: TemplateLang }) {
  const { memory } = template;
  return (
    <div className="border-b border-border px-4 py-3 text-xs">
      <p className="mb-1.5 font-semibold text-foreground">
        Memory {formatMemoryOf(memory, memory.total)}
        {layoutLabel(memory) && (
          <span className="ml-2 font-normal text-muted-foreground">{layoutLabel(memory)}</span>
        )}
      </p>
      <div className="grid grid-cols-[auto_auto_1fr] gap-x-4 gap-y-1">
        {memoryGroups(template).map(({ id, label }) => {
          const { arrays, total } = memory[id];
          const uniform = arrays.every((a) => a.size === arrays[0].size);
          const count = arrays.length;
          return (
            <div key={id} className="contents">
              <span className="text-muted-foreground">
                {label}
                {count > 0 && id !== "other" && ` (${fieldCount(count)})`}
              </span>
              <span className="text-foreground">{count ? formatMemoryOf(memory, total) : "0"}</span>
              <span className={count === 0 ? "text-muted-foreground" : "text-foreground"}>
                {count === 0
                  ? "none"
                  : arrays.map((a, k) => (
                      <span key={a.name}>
                        {k > 0 && ", "}
                        <code className="font-mono">{a.name}</code>
                        {!uniform && `: ${formatMemoryOf(memory, a.size)}`}
                      </span>
                    ))}
              </span>
            </div>
          );
        })}
      </div>
      {(memory.notes?.[lang] ?? memory.note) && (
        <p className="mt-1.5 text-muted-foreground">{memory.notes?.[lang] ?? memory.note}</p>
      )}
    </div>
  );
}

const LANG_STORAGE_KEY = "rangeQueryPicker.lang";
const SPARSE_STORAGE_KEY = "rangeQueryPicker.sparse";

// The sparse mode lives in localStorage so it survives reloads; useSyncExternalStore reads it without a server /
// client mismatch (the server always renders "none"). Stored as "0" / "1" / "2" ("1" was the old "include" checkbox).
const sparseListeners = new Set<() => void>();
const subscribeSparse = (onChange: () => void) => {
  sparseListeners.add(onChange);
  return () => {
    sparseListeners.delete(onChange);
  };
};
function readSparse(): SparseMode {
  try {
    const v = window.localStorage.getItem(SPARSE_STORAGE_KEY);
    return v === "2" ? "only" : v === "1" ? "include" : "none";
  } catch {
    return "none";
  }
}
function writeSparse(mode: SparseMode) {
  try {
    window.localStorage.setItem(SPARSE_STORAGE_KEY, mode === "only" ? "2" : mode === "include" ? "1" : "0");
  } catch {}
  sparseListeners.forEach((notify) => notify());
}

function readPreferredLang(): TemplateLang {
  try {
    return window.localStorage.getItem(LANG_STORAGE_KEY) === "cpp" ? "cpp" : "py";
  } catch {
    return "py";
  }
}

function CodeDrawer({
  template,
  selected,
  onClose,
}: {
  template: TemplateView;
  selected: Set<OpId>;
  onClose: () => void;
}) {
  const [preferred, setPreferred] = useState<TemplateLang>(readPreferredLang);
  const lang = template.langs.includes(preferred) ? preferred : template.langs[0];
  const [loaded, setLoaded] = useState<{ key: string; code: string | null; failed: boolean } | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const fileName = `${template.file}.${lang}`;
  const path = `${template.folder}/${fileName}`;
  const code = loaded?.key === path ? loaded.code : null;
  const failed = loaded?.key === path && loaded.failed;
  const copied = copiedKey === path;

  useEffect(() => {
    let cancelled = false;
    fetch(`/range-query-templates/${encodeURIComponent(template.folder)}/${fileName}`)
      .then((res) => (res.ok ? res.text() : Promise.reject(res.status)))
      .then((text) => !cancelled && setLoaded({ key: path, code: text, failed: false }))
      .catch(() => !cancelled && setLoaded({ key: path, code: null, failed: true }));
    return () => {
      cancelled = true;
    };
  }, [template.folder, fileName, path]);

  const chooseLang = (l: TemplateLang) => {
    setPreferred(l);
    try {
      window.localStorage.setItem(LANG_STORAGE_KEY, l);
    } catch {}
  };

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const copy = async () => {
    if (code === null) return;
    await navigator.clipboard.writeText(code);
    setCopiedKey(path);
  };

  return (
    <div className="fixed inset-0 z-[60] flex justify-end font-[family-name:var(--font-dm-sans)]">
      <button type="button" aria-label="Close" onClick={onClose} className="absolute inset-0 bg-foreground/20" />
      <div className="relative flex h-full w-[min(900px,94vw)] flex-col border-l border-border bg-background shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-border p-4">
          <div className="min-w-0">
            <p className="text-sm font-semibold text-foreground">
              {templateKindLabel(template)}
            </p>
            <p className="mt-1 break-all font-mono text-xs text-muted-foreground">{template.folder}</p>
          </div>
          <div className="flex flex-shrink-0 items-center gap-2">
            <div className="flex overflow-hidden rounded-md border border-border text-xs" role="group" aria-label="Language">
              {(["py", "cpp"] as const).map((l) => {
                const available = template.langs.includes(l);
                return (
                  <button
                    key={l}
                    type="button"
                    disabled={!available}
                    aria-pressed={lang === l}
                    onClick={() => chooseLang(l)}
                    title={available ? undefined : `No ${TEMPLATE_LANG_LABELS[l]} version yet`}
                    className={`px-2.5 py-1 ${
                      lang === l ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
                    } disabled:cursor-not-allowed disabled:opacity-40`}
                  >
                    {TEMPLATE_LANG_LABELS[l]}
                  </button>
                );
              })}
            </div>
            <button
              type="button"
              onClick={copy}
              disabled={code === null}
              className="rounded-md border border-border px-2.5 py-1 text-xs text-foreground hover:bg-muted disabled:opacity-50"
            >
              {copied ? "Copied" : "Copy"}
            </button>
            <a
              href={`${GITHUB_BASE}${encodeURIComponent(template.folder)}/${fileName}`}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-md border border-border px-2.5 py-1 text-xs text-foreground hover:bg-muted"
            >
              GitHub ↗
            </a>
            <button
              type="button"
              onClick={onClose}
              aria-label="Close"
              className="px-1.5 text-lg leading-none text-muted-foreground hover:text-foreground"
            >
              ×
            </button>
          </div>
        </div>
        <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5 border-b border-border px-4 py-3 text-xs">
          {[...template.operations]
            .sort((a, b) => Number(selected.has(b)) - Number(selected.has(a)))
            .map((op) => (
              <div key={op} className="contents">
                <span className={`font-mono ${selected.has(op) ? "font-medium text-primary" : "text-muted-foreground"}`}>
                  {op}
                </span>
                <span className={selected.has(op) ? "text-foreground" : "text-muted-foreground"}>
                  {formatCost(opCost(template, op))}
                </span>
              </div>
            ))}
          <span className="font-mono text-muted-foreground">build</span>
          <span className="text-muted-foreground">{formatCost(template.build)}</span>
        </div>
        <UsagePanel template={template} selected={selected} lang={lang} />
        <MemoryPanel template={template} lang={lang} />
        <pre className="flex-1 overflow-auto bg-card p-4 font-mono text-xs leading-relaxed text-foreground">
          {failed ? "Couldn't load this template." : (code ?? "Loading…")}
        </pre>
      </div>
    </div>
  );
}

// Ops that change the array (no result to read): the range updates and every point op but pointGet.
const UPDATE_OPS = new Set<OpId>(
  OP_GROUPS.filter((g) => g.id === "range-updates" || g.id === "point")
    .flatMap((g) => g.tiers.flatMap((t) => t.ops.map((o) => o.id)))
    .filter((id) => id !== "pointGet")
);

// What each constructor argument is, by its name in the source ("lo" / "hi" / "points" are covered by the sparse
// sentences in UsagePanel).
const CTOR_ARG_NOTES: Record<string, { py: string; cpp: string }> = {
  arr: { py: "arr: the initial array (a list), 0-indexed", cpp: "arr: the initial array (vector<long long>), 0-indexed" },
  a: { py: "a: the initial array (a list), 0-indexed", cpp: "a: the initial array (vector<long long>), 0-indexed" },
  points: {
    py: "points: a list of (index, value) pairs, distinct indices in [lo, hi]",
    cpp: "points: vector<pair<long long, long long>> of (index, value), distinct indices in [lo, hi]",
  },
  mod: { py: "the modulus p", cpp: "the modulus p" },
  bits: { py: "values live in [0, 2^bits)", cpp: "values live in [0, 2^bits)" },
};

// "Usage": construct, then one block per selected op. Every statement has its comment on the lines above it.
function UsagePanel({ template, selected, lang }: { template: TemplateView; selected: Set<OpId>; lang: TemplateLang }) {
  const usage = template.usage[lang];
  if (!usage) return null;
  const ops = template.operations.filter((op) => selected.has(op));
  const shown = ops.length ? ops : template.operations;
  const cpp = lang === "cpp";
  const cm = cpp ? "//" : "#";
  const neededClasses = [...new Set(shown.map((op) => usage.methods[op]!.cls))].sort((a, b) => a - b);
  const varOf = (k: number) =>
    neededClasses.length === 1 ? "seg" : usage.classes[k].className[0].toLowerCase() + usage.classes[k].className.slice(1);
  const typeOf = (ret = "") => ret.replace(/\bT\b/g, "long long").replace(/\bS\b/g, "long long");
  const sparse = template.file === "sparse";
  const fromPoints = sparse && isBuiltFromPoints(template.memory);

  const blocks: { comments: string[]; code: string }[] = [];
  for (const k of neededClasses) {
    const cls = usage.classes[k];
    const requiredParams = cls.ctor.filter((p) => p.default === undefined);
    const required = requiredParams.map((p) => p.name);
    const optional = cls.ctor.filter((p) => p.default !== undefined);
    // C++17 deduces T from a vector argument (vector<T>, vector<pair<long long, T>>), unless a scalar T argument
    // (e.g. a literal 3, an int) could disagree with it; then, or when T appears in no argument, write it out.
    const deducible =
      requiredParams.some((p) => /vector<.*\bT\b/.test(p.type ?? "")) &&
      !requiredParams.some((p) => /^(const\s+)?T\s*&?$/.test(p.type ?? ""));
    if (cpp && cls.pool)
      blocks.push({
        comments: [`Between test cases: frees every ${cls.className}<long long> (they all share one node pool).`],
        code: `${cls.className}<long long>::resetPool();`,
      });
    const comments = [
      ...(!sparse
        ? []
        : fromPoints
          ? ["Indices are any integers in [lo, hi] (negative is fine); every index not in points is 0."]
          : [
              "Every index in [lo, hi] starts at 0 (any integers, negative is fine).",
              "Untouched indices read as 0, e.g. the max of an untouched range is 0, not -inf.",
            ]),
      ...required.flatMap((n) => (CTOR_ARG_NOTES[n] && !["mod", "bits"].includes(n) ? [CTOR_ARG_NOTES[n][lang]] : [])),
      ...optional.map((p) => `Optional: ${p.name} (default ${p.default})${CTOR_ARG_NOTES[p.name] ? `, ${CTOR_ARG_NOTES[p.name][lang]}` : ""}.`),
      ...(cpp
        ? [deducible ? "T is deduced from the vector (vector<long long> gives T = long long)." : "T = long long (int works too)."]
        : []),
    ];
    blocks.push({
      comments,
      code: cpp
        ? `${cls.className}${deducible ? "" : "<long long>"} ${varOf(k)}(${required.join(", ")});`
        : `${varOf(k)} = ${cls.className}(${required.join(", ")})`,
    });
  }
  for (const op of shown) {
    const m = usage.methods[op]!;
    const call = `${varOf(m.cls)}.${op}(${m.params.join(", ")})`;
    let code: string;
    if (UPDATE_OPS.has(op)) code = cpp ? `${call};` : call;
    else if (op === "rangeMode") code = cpp ? `auto [value, freq] = ${call};` : `value, freq = ${call}`;
    else code = cpp ? `${typeOf(m.returns) || "auto"} ${op} = ${call};` : `${op} = ${call}`;
    // in a sparse version, every query line says what the indices nobody wrote hold
    const zeros = !sparse || UPDATE_OPS.has(op) ? "" : fromPoints ? "indices not in points count as 0" : "never-updated indices count as 0";
    const doc = [m.doc, zeros].filter(Boolean).join("; ");
    blocks.push({ comments: doc ? [doc] : [], code });
  }

  return (
    <div className="border-b border-border px-4 py-3 text-xs">
      <p className="mb-1.5 font-semibold text-foreground">Usage</p>
      <pre className="overflow-x-auto rounded-md bg-card p-3 font-mono text-[11px] leading-relaxed text-foreground">
        {blocks.map((b, i) => (
          <span key={i}>
            {i > 0 && "\n"}
            {b.comments.map((c, j) => (
              <span key={j} className="text-muted-foreground">
                {`${cm} ${c}\n`}
              </span>
            ))}
            {`${b.code}\n`}
          </span>
        ))}
      </pre>
    </div>
  );
}

const opName = (op: Op) => op.signature.split("(")[0];
const opArgs = (op: Op) => op.signature.slice(opName(op).length);

const TIER_STYLES: Record<TierKind, { label: string; badge: string }> = {
  common: { label: "Common", badge: "border-stone-300 bg-stone-100 text-stone-600" },
  uncommon: { label: "Uncommon", badge: "border-emerald-200 bg-emerald-50 text-emerald-700" },
  rare: { label: "Rare", badge: "border-amber-200 bg-amber-50 text-amber-700" },
  mod: { label: "Mod p", badge: "border-sky-200 bg-sky-50 text-sky-700" },
  bitOps: { label: "Bit ops", badge: "border-violet-200 bg-violet-50 text-violet-700" },
};

function TierBadge({ kind, label: labelOverride }: { kind: TierKind; label?: string }) {
  const { label: kindLabel, badge } = TIER_STYLES[kind];
  const label = labelOverride ?? kindLabel;
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2 py-0.5 font-[family-name:var(--font-dm-sans)] text-[10px] font-bold uppercase tracking-wider ${badge}`}
    >
      {label}
    </span>
  );
}

export function RangeQueryPicker() {
  const [selected, setSelected] = useState<Set<OpId>>(new Set());
  const [openTemplate, setOpenTemplate] = useState<TemplateView | null>(null);
  const sparseMode = useSyncExternalStore(subscribeSparse, readSparse, (): SparseMode => "none");

  const toggle = (id: OpId) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectedOps = ALL_OPS.filter((op) => selected.has(op.id));
  const matches = matchTemplates(selected, sparseMode);

  return (
    <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-24 font-[family-name:var(--font-dm-sans)]">
      <header className="mb-6 flex items-center justify-between gap-4">
        <h1 className="font-[family-name:var(--font-playfair)] text-3xl font-bold text-foreground">
          Range Query Picker
        </h1>
        <div className="flex items-center gap-2">
        <div className="flex overflow-hidden rounded-md border border-border text-xs font-medium" role="radiogroup" aria-label="Sparse versions">
          {SPARSE_MODES.map(({ mode, label, title }) => (
            <button
              key={mode}
              type="button"
              role="radio"
              aria-checked={sparseMode === mode}
              title={title}
              onClick={() => writeSparse(mode)}
              className={`px-3 py-1.5 transition-colors ${
                sparseMode === mode ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <button
          type="button"
          onClick={() => setSelected(new Set())}
          disabled={selectedOps.length === 0}
          className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-muted disabled:cursor-default disabled:opacity-40 disabled:hover:bg-transparent"
        >
          Unselect all
        </button>
        </div>
      </header>

      <div className="grid gap-4 lg:grid-cols-[minmax(0,1fr)_300px]">
        <div className="columns-1 gap-4 md:columns-2 xl:columns-3">
          {OP_GROUPS.map((group) => (
            <section
              key={group.id}
              className="mb-4 break-inside-avoid rounded-xl border border-border bg-card p-4"
            >
              <div className="mb-2.5 flex items-baseline justify-between gap-3">
                <h2 className="text-sm font-semibold text-foreground">{group.title}</h2>
                <span className="text-xs text-muted-foreground">{group.blurb}</span>
              </div>
              <div className="-mx-2 grid grid-cols-[auto_auto_minmax(0,1fr)]">
                {group.tiers.flatMap((tier, tierIdx) => [
                  <h3
                    key={tier.label ?? tier.kind}
                    className={`col-span-3 flex items-center gap-2 px-2 pb-1 ${tierIdx === 0 ? "" : "mt-3"}`}
                  >
                    <TierBadge kind={tier.kind} label={tier.label} />
                    <span aria-hidden className="h-px flex-1 bg-gradient-to-r from-border to-transparent" />
                  </h3>,
                  ...tier.ops.map((op) => {
                    const isOn = selected.has(op.id);
                    return (
                      <button
                        key={op.id}
                        type="button"
                        aria-pressed={isOn}
                        onClick={() => toggle(op.id)}
                        title={op.signature}
                        className={`col-span-3 grid grid-cols-subgrid items-baseline gap-x-3 rounded-md px-2 py-1 text-left transition-colors ${
                          isOn ? "bg-primary/15" : "hover:bg-muted"
                        }`}
                      >
                        <span
                          aria-hidden
                          className={`relative top-0.5 flex h-3.5 w-3.5 items-center justify-center self-start rounded-sm border text-[9px] leading-none ${
                            isOn ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background"
                          }`}
                        >
                          {isOn ? "✓" : ""}
                        </span>
                        <span
                          className={`whitespace-nowrap font-mono text-[13px] ${
                            isOn ? "font-medium text-primary" : "text-foreground"
                          }`}
                        >
                          {opName(op)}
                          {op.showArgs && (
                            <span className="font-normal text-muted-foreground">{opArgs(op)}</span>
                          )}
                        </span>
                        <span className="min-w-0 text-xs text-muted-foreground">{op.description}</span>
                      </button>
                    );
                  }),
                ])}
              </div>
            </section>
          ))}
        </div>

        <aside className="self-start lg:sticky lg:top-20">
          <div className="rounded-xl border border-border bg-card p-4">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-foreground">
                Selection
                {selectedOps.length > 0 && (
                  <span className="ml-1.5 font-normal text-muted-foreground">{selectedOps.length}</span>
                )}
              </h2>
              {selectedOps.length > 0 && (
                <button
                  type="button"
                  onClick={() => setSelected(new Set())}
                  className="text-xs text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
                >
                  Clear
                </button>
              )}
            </div>

            {selectedOps.length === 0 ? (
              <p className="text-xs text-muted-foreground">Nothing picked yet.</p>
            ) : (
              <ul className="space-y-1.5">
                {selectedOps.map((op) => (
                  <li key={op.id} className="flex items-center justify-between gap-2">
                    <code className="truncate font-mono text-xs text-foreground">{op.signature}</code>
                    <button
                      type="button"
                      onClick={() => toggle(op.id)}
                      aria-label={`Remove ${opName(op)}`}
                      className="flex-shrink-0 text-sm leading-none text-muted-foreground hover:text-foreground"
                    >
                      ×
                    </button>
                  </li>
                ))}
              </ul>
            )}

            <div className="mt-4 border-t border-border pt-3">
              <h2 className="text-sm font-semibold text-foreground">
                Templates
                {matches.length > 0 && (
                  <span className="ml-1.5 font-normal text-muted-foreground">{matches.length}</span>
                )}
              </h2>
              {selected.size === 0 ? (
                <p className="mt-1 text-xs text-muted-foreground">
                  Pick operations to see templates that cover them.
                </p>
              ) : matches.length === 0 ? (
                <p className="mt-1 text-xs text-muted-foreground">No template covers this selection yet.</p>
              ) : (
                <ul className="mt-2 space-y-1.5">
                  {matches.map(({ template, extra, costs }, i) => {
                    return (
                    <li key={`${template.folder}/${template.file}`}>
                      <button
                        type="button"
                        onClick={() => setOpenTemplate(template)}
                        className="w-full rounded-lg border border-border bg-background p-2 text-left transition-colors hover:border-primary/50"
                      >
                        <span className="flex items-center justify-between gap-2">
                          <span className="text-xs font-medium text-foreground">
                            {templateKindLabel(template)}
                          </span>
                          {i === 0 && (
                            <span className="rounded-full bg-primary/15 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
                              Best match
                            </span>
                          )}
                        </span>
                        <span className="mt-1.5 grid grid-cols-[auto_1fr] gap-x-3 gap-y-0.5 text-[11px] leading-snug">
                          {costs.map((c) => (
                            <span key={c.op} className="contents">
                              <span className="font-mono text-muted-foreground">{c.op}</span>
                              <span className="text-foreground">{formatCost(c.cost)}</span>
                            </span>
                          ))}
                          <span className="font-mono text-muted-foreground">build</span>
                          <span className="text-foreground">{formatCost(template.build)}</span>
                        </span>
                        <span className="mt-1.5 block text-[11px] leading-snug text-muted-foreground">
                          <span className="block">
                            Memory <span className="text-foreground">{formatMemoryOf(template.memory, template.memory.total)}</span>
                            {layoutLabel(template.memory) && ` (${layoutLabel(template.memory)})`}
                          </span>
                          {memoryGroups(template).map(({ id, label }) => (
                            <span key={id} className="block pl-3">
                              {label} —{" "}
                              {template.memory[id].arrays.map((a) => a.name).join(", ") || "none"}
                            </span>
                          ))}
                        </span>
                        {extra.length > 0 && (
                          <span className="mt-1.5 block text-[11px] leading-snug text-muted-foreground">
                            Also supports: {extra.join(", ")}
                          </span>
                        )}
                      </button>
                    </li>
                    );
                  })}
                </ul>
              )}
            </div>
          </div>
        </aside>
      </div>

      {openTemplate && (
        <CodeDrawer
          key={`${openTemplate.folder}/${openTemplate.file}`}
          template={openTemplate}
          selected={selected}
          onClose={() => setOpenTemplate(null)}
        />
      )}
    </main>
  );
}
