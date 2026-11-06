"use client";

import {
  useEffect,
  useMemo,
  useRef,
  useState,
  useSyncExternalStore,
} from "react";
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
  { href: "/templates/sets", label: "Sets" },
  { href: "/templates/misc", label: "Misc." },
  { href: "/templates/golden-references", label: "Golden References" },
];

// the picker tabs, with the page's controls (children) at the right end of the same row
function PickerTabs({ children }: { children?: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <nav
      className="mb-4 flex items-center gap-1 border-b border-border text-sm font-medium"
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
      {children && (
        <div className="ml-auto flex items-center gap-2 pb-1">{children}</div>
      )}
    </nav>
  );
}

// What the Fast mode panel says.
export type FastInfo = { how: string; drawbacks: string[]; noSanitize: { text: string; code?: string }[] };

// A template you fill in yourself (the generic seg trees): the file is at publicBase/<folder>/<file>.<lang>, and on
// GitHub at githubUrl + <file>.<lang>. ops: every op with its cost, in the catalog's cost format ("log(N) expected");
// note: a line under them. title: the description on its Misc tab card.
export type FillIn = {
  label: string;
  title: string;
  folder: string;
  file: string;
  githubUrl: string;
  ops: [string, string][];
  note?: string;
  // the languages it comes in (both if left out): the drawer offers only these
  langs?: TemplateLang[];
  // the C++ file comes in three example levels (file.simple.cpp, file.cpp, file.complex.cpp): a selector picks one
  cppLevels?: boolean;
  // there's a version without rangeReverse (file[.level].norev.*): a checkbox, off by default, adds it back
  reverseToggle?: boolean;
  // there's a recursive version that prints the tree after every operation (file[.level].debug.*): a version option
  debugToggle?: boolean;
  // there's a C++ fast version (file[.level][.norev].fast.cpp): a version option, and what its panel says
  fast?: FastInfo;
  // another version behind a checkbox, on the card and by the ops in its drawer (off by default, remembered): its
  // label, hover text, where it's remembered, and what changes while it's ticked (e.g. the in-place next permutation)
  variant?: { label: string; title: string; storageKey: string; on: Partial<Pick<FillIn, "label" | "file" | "ops">> };
};

// a section of a templates tab without a picker
export type MiscSection = { title: string; items: FillIn[] };

// a remembered checkbox, the same everywhere it shows (writeStored tells every subscriber)
function useStoredFlag(key: string): [boolean, (on: boolean) => void] {
  const on = useSyncExternalStore(subscribeMode, () => !!key && readStored(key) === "1", () => false);
  return [on, (v: boolean) => writeStored(key, v ? "1" : "0")];
}

const withVariant = (f: FillIn, on: boolean): FillIn => (on && f.variant ? { ...f, ...f.variant.on } : f);

const REVERSE_STORAGE_KEY = "templatePicker.withReverse";

// the C++ example levels of a fill-in template, and the file each one is (basic is the plain file)
const CPP_LEVELS = [
  { id: "simple", label: "Simple types", title: "Plain types, no structs: e.g. using Node = long long; (a max)", suffix: ".simple" },
  { id: "basic", label: "Basic struct", title: "A struct with int fields, e.g. tot and mn", suffix: "" },
  { id: "complex", label: "Complex struct", title: "A struct holding an array (letter counts), = {} so it starts at 0, loops in combine", suffix: ".complex" },
] as const;
type CppLevel = (typeof CPP_LEVELS)[number]["id"];
const CPP_LEVEL_STORAGE_KEY = "templatePicker.cppLevel";
const readCppLevel = (): CppLevel => {
  const v = readStored(CPP_LEVEL_STORAGE_KEY);
  return CPP_LEVELS.some((l) => l.id === v) ? (v as CppLevel) : "basic";
};

// which version of a fill-in template to show; a template offers the ones it has (Python has no fast version)
const GENERIC_VERSIONS = [
  { id: "default", label: "Default", title: "The normal version" },
  { id: "debug", label: "Debug (recursive)", title: "A recursive version you can read and change, which prints the tree after every operation" },
  { id: "fast", label: "Fast", title: "C++ only. Sanitizers are skipped here and in what you fill in, so a bad access there goes unreported" },
] as const;
type GenericVersion = (typeof GENERIC_VERSIONS)[number]["id"];
const GENERIC_VERSION_STORAGE_KEY = "templatePicker.genericVersion";
const readGenericVersion = (): GenericVersion => {
  const v = readStored(GENERIC_VERSION_STORAGE_KEY);
  return GENERIC_VERSIONS.some((g) => g.id === v) ? (v as GenericVersion) : "default";
};

// Everything a picker page decides for itself; the rest (op grid, matching, ranking, cards, code drawer with usage
// and memory) is shared.
export type CtorNote = { py: string; cpp: string; inCall?: boolean };

export interface PickerCatalog<V extends PickerTemplate> {
  title: string;
  opGroups: PickerOpGroup[];
  // a short "still to add" list shown under the op columns
  planned?: string[];
  // templates outside the op grid that you fill in yourself (range queries: the generic seg trees), one button each
  // in the toolbar: the file is at publicBase/<folder>/<file>.<lang>, and on GitHub at githubUrl + <file>.<lang>
  fillIns?: FillIn[];
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
    // (optional) what a template becomes while the box is ticked (range queries: its letters version), null = left out
    view?: (t: V) => V | null;
    disabledOps: ReadonlySet<string>;
    disabledTitle: string;
    // (optional) while the box is ticked: how operation text reads, and what T is in the usage lines
    rename?: (text: string, lang?: TemplateLang) => string;
    elem?: string;
  };
  // another file of a template (sets: FastSet without duplicates, built in O(U/64)): the drawer has a checkbox next
  // to build that switches to it, and a card whose selected ops it covers shows both builds
  variant?: {
    file: string;
    label: string;
    title: string;
    of: (t: V) => Partial<V> | undefined;
  };
  // a harder-tuned second file of a template (sets: fast.cpp): the drawer has a toggle that switches to it, and
  // explain fills the panel shown while it's on
  fastMode?: {
    label: string;
    explain: (t: V) => FastInfo;
    title: string;
    has: (t: V) => boolean;
  };
  // a template may need a selected op before it is offered (range queries: mod-p templates)
  allowed?: (t: V, picked: string[]) => boolean;
  // per data structure type, show only variants that are a real trade-off, at most this many (sets: thousands of
  // variants would bury the other structures): one is left out only when a shown one of its type is no worse in every
  // way (see beats), the same rule the catalog checks use to call a template dominated
  perType?: number;
  // what else a shown template s must match to make template m pointless, beyond the selected ops' costs, memory and
  // build (range queries: needing every value up front, sparse indices; sets: values, key types, cached extras)
  noWorse?: (s: V, m: V) => boolean;
  kindLabel: (t: V) => string;
  memoryGroups: (t: V) => { id: "node" | "tags" | "other"; label: string }[];
  layoutLabel: (m: MemoryBreakdown) => string | null;
  // ops with nothing to read back (the usage panel calls them without binding a result)
  updateOps: ReadonlySet<string>;
  // usage panel: the variable name, notes per constructor argument name, comment lines before a constructor, a note
  // appended to a query's comment, and ops that return a pair to unpack
  varName: string;
  // per constructor argument name; a function when they depend on the template (range queries: letters versions)
  // inCall: an optional argument shown in the example call anyway (e.g. the initial array), with "leave it out" in its note
  ctorNotes: Record<string, CtorNote> | ((t: V) => Record<string, CtorNote>);
  ctorComments?: (t: V, lang: TemplateLang) => string[];
  queryNote?: (t: V, op: string) => string;
  // ops whose result is shown with names in the usage lines, update ops included (cut -> piece; split -> left, right)
  pairResults?: Record<string, string[]>;
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
// how sure a bound is: worst case beats amortized and expected, which don't compare (and "?" is weaker still)
const guarantee = (cost: string) =>
  `${/ amortized/.test(cost) ? "amortized" : / expected/.test(cost) ? "expected" : "worst"}${cost.endsWith(" ?") ? "?" : ""}`;
const noWeaker = (s: string, m: string) => {
  const a = guarantee(s), b = guarantee(m);
  return a === b || a === "worst" || (a.startsWith("worst") && b.endsWith("?"));
};
const withinCaps = (t: PickerTemplate, caps: Record<string, number>) =>
  Object.entries(caps).every(([op, cap]) => costValue(opCost(t, op)) <= cap);

// The cost levels the given matches offer for op (cheapest first): the choices of op's complexity cap
function capChoices(matches: { template: PickerTemplate }[], op: string) {
  // O(1) is always offered, even when nothing reaches it (picking it then shows that no template does)
  const byValue = new Map<number, string>([[costValue("1"), "1"]]);
  for (const { template } of matches) {
    const cost = baseCost(opCost(template, op));
    byValue.set(costValue(cost), cost);
  }
  return [...byValue.entries()].sort((a, b) => a[0] - b[0]);
}
const tracked = (t: PickerTemplate) =>
  (t as { tracks?: string[] }).tracks?.length ?? 0;

// Templates covering every selected op, ranked by: slowest selected op, total cost of selected ops, fewest amortized /
// expected bounds, fewest cached extras, data structure type, memory, then fewest extra ops. Ops you didn't select
// don't count against a template.
function matchTemplates<V extends PickerTemplate>(
  catalog: PickerCatalog<V>,
  selected: Set<string>,
  mode: string,
  flagOn = false,
) {
  if (selected.size === 0) return [];
  const picked = [...selected];
  const flag = catalog.flag;
  return catalog.modes
    .views(mode)
    .map((t) => (flagOn && flag?.view ? flag.view(t) : t))
    .filter((t): t is V => t !== null)
    .filter((t) => !flagOn || (flag?.keep(t) ?? true))
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
        weak: costs.filter((c) => !guarantee(c.cost).startsWith("worst")).length,
      };
    })
    .sort(
      // worst selected op first, then all selected ops together, and only then the structure's constant factor
      (a, b) =>
        a.bottleneck.value - b.bottleneck.value ||
        a.total - b.total ||
        // then fewer amortized / expected bounds among the selected ops (worst case first on a tie)
        a.weak - b.weak ||
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
  flagOn,
  onClose,
}: {
  catalog: PickerCatalog<V>;
  template: V;
  selected: Set<string>;
  flagOn: boolean;
  onClose: () => void;
}) {
  const variant = catalog.variant?.of(base);
  const [useVariant, setUseVariant] = useState(false);
  const hasFast = catalog.fastMode?.has(base) ?? false;
  const [useFast, setUseFast] = useState(false);
  const fastInfo = useFast && hasFast ? catalog.fastMode!.explain(base) : null;
  const chosen = (
    useVariant && variant
      ? { ...base, ...variant, file: catalog.variant!.file }
      : base
  ) as V;
  const template = (
    useFast && hasFast
      ? {
          ...chosen,
          file: chosen.file === "template" ? "fast" : `${chosen.file}-fast`,
          langs: ["cpp"] as TemplateLang[],
        }
      : chosen
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
            {hasFast && (
              <label
                title={catalog.fastMode!.title}
                className="inline-flex cursor-pointer items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground"
              >
                <input
                  type="checkbox"
                  checked={useFast}
                  onChange={(e) => setUseFast(e.target.checked)}
                  className="accent-primary"
                />
                {catalog.fastMode!.label}
              </label>
            )}
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
          {fastInfo && <FastPanel info={fastInfo} />}
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
            flagOn={flagOn}
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

// Shown at the top of a drawer while fast mode is on.
function FastPanel({ info }: { info: FastInfo }) {
  return (
    <div className="grid gap-2 border-b border-border bg-muted/40 px-4 py-3 text-xs leading-5 text-muted-foreground">
      <p className="text-sm font-semibold text-foreground">Fast mode</p>
      <div>
        <p className="font-medium text-foreground">Why it's faster</p>
        <p>{info.how}</p>
      </div>
      <div>
        <p className="font-medium text-foreground">Drawbacks</p>
        <ul className="list-disc pl-4">
          {info.drawbacks.map((drawback) => (
            <li key={drawback}>{drawback}</li>
          ))}
        </ul>
      </div>
      <div>
        <p className="font-medium text-foreground">LEETCODE_NO_SANITIZE</p>
        {info.noSanitize.map(({ text, code }) => (
          <div key={text}>
            <p>{text}</p>
            {code && <pre className="overflow-x-auto font-mono">{code}</pre>}
          </div>
        ))}
      </div>
    </div>
  );
}

// One choice out of a few, as joined buttons with a label before them.
function ChoiceRow<T extends string>({
  label,
  options,
  value,
  onChoose,
}: {
  label: string;
  options: readonly { id: T; label: string; title: string }[];
  value: T;
  onChoose: (id: T) => void;
}) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-muted-foreground">{label}</span>
      <div className="flex overflow-hidden rounded-md border border-border" role="radiogroup" aria-label={label}>
        {options.map((option) => (
          <button
            key={option.id}
            type="button"
            role="radio"
            aria-checked={value === option.id}
            title={option.title}
            onClick={() => onChoose(option.id)}
            className={`px-2.5 py-1 ${
              value === option.id ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// A fill-in template (catalog.fillIns): just the file, in either language, with Copy and GitHub.
function FillInDrawer({
  catalog,
  fillIn: base,
  onClose,
}: {
  catalog: { publicBase: string; remoteBase?: string };
  fillIn: FillIn;
  onClose: () => void;
}) {
  const [preferred, setLang] = useState<TemplateLang>(readPreferredLang);
  const langs = base.langs ?? (["py", "cpp"] as TemplateLang[]);
  const lang = langs.includes(preferred) ? preferred : langs[0];
  const [level, setLevel] = useState<CppLevel>(readCppLevel);
  const [withReverse, chooseReverse] = useStoredFlag(REVERSE_STORAGE_KEY);
  const [version, setVersion] = useState<GenericVersion>(readGenericVersion);
  const [variantOn, chooseVariant] = useStoredFlag(base.variant?.storageKey ?? "");
  const fillIn = withVariant(base, variantOn);
  const levels = lang === "cpp" && fillIn.cppLevels;
  const suffix = levels ? CPP_LEVELS.find((l) => l.id === level)!.suffix : "";
  const noRev = fillIn.reverseToggle && !withReverse ? ".norev" : "";
  const versions = GENERIC_VERSIONS.filter(
    (v) =>
      v.id === "default" ||
      (v.id === "debug" && fillIn.debugToggle) ||
      (v.id === "fast" && fillIn.fast && lang === "cpp"),
  );
  const activeVersion = versions.some((v) => v.id === version) ? version : "default";
  const versionSuffix = activeVersion === "default" ? "" : `.${activeVersion}`;
  const fileName = `${fillIn.file}${suffix}${noRev}${versionSuffix}.${lang}`;
  const ops = noRev ? fillIn.ops.filter(([op]) => !op.startsWith("rangeReverse")) : fillIn.ops;
  const url = codeUrl(catalog, fillIn.folder, fileName);
  const [loaded, setLoaded] = useState<{ url: string; code: string | null } | null>(null);
  const [copiedUrl, setCopiedUrl] = useState<string | null>(null);
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

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  const chooseLang = (l: TemplateLang) => {
    setLang(l);
    writeStored(LANG_STORAGE_KEY, l);
  };
  const chooseLevel = (l: CppLevel) => {
    setLevel(l);
    writeStored(CPP_LEVEL_STORAGE_KEY, l);
  };
  const chooseVersion = (v: GenericVersion) => {
    setVersion(v);
    writeStored(GENERIC_VERSION_STORAGE_KEY, v);
  };
  const copy = async () => {
    if (!code) return;
    await navigator.clipboard.writeText(code);
    setCopiedUrl(url);
  };

  return (
    <div className="fixed inset-0 z-[60] flex justify-end font-[family-name:var(--font-dm-sans)]">
      <button type="button" aria-label="Close" onClick={onClose} className="absolute inset-0 bg-foreground/20" />
      <div className="relative flex h-full w-[min(900px,94vw)] flex-col border-l border-border bg-background shadow-2xl">
        <div className="flex items-start justify-between gap-4 border-b border-border p-4">
          <div className="min-w-0">
            <p className="text-sm font-semibold text-foreground">{fillIn.label}</p>
          </div>
          <div className="flex flex-shrink-0 items-center gap-2">
            <div className="flex overflow-hidden rounded-md border border-border text-xs" role="group" aria-label="Language">
              {langs.map((l) => (
                <button
                  key={l}
                  type="button"
                  aria-pressed={lang === l}
                  onClick={() => chooseLang(l)}
                  className={`px-2.5 py-1 ${
                    lang === l ? "bg-primary text-primary-foreground" : "text-foreground hover:bg-muted"
                  }`}
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
              {copiedUrl === url ? "Copied" : "Copy"}
            </button>
            <a
              href={`${fillIn.githubUrl}${fileName}`}
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
        {(levels || versions.length > 1) && (
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2 border-b border-border px-4 py-2 text-xs">
            {levels && <ChoiceRow label="Examples:" options={CPP_LEVELS} value={level} onChoose={chooseLevel} />}
            {versions.length > 1 && (
              <ChoiceRow label="Version:" options={versions} value={activeVersion} onChoose={chooseVersion} />
            )}
          </div>
        )}
        <div className="min-h-0 flex-1 overflow-y-auto">
          {activeVersion === "fast" && <FastPanel info={fillIn.fast!} />}
          {/* every op is there whatever you need, so all of them are highlighted */}
          <div className="border-b border-border px-4 py-3 text-xs">
            <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-0.5">
              {ops.map(([op, cost]) => (
                <div key={op} className="contents">
                  <span className="font-mono font-medium text-primary">{op}</span>
                  <span className="text-foreground">{formatCost(cost)}</span>
                </div>
              ))}
            </div>
            {(fillIn.reverseToggle || fillIn.variant) && (
              <div className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
                {fillIn.reverseToggle && (
                  <label
                    title="With rangeReverse the template also needs reverse(node), the node of a segment read backwards"
                    className="flex w-fit cursor-pointer items-center gap-1.5 text-foreground"
                  >
                    <input type="checkbox" checked={withReverse} onChange={(e) => chooseReverse(e.target.checked)} className="accent-primary" />
                    <span className="font-mono">rangeReverse</span>
                  </label>
                )}
                {base.variant && (
                  <label title={base.variant.title} className="flex w-fit cursor-pointer items-center gap-1.5 text-foreground">
                    <input type="checkbox" checked={variantOn} onChange={(e) => chooseVariant(e.target.checked)} className="accent-primary" />
                    {base.variant.label}
                  </label>
                )}
              </div>
            )}
            {fillIn.note && <p className="mt-2 text-muted-foreground">{fillIn.note}</p>}
          </div>
          <pre className="overflow-x-auto bg-card p-4 font-mono text-xs leading-relaxed text-foreground">
            {code === null ? "Couldn't load this template." : (code ?? "Loading…")}
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
  flagOn,
  lang,
}: {
  catalog: PickerCatalog<V>;
  template: V;
  usage: Usage | undefined;
  selected: Set<string>;
  flagOn: boolean;
  lang: TemplateLang;
}) {
  if (!usage) return null;
  const ops = template.operations.filter((op) => selected.has(op));
  const shown = ops.length ? ops : template.operations;
  const cpp = lang === "cpp";
  const cm = cpp ? "//" : "#";
  const notes = typeof catalog.ctorNotes === "function" ? catalog.ctorNotes(template) : catalog.ctorNotes;
  const flagged = flagOn ? catalog.flag : undefined;
  const reword = (text: string) => flagged?.rename?.(text, lang) ?? text;
  const elem = flagged?.elem ?? ((template as { chars?: boolean }).chars ? "char" : "long long"); // what T is in the usage lines
  const neededClasses = [
    ...new Set(shown.map((op) => usage.methods[op]!.cls)),
  ].sort((a, b) => a - b);
  const varOf = (k: number) =>
    neededClasses.length === 1
      ? catalog.varName
      : usage.classes[k].className[0].toLowerCase() +
        usage.classes[k].className.slice(1);
  const typeOf = (ret = "") =>
    ret.replace(/\bT\b/g, elem).replace(/\bS\b/g, "long long");

  const blocks: { comments: string[]; code: string }[] = [];
  for (const k of neededClasses) {
    const cls = usage.classes[k];
    const shownOptional = (p: { name: string; default?: string }) => p.default !== undefined && !!notes[p.name]?.inCall;
    const requiredParams = cls.ctor.filter((p) => p.default === undefined || shownOptional(p));
    const required = requiredParams.map((p) => p.name);
    const optional = cls.ctor.filter((p) => p.default !== undefined && !shownOptional(p));
    // C++17 deduces T from a vector argument (vector<T>, vector<pair<long long, T>>), unless a scalar T argument
    // (e.g. a literal 3, an int) could disagree with it; then, or when T appears in no argument, write it out.
    const deducible =
      requiredParams.some((p) => /vector<.*\bT\b/.test(p.type ?? "")) &&
      !requiredParams.some((p) => /^(const\s+)?T\s*&?$/.test(p.type ?? ""));
    if (cpp && cls.pool)
      blocks.push({
        comments: [
          `Between test cases: frees every ${cls.className}<${elem}> (they all share one node pool).`,
        ],
        code: `${cls.className}<${elem}>::resetPool();`,
      });
    const comments = [
      ...(catalog.ctorComments?.(template, lang) ?? []),
      ...requiredParams.flatMap((p) =>
        notes[p.name] && !["mod", "bits"].includes(p.name)
          ? [notes[p.name][lang] + (shownOptional(p) ? " (optional: leave it out to start empty)" : "")]
          : [],
      ),
      ...optional.map(
        (p) =>
          `Optional: ${p.name} (default ${p.default})${notes[p.name] ? `, ${notes[p.name][lang]}` : ""}.`,
      ),
      ...(cpp
        ? [
            deducible
              ? `T is deduced from the vector (vector<${elem}> gives T = ${elem}).`
              : `T = ${elem}${elem === "long long" ? " (int works too)" : ""}.`,
          ]
        : []),
    ];
    const type = `${cls.className}${deducible ? "" : `<${elem}>`}`;
    blocks.push({
      comments: comments.map(reword),
      // (no arguments: "Name<long long> x;", since "x()" would declare a function)
      code: cpp
        ? `${type} ${varOf(k)}${required.length ? `(${required.join(", ")})` : ""};`
        : `${varOf(k)} = ${cls.className}(${required.join(", ")})`,
    });
  }
  for (const op of shown) {
    const m = usage.methods[op]!;
    const call = `${varOf(m.cls)}.${op}(${m.params.map(reword).join(", ")})`;
    const pair = catalog.pairResults?.[op];
    let code: string;
    if (pair?.length === 1) code = cpp ? `auto ${pair[0]} = ${call};` : `${pair[0]} = ${call}`;
    else if (pair)
      code = cpp
        ? `auto [${pair.join(", ")}] = ${call};`
        : `${pair.join(", ")} = ${call}`;
    else if (catalog.updateOps.has(op)) code = cpp ? `${call};` : call;
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
    blocks.push({ comments: doc ? [reword(doc)] : [], code });
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
  mod: { label: "% MOD", badge: "border-sky-200 bg-sky-50 text-sky-700" },
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
      className={`inline-flex items-center rounded-full border px-1.5 font-[family-name:var(--font-dm-sans)] text-[9px] font-bold uppercase leading-[14px] tracking-wider ${badge}`}
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
  const [openFillIn, setOpenFillIn] = useState<FillIn | null>(null);
  const [fillInMenu, setFillInMenu] = useState(false); // the "Generic seg trees" menu is open
  const [expanded, setExpanded] = useState<Set<string>>(new Set()); // collapsible groups clicked open
  const [openTypes, setOpenTypes] = useState<Map<string, number>>(new Map()); // result type -> left-out variants shown
  const [query, setQuery] = useState(""); // the search box: only ops whose name or description contains it
  // the bottom sheet (selection + templates) and its current height
  const sheetRef = useRef<HTMLElement>(null);
  const [sheetHeight, setSheetHeight] = useState(0);
  const [sheetHidden, setSheetHidden] = useState(false); // closed with its x; picking an op opens it again
  const sheetOpen = selected.size > 0 && !sheetHidden;
  useEffect(() => {
    const el = sheetRef.current;
    if (!sheetOpen || !el) return;
    const ro = new ResizeObserver(() => setSheetHeight(el.offsetHeight + 24));
    ro.observe(el);
    return () => ro.disconnect();
  }, [sheetOpen]);
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
  const reword = (text: string) => (flagOn && flag?.rename ? flag.rename(text) : text);

  const toggle = (id: string) => {
    if (isDisabled(id)) return;
    setSheetHidden(false);
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
  // matches come best first; each type's left-out variants are counted on its first card: those a shown one beats,
  // and real trade-offs past the per-type limit
  const hidden = new Map<string, number>();
  const overflow = new Map<string, number>();
  const shownOf = new Map<string, typeof capped>();
  const kept = catalog.perType
    ? capped.filter((m) => {
        const type = m.template.dataStructureType;
        const shown = shownOf.get(type) ?? [];
        // s beats m: no slower on a selected op (with as sure a bound), no more memory or build, and nothing else m
        // is better at
        const covered = shown.some(
          (s) =>
            s.costs.every((c, k) => c.value <= m.costs[k].value && noWeaker(c.cost, m.costs[k].cost)) &&
            memoryValue(s.template.memory) <= memoryValue(m.template.memory) &&
            costValue(s.template.build) <= costValue(m.template.build) &&
            (catalog.noWorse?.(s.template, m.template) ?? true),
        );
        if (covered || shown.length >= catalog.perType!) {
          const into = covered ? hidden : overflow;
          into.set(type, (into.get(type) ?? 0) + 1);
          return false;
        }
        shownOf.set(type, [...shown, m]);
        return true;
      })
    : capped;
  // a type clicked open shows the variants it left out, MORE_STEP more per click, right after its last shown card
  // (best first)
  const MORE_STEP = 10;
  const keptSet = new Set(kept);
  const lastShown = new Map([...shownOf].map(([type, shown]) => [type, shown[shown.length - 1]]));
  const leftOut = (type: string) => capped.filter((x) => x.template.dataStructureType === type && !keptSet.has(x));
  const matches = kept.flatMap((m) => {
    const type = m.template.dataStructureType;
    if (!openTypes.has(type) || lastShown.get(type) !== m) return [m];
    return [m, ...leftOut(type).slice(0, openTypes.get(type))];
  });
  const fullView = openTypes.size > 0;
  const showMore = (type: string) =>
    setOpenTypes((prev) => new Map(prev).set(type, (prev.get(type) ?? 0) + MORE_STEP));
  const showFewer = (type: string) =>
    setOpenTypes((prev) => {
      const next = new Map(prev);
      next.delete(type);
      return next;
    });
  // the "+N more" / "Show fewer" links of a type: under its first card, or at the bottom of its column in the full view
  const moreLinks = (type: string) => {
    const total = (hidden.get(type) ?? 0) + (overflow.get(type) ?? 0);
    const left = total - Math.min(openTypes.get(type) ?? 0, total);
    if (total === 0) return null;
    const step = Math.min(MORE_STEP, left);
    const link = "block text-left text-[11px] leading-snug text-primary hover:underline";
    return (
      <span className="mt-1 flex flex-wrap gap-x-3">
        {left > 0 && (
          <button type="button" onClick={() => showMore(type)} className={link}>
            +{step} more {step === 1 ? "variant" : "variants"}
            {left > step && ` (${left} left)`}
          </button>
        )}
        {openTypes.has(type) && (
          <button type="button" onClick={() => showFewer(type)} className={link}>
            Show fewer
          </button>
        )}
      </span>
    );
  };
  const firstOfType = (t: V) =>
    shownOf.get(t.dataStructureType)?.[0]?.template === t;
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

  // one result card (i: its rank among all matches, 0 = best)
  const renderCard = ({ template, extra, costs }: (typeof matches)[number], i: number) => {
    const layout = catalog.layoutLabel(template.memory);
    return (
      <li
        key={`${template.folder}/${template.file}`}
        className="flex w-[26rem] flex-shrink-0 flex-col"
      >
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
          className="flex w-full flex-1 flex-col justify-start rounded-lg border border-border bg-background px-2.5 py-1.5 text-left transition-colors hover:border-primary/50"
        >
          <span className="flex items-start justify-between gap-2">
            <span className="text-xs font-medium text-foreground">
              {catalog.kindLabel(template)}
            </span>
            {i === 0 && (
              <span className="shrink-0 whitespace-nowrap rounded-full bg-primary/15 px-1.5 py-0.5 text-[10px] font-semibold text-primary">
                Best match
              </span>
            )}
          </span>
          {/* costs as one wrapped line of "op cost" pairs */}
          <span className="mt-1 flex flex-wrap gap-x-3 text-[11px] leading-snug">
            {costs.map((c) => (
              <span key={c.op}>
                <span className="font-mono text-muted-foreground">
                  {c.op}
                </span>{" "}
                <span className="text-foreground">
                  {formatCost(c.cost)}
                </span>
              </span>
            ))}
            <span>
              <span className="font-mono text-muted-foreground">
                build
              </span>{" "}
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
          </span>
          {/* memory on one line: the total, then each group's arrays */}
          <span className="mt-1 block text-[11px] leading-snug text-muted-foreground">
            Memory{" "}
            <span className="text-foreground">
              {formatMemoryOf(
                template.memory,
                template.memory.total,
              )}
            </span>
            {layout && ` (${layout})`}
            {catalog
              .memoryGroups(template)
              .map(
                ({ id, label }) =>
                  ` · ${label}: ${
                    template.memory[id].arrays
                      .map((a) => a.name)
                      .join(", ") || "none"
                  }`,
              )
              .join("")}
          </span>
          {extra.length > 0 && (
            <span
              title={extra.join(", ")}
              className="mt-1 line-clamp-2 text-[11px] leading-snug text-muted-foreground"
            >
              Also: {extra.join(", ")}
            </span>
          )}
        </button>
        {!fullView && firstOfType(template) && moreLinks(template.dataStructureType)}
      </li>
    );
  };
  // once a type is clicked open the sheet fills the screen: one column per type (in rank order), each scrolling down
  const columns = [...new Set(matches.map((m) => m.template.dataStructureType))].map((type) =>
    matches.filter((m) => m.template.dataStructureType === type),
  );

  return (
    <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-16 font-[family-name:var(--font-dm-sans)]">
      {/* the tab row and the selection stay put; only the operations scroll */}
      <div className="sticky top-16 z-30 -mx-6 bg-background px-6 pt-2">
        <h1 className="sr-only">{catalog.title}</h1>
        <PickerTabs>
          <>
            {catalog.fillIns && catalog.fillIns.length > 0 && (
              <div className="relative">
                <button
                  type="button"
                  aria-expanded={fillInMenu}
                  onClick={() => setFillInMenu((o) => !o)}
                  className="rounded-md border border-border px-3 py-1.5 text-xs font-medium text-foreground transition-colors hover:bg-muted"
                >
                  Generic seg trees ▾
                </button>
                {fillInMenu && (
                  <>
                    <button
                      type="button"
                      aria-label="Close menu"
                      onClick={() => setFillInMenu(false)}
                      className="fixed inset-0 z-40 cursor-default"
                    />
                    <ul className="absolute right-0 z-50 mt-1 w-56 overflow-hidden rounded-md border border-border bg-background py-1 shadow-lg">
                      {catalog.fillIns.map((f) => (
                        <li key={f.file}>
                          <button
                            type="button"
                            onClick={() => {
                              setOpenFillIn(f);
                              setFillInMenu(false);
                            }}
                            className="block w-full px-3 py-2 text-left hover:bg-muted"
                          >
                            <span className="block text-xs font-medium text-foreground">{f.label}</span>
                          </button>
                        </li>
                      ))}
                    </ul>
                  </>
                )}
              </div>
            )}
            <input
              type="search"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search operations…"
              aria-label="Search operations"
              className="w-56 rounded-md border border-border bg-background px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:border-primary focus:outline-none"
            />
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
          </>
        </PickerTabs>
      </div>

      <div className="columns-1 gap-3 md:columns-2 xl:columns-3">
        {catalog.opGroups.map((group) => {
          // while searching: only the matching ops, groups without one hidden, collapsed groups open
          const q = query.trim().toLowerCase();
          const tiers = q
            ? group.tiers
                .map((t) => ({
                  ...t,
                  ops: t.ops.filter((op) =>
                    `${op.signature} ${op.description}`
                      .toLowerCase()
                      .includes(q),
                  ),
                }))
                .filter((t) => t.ops.length > 0)
            : group.tiers;
          if (q && tiers.length === 0) return null;
          const closed = !q && group.collapsible && !expanded.has(group.id);
          const picked = group.tiers.reduce(
            (n, t) => n + t.ops.filter((op) => active.has(op.id)).length,
            0,
          );
          const heading = (
            <>
              <h2 className="flex items-center gap-1.5 text-sm font-semibold text-foreground">
                {group.collapsible && (
                  <span
                    aria-hidden
                    className={`inline-block text-[10px] text-muted-foreground transition-transform ${closed ? "" : "rotate-90"}`}
                  >
                    ▶
                  </span>
                )}
                {group.title}
                {closed && picked > 0 && (
                  <span className="rounded bg-primary/15 px-1.5 py-0.5 text-[11px] font-medium text-primary">
                    {picked} selected
                  </span>
                )}
              </h2>
            </>
          );
          return (
            <section
              key={group.id}
              className="mb-3 break-inside-avoid rounded-xl border border-border bg-card px-3 py-2.5"
            >
              {group.collapsible ? (
                <button
                  type="button"
                  aria-expanded={!closed}
                  onClick={() =>
                    setExpanded((prev) => {
                      const next = new Set(prev);
                      if (next.has(group.id)) next.delete(group.id);
                      else next.add(group.id);
                      return next;
                    })
                  }
                  className={`flex w-full items-baseline justify-between gap-3 text-left ${closed ? "" : "mb-1.5"}`}
                >
                  {heading}
                </button>
              ) : (
                <div className="mb-1.5 flex items-baseline justify-between gap-3">
                  {heading}
                </div>
              )}
              {!closed && (
                <div className="-mx-2 grid grid-cols-[auto_auto_minmax(0,1fr)]">
                  {tiers.flatMap((tier, tierIdx) => [
                    // a "topic" tier with no label is just the group's list: no header
                    // the "common" tier is just the top of the list (no header); a "topic" tier with no label too
                    tier.kind === "common" ||
                    (tier.kind === "topic" && !tier.label) ? null : (
                      <h3
                        key={tier.label ?? tier.kind}
                        className={`col-span-3 flex items-center gap-2 px-2 ${tierIdx === 0 ? "" : "mt-1.5"}`}
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
                          className={`col-span-3 grid grid-cols-subgrid items-baseline gap-x-2 rounded-md px-2 py-0.5 text-left transition-colors ${
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
                            className={`whitespace-nowrap font-mono text-xs ${isOn ? "font-medium text-primary" : "text-foreground"}`}
                          >
                            {opName(op)}
                            <span className="font-normal text-muted-foreground">
                              {reword(opArgs(op))}
                            </span>
                          </span>
                          <span className="min-w-0 text-[11px] leading-snug text-muted-foreground">
                            {reword(op.description)}
                          </span>
                        </button>
                      );
                    }),
                  ])}
                </div>
              )}
            </section>
          );
        })}
      </div>

      {catalog.planned && catalog.planned.length > 0 && (
        <p className="mt-4 text-xs text-muted-foreground">
          <span className="font-medium">Still to add:</span> {catalog.planned.join(" · ")}
        </p>
      )}

      {/* room below the content for the bottom sheet, so it can always be scrolled clear of it */}
      {sheetOpen && <div aria-hidden style={{ height: sheetHeight }} />}
      {selected.size > 0 && sheetHidden && (
        <button
          type="button"
          onClick={() => setSheetHidden(false)}
          className="fixed bottom-0 left-1/2 z-40 -translate-x-1/2 rounded-t-lg border border-b-0 border-border bg-card px-4 py-1.5 text-xs font-medium text-foreground shadow-[0_-4px_16px_rgba(0,0,0,0.10)] hover:bg-muted"
        >
          ▲ {selectedOps.length} selected · {matches.length} template
          {matches.length === 1 ? "" : "s"}
        </button>
      )}
      {sheetOpen && (
        <section
          ref={sheetRef}
          className={`fixed inset-x-3 bottom-0 z-40 mx-auto max-w-[1760px] rounded-t-xl border border-b-0 border-border bg-card px-4 pb-3 pt-3 shadow-[0_-8px_30px_rgba(0,0,0,0.12)] ${
            fullView ? "top-20 flex flex-col overflow-hidden" : "max-h-[45vh] overflow-y-auto"
          }`}
        >
          <div className="flex flex-wrap items-center gap-x-3 gap-y-2">
            <h2 className="text-sm font-semibold text-foreground">
              Selection
              {selectedOps.length > 0 && (
                <span className="ml-1.5 font-normal text-muted-foreground">
                  {selectedOps.length}
                </span>
              )}
            </h2>
            {selectedOps.length > 0 && (
              <ul className="flex flex-wrap gap-2">
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
                      className="inline-flex items-center gap-2 rounded-md border border-border bg-background px-2 py-1"
                    >
                      <code className="font-mono text-xs text-foreground">
                        {reword(op.signature)}
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
            {fullView && (
              <button
                type="button"
                onClick={() => setOpenTypes(new Map())}
                title="Back to the short row of best variants"
                className="ml-auto rounded-md border border-border px-2.5 py-1 text-xs text-foreground hover:bg-muted"
              >
                Collapse all
              </button>
            )}
            <button
              type="button"
              onClick={() => setSheetHidden(true)}
              aria-label="Close the templates panel"
              title="Close (pick an op to open it again)"
              className={`${fullView ? "" : "ml-auto "}flex h-8 w-8 items-center justify-center rounded-md text-2xl leading-none text-muted-foreground transition-colors hover:bg-muted hover:text-foreground`}
            >
              ×
            </button>
          </div>

          <div className={`mt-2 border-t border-border pt-2 ${fullView ? "flex min-h-0 flex-1 flex-col" : ""}`}>
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
              fullView ? (
                <div className="mt-2 flex min-h-0 flex-1 items-start gap-3 overflow-auto pb-2">
                  {columns.map((col) => (
                    <div key={col[0].template.dataStructureType} className="flex flex-shrink-0 flex-col">
                      <ul className="flex flex-col gap-3">{col.map((m) => renderCard(m, matches.indexOf(m)))}</ul>
                      {moreLinks(col[0].template.dataStructureType)}
                    </div>
                  ))}
                </div>
              ) : (
                <ul className="mt-2 flex gap-3 overflow-x-auto pb-2">{matches.map(renderCard)}</ul>
              )
            )}
          </div>
        </section>
      )}

      {openTemplate && (
        <CodeDrawer
          key={`${openTemplate.folder}/${openTemplate.file}`}
          catalog={catalog}
          template={openTemplate}
          selected={selected}
          flagOn={flagOn}
          onClose={() => setOpenTemplate(null)}
        />
      )}
      {openFillIn && (
        <FillInDrawer
          key={openFillIn.file}
          catalog={catalog}
          fillIn={openFillIn}
          onClose={() => setOpenFillIn(null)}
        />
      )}
    </main>
  );
}

// A templates tab without a picker (Misc., Golden References): sections of cards, each opening the same drawer as the
// pickers' fill-ins, and a "still to add" note under them.
export function MiscTemplates({
  title,
  sections,
  publicBase,
  planned = [],
}: {
  title: string;
  sections: MiscSection[];
  publicBase: string;
  planned?: string[];
}) {
  const [open, setOpen] = useState<FillIn | null>(null);
  return (
    <main className="mx-auto max-w-[1800px] px-6 pb-16 pt-16 font-[family-name:var(--font-dm-sans)]">
      <div className="sticky top-16 z-30 -mx-6 bg-background px-6 pt-2">
        <h1 className="sr-only">{title}</h1>
        <PickerTabs />
      </div>
      {sections.map((section) => (
        <section key={section.title} className="mb-6">
          <h2 className="mb-2 text-sm font-semibold text-foreground">{section.title}</h2>
          <div className="flex flex-wrap gap-3">
            {section.items.map((f) => (
              <MiscCard key={f.file} item={f} onOpen={() => setOpen(f)} />
            ))}
          </div>
        </section>
      ))}
      {planned.length > 0 && (
        <p className="mt-4 text-xs text-muted-foreground">
          <span className="font-medium">Still to add:</span> {planned.join(" · ")}
        </p>
      )}
      {open && <FillInDrawer key={open.file} catalog={{ publicBase }} fillIn={open} onClose={() => setOpen(null)} />}
    </main>
  );
}

// a Misc card: its label (the variant's while ticked), opening the drawer; a card with a variant shows its checkbox
function MiscCard({ item, onOpen }: { item: FillIn; onOpen: () => void }) {
  const [on, choose] = useStoredFlag(item.variant?.storageKey ?? "");
  const f = withVariant(item, on);
  return (
    <div className="rounded-lg border border-border bg-card transition-colors hover:border-primary">
      <button type="button" onClick={onOpen} className="block w-full p-3 text-left">
        <span className="block text-sm font-medium text-foreground">{f.label}</span>
        {f.title && <span className="mt-1 block text-xs leading-snug text-muted-foreground">{f.title}</span>}
      </button>
      {item.variant && (
        <label title={item.variant.title} className="-mt-1 flex w-fit cursor-pointer items-center gap-1.5 px-3 pb-2.5 text-xs text-muted-foreground">
          <input type="checkbox" checked={on} onChange={(e) => choose(e.target.checked)} className="accent-primary" />
          {item.variant.label}
        </label>
      )}
    </div>
  );
}
