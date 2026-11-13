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
        {cards.map((c) =>
          c.kind === "bitset" ? (
            // the whole card opens the bitset
            <button
              key={c.id}
              type="button"
              onClick={() => setOpen(c.fillIn)}
              className="group mb-3 block w-full break-inside-avoid rounded-xl border border-border bg-card px-3 py-2.5 text-left transition-colors hover:border-primary/40 hover:bg-muted/60"
            >
              <span className="mb-1.5 block text-sm font-semibold text-foreground">{c.title}</span>
              <span className="block px-2 py-0.5 font-mono text-xs font-medium text-primary group-hover:underline">DynamicBitset</span>
            </button>
          ) : (
            <section key={c.id} className="mb-3 break-inside-avoid rounded-xl border border-border bg-card px-3 py-2.5">
              {c.kind === "xor-basis" ? (
                <XorBasisPicker title={c.title} note={c.note} onOpen={setOpen} />
              ) : (
                <RowsCard title={c.title} note={c.note} rows={c.rows} onOpen={setOpen} />
              )}
            </section>
          ),
        )}
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

// Same look as the Eertree picker: one row per op (method -> what it returns, what it does underneath), then the
// template cards. The bases are listed lightest first and each one does everything the ones after it do at the same
// cost or cheaper, so once something is ticked the first basis that has all of it is the only card.
function XorBasisPicker({ title, onOpen }: { title: string; note?: string; onOpen: (f: FillIn) => void }) {
  const [picked, setPicked] = useState<ReadonlySet<string>>(() => new Set());
  const toggle = (id: string) =>
    setPicked((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  const ids = XOR_BASIS_OP_GROUPS.flatMap((g) => g.ops.map((op) => op.id)).filter((id) => picked.has(id));
  const fits = XOR_BASIS_TEMPLATES.filter((t) => ids.every((id) => id in t.costs));
  const shown = picked.size ? fits.slice(0, 1) : XOR_BASIS_TEMPLATES;
  const signature = (id: string) =>
    XOR_BASIS_OP_GROUPS.flatMap((g) => g.ops).find((op) => op.id === id)?.signature ?? id;
  const heading = (text: string, first = false) => (
    <div className={`mb-1 text-[11px] font-semibold uppercase tracking-wide text-muted-foreground ${first ? "" : "mt-3"}`}>{text}</div>
  );
  return (
    <div className="text-xs">
      <div className="mb-2 text-sm font-semibold text-foreground">{title}</div>
      {XOR_BASIS_OP_GROUPS.map((group, k) => (
        <div key={group.title}>
          {heading(group.title, k === 0)}
          <div className="flex flex-col">
            {group.ops.map((op) => {
              const on = picked.has(op.id);
              return (
                <button
                  key={op.id}
                  type="button"
                  aria-pressed={on}
                  onClick={() => toggle(op.id)}
                  className={`grid grid-cols-[auto_1fr] items-start gap-x-2 rounded px-1.5 py-1 text-left ${on ? "bg-primary/15" : "hover:bg-muted"}`}
                >
                  <span
                    aria-hidden
                    className={`relative top-0.5 flex h-3.5 w-3.5 items-center justify-center self-start rounded-sm border text-[9px] leading-none ${
                      on ? "border-primary bg-primary text-primary-foreground" : "border-border bg-background"
                    }`}
                  >
                    {on ? "✓" : ""}
                  </span>
                  <span className="min-w-0">
                    <span className="block break-words font-mono text-xs">
                      <span className={on ? "font-medium text-primary" : "text-foreground"}>{op.signature}</span>
                      <span className="text-muted-foreground"> -&gt; {op.returns}</span>
                    </span>
                    <span className="block text-[11px] leading-snug text-muted-foreground">{op.does}</span>
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      ))}
      {heading(shown.length === 1 ? "Template" : "Templates")}
      {shown.length === 0 ? (
        <p className="text-muted-foreground">
          No one basis does all of these: the subarray questions come from RangeXorBasis, which takes no updates.
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {shown.map((t) => (
            <button
              key={t.name}
              type="button"
              onClick={() => onOpen(t.fillIn)}
              className="group rounded-lg border border-primary/40 bg-primary/5 p-3 text-left shadow-sm transition-colors hover:border-primary hover:bg-primary/10"
            >
              <span className="mb-1.5 flex items-center justify-between gap-6">
                <span className="text-sm font-medium text-foreground">{t.name}</span>
                <span className="text-xs font-medium text-primary group-hover:underline">Open code →</span>
              </span>
              <span className="grid grid-cols-[auto_auto] justify-start gap-x-4 gap-y-0.5">
                <span className="font-mono text-primary">{t.name}(arr)</span>
                <span className="text-foreground">{t.build}</span>
                {ids.map((id) => (
                  <span key={id} className="contents">
                    <span className="break-all font-mono text-primary">{signature(id)}</span>
                    <span className="text-foreground">{t.costs[id]}</span>
                  </span>
                ))}
              </span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
