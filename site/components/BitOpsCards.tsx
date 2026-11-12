"use client";

import { useState } from "react";
import { FillInDrawer, PickerTabs, type FillIn } from "@/components/TemplatePicker";
import {
  XOR_BASIS_OP_GROUPS,
  XOR_BASIS_TEMPLATES,
  type BitCard,
  type CardFn,
  type CardRow,
} from "@/lib/bit-operations";

// The Bit ops & Bitset tab: one card per kind of question, laid out in columns like the range query picker's op
// groups. A card lists its functions (call, cost, and whether it returns one number or a list); a mod switch on the card
// swaps in the mod versions. The XOR basis card is a small op selector that picks between the three bases. Clicking a
// function opens the code drawer.
export function BitOpsCards({ title, cards, publicBase }: { title: string; cards: BitCard[]; publicBase: string }) {
  const [open, setOpen] = useState<FillIn | null>(null);
  return (
    <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-16 font-[family-name:var(--font-dm-sans)]">
      <div className="sticky top-16 z-30 -mx-6 bg-background px-6 pt-2">
        <h1 className="sr-only">{title}</h1>
        <PickerTabs />
      </div>
      <div className="columns-1 gap-3 lg:columns-2 2xl:columns-3">
        {cards.map((c) => (
          <section key={c.id} className="mb-3 break-inside-avoid rounded-xl border border-border bg-card px-3 py-2.5">
            {c.kind === "bitset" ? (
              <>
                <CardHeading title={c.title} />
                <button
                  type="button"
                  onClick={() => setOpen(c.fillIn)}
                  className="rounded-md px-2 py-0.5 font-mono text-xs font-medium text-primary hover:bg-muted hover:underline"
                >
                  DynamicBitset
                </button>
              </>
            ) : c.kind === "xor-basis" ? (
              <XorBasisPicker title={c.title} note={c.note} onOpen={setOpen} />
            ) : (
              <RowsCard title={c.title} note={c.note} rows={c.rows} onOpen={setOpen} />
            )}
          </section>
        ))}
      </div>
      {open && <FillInDrawer key={open.file} catalog={{ publicBase }} fillIn={open} onClose={() => setOpen(null)} />}
    </main>
  );
}

function CardHeading({ title, note, children }: { title: string; note?: string; children?: React.ReactNode }) {
  return (
    <div className="mb-1.5 flex items-baseline justify-between gap-3">
      <h2 className="flex items-baseline gap-2 text-sm font-semibold text-foreground">
        {title}
        {note && <span className="text-[11px] font-normal text-muted-foreground">{note}</span>}
      </h2>
      {children}
    </div>
  );
}

function RowsCard({ title, note, rows, onOpen }: { title: string; note?: string; rows: CardRow[]; onOpen: (f: FillIn) => void }) {
  const [mod, setMod] = useState(false);
  const anyMod = rows.some((r) => r.mod);
  return (
    <>
      <CardHeading title={title} note={note}>
        {anyMod && (
          <label className="flex cursor-pointer items-center gap-1 text-[11px] text-muted-foreground" title="Show the versions that return the answer mod mod">
            <input type="checkbox" checked={mod} onChange={(e) => setMod(e.target.checked)} className="accent-primary" />
            mod
          </label>
        )}
      </CardHeading>
      <div className="-mx-2 grid grid-cols-[auto_auto_minmax(0,1fr)] items-baseline">
        {rows.map((row) => {
          const noMod = mod && !row.mod;
          const shown: CardFn = mod && row.mod ? row.mod : row;
          return (
            <button
              key={row.call}
              type="button"
              onClick={() => onOpen(shown.fillIn)}
              title={noMod ? "This one has no mod version" : undefined}
              className={`col-span-3 grid grid-cols-subgrid items-baseline gap-x-3 rounded-md px-2 py-0.5 text-left transition-colors hover:bg-muted ${noMod ? "opacity-40" : ""}`}
            >
              <span className="whitespace-nowrap font-mono text-xs font-medium text-primary">{shown.call}</span>
              <span className="whitespace-nowrap font-mono text-[11px] text-muted-foreground">{shown.cost}</span>
              <span className="min-w-0 text-[11px] leading-snug text-foreground">→ {shown.returns}</span>
            </button>
          );
        })}
      </div>
    </>
  );
}

// tick the ops you need; the lightest basis that has all of them is the pick (and any other that also fits)
function XorBasisPicker({ title, note, onOpen }: { title: string; note?: string; onOpen: (f: FillIn) => void }) {
  const [picked, setPicked] = useState<Set<string>>(new Set());
  const toggle = (id: string) =>
    setPicked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  const ids = [...picked];
  const fits = XOR_BASIS_TEMPLATES.filter((t) => ids.every((id) => id in t.costs));
  return (
    <>
      <CardHeading title={title} note={note}>
        {picked.size > 0 && (
          <button type="button" onClick={() => setPicked(new Set())} className="text-[11px] text-muted-foreground hover:text-foreground">
            Clear
          </button>
        )}
      </CardHeading>
      <div className="-mx-2 grid grid-cols-[auto_auto_minmax(0,1fr)]">
        {XOR_BASIS_OP_GROUPS.flatMap((group, k) => [
          <h3 key={group.title} className={`col-span-3 px-2 text-[10px] font-semibold uppercase tracking-wide text-muted-foreground ${k ? "mt-1.5" : ""}`}>
            {group.title}
          </h3>,
          ...group.ops.map((op) => {
            const on = picked.has(op.id);
            return (
              <button
                key={op.id}
                type="button"
                aria-pressed={on}
                onClick={() => toggle(op.id)}
                className={`col-span-3 grid grid-cols-subgrid items-baseline gap-x-2 rounded-md px-2 py-0.5 text-left transition-colors ${on ? "bg-primary/15" : "hover:bg-muted"}`}
              >
                <span
                  aria-hidden
                  className={`relative top-0.5 flex h-3.5 w-3.5 items-center justify-center self-start rounded-sm border text-[9px] leading-none ${on ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background"}`}
                >
                  {on ? "✓" : ""}
                </span>
                <span className={`whitespace-nowrap font-mono text-xs ${on ? "font-medium text-primary" : "text-foreground"}`}>{op.signature}</span>
                <span className="min-w-0 text-[11px] leading-snug text-muted-foreground">{op.does}</span>
              </button>
            );
          }),
        ])}
      </div>
      <div className="mt-2 border-t border-border pt-2">
        {fits.length === 0 ? (
          <p className="text-[11px] text-muted-foreground">
            No one basis does all of these: the subarray questions come from RangeXorBasis, which takes no updates.
          </p>
        ) : (
          <div className="flex flex-col gap-1.5">
            {(picked.size ? fits : XOR_BASIS_TEMPLATES).map((t, i) => (
              <div key={t.name} className="rounded-md border border-border px-2 py-1">
                <div className="flex items-baseline gap-2">
                  <button type="button" onClick={() => onOpen(t.fillIn)} className="font-mono text-xs font-medium text-primary hover:underline">
                    {t.name}
                  </button>
                  {picked.size > 0 && i === 0 && (
                    <span className="rounded bg-primary/15 px-1.5 py-0.5 text-[10px] font-medium text-primary">Best match</span>
                  )}
                  <span className="font-mono text-[11px] text-muted-foreground">build {t.build}</span>
                </div>
                {picked.size > 0 && (
                  <div className="mt-0.5 flex flex-wrap gap-x-3 gap-y-0.5 font-mono text-[11px] text-muted-foreground">
                    {ids.map((id) => (
                      <span key={id}>
                        {id} {t.costs[id]}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
