"use client";

import { useMemo, useState } from "react";
import { FillInDrawer, type FillIn } from "@/components/TemplatePicker";
import { costValue, formatCost } from "@/lib/template-picker";
import {
  EERTREE_GROUPS,
  EERTREE_QUERIES,
  EERTREE_UPDATES,
  EERTREE_VARIANTS,
  keepTickedOps,
  type EertreeOp,
  type EertreeVariant,
} from "@/lib/eertree-picker";

const GITHUB = "https://github.com/ishaanbuildsthings/leetcode/blob/main/templates/ultimate-template-tool/strings/";

// b is no better than a: same or worse at every row (both list the same rows for the same ticks). A cost in σ (the number
// of distinct items, anywhere from 2 to n) only counts as no worse if it's no worse at both extremes
const atAlphabet = (cost: string, big: boolean) =>
  costValue(big ? cost.replace(/log\(σ\)/g, "log(N)").replace(/σ/g, "N") : cost.replace(/log\(σ\)/g, "1").replace(/σ/g, "2"));
const atMost = (x: string, y: string) =>
  x === y || (atAlphabet(x, false) <= atAlphabet(y, false) && atAlphabet(x, true) <= atAlphabet(y, true));
const noBetter = (a: [string, string][], b: [string, string][]) =>
  a.length === b.length && a.every(([, cost], i) => atMost(cost, b[i][1]));

// The Eertree section of the Strings tab: tick ops, see the templates that have them all (dropping any that another
// one matches or beats on every cost), open one to get its code with only the ticked ops.
export function EertreePicker({ publicBase }: { publicBase: string }) {
  const [ticked, setTicked] = useState<ReadonlySet<string>>(() => new Set());
  const [open, setOpen] = useState<EertreeVariant | null>(null);
  const toggle = (id: string, on: boolean) =>
    setTicked((prev) => {
      const next = new Set(prev);
      if (on) next.add(id);
      else next.delete(id);
      return next;
    });

  const frontier = useMemo(() => {
    const fits = EERTREE_VARIANTS.filter((v) => [...ticked].every((id) => v.supports.has(id)));
    const costs = new Map(fits.map((v) => [v, v.costs(ticked)]));
    return fits.filter((v, i) => !fits.some((w, j) => j < i && noBetter(costs.get(w)!, costs.get(v)!)));
  }, [ticked]);

  const fillIn = (v: EertreeVariant): FillIn => ({
    label: v.label(ticked),
    title: "",
    folder: "_strings",
    file: v.file,
    githubUrl: GITHUB,
    ops: v.costs(ticked),
    note: ["Takes any sequence (str / list / tuple, C++ string / vector).", v.note?.(ticked) ?? ""]
      .filter(Boolean)
      .join(" "),
    transform: (code: string) => keepTickedOps(code, new Set([...ticked, ...(v.tags ?? [])])),
  });

  // a row like the range picker's: box, name, and what it does
  const row = (op: EertreeOp) => {
    const isOn = ticked.has(op.id);
    return (
      <button
        key={op.id}
        type="button"
        title={op.title}
        aria-pressed={isOn}
        onClick={() => toggle(op.id, !isOn)}
        className={`grid grid-cols-[auto_1fr] items-start gap-x-2 rounded px-1.5 py-1 text-left ${isOn ? "bg-primary/15" : "hover:bg-muted"}`}
      >
        <span
          aria-hidden
          className={`relative top-0.5 flex h-3.5 w-3.5 items-center justify-center self-start rounded-sm border text-[9px] leading-none ${
            isOn ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background"
          }`}
        >
          {isOn ? "✓" : ""}
        </span>
        <span className="min-w-0">
          {op.methods.map((method, i) => (
            <span key={method} className="block whitespace-nowrap font-mono text-xs">
              <span className={isOn ? "font-medium text-primary" : "text-foreground"}>{method}</span>
              {op.returns[i] && <span className="text-muted-foreground"> -&gt; {op.returns[i]}</span>}
            </span>
          ))}
          <span className="block text-[11px] leading-snug text-muted-foreground">{op.description}</span>
        </span>
      </button>
    );
  };
  const heading = (text: string) => (
    <div className="mb-1 mt-3 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground first:mt-0">{text}</div>
  );

  return (
    <div className="flex flex-wrap items-start gap-3 text-xs">
      <div className="max-w-2xl rounded-lg border border-border bg-card p-3">
        <div className="mb-2 text-sm font-medium text-foreground">Eertree (palindromic tree)</div>
        {heading("Updates")}
        <div className="flex flex-col">{EERTREE_UPDATES.map(row)}</div>
        {EERTREE_GROUPS.map((group) => (
          <div key={group} className="mt-3">
            {heading(group)}
            <div className="flex flex-col">{EERTREE_QUERIES.filter((q) => q.group === group).map(row)}</div>
          </div>
        ))}
      </div>
      <div className="flex shrink-0 flex-col gap-3">
        {heading(frontier.length === 1 ? "Template" : "Templates")}
        {frontier.length === 0 && (
          <p className="max-w-xs text-muted-foreground">
            No template has these together: the per-index queries need the sequence to only change at its right end.
          </p>
        )}
        {frontier.map((v) => (
          <button
            key={v.id}
            type="button"
            onClick={() => setOpen(v)}
            className="group rounded-lg border border-primary/40 bg-primary/5 p-3 text-left shadow-sm transition-colors hover:border-primary hover:bg-primary/10"
          >
            <span className="mb-1.5 flex items-center justify-between gap-6">
              <span className="text-sm font-medium text-foreground">{v.label(ticked)}</span>
              <span className="text-xs font-medium text-primary group-hover:underline">Open code →</span>
            </span>
            <span className="grid grid-cols-[auto_auto] gap-x-4 gap-y-0.5">
              {v.costs(ticked).map(([op, cost]) => (
                <span key={op} className="contents">
                  <span className="font-mono text-primary">{op}</span>
                  <span className="text-foreground">{formatCost(cost)}</span>
                </span>
              ))}
            </span>
          </button>
        ))}
      </div>
      {open && <FillInDrawer key={open.id} catalog={{ publicBase }} fillIn={fillIn(open)} onClose={() => setOpen(null)} />}
    </div>
  );
}
