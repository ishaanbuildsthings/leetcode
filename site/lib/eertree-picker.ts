// The Eertree op picker (Strings tab): templates/ultimate-template-tool/strings/Eertree.{py,cpp} hold every op, with
// each optional part between marker lines. A line "# @if a b+c" (or "// @if ...") opens a block kept when any
// space-separated term holds, where a term holds when every '+'-joined op in it is ticked; "@else" and "@endif" close
// it; blocks nest. Marker lines never reach the output. (string-tests/eertree_strip.py is the same, for the tests.)

const MARK = /^\s*(?:#|\/\/) @(if|else|endif)\b ?(.*)$/;

export function keepTickedOps(code: string, ticked: ReadonlySet<string>): string {
  const out: string[] = [];
  const stack: { parent: boolean; cond: boolean }[] = [];
  let keeping = true;
  for (const line of code.split("\n")) {
    const m = line.match(MARK);
    if (!m) {
      if (keeping) out.push(line);
      continue;
    }
    const [, kind, rest] = m;
    if (kind === "if") {
      const cond = rest
        .trim()
        .split(/\s+/)
        .some((term) => term.split("+").every((op) => ticked.has(op)));
      stack.push({ parent: keeping, cond });
      keeping = keeping && cond;
    } else if (kind === "else") {
      const top = stack[stack.length - 1];
      top.cond = !top.cond;
      keeping = top.parent && top.cond;
    } else {
      keeping = stack.pop()!.parent;
    }
  }
  return out.join("\n");
}

// one checkbox each: its marker name, the methods it adds (as the template spells them), its hover text and the
// short description beside it
// returns[i] = what methods[i] returns ("" for nothing), shown after an arrow
export type EertreeOp = { id: string; methods: string[]; returns: string[]; title: string; description: string; group?: EertreeGroup };

// the query headings in the picker, in order
export const EERTREE_GROUPS = ["Ending at R", "Starting at L", "Whole sequence"] as const;
export type EertreeGroup = (typeof EERTREE_GROUPS)[number];

export const EERTREE_UPDATES: EertreeOp[] = [
  { id: "append", returns: [""], description: "add x at the end", methods: ["append(x)"], title: "Add x to the end" },
  { id: "appendLeft", returns: [""], description: "add x at the front", methods: ["appendLeft(x)"], title: "Add x to the front" },
  { id: "pop", returns: ["the last letter"], description: "removes the last letter from the eertree", methods: ["pop()"], title: "Remove and return the last item" },
  { id: "popLeft", returns: ["the first letter"], description: "removes the first letter from the eertree", methods: ["popLeft()"], title: "Remove and return the first item" },
];

export const EERTREE_QUERIES: EertreeOp[] = [
  { id: "longestPalEndingAtCurrentR", returns: ["length"], group: "Ending at R", description: "length of the longest palindrome ending at the current right end", methods: ["longestPalEndingAtCurrentR()"], title: "Length of the longest palindrome ending at the last item" },
  { id: "numPalsEndingAtCurrentR", returns: ["count"], group: "Ending at R", description: "number of palindromic substrings ending at the current right end", methods: ["numPalsEndingAtCurrentR()"], title: "How many palindromic substrings end at the last item" },
  { id: "leftmostLForPalEndingAtR", returns: ["l"], group: "Ending at R", description: "smallest l with seq[l..r] a palindrome", methods: ["leftmostLForPalEndingAtR(r)"], title: "The smallest l such that seq[l..r] is a palindrome (the longest palindrome ending at r)" },
  { id: "leftmostLForPalEndingAtEachR", returns: ["list of l, one per r"], group: "Ending at R", description: "leftmostLForPalEndingAtR for every r", methods: ["leftmostLForPalEndingAtEachR()"], title: "res[r] = leftmostLForPalEndingAtR(r) for every r" },
  { id: "numDistinctPalsInPrefixEndingAtR", returns: ["count"], group: "Ending at R", description: "distinct palindromic substrings of seq[0..r]", methods: ["numDistinctPalsInPrefixEndingAtR(r)"], title: "How many distinct palindromic substrings seq[0..r] has" },
  { id: "numDistinctPalsInPrefixEndingAtEachR", returns: ["list of counts, one per r"], group: "Ending at R", description: "numDistinctPalsInPrefixEndingAtR for every r", methods: ["numDistinctPalsInPrefixEndingAtEachR()"], title: "res[r] = numDistinctPalsInPrefixEndingAtR(r) for every r" },
  { id: "numPalsEndingAtR", returns: ["count"], group: "Ending at R", description: "palindromic substrings ending exactly at r", methods: ["numPalsEndingAtR(r)"], title: "How many palindromic substrings end exactly at r" },
  { id: "numPalsEndingAtEachR", returns: ["list of counts, one per r"], group: "Ending at R", description: "numPalsEndingAtR for every r", methods: ["numPalsEndingAtEachR()"], title: "res[r] = numPalsEndingAtR(r) for every r" },
  { id: "longestPalStartingAtCurrentL", returns: ["length"], group: "Starting at L", description: "length of the longest palindrome starting at the current left end", methods: ["longestPalStartingAtCurrentL()"], title: "Length of the longest palindrome starting at the first item" },
  { id: "numPalsStartingAtCurrentL", returns: ["count"], group: "Starting at L", description: "number of palindromic substrings starting at the current left end", methods: ["numPalsStartingAtCurrentL()"], title: "How many palindromic substrings start at the first item" },
  { id: "rightmostRForPalStartingAtL", returns: ["r"], group: "Starting at L", description: "largest r with seq[l..r] a palindrome", methods: ["rightmostRForPalStartingAtL(l)"], title: "The largest r such that seq[l..r] is a palindrome" },
  { id: "rightmostRForPalStartingAtEachL", returns: ["list of r, one per l"], group: "Starting at L", description: "rightmostRForPalStartingAtL for every l", methods: ["rightmostRForPalStartingAtEachL()"], title: "res[l] = rightmostRForPalStartingAtL(l) for every l" },
  { id: "numDistinctPals", returns: ["count"], group: "Whole sequence", description: "number of distinct palindromic substrings", methods: ["numDistinctPals()"], title: "How many distinct palindromic substrings" },
  { id: "numPalsTotal", returns: ["count"], group: "Whole sequence", description: "number of palindromic substrings, counting repeats (\"aa\" → 3)", methods: ["numPalsTotal()"], title: "Total palindromic substrings with multiplicity (\"aa\" has 3)" },
  {
    id: "distinctPalsWithCounts", returns: ["list of (l, r, count)"], group: "Whole sequence", description: "per distinct palindrome: its first occurrence seq[l..r] and how often it occurs",
    methods: ["distinctPalsWithCounts()"],
    title: "(l, r, count) per distinct palindrome: its first occurrence and how many times it occurs",
  },
  { id: "longestPal", returns: ["length"], group: "Whole sequence", description: "length of the longest palindromic substring", methods: ["longestPal()"], title: "Length of the longest palindromic substring" },
  { id: "minPalPartition", returns: ["count"], group: "Whole sequence", description: "fewest palindromes the sequence can be cut into", methods: ["minPalPartition()"], title: "Fewest palindromes the sequence can be cut into" },
];

// A template on the frontier: which ops it has, and its constructor + op costs for a given set of ticks
export type EertreeVariant = {
  id: string;
  file: string;
  label: (ticked: ReadonlySet<string>) => string;
  // extra marker names this variant switches on in the file (e.g. which link structure append uses)
  tags?: string[];
  supports: ReadonlySet<string>;
  // the constructor, then the ticked ops, then "memory": the card's rows
  costs: (ticked: ReadonlySet<string>) => [string, string][];
  note?: (ticked: ReadonlySet<string>) => string;
};

const QUERY_COST: Record<string, string> = {
  leftmostLForPalEndingAtEachR: "N",
  rightmostRForPalStartingAtEachL: "N",
  numDistinctPalsInPrefixEndingAtEachR: "N",
  numPalsEndingAtEachR: "N",
  distinctPalsWithCounts: "N",
  minPalPartition: "N*log(N)",
};

const END_QUERIES = [
  "longestPalEndingAtCurrentR", "longestPalStartingAtCurrentL", "numPalsEndingAtCurrentR", "numPalsStartingAtCurrentL",
  "numDistinctPals", "numPalsTotal", "longestPal",
];

// the one-ended Eertree with one way to find where append goes: they only differ once append and pop are both ticked
// (append can't lean on amortization when pops undo it), trading append time against memory; σ = number of distinct items
const LINKS = [
  { tag: "quickLinks", name: "quick links", append: "log(N) expected", build: "N*log(N) expected", memory: "N" },
  { tag: "itemLinks", name: "per-item links", append: "σ expected", build: "N*σ expected", memory: "N*σ" },
  { tag: "persistentLinks", name: "persistent links", append: "log(σ) expected", build: "N*log(σ) expected", memory: "N*log(σ)" },
];
const bothEnds = (ticked: ReadonlySet<string>) => ticked.has("append") && ticked.has("pop");

export const EERTREE_VARIANTS: EertreeVariant[] = [
  ...LINKS.map(
    (link): EertreeVariant => ({
      id: `Eertree-${link.tag}`,
      file: "Eertree",
      label: (ticked) => (bothEnds(ticked) ? `Eertree (${link.name})` : "Eertree"),
      tags: [link.tag],
      supports: new Set(["append", "pop", ...EERTREE_QUERIES.map((q) => q.id)]),
      costs: (ticked) => {
        const both = bothEnds(ticked);
        const ops: [string, string][] = [["Eertree(arrOrString)", both ? link.build : "N expected"]];
        if (ticked.has("append")) ops.push(["append(x)", both ? link.append : "1 amortized expected"]);
        if (ticked.has("pop")) ops.push(["pop()", "1 expected"]);
        for (const q of EERTREE_QUERIES) if (ticked.has(q.id)) ops.push([q.methods[0], QUERY_COST[q.id] ?? "1"]);
        ops.push(["memory", both ? link.memory : "N"]);
        return ops;
      },
      note: (ticked) =>
        [
          bothEnds(ticked) && link.tag !== "quickLinks" ? "alphabet = number of distinct items." : "",
          (ticked.has("rightmostRForPalStartingAtL") || ticked.has("rightmostRForPalStartingAtEachL")) &&
          (ticked.has("append") || ticked.has("pop"))
            ? "rightmostRForPalStartingAtL rebuilds the reversed eertree in O(n) expected on its first call after an append or pop."
            : "",
        ]
          .filter(Boolean)
          .join(" "),
    }),
  ),
  {
    id: "DoubleEndedEertree",
    file: "DoubleEndedEertree",
    label: () => "Double-ended eertree",
    supports: new Set(["append", "appendLeft", ...END_QUERIES]),
    costs: (ticked) => {
      const ops: [string, string][] = [["DoubleEndedEertree(arrOrString)", "N expected"]];
      if (ticked.has("append")) ops.push(["append(x)", "1 amortized expected"]);
      if (ticked.has("appendLeft")) ops.push(["appendLeft(x)", "1 amortized expected"]);
      for (const id of END_QUERIES) if (ticked.has(id)) ops.push([`${id}()`, "1"]);
      ops.push(["memory", "N"]);
      return ops;
    },
  },
  // the deque version with the same three ways to find where a push goes; there pushes can never lean on amortization
  ...[
    { tag: "quickLinks", name: "quick links", push: "log(N) amortized expected", pop: "1 expected", build: "N*log(N) expected", memory: "N" },
    { tag: "itemLinks", name: "per-item links", push: "σ amortized expected", pop: "σ expected", build: "N*σ expected", memory: "N*σ" },
    { tag: "persistentLinks", name: "persistent links", push: "log(σ) amortized expected", pop: "log(σ) expected", build: "N*log(σ) expected", memory: "N*log(σ)" },
  ].map(
    (link): EertreeVariant => ({
      id: `DequeEertree-${link.tag}`,
      file: "DequeEertree",
      label: () => `Deque eertree (${link.name})`,
      tags: [link.tag],
      supports: new Set(["append", "appendLeft", "pop", "popLeft", ...END_QUERIES]),
      costs: (ticked) => {
        const ops: [string, string][] = [["DequeEertree(arrOrString)", link.build]];
        if (ticked.has("append")) ops.push(["append(x)", link.push]);
        if (ticked.has("appendLeft")) ops.push(["appendLeft(x)", link.push]);
        if (ticked.has("pop")) ops.push(["pop()", link.pop]);
        if (ticked.has("popLeft")) ops.push(["popLeft()", link.pop]);
        for (const id of END_QUERIES) if (ticked.has(id)) ops.push([`${id}()`, "1"]);
        ops.push(["memory", link.memory]);
        return ops;
      },
      note: () =>
        (link.tag === "quickLinks" ? "" : "alphabet = number of distinct items. ") +
        "Memory counts the largest size the deque has reached.",
    }),
  ),
];
