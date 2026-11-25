"use client";

import { useState } from "react";
import { FillInDrawer, type FillIn } from "@/components/TemplatePicker";
import { formatCost } from "@/lib/template-picker";
import { keepTickedOps } from "@/lib/eertree-picker";

// One op of a file whose parts sit between "@if <id>" marker lines (the Eertree's rules: lib/eertree-picker.ts):
// how it's called, what it returns, a worked example, a note, and its cost
// grows: (optional) for ops that lazily grow a table, what makes them grow ("bigger n"), shown under the cost as
// "lazily grows when called with bigger n"
export type PickerOp = { id: string; call: string; returns: string; example?: string; note?: string; cost: string; grows?: string };
// setup: the constructor the group's ops need, listed first in the drawer whenever one of them is shown
export type PickerOpGroup = { title: string; ops: PickerOp[]; setup?: { call: string; returns: string; cost: string } };

// the trimmed file without the blank lines the removed blocks leave behind
const tidy = (code: string) => code.replace(/\n{3,}/g, "\n\n").replace(/\n\n(\s*\};)/g, "\n$1").replace(/\s+$/, "\n");

// A Misc-style section where every op of one file is on show as a checkbox; the code keeps just the ticked ops (all of
// them when nothing is ticked) and whatever they share.
export function OpPicker({
  title,
  folder,
  file,
  githubUrl,
  groups,
  note,
  intro,
  publicBase,
}: {
  title: string;
  folder: string;
  file: string;
  githubUrl: string;
  groups: PickerOpGroup[];
  note?: string;
  // (optional) a line under the title, before the ops (e.g. which of two versions to pick)
  intro?: React.ReactNode;
  publicBase: string;
}) {
  const all = groups.flatMap((g) => g.ops);
  const [ticked, setTicked] = useState<ReadonlySet<string>>(() => new Set());
  const [open, setOpen] = useState(false);
  const toggle = (id: string) =>
    setTicked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  const shown = ticked.size ? all.filter((op) => ticked.has(op.id)) : all;
  const keep = new Set(shown.map((op) => op.id));
  const fillIn: FillIn = {
    label: ticked.size ? `${title}: ${ticked.size} of ${all.length} ops` : `${title}: every op`,
    title: "",
    folder,
    file,
    githubUrl,
    ops: [
      // each constructor the shown ops need, once, before them
      ...[
        ...new Map(
          groups
            .filter((g) => g.setup && g.ops.some((op) => keep.has(op.id)))
            .map((g) => [g.setup!.call, [`${g.setup!.call} -> ${g.setup!.returns}`, g.setup!.cost] as [string, string]]),
        ).values(),
      ],
      ...shown.map((op): [string, string] => [
        `${op.call} -> ${op.returns}${op.grows ? ` (lazily grows when called with ${op.grows})` : ""}`,
        op.cost,
      ]),
    ],
    note,
    transform: (code: string) => tidy(keepTickedOps(code, keep)),
  };

  const row = (op: PickerOp) => {
    const isOn = ticked.has(op.id);
    return (
      <button
        key={op.id}
        type="button"
        aria-pressed={isOn}
        onClick={() => toggle(op.id)}
        className={`grid grid-cols-[auto_1fr_auto] items-start gap-x-2 rounded px-1.5 py-1 text-left ${isOn ? "bg-primary/15" : "hover:bg-muted"}`}
      >
        <span
          aria-hidden
          className={`relative top-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-sm border text-[9px] leading-none ${
            isOn ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background"
          }`}
        >
          {isOn ? "✓" : ""}
        </span>
        <span className="min-w-0">
          <span className="block font-mono text-xs">
            <span className={isOn ? "font-medium text-primary" : "text-foreground"}>{op.call}</span>
            <span className="text-muted-foreground"> -&gt; {op.returns}</span>
          </span>
          {op.example && <span className="block font-mono text-[11px] text-muted-foreground">e.g. {op.example}</span>}
          {op.note && <span className="block text-[11px] leading-snug text-muted-foreground">{op.note}</span>}
        </span>
        <span className="text-right text-[11px] text-foreground">
          <span className="whitespace-nowrap">{formatCost(op.cost)}</span>
          {op.grows && (
            <span className="block max-w-[11rem] text-[11px] leading-snug text-muted-foreground">
              lazily grows when called with {op.grows}
            </span>
          )}
        </span>
      </button>
    );
  };

  return (
    <div className="flex flex-wrap items-start gap-3 text-xs">
      <div className="max-w-4xl rounded-lg border border-border bg-card p-3">
        <div className="mb-2 flex items-center justify-between gap-6">
          <span className="text-sm font-medium text-foreground">{title}</span>
          <button
            type="button"
            onClick={() => setOpen(true)}
            className="rounded-md border border-primary/40 bg-primary/5 px-2.5 py-1 text-xs font-medium text-primary hover:border-primary hover:bg-primary/10"
          >
            Open code{ticked.size ? ` (${ticked.size} picked)` : ""} →
          </button>
        </div>
        {intro && <div className="mb-2 max-w-3xl text-[11px] leading-snug text-muted-foreground">{intro}</div>}
        {groups.map((g) => (
          <div key={g.title} className="mt-2 first:mt-0">
            {g.title && <div className="mb-1 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground">{g.title}</div>}
            <div className="flex flex-col">{g.ops.map(row)}</div>
          </div>
        ))}
      </div>
      {open && <FillInDrawer key={[...keep].join(",")} catalog={{ publicBase }} fillIn={fillIn} onClose={() => setOpen(false)} />}
    </div>
  );
}
