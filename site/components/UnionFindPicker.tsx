"use client";

import { useEffect, useMemo, useState } from "react";
import { FillInDrawer, MiscCard, PickerTabs, type FillIn } from "@/components/TemplatePicker";
import { TEMPLATE_LANG_LABELS, type TemplateLang } from "@/lib/template-picker";
import {
  UNION_FIND_BASE_OPS,
  UNION_FIND_CLASS,
  UNION_FIND_EXTRA_OPS,
  UNION_FIND_EXTRAS,
} from "@/lib/generated/union-find-templates";

// The Union find tab: pick a find mode and any extras, and the matching template (one of the generated
// templates/ultimate-template-tool/union-find/<mode>[-extra...] folders) shows on the right, with its ops.

type Mode = "compress" | "nocompress" | "rollback";
type Extra = (typeof UNION_FIND_EXTRAS)[number];

const PUBLIC = "/union-find-templates";
const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/union-find/";

const MODES: { id: Mode; label: string; text: string }[] = [
  {
    id: "compress",
    label: "Path compression",
    text: "Fastest, about O(1) per op. Parents get rewritten as you go.",
  },
  {
    id: "nocompress",
    label: "No path compression",
    text: "O(log n) per op, but a parent never changes once set, so the forest records every merge and you can walk it yourself. Adds uniteAUnderB, and unite returns (winner, loser).",
  },
  {
    id: "rollback",
    label: "Rollback",
    text: "No compression plus an undo stack: rollback() undoes the last unite, checkpoint() / rollbackTo(k) jump back. Offline dynamic connectivity, backtracking.",
  },
];

const EXTRAS: { id: Extra; label: string; text: string; needs?: Mode; needsText?: string }[] = [
  { id: "values", label: "Component sum / min / max", text: "componentSum, componentMin, componentMax of the elements' values (vals are numbers)." },
  {
    id: "merge",
    label: "Your own merge",
    text: "Fill in a Node, baseFn(v, i) and combine(big, small), like the generic seg tree: componentData(i). combine runs once per merge, with the bigger side first (small-to-large).",
  },
  { id: "members", label: "List members fast", text: "elementsInGroup(i) in O(size of the group) instead of O(n): each component's members are linked in a circle." },
  { id: "edges", label: "Edge counts", text: "edgeCount(i), isTree(i): every unite counts as an edge, even inside a component, so cycles show up." },
  {
    id: "potential",
    label: "Weighted (potential)",
    text: "unite(i, j, w) says value[j] − value[i] = w; diff(i, j) reads it back. For parity / two-colouring, swap + and − for ^.",
  },
  {
    id: "time",
    label: "Connected at time t",
    text: "firstConnectedTime(i, j): after how many unites two elements first joined; connectedAt(i, j, t).",
    needs: "nocompress",
    needsText: "Needs No path compression: it walks the record of merges",
  },
  { id: "grow", label: "Add elements", text: "add(val): a new element in its own component, so you can start empty." },
];

const OTHERS: FillIn[] = [
  {
    label: "Next free index",
    title: "nextFree(i) / prevFree(i) jump to the nearest index not taken yet; take(i) and takeRange(l, r) use them up. Painting intervals, first unused slot",
    folder: "_next-free",
    file: "template",
    githubUrl: `${GITHUB}_next-free/`,
    ops: [
      ["nextFree(i)", "1 amortized"],
      ["prevFree(i)", "1 amortized"],
      ["isFree(i)", "1 amortized"],
      ["take(i)", "1 amortized"],
      ["takeRange(l, r)", "1 amortized"],
      ["build", "N"],
    ],
    note: "O(1) here means O(α(n)) amortized. takeRange costs that much per index it takes, so O(n α(n)) over all calls together.",
  },
  {
    label: "Fully dynamic connectivity (HDLT)",
    title: "Add and remove edges online, with connectivity queries in between (Holm, de Lichtenberg, Thorup)",
    folder: "_hdlt",
    file: "hdlt",
    githubUrl: "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/union-find/",
    ops: [
      ["addEdge(u, v)", "log^2(N) amortized"],
      ["removeEdge(e)", "log^2(N) amortized"],
      ["removeEdgeBetween(u, v)", "log^2(N) amortized"],
      ["areConnected(u, v)", "log(N)"],
      ["size(u)", "log(N)"],
      ["numComponents()", "1"],
      ["componentId(u)", "log(N)"],
      ["roots()", "N*log(N)"],
      ["groups()", "N*log(N)"],
      ["sizes()", "N*log(N)"],
      ["elementsInGroup(u)", "N*log(N)"],
      ["build", "N*log(N)"],
    ],
    note: "If the edges are all known ahead of time, the Rollback union find over a segment tree on time is simpler and faster.",
  },
];

const opName = (op: string) => op.split("(")[0];

// "α(n) amortized" -> "O(α(n)) amortized", "1 per unite undone" -> "O(1) per unite undone"
function showCost(cost: string) {
  const m = cost.match(/^(α\(n\)|n log n|log n|size of the group|n|1)(.*)$/);
  return m ? `O(${m[1]})${m[2]}` : cost;
}

function folderOf(mode: Mode, extras: Set<Extra>) {
  return [mode, ...UNION_FIND_EXTRAS.filter((e) => extras.has(e))].join("-");
}

function opsOf(mode: Mode, extras: Set<Extra>): [string, string][] {
  const ops = UNION_FIND_BASE_OPS[mode].filter(([op]) => op !== "build");
  for (const e of UNION_FIND_EXTRAS) {
    if (!extras.has(e)) continue;
    for (const [op, cost] of UNION_FIND_EXTRA_OPS[mode][e]) {
      const k = ops.findIndex(([o]) => opName(o) === opName(op));
      if (k >= 0) ops[k] = [op, cost];
      else ops.push([op, cost]);
    }
  }
  return [...ops, ["build", "n"]];
}

const texts = new Map<string, Promise<string>>();
function loadText(url: string) {
  let p = texts.get(url);
  if (!p) {
    p = fetch(url).then((res) => (res.ok ? res.text() : Promise.reject(res.status)));
    p.catch(() => texts.delete(url));
    texts.set(url, p);
  }
  return p;
}

function Check({ on, round }: { on: boolean; round?: boolean }) {
  return (
    <span
      aria-hidden
      className={`relative top-0.5 flex h-3.5 w-3.5 flex-shrink-0 items-center justify-center self-start border text-[9px] leading-none ${
        round ? "rounded-full" : "rounded-sm"
      } ${on ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background"}`}
    >
      {on ? (round ? "●" : "✓") : ""}
    </span>
  );
}

export function UnionFindPicker() {
  const [mode, setMode] = useState<Mode>("compress");
  const [extras, setExtras] = useState<Set<Extra>>(new Set());
  const [lang, setLang] = useState<TemplateLang>("py");
  const [open, setOpen] = useState<FillIn | null>(null);
  const [loaded, setLoaded] = useState<{ url: string; code: string | null } | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  const usable = (e: (typeof EXTRAS)[number]) => !e.needs || e.needs === mode;
  const chooseMode = (m: Mode) => {
    setMode(m);
    // an extra this mode can't have is dropped, so the template shown always matches what's ticked
    setExtras((prev) =>
      new Set(
        [...prev].filter((id) => {
          const e = EXTRAS.find((x) => x.id === id)!;
          return !e.needs || e.needs === m;
        }),
      ),
    );
  };
  const toggle = (id: Extra) =>
    setExtras((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const folder = folderOf(mode, extras);
  const fileName = `template.${lang}`;
  const url = `${PUBLIC}/${folder}/${fileName}`;
  const ops = useMemo(() => opsOf(mode, extras), [mode, extras]);
  const code = loaded?.url === url ? loaded.code : undefined;

  useEffect(() => {
    let cancelled = false;
    loadText(url)
      .then((text) => !cancelled && setLoaded({ url, code: text }))
      .catch(() => !cancelled && setLoaded({ url, code: null }));
    return () => {
      cancelled = true;
    };
  }, [url]);

  const copy = async () => {
    if (!code) return;
    await navigator.clipboard.writeText(code);
    setCopied(url);
  };

  return (
    <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-16 font-[family-name:var(--font-dm-sans)]">
      <div className="sticky top-16 z-30 -mx-6 bg-background px-6 pt-2">
        <h1 className="sr-only">Union find templates</h1>
        <PickerTabs />
      </div>
      <div className="grid gap-4 lg:grid-cols-[minmax(320px,420px)_minmax(0,1fr)]">
        <div className="flex flex-col gap-3">
          <section className="rounded-xl border border-border bg-card px-3 py-2.5">
            <h2 className="mb-1.5 text-sm font-semibold text-foreground">Find</h2>
            <div role="radiogroup" aria-label="Find mode" className="-mx-2 flex flex-col">
              {MODES.map((m) => {
                const on = mode === m.id;
                return (
                  <button
                    key={m.id}
                    type="button"
                    role="radio"
                    aria-checked={on}
                    onClick={() => chooseMode(m.id)}
                    className={`flex gap-2 rounded-md px-2 py-1 text-left transition-colors ${on ? "bg-primary/15" : "hover:bg-muted"}`}
                  >
                    <Check on={on} round />
                    <span className="min-w-0">
                      <span className={`block text-xs ${on ? "font-medium text-primary" : "text-foreground"}`}>{m.label}</span>
                      <span className="block text-[11px] leading-snug text-muted-foreground">{m.text}</span>
                    </span>
                  </button>
                );
              })}
            </div>
          </section>
          <section className="rounded-xl border border-border bg-card px-3 py-2.5">
            <div className="mb-1.5 flex items-baseline justify-between gap-3">
              <h2 className="text-sm font-semibold text-foreground">Extras</h2>
              {extras.size > 0 && (
                <button type="button" onClick={() => setExtras(new Set())} className="text-xs text-muted-foreground hover:text-foreground">
                  Unselect all
                </button>
              )}
            </div>
            <div className="-mx-2 flex flex-col">
              {EXTRAS.map((e) => {
                const off = !usable(e);
                const on = extras.has(e.id);
                return (
                  <button
                    key={e.id}
                    type="button"
                    aria-pressed={on}
                    disabled={off}
                    title={off ? e.needsText : undefined}
                    onClick={() => toggle(e.id)}
                    className={`flex gap-2 rounded-md px-2 py-1 text-left transition-colors ${
                      off ? "cursor-not-allowed opacity-35" : on ? "bg-primary/15" : "hover:bg-muted"
                    }`}
                  >
                    <Check on={on} />
                    <span className="min-w-0">
                      <span className={`block text-xs ${on ? "font-medium text-primary" : "text-foreground"}`}>{e.label}</span>
                      <span className="block text-[11px] leading-snug text-muted-foreground">
                        {off ? `${e.needsText}. ` : ""}
                        {e.text}
                      </span>
                    </span>
                  </button>
                );
              })}
            </div>
          </section>
          <section className="rounded-xl border border-border bg-card px-3 py-2.5">
            <h2 className="mb-2 text-sm font-semibold text-foreground">Other union finds</h2>
            <div className="flex flex-col gap-2">
              {OTHERS.map((f) => (
                <MiscCard key={f.folder} item={f} onOpen={() => setOpen(f)} />
              ))}
            </div>
          </section>
        </div>
        <section className="flex min-w-0 flex-col self-start rounded-xl border border-border bg-card lg:sticky lg:top-32 lg:max-h-[calc(100vh-9rem)]">
          <div className="flex items-start justify-between gap-4 border-b border-border p-3">
            <div className="min-w-0">
              <p className="text-sm font-semibold text-foreground">{UNION_FIND_CLASS[mode]}</p>
              <p className="break-all font-mono text-[11px] text-muted-foreground">{folder}</p>
            </div>
            <div className="flex flex-shrink-0 items-center gap-2">
              <div className="flex overflow-hidden rounded-md border border-border text-xs" role="group" aria-label="Language">
                {(["py", "cpp"] as TemplateLang[]).map((l) => (
                  <button
                    key={l}
                    type="button"
                    aria-pressed={lang === l}
                    onClick={() => setLang(l)}
                    className={`px-2.5 py-1 ${lang === l ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"}`}
                  >
                    {TEMPLATE_LANG_LABELS[l]}
                  </button>
                ))}
              </div>
              <button
                type="button"
                onClick={copy}
                disabled={!code}
                className="rounded-md border border-border px-2.5 py-1 text-xs text-foreground hover:bg-muted disabled:opacity-50"
              >
                {copied === url ? "Copied" : "Copy"}
              </button>
              <a
                href={`${GITHUB}${folder}/${fileName}`}
                target="_blank"
                rel="noopener noreferrer"
                className="rounded-md border border-border px-2.5 py-1 text-xs text-foreground hover:bg-muted"
              >
                GitHub ↗
              </a>
            </div>
          </div>
          <div className="min-h-0 flex-1 overflow-y-auto">
            <div className="border-b border-border px-3 py-2.5 text-xs">
              <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5">
                {ops.map(([op, cost]) => (
                  <div key={op} className="contents">
                    <span className="font-mono font-medium text-primary">{op}</span>
                    <span className="text-foreground">{showCost(cost)}</span>
                  </div>
                ))}
              </div>
            </div>
            <pre className="overflow-x-auto p-4 font-mono text-xs leading-relaxed text-foreground">
              {code === null ? "Couldn't load this template." : (code ?? "Loading…")}
            </pre>
          </div>
        </section>
      </div>
      {open && <FillInDrawer key={open.file} catalog={{ publicBase: PUBLIC }} fillIn={open} onClose={() => setOpen(null)} />}
    </main>
  );
}
