"use client";

import { useEffect, useState } from "react";
import {
  OP_GROUPS,
  DATA_STRUCTURE_TYPES,
  DATA_STRUCTURE_TYPE_LABELS,
  costValue,
  formatCost,
  formatMemory,
  TREE_LAYOUT_LABELS,
  TREE_LAYOUT_SHORT,
  type MemoryBreakdown,
  type Op,
  type OpId,
  type RangeQueryTemplate,
  type TierKind,
  type TemplateLang,
  TEMPLATE_LANG_LABELS,
} from "@/lib/range-query-picker";
import { RANGE_QUERY_TEMPLATES } from "@/lib/generated/range-query-templates";

const ALL_OPS: Op[] = OP_GROUPS.flatMap((g) => g.tiers.flatMap((t) => t.ops));

const GITHUB_BASE = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/range-queries/";

const opCost = (t: RangeQueryTemplate, op: OpId) => t.complexities[op] ?? "?";

// Templates covering every selected op, ranked by: slowest selected op, data structure type, total cost
// of selected ops, memory, then fewest extra ops. Type outranks total because amortized bounds on heavy
// structures (beats) hide large constants. Ops you didn't select don't count against a template.
function matchTemplates(selected: Set<OpId>) {
  if (selected.size === 0) return [];
  const picked = [...selected];
  return RANGE_QUERY_TEMPLATES.filter((t) => picked.every((op) => t.operations.includes(op)))
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
        costValue(a.template.memory.total) - costValue(b.template.memory.total) ||
        a.extra.length - b.extra.length ||
        a.template.folder.localeCompare(b.template.folder)
    );
}

const MEMORY_GROUP_LABELS = { node: "Node data", tags: "Lazy tags", other: "Other" } as const;
const MEMORY_GROUPS = ["node", "tags", "other"] as const;

// "32N node + 20N tags": the non-empty groups, for the card line.
function memorySplit(memory: MemoryBreakdown): string | null {
  const parts = MEMORY_GROUPS.filter((g) => memory[g].arrays.length).map((g) => {
    const size = formatMemory(memory[g].total);
    return `${size.includes(" + ") ? `(${size})` : size} ${g}`;
  });
  return parts.length > 1 ? parts.join(" + ") : null;
}

function MemoryPanel({ memory }: { memory: MemoryBreakdown }) {
  return (
    <div className="border-b border-border px-4 py-3 text-xs">
      <p className="mb-1.5 font-semibold text-foreground">
        Memory {formatMemory(memory.total)}
        <span className="ml-2 font-normal text-muted-foreground">{TREE_LAYOUT_LABELS[memory.layout]}</span>
      </p>
      <div className="grid grid-cols-[auto_auto_1fr] gap-x-4 gap-y-1">
        {MEMORY_GROUPS.map((g) => {
          const { arrays, total } = memory[g];
          const uniform = arrays.every((a) => a.size === arrays[0].size);
          const count = arrays.length;
          return (
            <div key={g} className="contents">
              <span className="text-muted-foreground">
                {MEMORY_GROUP_LABELS[g]}
                {count > 0 && ` (${count} ${count === 1 ? "field" : "fields"})`}
              </span>
              <span className="text-foreground">{count ? formatMemory(total) : "0"}</span>
              <span className="font-mono text-muted-foreground">
                {count === 0
                  ? "none"
                  : uniform
                    ? arrays.map((a) => a.name).join(", ")
                    : arrays.map((a) => `${a.name} ${formatMemory(a.size)}`).join(", ")}
              </span>
            </div>
          );
        })}
      </div>
      {memory.note && <p className="mt-1.5 text-muted-foreground">{memory.note}</p>}
    </div>
  );
}

const LANG_STORAGE_KEY = "rangeQueryPicker.lang";

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
  template: RangeQueryTemplate;
  selected: Set<OpId>;
  onClose: () => void;
}) {
  const [preferred, setPreferred] = useState<TemplateLang>(readPreferredLang);
  const lang = template.langs.includes(preferred) ? preferred : template.langs[0];
  const [loaded, setLoaded] = useState<{ key: string; code: string | null; failed: boolean } | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const path = `${template.folder}/template.${lang}`;
  const code = loaded?.key === path ? loaded.code : null;
  const failed = loaded?.key === path && loaded.failed;
  const copied = copiedKey === path;

  useEffect(() => {
    let cancelled = false;
    fetch(`/range-query-templates/${encodeURIComponent(template.folder)}/template.${lang}`)
      .then((res) => (res.ok ? res.text() : Promise.reject(res.status)))
      .then((text) => !cancelled && setLoaded({ key: path, code: text, failed: false }))
      .catch(() => !cancelled && setLoaded({ key: path, code: null, failed: true }));
    return () => {
      cancelled = true;
    };
  }, [template.folder, lang, path]);

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
              {DATA_STRUCTURE_TYPE_LABELS[template.dataStructureType]}
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
              href={`${GITHUB_BASE}${encodeURIComponent(template.folder)}/template.${lang}`}
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
        <MemoryPanel memory={template.memory} />
        <pre className="flex-1 overflow-auto bg-card p-4 font-mono text-xs leading-relaxed text-foreground">
          {failed ? "Couldn't load this template." : (code ?? "Loading…")}
        </pre>
      </div>
    </div>
  );
}

const opName = (op: Op) => op.signature.split("(")[0];
const opArgs = (op: Op) => op.signature.slice(opName(op).length);

const TIER_STYLES: Record<TierKind, { label: string; badge: string }> = {
  common: { label: "Common", badge: "border-stone-300 bg-stone-100 text-stone-600" },
  uncommon: { label: "Uncommon", badge: "border-emerald-200 bg-emerald-50 text-emerald-700" },
  rare: { label: "Rare", badge: "border-amber-200 bg-amber-50 text-amber-700" },
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
  const [openTemplate, setOpenTemplate] = useState<RangeQueryTemplate | null>(null);

  const toggle = (id: OpId) => {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const selectedOps = ALL_OPS.filter((op) => selected.has(op.id));
  const matches = matchTemplates(selected);

  return (
    <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-24 font-[family-name:var(--font-dm-sans)]">
      <header className="mb-6">
        <h1 className="font-[family-name:var(--font-playfair)] text-3xl font-bold text-foreground">
          Range Query Picker
        </h1>
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
                    <li key={template.folder}>
                      <button
                        type="button"
                        onClick={() => setOpenTemplate(template)}
                        className="w-full rounded-lg border border-border bg-background p-2 text-left transition-colors hover:border-primary/50"
                      >
                        <span className="flex items-center justify-between gap-2">
                          <span className="text-xs font-medium text-foreground">
                            {DATA_STRUCTURE_TYPE_LABELS[template.dataStructureType]}
                          </span>
                          <span className="flex items-center gap-1.5">
                            {i === 0 && (
                              <span className="rounded-full bg-primary/15 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
                                Best match
                              </span>
                            )}
                            <span className="font-mono text-[10px] uppercase text-muted-foreground">
                              {template.langs.map((l) => (l === "cpp" ? "C++" : "PY")).join(" · ")}
                            </span>
                          </span>
                        </span>
                        <span className="mt-1.5 grid grid-cols-[auto_1fr] gap-x-3 gap-y-0.5 text-[11px] leading-snug">
                          {costs.map((c) => (
                            <span key={c.op} className="contents">
                              <span className="font-mono text-muted-foreground">{c.op}</span>
                              <span className="text-foreground">{formatCost(c.cost)}</span>
                            </span>
                          ))}
                        </span>
                        <span className="mt-1.5 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-[11px] leading-snug text-muted-foreground">
                          <span>
                            Memory <span className="text-foreground">{formatMemory(template.memory.total)}</span>
                            {memorySplit(template.memory) && <span> ({memorySplit(template.memory)})</span>}
                          </span>
                          {TREE_LAYOUT_SHORT[template.memory.layout] && (
                            <span>· {TREE_LAYOUT_SHORT[template.memory.layout]}</span>
                          )}
                          <span>
                            · Build <span className="text-foreground">{formatCost(template.build)}</span>
                          </span>
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
          key={openTemplate.folder}
          template={openTemplate}
          selected={selected}
          onClose={() => setOpenTemplate(null)}
        />
      )}
    </main>
  );
}
