"use client";

import { useState } from "react";
import { FillInDrawer, PickerTabs, type FillIn } from "@/components/TemplatePicker";

// A templates tab laid out as one aligned table, grouped by what you want to compute: each row is one function (or a
// family of them, e.g. the AND / OR / XOR versions behind a small switch, and a mod version behind a checkbox), with its
// cost and what it computes in words. Clicking a row opens the code drawer.

// one version of a row: what the row shows while it's picked, and the file the drawer opens
export type RowVersion = { call: string; does: string; cost: string; fillIn: FillIn };
// a choice on the row's switch (AND / OR / XOR), with its mod version if there is one
export type RowChoice = RowVersion & { key: string; title?: string; mod?: RowVersion };
export type RowItem = { id: string; choices: RowChoice[] };
export type RowSection = { title: string; note?: string; rows: RowItem[] };

export function RowTemplates({ title, sections, publicBase }: { title: string; sections: RowSection[]; publicBase: string }) {
  const [open, setOpen] = useState<FillIn | null>(null);
  return (
    <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-16 font-[family-name:var(--font-dm-sans)]">
      <div className="sticky top-16 z-30 -mx-6 bg-background px-6 pt-2">
        <h1 className="sr-only">{title}</h1>
        <PickerTabs />
      </div>
      {/* one grid for the whole page, so every section's columns line up */}
      <div className="grid grid-cols-[auto_auto_auto_auto_minmax(0,1fr)] items-baseline gap-x-4 rounded-xl border border-border bg-card px-4 py-3">
        {sections.map((section, k) => (
          <div key={section.title} className="contents">
            <h2 className={`col-span-5 flex items-baseline gap-2 px-2 pb-1 text-sm font-semibold text-foreground ${k ? "mt-4 border-t border-border pt-3" : ""}`}>
              {section.title}
              {section.note && <span className="text-[11px] font-normal text-muted-foreground">{section.note}</span>}
            </h2>
            {section.rows.map((row) => (
              <Row key={row.id} row={row} onOpen={setOpen} />
            ))}
          </div>
        ))}
      </div>
      {open && <FillInDrawer key={open.file} catalog={{ publicBase }} fillIn={open} onClose={() => setOpen(null)} />}
    </main>
  );
}

function Row({ row, onOpen }: { row: RowItem; onOpen: (f: FillIn) => void }) {
  const [key, setKey] = useState(row.choices[0].key);
  const [mod, setMod] = useState(false);
  const choice = row.choices.find((c) => c.key === key) ?? row.choices[0];
  const shown: RowVersion = mod && choice.mod ? choice.mod : choice;
  const anyMod = row.choices.some((c) => c.mod);
  return (
    <div className="col-span-5 grid grid-cols-subgrid items-baseline rounded-md px-2 py-1 transition-colors hover:bg-muted">
      <span className="flex">
        {row.choices.length > 1 && (
          <span className="flex overflow-hidden rounded border border-border text-[10px] font-medium" role="group" aria-label="Which operation">
            {row.choices.map((c) => (
              <button
                key={c.key}
                type="button"
                title={c.title}
                aria-pressed={c.key === choice.key}
                onClick={() => setKey(c.key)}
                className={`px-1.5 py-0.5 ${c.key === choice.key ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-background"}`}
              >
                {c.key}
              </button>
            ))}
          </span>
        )}
      </span>
      <span className="flex">
        {anyMod && (
          <label
            title={choice.mod ? `Use ${choice.mod.call}: the same answer, mod mod` : "This one has no mod version"}
            className={`flex items-center gap-1 text-[11px] ${choice.mod ? "cursor-pointer text-muted-foreground" : "cursor-not-allowed opacity-35"}`}
          >
            <input
              type="checkbox"
              checked={mod && !!choice.mod}
              disabled={!choice.mod}
              onChange={(e) => setMod(e.target.checked)}
              className="accent-primary"
            />
            mod
          </label>
        )}
      </span>
      <button type="button" onClick={() => onOpen(shown.fillIn)} className="whitespace-nowrap text-left font-mono text-xs font-medium text-primary hover:underline">
        {shown.call}
      </button>
      <span className="whitespace-nowrap font-mono text-[11px] text-muted-foreground">{shown.cost}</span>
      <button type="button" onClick={() => onOpen(shown.fillIn)} className="min-w-0 text-left text-xs text-foreground">
        {shown.does}
      </button>
    </div>
  );
}
