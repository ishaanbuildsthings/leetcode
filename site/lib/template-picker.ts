// Shared by every template picker (range queries, sets): template shape, usage data, and how costs and memory are
// written and ranked. Each picker supplies its own operations and labels (see components/TemplatePicker.tsx).

export interface PickerOp {
  id: string;
  signature: string;
  description: string;
  // (optional) the same op done mod a fixed MOD, picked by a checkbox under this op instead of as its own row (tree
  // queries: nodePathAdd -> nodePathAddMod); checking it swaps which of the two ids is selected
  modVariant?: PickerOp;
}

// every op a tier offers, the mod variants behind checkboxes included
export const tierOps = (tier: PickerOpTier): PickerOp[] =>
  tier.ops.flatMap((op) => (op.modVariant ? [op, op.modVariant] : [op]));

// "topic" groups ops by what they do rather than how often they come up; it always carries a label
export type TierKind =
  "common" | "uncommon" | "rare" | "mod" | "bitOps" | "topic";

export interface PickerOpTier {
  kind: TierKind;
  // Overrides the badge text; the kind still sets the color.
  label?: string;
  // (optional) which section of its group the tier is in: sectioned tiers sit behind a small switch, one section at a
  // time, below the group's unsectioned tiers (tree queries: One node always shows; Path a..b / Subtree of v switch)
  section?: string;
  ops: PickerOp[];
}

export interface PickerOpGroup {
  id: string;
  title: string;
  // (optional) a short muted note beside the title (tree queries: "(a, b can be either order)" on the edge groups)
  note?: string;
  // shown as just its header until clicked open (closed on every page load)
  collapsible?: boolean;
  tiers: PickerOpTier[];
}

// A template as a picker shows it: one variant (file "template", or "sparse" for a range query's sparse version).
export interface PickerTemplate {
  folder: string;
  file: string;
  langs: TemplateLang[];
  operations: string[];
  dataStructureType: string;
  complexities: Partial<Record<string, string>>;
  build: string;
  memory: MemoryBreakdown;
  // inline, or (sets) left out and fetched from <publicBase>/<folder>/<file>.usage.json when the drawer opens
  usage?: Partial<Record<TemplateLang, Usage>>;
}

export type TemplateLang = "py" | "cpp";

export const TEMPLATE_LANG_LABELS: Record<TemplateLang, string> = {
  py: "Python",
  cpp: "C++",
};

// How to call a template, read from its source by the generator: the classes to construct and, per operation,
// which class has it, its parameter names, (C++) its return type, and the comment above it.
export interface UsageParam {
  name: string;
  type?: string;
  default?: string;
}

export interface UsageClass {
  className: string;
  doc: string;
  ctor: UsageParam[];
  ctorDoc: string;
  // C++: a plain struct (not templated on T), so it's constructed without <T>
  plain?: boolean;
}

export interface UsageMethod {
  cls: number;
  params: string[];
  returns?: string;
  doc: string;
}

export interface Usage {
  classes: UsageClass[];
  methods: Partial<Record<string, UsageMethod>>;
}

// A static template's sparse version is built from N given values, so its memory is a total in N; a
// dynamic one starts all zeros and its memory is counted per update.
export function isBuiltFromPoints(memory: MemoryBreakdown): boolean {
  return memory.layout === "sparse" && /\bN\b/.test(memory.total);
}

export type TreeLayout =
  "2n-iterative" | "pow2-iterative" | "4n-recursive" | "sparse" | "none";

export const TREE_LAYOUT_LABELS: Record<TreeLayout, string> = {
  "2n-iterative": "2N iterative tree",
  "pow2-iterative": "4N iterative tree",
  "4n-recursive": "4N recursive tree",
  sparse: "dynamic tree, any index range",
  none: "not a segment tree",
};

// Every array a template allocates, with its length (e.g. "4*N"), grouped by role. Totals are computed by the generator.
export interface MemoryGroup {
  arrays: { name: string; size: string }[];
  total: string;
}

export interface MemoryBreakdown {
  layout: TreeLayout;
  node: MemoryGroup;
  tags: MemoryGroup;
  other: MemoryGroup;
  note?: string;
  // the note as each language's file has it (they describe different implementations)
  notes?: Partial<Record<TemplateLang, string>>;
  total: string;
}

// Typical contest sizes (N elements, values up to U, Q updates), used to turn a cost string into a number for ranking.
const SIZES = { N: 2e5, U: 1e9, Q: 2e5 };
const FACTOR_VALUES: Record<string, number> = {
  "1": 1,
  // union find: α(N) is at most about 4; K = the size of the group a call lists (ranked as a typical small group)
  "α(N)": 3,
  K: 20,
  N: SIZES.N,
  "log(N)": Math.log2(SIZES.N),
  "log^2(N)": Math.log2(SIZES.N) ** 2,
  // (a tree path over a log^2 range op: the tree query templates)
  "log^3(N)": Math.log2(SIZES.N) ** 3,
  "sqrt(N)": Math.sqrt(SIZES.N),
  "sqrt(NlogN)": Math.sqrt(SIZES.N * Math.log2(SIZES.N)),
  "sqrt(N/logN)": Math.sqrt(SIZES.N / Math.log2(SIZES.N)),
  U: SIZES.U,
  "U/64": SIZES.U / 64,
  // a bitset with a bit per distinct value (the count-distinct path templates): ranked as about 1,000 distinct values
  "D/64": 16,
  "log(U)": Math.log2(SIZES.U),
  "log64(U)": Math.log2(SIZES.U) / 6,
  "log(log(U))": Math.log2(Math.log2(SIZES.U)),
  // Pollard rho on a value too big for the sieve: about U^(1/4) steps expected
  "U^(1/4)": SIZES.U ** 0.25,
  // the bit operation templates: B = number of bits in the largest value
  B: 30,
  "B^2": 900,
  "2^B": 2 ** 20,
};

export function costValue(cost: string): number {
  return cost
    .replace(/ \?$/, "")
    .replace(/ (amortized expected|amortized|expected)$/, "")
    .split("+")
    .reduce(
      (sum, term) =>
        sum + term.split("*").reduce((prod, f) => prod * factorValue(f), 1),
      0,
    );
}

const isConstant = (f: string) => /^\d+$/.test(f);
const factorValue = (f: string) =>
  isConstant(f) ? Number(f) : FACTOR_VALUES[f];

// "36*N" -> "36N", "2*N*log(N)" -> "2N · log N"
function formatTerm(term: string): string {
  const factors = term.split("*");
  const constant = factors
    .filter(isConstant)
    .reduce((prod, f) => prod * Number(f), 1);
  const rest = factors
    .filter((f) => !isConstant(f) && f !== "1")
    .map((f) => PRETTY_FACTORS[f]);
  if (rest.length === 0) return String(constant);
  return (constant === 1 ? "" : String(constant)) + rest.join(" · ");
}

// Memory is a count of stored values, shown as a size with an explicit coefficient: "1N", "4N", "1N · log N", "3√N".
// A dynamic sparse version (starts all zeros) has its memory sizes counted per update: shown as Q · (...) and ranked
// as Q times that. A static one built from given values has plain sizes in N.
export function isPerUpdate(memory: MemoryBreakdown): boolean {
  return memory.layout === "sparse" && !isBuiltFromPoints(memory);
}

// A size from this template's memory breakdown; a per-update size is multiplied by Q (e.g. 2 + 6*log(U) -> "2Q + 6Q log U").
export function formatMemoryOf(memory: MemoryBreakdown, size: string): string {
  if (!isPerUpdate(memory) || size === "0") return formatMemory(size);
  return formatMemory(
    size
      .split("+")
      .map((term) => `${term}*Q`)
      .join("+"),
  );
}

// The template's total memory as a number, for ranking.
export function memoryValue(memory: MemoryBreakdown): number {
  return costValue(memory.total) * (isPerUpdate(memory) ? SIZES.Q : 1);
}

// "2*N*log(N)+4*N" -> "2N*logN + 4N": the coefficient and one-letter variables (N, Q, U) form one block ("6Q"),
// other factors are written without spaces ("logU", "√N") and joined to it by "*"; terms are joined by " + ".
export function formatMemory(memory: string): string {
  if (memory === "0") return "0";
  const LETTERS = ["N", "Q", "U"];
  return memory
    .split("+")
    .map((term) => {
      const factors = term.split("*");
      const constant = factors
        .filter(isConstant)
        .reduce((prod, f) => prod * Number(f), 1);
      const vars = factors.filter((f) => !isConstant(f) && f !== "1");
      const letters = LETTERS.filter((v) => vars.includes(v)).join("");
      const rest = vars
        .filter((f) => !LETTERS.includes(f))
        .map((f) => PRETTY_FACTORS[f]);
      const head =
        (constant === 1 && (letters || rest.length) ? "" : String(constant)) +
        letters;
      return [head, ...rest].filter(Boolean).join("*");
    })
    .join(" + ");
}

// How a memory factor is written: no inner spaces, so "logU" reads as one thing next to a "*".
const PRETTY_FACTORS: Record<string, string> = {
  "1": "1",
  "α(N)": "α(N)",
  K: "K",
  Q: "Q",
  N: "N",
  "log(N)": "logN",
  "log^2(N)": "log²N",
  "log^3(N)": "log³N",
  "sqrt(N)": "√N",
  "sqrt(NlogN)": "√(NlogN)",
  "sqrt(N/logN)": "√(N/logN)",
  U: "U",
  "U/64": "U/64",
  "D/64": "D/64",
  "N/64": "N/64",
  "L/64": "L/64",
  "log(U)": "logU",
  "log64(U)": "log₆₄U",
  "log(log(U))": "loglogU",
  "U^(1/4)": "U¹ᐟ⁴",
  // the matrix templates: shapes A[x, y] @ B[y, z], square M[k, k], power p, recurrence order d, sequence length L
  x: "x",
  y: "y",
  z: "z",
  "y/64": "y/64",
  "z/64": "z/64",
  "k^2": "k²",
  "k^2/64": "k²/64",
  "k^3": "k³",
  "k^3/64": "k³/64",
  "log(p)": "log p",
  "log(P)": "log P",
  "d^2": "d²",
  "log(n)": "log n",
  "L^2": "L²",
  "min(x,y)": "min(x, y)",
  // the string templates: N = text length, M = pattern length, σ = number of distinct items (shown as "alphabet")
  M: "M",
  "σ": "alphabet",
  "log(σ)": "log alphabet",
  "sqrt(M)": "√M",
  // the combinatorics templates
  "log(e)": "log e",
  "log(MOD)": "log MOD",
  "log(x)": "log x",
  // the bit operation templates: B = number of bits in the largest value
  B: "B",
  "B^2": "B²",
  "2^B": "2ᴮ",
};

export function formatCost(cost: string): string {
  const unsure = cost.endsWith(" ?");
  const rest = cost.replace(/ \?$/, "");
  const kind = rest.match(/ (amortized expected|amortized|expected)$/)?.[1];
  const body = rest
    .replace(/ (amortized expected|amortized|expected)$/, "")
    .split("+")
    .map(formatTerm)
    .join(" + ");
  return `O(${body})${unsure ? "?" : ""}${kind ? ` ${kind}` : ""}`;
}
