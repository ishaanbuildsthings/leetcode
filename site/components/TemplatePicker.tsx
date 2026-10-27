"use client";

import { useEffect, useMemo, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  costValue,
  formatCost,
  formatMemoryOf,
  memoryValue,
  TEMPLATE_LANG_LABELS,
  type MemoryBreakdown,
  type PickerOp,
  type PickerOpGroup,
  type PickerTemplate,
  type TemplateLang,
  type TierKind,
  type Usage,
} from "@/lib/template-picker";
import { readUsage } from "@/lib/template-usage";

// The picker pages, shown as tabs above each one.
const PICKER_PAGES = [
  { href: "/templates/range-queries", label: "Range queries" },
  { href: "/templates/sets", label: "Ordered sets (no indices)" },
];

function PickerTabs() {
  const pathname = usePathname();
  return (
    <nav
      className="mb-4 flex gap-1 border-b border-border text-sm font-medium"
      aria-label="Template pickers"
    >
      {PICKER_PAGES.map((p) => {
        const active = pathname === p.href;
        return (
          <Link
            key={p.href}
            href={p.href}
            aria-current={active ? "page" : undefined}
            className={`-mb-px border-b-2 px-3 py-2 transition-colors ${
              active
                ? "border-primary text-foreground"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {p.label}
          </Link>
        );
      })}
    </nav>
  );
}

// Everything a picker page decides for itself; the rest (op grid, matching, ranking, cards, code drawer with usage
// and memory) is shared.
export interface PickerCatalog<V extends PickerTemplate> {
  title: string;
  opGroups: PickerOpGroup[];
  // where the static copies live (fetched on click) and where the files are on GitHub
  publicBase: string;
  githubBase: string;
  // in production, fetch the code from here instead of publicBase (sets: raw GitHub, so the CDN doesn't carry thousands
  // of files); `next dev` always uses publicBase, the copies on disk, so it works offline
  remoteBase?: string;
  // data structure types, lightest constant factor first (a ranking tie-breaker)
  typeOrder: readonly string[];
  // a switch above the grid choosing which templates compete (range queries: sparse versions; sets: what you know)
  modes: {
    ariaLabel: string;
    storageKey: string;
    options: { mode: string; label: string; title: string }[];
    // the mode for a stored value (null: nothing stored)
    parse: (stored: string | null) => string;
    views: (mode: string) => V[];
  };
  // an optional checkbox next to the switch (sets: tuple values): when on, only templates passing keep compete and
  // the ops in disabledOps are greyed out and can't be picked
  flag?: {
    label: string;
    title: string;
    storageKey: string;
    keep: (t: V) => boolean;
    disabledOps: ReadonlySet<string>;
    disabledTitle: string;
  };
  // another file of a template (sets: FastSet without duplicates, built in O(U/64)): the drawer has a checkbox next
  // to build that switches to it, and a card whose selected ops it covers shows both builds
  variant?: {
    file: string;
    label: string;
    title: string;
    of: (t: V) => Partial<V> | undefined;
  };
  // a template may need a selected op before it is offered (range queries: mod-p templates)
  allowed?: (t: V, picked: string[]) => boolean;
  // show only each data structure type's best match (sets: thousands of variants would bury the other structures)
  onePerType?: boolean;
  kindLabel: (t: V) => string;
  memoryGroups: (t: V) => { id: "node" | "tags" | "other"; label: string }[];
  layoutLabel: (m: MemoryBreakdown) => string | null;
  // ops with nothing to read back (the usage panel calls them without binding a result)
  updateOps: ReadonlySet<string>;
  // usage panel: the variable name, notes per constructor argument name, comment lines before a constructor, a note
  // appended to a query's comment, and ops that return a pair to unpack
  varName: string;
  ctorNotes: Record<string, { py: string; cpp: string }>;
  ctorComments?: (t: V, lang: TemplateLang) => string[];
  queryNote?: (t: V, op: string) => string;
  pairResults?: Record<string, [string, string]>;
}

const opCost = (t: PickerTemplate, op: string) => t.complexities[op] ?? "?";

// A template file's URL, and its text fetched once per page: hovering a card starts the fetch, so the drawer usually
// opens on code that's already here. A failed fetch is forgotten, so the next open tries again.
function codeUrl(
  catalog: { publicBase: string; remoteBase?: string },
  folder: string,
  fileName: string,
) {
  const base =
    process.env.NODE_ENV !== "development" && catalog.remoteBase
      ? catalog.remoteBase
      : catalog.publicBase;
  return `${base}/${encodeURIComponent(folder)}/${fileName}`;
}
const texts = new Map<string, Promise<string>>();
function loadText(url: string): Promise<string> {
  let p = texts.get(url);
  if (!p) {
    p = fetch(url).then((res) =>
      res.ok ? res.text() : Promise.reject(res.status),
    );
    p.catch(() => texts.delete(url));
    texts.set(url, p);
  }
  return p;
}
// a cost without its amortized / expected / ? qualifiers: what a complexity cap compares
const baseCost = (cost: string) =>
  cost.replace(/ \?$/, "").replace(/ (amortized|expected)$/, "");
const withinCaps = (t: PickerTemplate, caps: Record<string, number>) =>
  Object.entries(caps).every(([op, cap]) => costValue(opCost(t, op)) <= cap);

// The cost levels the given matches offer for op (cheapest first): the choices of op's complexity cap
function capChoices(matches: { template: PickerTemplate }[], op: string) {
  const byValue = new Map<number, string>();
  for (const { template } of matches) {
    const cost = baseCost(opCost(template, op));
    byValue.set(costValue(cost), cost);
  }
  return [...byValue.entries()].sort((a, b) => a[0] - b[0]);
}
const tracked = (t: PickerTemplate) =>
  (t as { tracks?: string[] }).tracks?.length ?? 0;

// Templates covering every selected op, ranked by: slowest selected op, data structure type, total cost of selected
// ops, memory, then fewest extra ops. Type outranks total because amortized bounds on heavy structures (beats) hide
// large constants. Ops you didn't select don't count against a template.
function matchTemplates<V extends PickerTemplate>(
  catalog: PickerCatalog<V>,
  selected: Set<string>,
  mode: string,
  flagOn = false,
) {
  if (selected.size === 0) return [];
  const picked = [...selected];
  return catalog.modes
    .views(mode)
    .filter((t) => !flagOn || (catalog.flag?.keep(t) ?? true))
    .filter(
      (t) =>
        picked.every((op) => t.operations.includes(op)) &&
        (catalog.allowed?.(t, picked) ?? true),
    )
    .map((t) => {
      const costs = picked.map((op) => ({
        op,
        cost: opCost(t, op),
        value: costValue(opCost(t, op)),
      }));
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
      // worst selected op first, then all selected ops together, and only then the structure's constant factor
      (a, b) =>
        a.bottleneck.value - b.bottleneck.value ||
        a.total - b.total ||
        // then the variant that keeps less current on every update (sets: cached min / max, medians, mex)
        tracked(a.template) - tracked(b.template) ||
        catalog.typeOrder.indexOf(a.template.dataStructureType) -
          catalog.typeOrder.indexOf(b.template.dataStructureType) ||
        memoryValue(a.template.memory) - memoryValue(b.template.memory) ||
        a.extra.length - b.extra.length ||
        a.template.folder.localeCompare(b.template.folder) ||
        a.template.file.localeCompare(b.template.file),
    );
}

// "1 field" / "3 fields" / "none", for the drawer's memory lines.
function fieldCount(n: number): string {
  return n === 0 ? "none" : `${n} ${n === 1 ? "field" : "fields"}`;
}

function MemoryPanel<V extends PickerTemplate>({
  catalog,
  template,
  lang,
}: {
  catalog: PickerCatalog<V>;
  template: V;
  lang: TemplateLang;
}) {
  const { memory } = template;
  const layout = catalog.layoutLabel(memory);
  return (
    <div className="border-b border-border px-4 py-3 text-xs">
      <p className="mb-1.5 font-semibold text-foreground">
        Memory {formatMemoryOf(memory, memory.total)}
        {layout && (
          <span className="ml-2 font-normal text-muted-foreground">
            {layout}
          </span>
        )}
      </p>
      <div className="grid grid-cols-[auto_auto_1fr] gap-x-4 gap-y-1">
        {catalog.memoryGroups(template).map(({ id, label }) => {
          const { arrays, total } = memory[id];
          const uniform = arrays.every((a) => a.size === arrays[0].size);
          const count = arrays.length;
          return (
            <div key={id} className="contents">
              <span className="text-muted-foreground">
                {label}
                {count > 0 && id !== "other" && ` (${fieldCount(count)})`}
              </span>
              <span className="text-foreground">
                {count ? formatMemoryOf(memory, total) : "0"}
              </span>
              <span
                className={
                  count === 0 ? "text-muted-foreground" : "text-foreground"
                }
              >
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
        <p className="mt-1.5 text-muted-foreground">
          {memory.notes?.[lang] ?? memory.note}
        </p>
      )}
    </div>
  );
}

const LANG_STORAGE_KEY = "rangeQueryPicker.lang"; // shared by every picker: one preferred language

// Each picker's mode lives in localStorage so it survives reloads; useSyncExternalStore reads it without a server /
// client mismatch (the server renders the mode for "nothing stored").
const modeListeners = new Set<() => void>();
const subscribeMode = (onChange: () => void) => {
  modeListeners.add(onChange);
  return () => {
    modeListeners.delete(onChange);
  };
};
function readStored(key: string): string | null {
  try {
    return window.localStorage.getItem(key);
  } catch {
    return null;
  }
}
function writeStored(key: string, value: string) {
  try {
    window.localStorage.setItem(key, value);
  } catch {}
  modeListeners.forEach((notify) => notify());
}

function readPreferredLang(): TemplateLang {
  return readStored(LANG_STORAGE_KEY) === "cpp" ? "cpp" : "py";
}

function CodeDrawer<V extends PickerTemplate>({
  catalog,
  template: base,
  selected,
  onClose,
}: {
  catalog: PickerCatalog<V>;
  template: V;
  selected: Set<string>;
  onClose: () => void;
}) {
  const variant = catalog.variant?.of(base);
  const [useVariant, setUseVariant] = useState(false);
  const template = (
    useVariant && variant
      ? { ...base, ...variant, file: catalog.variant!.file }
      : base
  ) as V;
  const [preferred, setPreferred] = useState<TemplateLang>(readPreferredLang);
  const lang = template.langs.includes(preferred)
    ? preferred
    : template.langs[0];
  const [loaded, setLoaded] = useState<{
    key: string;
    code: string | null;
    failed: boolean;
  } | null>(null);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);
  const fileName = `${template.file}.${lang}`;
  const path = `${template.folder}/${fileName}`;
  const code = loaded?.key === path ? loaded.code : null;
  const failed = loaded?.key === path && loaded.failed;
  const copied = copiedKey === path;
  // (sets) no usage in the catalog: read it from the code, like the build script does
  const usage = useMemo(
    () =>
      template.usage?.[lang] ??
      (code === null
        ? undefined
        : (readUsage(code, lang, template.operations) ?? undefined)),
    [template.usage, template.operations, code, lang],
  );
  const url = codeUrl(catalog, template.folder, fileName);

  useEffect(() => {
    let cancelled = false;
    loadText(url)
      .then(
        (text) =>
          !cancelled && setLoaded({ key: path, code: text, failed: false }),
      )
      .catch(
        () => !cancelled && setLoaded({ key: path, code: null, failed: true }),
      );
    return () => {
      cancelled = true;
    };
  }, [url, path]);

  const chooseLang = (l: TemplateLang) => {
    setPreferred(l);
    writeStored(LANG_STORAGE_KEY, l);
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
      <button
        type="button"
        aria-label="Close"
        onClick={onClose}
        className="absolute inset-0 bg-foreground/20"
      />
      <div className="relative flex h-full w-[min(900px,94vw)] flex-col border-l border-border bg-background shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-border p-4">
          <div className="min-w-0">
            <p className="text-sm font-semibold text-foreground">
              {catalog.kindLabel(template)}
            </p>
            <p className="mt-1 break-all font-mono text-xs text-muted-foreground">
              {template.folder}
            </p>
          </div>
          <div className="flex flex-shrink-0 items-center gap-2">
            <div
              className="flex overflow-hidden rounded-md border border-border text-xs"
              role="group"
              aria-label="Language"
            >
              {(["py", "cpp"] as const).map((l) => {
                const available = template.langs.includes(l);
                return (
                  <button
                    key={l}
                    type="button"
                    disabled={!available}
                    aria-pressed={lang === l}
                    onClick={() => chooseLang(l)}
                    title={
                      available
                        ? undefined
                        : `No ${TEMPLATE_LANG_LABELS[l]} version yet`
                    }
                    className={`px-2.5 py-1 ${
                      lang === l
                        ? "bg-primary text-primary-foreground"
                        : "text-foreground hover:bg-muted"
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
              href={`${catalog.githubBase}${encodeURIComponent(template.folder)}/${fileName}`}
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
        {/* everything under the header scrolls together: a template with many ops can fill the drawer before the code */}
        <div className="min-h-0 flex-1 overflow-y-auto">
          <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5 border-b border-border px-4 py-3 text-xs">
            {/* the selected ops, then build (always paid, so always highlighted), then the rest */}
            {[
              ...template.operations
                .filter((op) => selected.has(op))
                .map((op) => [op, opCost(template, op), true] as const),
              ["build", template.build, true] as const,
              ...template.operations
                .filter((op) => !selected.has(op))
                .map((op) => [op, opCost(template, op), false] as const),
            ].map(([op, cost, on]) => (
              <div key={op} className="contents">
                <span
                  className={`font-mono ${on ? "font-medium text-primary" : "text-muted-foreground"}`}
                >
                  {op}
                </span>
                <span
                  className={on ? "text-foreground" : "text-muted-foreground"}
                >
                  {formatCost(cost)}
                  {op === "build" && variant && (
                    <label
                      title={catalog.variant!.title}
                      className="ml-3 inline-flex cursor-pointer items-center gap-1.5 text-muted-foreground hover:text-foreground"
                    >
                      <input
                        type="checkbox"
                        checked={useVariant}
                        onChange={(e) => setUseVariant(e.target.checked)}
                        className="accent-primary"
                      />
                      {catalog.variant!.label}
                    </label>
                  )}
                </span>
              </div>
            ))}
          </div>
          <UsagePanel
            catalog={catalog}
            template={template}
            usage={usage}
            selected={selected}
            lang={lang}
          />
          <MemoryPanel catalog={catalog} template={template} lang={lang} />
          <pre className="overflow-x-auto bg-card p-4 font-mono text-xs leading-relaxed text-foreground">
            {failed ? "Couldn't load this template." : (code ?? "Loading…")}
          </pre>
        </div>
      </div>
    </div>
  );
}

// "Usage": construct, then one block per selected op. Every statement has its comment on the lines above it.
function UsagePanel<V extends PickerTemplate>({
  catalog,
  template,
  usage,
  selected,
  lang,
}: {
  catalog: PickerCatalog<V>;
  template: V;
  usage: Usage | undefined;
  selected: Set<string>;
  lang: TemplateLang;
}) {
  if (!usage) return null;
  const ops = template.operations.filter((op) => selected.has(op));
  const shown = ops.length ? ops : template.operations;
  const cpp = lang === "cpp";
  const cm = cpp ? "//" : "#";
  const notes = catalog.ctorNotes;
  const neededClasses = [
    ...new Set(shown.map((op) => usage.methods[op]!.cls)),
  ].sort((a, b) => a - b);
  const varOf = (k: number) =>
    neededClasses.length === 1
      ? catalog.varName
      : usage.classes[k].className[0].toLowerCase() +
        usage.classes[k].className.slice(1);
  const typeOf = (ret = "") =>
    ret.replace(/\bT\b/g, "long long").replace(/\bS\b/g, "long long");

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
        comments: [
          `Between test cases: frees every ${cls.className}<long long> (they all share one node pool).`,
        ],
        code: `${cls.className}<long long>::resetPool();`,
      });
    const comments = [
      ...(catalog.ctorComments?.(template, lang) ?? []),
      ...required.flatMap((n) =>
        notes[n] && !["mod", "bits"].includes(n) ? [notes[n][lang]] : [],
      ),
      ...optional.map(
        (p) =>
          `Optional: ${p.name} (default ${p.default})${notes[p.name] ? `, ${notes[p.name][lang]}` : ""}.`,
      ),
      ...(cpp
        ? [
            deducible
              ? "T is deduced from the vector (vector<long long> gives T = long long)."
              : "T = long long (int works too).",
          ]
        : []),
    ];
    const type = `${cls.className}${deducible ? "" : "<long long>"}`;
    blocks.push({
      comments,
      // (no arguments: "Name<long long> x;", since "x()" would declare a function)
      code: cpp
        ? `${type} ${varOf(k)}${required.length ? `(${required.join(", ")})` : ""};`
        : `${varOf(k)} = ${cls.className}(${required.join(", ")})`,
    });
  }
  for (const op of shown) {
    const m = usage.methods[op]!;
    const call = `${varOf(m.cls)}.${op}(${m.params.join(", ")})`;
    const pair = catalog.pairResults?.[op];
    let code: string;
    if (catalog.updateOps.has(op)) code = cpp ? `${call};` : call;
    else if (pair)
      code = cpp
        ? `auto [${pair.join(", ")}] = ${call};`
        : `${pair.join(", ")} = ${call}`;
    else
      code = cpp
        ? `${typeOf(m.returns) || "auto"} ${op} = ${call};`
        : `${op} = ${call}`;
    const doc = [
      m.doc,
      catalog.updateOps.has(op)
        ? ""
        : (catalog.queryNote?.(template, op) ?? ""),
    ]
      .filter(Boolean)
      .join("; ");
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

const opName = (op: PickerOp) => op.signature.split("(")[0];
const opArgs = (op: PickerOp) => op.signature.slice(opName(op).length);

const TIER_STYLES: Record<TierKind, { label: string; badge: string }> = {
  common: {
    label: "Common",
    badge: "border-stone-300 bg-stone-100 text-stone-600",
  },
  uncommon: {
    label: "Uncommon",
    badge: "border-emerald-200 bg-emerald-50 text-emerald-700",
  },
  rare: { label: "Rare", badge: "border-amber-200 bg-amber-50 text-amber-700" },
  mod: { label: "Mod p", badge: "border-sky-200 bg-sky-50 text-sky-700" },
  bitOps: {
    label: "Bit ops",
    badge: "border-violet-200 bg-violet-50 text-violet-700",
  },
  topic: { label: "", badge: "border-stone-200 bg-white text-stone-500" },
};

function TierBadge({
  kind,
  label: labelOverride,
}: {
  kind: TierKind;
  label?: string;
}) {
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

export function TemplatePicker<V extends PickerTemplate>({
  catalog,
}: {
  catalog: PickerCatalog<V>;
}) {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  // per selected op, the most it may cost (a cost value); templates over any cap are left out
  const [caps, setCaps] = useState<Record<string, number>>({});
  const [openTemplate, setOpenTemplate] = useState<V | null>(null);
  const { modes } = catalog;
  const mode = useSyncExternalStore(
    subscribeMode,
    () => modes.parse(readStored(modes.storageKey)),
    () => modes.parse(null),
  );
  const { flag } = catalog;
  const flagOn = useSyncExternalStore(
    subscribeMode,
    () => !!flag && readStored(flag.storageKey) === "1",
    () => false,
  );
  const isDisabled = (id: string) => flagOn && !!flag?.disabledOps.has(id);

  const toggle = (id: string) => {
    if (isDisabled(id)) return;
    if (selected.has(id)) setCap(id, null);
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const allOps = catalog.opGroups.flatMap((g) => g.tiers.flatMap((t) => t.ops));
  // ops the checkbox disabled stay remembered but drop out of the selection while it is on
  const active = new Set([...selected].filter((id) => !isDisabled(id)));
  const selectedOps = allOps.filter((op) => active.has(op.id));
  const activeCaps = Object.fromEntries(
    Object.entries(caps).filter(([op]) => active.has(op)),
  );
  const uncapped = matchTemplates(catalog, active, mode, flagOn);
  const capped = uncapped.filter((m) => withinCaps(m.template, activeCaps));
  // matches come best first, so a type's first is its best; the rest of that type are only counted
  const others = new Map<string, number>();
  const matches = catalog.onePerType
    ? capped.filter(({ template: { dataStructureType: type } }) => {
        const seen = others.has(type);
        others.set(type, (others.get(type) ?? -1) + 1);
        return !seen;
      })
    : capped;
  // an op's choices come from the templates the other ops' caps allow, so every choice changes the result
  const choicesFor = (op: string) =>
    capChoices(
      uncapped.filter((m) =>
        withinCaps(
          m.template,
          Object.fromEntries(
            Object.entries(activeCaps).filter(([o]) => o !== op),
          ),
        ),
      ),
      op,
    );
  const setCap = (op: string, cap: number | null) =>
    setCaps((prev) => {
      const next = { ...prev };
      if (cap === null) delete next[op];
      else next[op] = cap;
      return next;
    });

  return (
    <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-24 font-[family-name:var(--font-dm-sans)]">
      <PickerTabs />
      <header className="mb-6 flex items-center justify-between gap-4">
        <h1 className="font-[family-name:var(--font-playfair)] text-3xl font-bold text-foreground">
          {catalog.title}
        </h1>
        <div className="flex items-center gap-2">
          {flag && (
            <label
              title={flag.title}
              className="flex cursor-pointer items-center gap-1.5 rounded-md border border-border px-3 py-1.5 text-xs font-medium text-foreground hover:bg-muted"
            >
              <input
                type="checkbox"
                checked={flagOn}
                onChange={(e) =>
                  writeStored(flag.storageKey, e.target.checked ? "1" : "0")
                }
                className="accent-primary"
              />
              {flag.label}
            </label>
          )}
          <div
            className="flex overflow-hidden rounded-md border border-border text-xs font-medium"
            role="radiogroup"
            aria-label={modes.ariaLabel}
          >
            {modes.options.map((o) => (
              <button
                key={o.mode}
                type="button"
                role="radio"
                aria-checked={mode === o.mode}
                title={o.title}
                onClick={() => writeStored(modes.storageKey, o.mode)}
                className={`px-3 py-1.5 transition-colors ${
                  mode === o.mode
                    ? "bg-primary text-primary-foreground"
                    : "text-foreground hover:bg-muted"
                }`}
              >
                {o.label}
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
          {catalog.opGroups.map((group) => (
            <section
              key={group.id}
              className="mb-4 break-inside-avoid rounded-xl border border-border bg-card p-4"
            >
              <div className="mb-2.5 flex items-baseline justify-between gap-3">
                <h2 className="text-sm font-semibold text-foreground">
                  {group.title}
                </h2>
                {group.blurb && (
                  <span className="text-xs text-muted-foreground">
                    {group.blurb}
                  </span>
                )}
              </div>
              <div className="-mx-2 grid grid-cols-[auto_auto_minmax(0,1fr)]">
                {group.tiers.flatMap((tier, tierIdx) => [
                  // a "topic" tier with no label is just the group's list: no header
                  tier.kind === "topic" && !tier.label ? null : (
                    <h3
                      key={tier.label ?? tier.kind}
                      className={`col-span-3 flex items-center gap-2 px-2 pb-1 ${tierIdx === 0 ? "" : "mt-3"}`}
                    >
                      <TierBadge kind={tier.kind} label={tier.label} />
                      <span
                        aria-hidden
                        className="h-px flex-1 bg-gradient-to-r from-border to-transparent"
                      />
                    </h3>
                  ),
                  ...tier.ops.map((op) => {
                    const off = isDisabled(op.id);
                    const isOn = active.has(op.id);
                    return (
                      <button
                        key={op.id}
                        type="button"
                        aria-pressed={isOn}
                        disabled={off}
                        onClick={() => toggle(op.id)}
                        title={off ? flag?.disabledTitle : op.signature}
                        className={`col-span-3 grid grid-cols-subgrid items-baseline gap-x-3 rounded-md px-2 py-1 text-left transition-colors ${
                          off
                            ? "cursor-not-allowed opacity-35"
                            : isOn
                              ? "bg-primary/15"
                              : "hover:bg-muted"
                        }`}
                      >
                        <span
                          aria-hidden
                          className={`relative top-0.5 flex h-3.5 w-3.5 items-center justify-center self-start rounded-sm border text-[9px] leading-none ${
                            isOn
                              ? "border-primary bg-primary text-primary-foreground"
                              : "border-border bg-background"
                          }`}
                        >
                          {isOn ? "✓" : ""}
                        </span>
                        <span
                          className={`whitespace-nowrap font-mono text-[13px] ${isOn ? "font-medium text-primary" : "text-foreground"}`}
                        >
                          {opName(op)}
                          <span className="font-normal text-muted-foreground">
                            {opArgs(op)}
                          </span>
                        </span>
                        <span className="min-w-0 text-xs text-muted-foreground">
                          {op.description}
                        </span>
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
                  <span className="ml-1.5 font-normal text-muted-foreground">
                    {selectedOps.length}
                  </span>
                )}
              </h2>
              {selectedOps.length > 0 && (
                <button
                  type="button"
                  onClick={() => {
                    setSelected(new Set());
                    setCaps({});
                  }}
                  className="text-xs text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
                >
                  Clear
                </button>
              )}
            </div>

            {selectedOps.length === 0 ? (
              <p className="text-xs text-muted-foreground">
                Nothing picked yet.
              </p>
            ) : (
              <ul className="space-y-1.5">
                {selectedOps.map((op) => {
                  const cap = activeCaps[op.id];
                  let choices = choicesFor(op.id);
                  // (a cap the other caps have since ruled out stays listed, so the dropdown still shows it)
                  if (cap !== undefined && !choices.some(([v]) => v === cap))
                    choices = [
                      ...choices,
                      capChoices(uncapped, op.id).find(([v]) => v === cap) ?? [
                        cap,
                        "?",
                      ],
                    ].sort((a, b) => a[0] - b[0]);
                  return (
                    <li
                      key={op.id}
                      className="flex items-center justify-between gap-2"
                    >
                      <code className="min-w-0 flex-1 truncate font-mono text-xs text-foreground">
                        {op.signature}
                      </code>
                      {(choices.length > 1 || op.id in activeCaps) && (
                        <select
                          value={activeCaps[op.id] ?? ""}
                          onChange={(e) =>
                            setCap(
                              op.id,
                              e.target.value === ""
                                ? null
                                : Number(e.target.value),
                            )
                          }
                          aria-label={`Most ${opName(op)} may cost`}
                          className={`flex-shrink-0 rounded border border-border bg-background px-1 py-0.5 font-mono text-[11px] ${
                            op.id in activeCaps
                              ? "text-foreground"
                              : "text-muted-foreground"
                          }`}
                        >
                          <option value="">any cost</option>
                          {choices.map(([value, cost]) => (
                            <option key={value} value={value}>
                              ≤ {formatCost(cost)}
                            </option>
                          ))}
                        </select>
                      )}
                      <button
                        type="button"
                        onClick={() => toggle(op.id)}
                        aria-label={`Remove ${opName(op)}`}
                        className="flex-shrink-0 text-sm leading-none text-muted-foreground hover:text-foreground"
                      >
                        ×
                      </button>
                    </li>
                  );
                })}
              </ul>
            )}

            <div className="mt-4 border-t border-border pt-3">
              <h2 className="text-sm font-semibold text-foreground">
                Templates
                {matches.length > 0 && (
                  <span className="ml-1.5 font-normal text-muted-foreground">
                    {matches.length}
                    {capped.length > matches.length &&
                      ` (best of ${capped.length} variants)`}
                  </span>
                )}
              </h2>
              {selected.size === 0 ? (
                <p className="mt-1 text-xs text-muted-foreground">
                  Pick operations to see templates that cover them.
                </p>
              ) : matches.length === 0 ? (
                <p className="mt-1 text-xs text-muted-foreground">
                  No template covers this selection yet.
                </p>
              ) : (
                <ul className="mt-2 space-y-1.5">
                  {matches.map(({ template, extra, costs }, i) => {
                    const layout = catalog.layoutLabel(template.memory);
                    return (
                      <li key={`${template.folder}/${template.file}`}>
                        <button
                          type="button"
                          onClick={() => setOpenTemplate(template)}
                          // start fetching its code (in the language the drawer will show) before the click
                          onMouseEnter={() => {
                            const pref = readPreferredLang();
                            const l = template.langs.includes(pref)
                              ? pref
                              : template.langs[0];
                            loadText(
                              codeUrl(
                                catalog,
                                template.folder,
                                `${template.file}.${l}`,
                              ),
                            ).catch(() => {});
                          }}
                          className="w-full rounded-lg border border-border bg-background p-2 text-left transition-colors hover:border-primary/50"
                        >
                          <span className="flex items-center justify-between gap-2">
                            <span className="text-xs font-medium text-foreground">
                              {catalog.kindLabel(template)}
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
                                <span className="font-mono text-muted-foreground">
                                  {c.op}
                                </span>
                                <span className="text-foreground">
                                  {formatCost(c.cost)}
                                </span>
                              </span>
                            ))}
                            <span className="font-mono text-muted-foreground">
                              build
                            </span>
                            <span className="text-foreground">
                              {formatCost(template.build)}
                              {(() => {
                                const alt = catalog.variant?.of(template);
                                return alt?.build &&
                                  [...active].every((op) =>
                                    alt.operations?.includes(op),
                                  )
                                  ? ` / ${formatCost(alt.build)}`
                                  : "";
                              })()}
                            </span>
                          </span>
                          <span className="mt-1.5 block text-[11px] leading-snug text-muted-foreground">
                            <span className="block">
                              Memory{" "}
                              <span className="text-foreground">
                                {formatMemoryOf(
                                  template.memory,
                                  template.memory.total,
                                )}
                              </span>
                              {layout && ` (${layout})`}
                            </span>
                            {catalog
                              .memoryGroups(template)
                              .map(({ id, label }) => (
                                <span key={id} className="block pl-3">
                                  {label} —{" "}
                                  {template.memory[id].arrays
                                    .map((a) => a.name)
                                    .join(", ") || "none"}
                                </span>
                              ))}
                          </span>
                          {extra.length > 0 && (
                            <span className="mt-1.5 block text-[11px] leading-snug text-muted-foreground">
                              Also supports: {extra.join(", ")}
                            </span>
                          )}
                          {(others.get(template.dataStructureType) ?? 0) >
                            0 && (
                            <span className="mt-1.5 block text-[11px] leading-snug text-muted-foreground">
                              {others.get(template.dataStructureType)} heavier{" "}
                              {others.get(template.dataStructureType) === 1
                                ? "variant"
                                : "variants"}{" "}
                              of this structure also match (they keep more
                              current, or cost more)
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
          catalog={catalog}
          template={openTemplate}
          selected={selected}
          onClose={() => setOpenTemplate(null)}
        />
      )}
    </main>
  );
}
