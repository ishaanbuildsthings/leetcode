"use client";

/* ── Sliding Window ──────────────────────────────────────── */
function SlidingWindow() {
  const cells = [2, 7, 1, 8, 3, 5, 4];
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative flex gap-1">
        {cells.map((v, i) => (
          <div
            key={i}
            className="flex h-9 w-9 items-center justify-center rounded-md bg-gray-100 text-xs font-semibold text-gray-500"
          >
            {v}
          </div>
        ))}
        {/* sliding window overlay */}
        <div
          className="pointer-events-none absolute top-0 h-9 rounded-md border-2 border-lime-500 bg-lime-400/15"
          style={{
            width: "calc(3 * 2.25rem + 2 * 0.25rem)",
            animation: "slideWindow 4s ease-in-out infinite",
          }}
        />
      </div>
      <span className="text-xs font-medium text-gray-400">Sliding Window</span>
    </div>
  );
}

/* ── Binary Tree BFS ─────────────────────────────────────── */
function TreeTraversal() {
  /*  Layout (cx,cy) for a 3-level binary tree inside a 160×90 viewbox */
  const nodes = [
    { cx: 80, cy: 16 },
    { cx: 44, cy: 46 },
    { cx: 116, cy: 46 },
    { cx: 26, cy: 76 },
    { cx: 62, cy: 76 },
    { cx: 98, cy: 76 },
    { cx: 134, cy: 76 },
  ];
  const edges: [number, number][] = [
    [0, 1],
    [0, 2],
    [1, 3],
    [1, 4],
    [2, 5],
    [2, 6],
  ];

  return (
    <div className="flex flex-col items-center gap-3">
      <svg viewBox="0 0 160 92" className="h-[92px] w-[160px]">
        {edges.map(([a, b], i) => (
          <line
            key={i}
            x1={nodes[a].cx}
            y1={nodes[a].cy}
            x2={nodes[b].cx}
            y2={nodes[b].cy}
            stroke="#e5e7eb"
            strokeWidth={2}
          />
        ))}
        {nodes.map((n, i) => (
          <circle
            key={i}
            cx={n.cx}
            cy={n.cy}
            r={10}
            fill="#f3f4f6"
            stroke="#d1d5db"
            strokeWidth={1.5}
            style={{
              animation: `bfsNode 3.5s ease-in-out infinite`,
              animationDelay: `${i * 0.35}s`,
            }}
          />
        ))}
      </svg>
      <span className="text-xs font-medium text-gray-400">Tree Traversal</span>
    </div>
  );
}

/* ── Two Pointers ────────────────────────────────────────── */
function TwoPointers() {
  const cells = [1, 3, 5, 7, 9, 11, 13];
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative flex gap-1">
        {cells.map((v, i) => (
          <div
            key={i}
            className="flex h-9 w-9 items-center justify-center rounded-md bg-gray-100 text-xs font-semibold text-gray-500"
          >
            {v}
          </div>
        ))}
        {/* left pointer */}
        <div
          className="absolute -bottom-4 text-[10px] font-bold text-emerald-500"
          style={{ animation: "ptrLeft 4s ease-in-out infinite" }}
        >
          L
        </div>
        {/* right pointer */}
        <div
          className="absolute -bottom-4 text-[10px] font-bold text-rose-500"
          style={{ animation: "ptrRight 4s ease-in-out infinite" }}
        >
          R
        </div>
      </div>
      <span className="mt-3 text-xs font-medium text-gray-400">
        Two Pointers
      </span>
    </div>
  );
}

/* ── Exported wrapper ────────────────────────────────────── */
export function PatternAnimations() {
  /* cell width = 2.25rem = 36px, gap = 0.25rem = 4px  →  step = 40px */
  return (
    <>
      <style>{`
        @keyframes slideWindow {
          0%, 10%   { transform: translateX(0); }
          20%, 30%  { transform: translateX(40px); }
          40%, 50%  { transform: translateX(80px); }
          60%, 70%  { transform: translateX(120px); }
          80%, 90%  { transform: translateX(160px); }
          100%      { transform: translateX(0); }
        }
        @keyframes bfsNode {
          0%, 100%  { fill: #f3f4f6; stroke: #d1d5db; }
          30%, 60%  { fill: #a3e635; stroke: #84cc16; }
        }
        @keyframes ptrLeft {
          0%, 10%   { left: 12px; }
          30%, 40%  { left: 52px; }
          60%, 70%  { left: 92px; }
          85%, 100% { left: 12px; }
        }
        @keyframes ptrRight {
          0%, 10%   { left: 252px; }
          30%, 40%  { left: 212px; }
          60%, 70%  { left: 172px; }
          85%, 100% { left: 252px; }
        }
      `}</style>
      <div className="flex flex-wrap items-end justify-center gap-10 md:gap-14">
        <SlidingWindow />
        <TreeTraversal />
        <TwoPointers />
      </div>
    </>
  );
}
