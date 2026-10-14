import { useEffect, useMemo, useRef, useState } from 'react'
import {
  ArrowDownToLine, ArrowLeft, ArrowRight, Check, ChevronDown, CircleHelp, DoorClosed, KeyRound,
  LoaderCircle, Pause, Play, RotateCcw, Shuffle, Sparkles, Upload, Waypoints,
} from 'lucide-react'
import { exportMaze, generateMaze, solveMaze, uploadMaze } from './services/api'
import type { MazeResponse, Position, SolverResult } from './types/maze'

const keyColors = ['#f2a93b', '#d46ad2', '#16a6a1', '#5a83e8', '#e4776e', '#94a33d']
const samePosition = (a: Position | undefined, b: Position) => !!a && a.row === b.row && a.col === b.col

function App() {
  const [maze, setMaze] = useState<MazeResponse | null>(null)
  const [solution, setSolution] = useState<SolverResult | null>(null)
  const [size, setSize] = useState(15)
  const [keyTypes, setKeyTypes] = useState(3)
  const [seed, setSeed] = useState('')
  const [busy, setBusy] = useState(false)
  const [running, setRunning] = useState(false)
  const [step, setStep] = useState(0)
  const [speed, setSpeed] = useState(5)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const fileInput = useRef<HTMLInputElement>(null)

  const currentStep = solution?.pathSteps[step]
  const currentPosition = currentStep?.position
  const pathCells = useMemo(() => new Set(solution?.path.map(p => `${p.row}:${p.col}`) ?? []), [solution])
  const inventory = currentStep?.inventory ?? []
  const completed = !!solution?.solvable && step >= solution.pathSteps.length - 1

  useEffect(() => {
    if (!running || !solution?.solvable) return
    const delay = Math.max(90, 1050 - speed * 175)
    const last = solution.pathSteps.length - 1
    if (step >= last) { setRunning(false); return }
    const timer = window.setTimeout(() => setStep(step + 1), delay)
    return () => window.clearTimeout(timer)
  }, [running, solution, speed, step])

  function loadMaze(next: MazeResponse, message: string) {
    setMaze(next)
    setKeyTypes(next.keyTypes)
    setSize(next.size)
    setSolution(null)
    setStep(0)
    setRunning(false)
    setError('')
    setNotice(message)
  }

  async function handleGenerate() {
    setBusy(true); setError(''); setNotice('')
    try {
      const parsedSeed = seed.trim() === '' ? undefined : Number(seed)
      if (parsedSeed !== undefined && !Number.isSafeInteger(parsedSeed)) throw new Error('Seed must be a whole number.')
      const next = await generateMaze(size, keyTypes, parsedSeed)
      loadMaze(next, `Generated a ${next.size} × ${next.size} maze${next.seed == null ? '' : ` with seed ${next.seed}`}.`)
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not generate the maze.') }
    finally { setBusy(false) }
  }

  async function handleSolve() {
    if (!maze) return
    setBusy(true); setError(''); setNotice('')
    try {
      const result = await solveMaze(maze)
      setSolution(result); setStep(0); setRunning(false)
      setNotice(result.solvable ? 'Shortest path is ready to play.' : 'This maze has no valid route to the exit.')
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not solve this maze.') }
    finally { setBusy(false) }
  }

  async function handleUpload(file?: File) {
    if (!file) return
    setBusy(true); setError(''); setNotice('')
    try { loadMaze(await uploadMaze(file, keyTypes), `Loaded ${file.name}.`) }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not read this maze file.') }
    finally { setBusy(false); if (fileInput.current) fileInput.current.value = '' }
  }

  async function handleExport() {
    if (!maze) return
    setBusy(true); setError('')
    try {
      const blob = await exportMaze(maze)
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a'); link.href = url; link.download = 'maze-solution.csv'; link.click()
      URL.revokeObjectURL(url); setNotice('Path-marked CSV downloaded.')
    } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not export this maze.') }
    finally { setBusy(false) }
  }

  function resetPlayback() { setRunning(false); setStep(0) }
  function moveStep(direction: -1 | 1) {
    if (!solution?.solvable) return
    setRunning(false)
    setStep(previous => Math.max(0, Math.min(solution.pathSteps.length - 1, previous + direction)))
  }

  return <main className="app-shell">
    <header className="topbar">
      <a className="brand" href="#top" aria-label="Maze Lab home"><span className="brand-mark"><Waypoints size={20} /></span><span>PATHFINDER<span className="brand-light"> LAB</span></span></a>
      <div className="topbar-right"><span className="live-dot" /> JAVA BFS ENGINE <span className="topbar-divider">·</span> READY</div>
    </header>

    <div className="page-wrap" id="top">
      <section className="hero">
        <div className="hero-copy">
          <div className="eyebrow"><Sparkles size={14} /> ALGORITHM PLAYGROUND <span className="eyebrow-line" /></div>
          <h1>Maze with <span>Keys &amp; Doors</span></h1>
          <p>Find the shortest route through a maze where every key changes what paths are possible.</p>
        </div>
        <div className="hero-chip"><span className="hero-chip-icon"><Waypoints size={18} /></span><span><b>Shortest-path visualizer</b><small>BFS · State-aware search</small></span></div>
      </section>

      <div className="workspace">
        <aside className="control-column">
          <section className="panel setup-panel">
            <div className="panel-heading"><span className="heading-icon"><Shuffle size={17} /></span><div><h2>Maze setup</h2><p>Build or bring your own puzzle</p></div></div>
            <label className="field-label" htmlFor="size">Grid size <span>{size} × {size}</span></label>
            <div className="select-wrap"><select id="size" value={size} onChange={e => setSize(Number(e.target.value))}>{[9, 11, 13, 15, 17, 19, 21, 25].map(n => <option key={n} value={n} disabled={n < keyTypes + 4}>{n} × {n}</option>)}</select><ChevronDown size={15} /></div>
            <label className="field-label" htmlFor="keys">Key / door pairs <span>1–6 types</span></label>
            <div className="select-wrap"><select id="keys" value={keyTypes} onChange={e => { const next = Number(e.target.value); setKeyTypes(next); if (size < next + 4) setSize([9, 11, 13, 15, 17, 19, 21, 25].find(candidate => candidate >= next + 4) ?? 25) }}>{[1, 2, 3, 4, 5, 6].map(n => <option key={n} value={n}>{n} {n === 1 ? 'pair' : 'pairs'}</option>)}</select><ChevronDown size={15} /></div>
            <label className="field-label" htmlFor="seed">Random seed <span>Optional</span></label>
            <input id="seed" className="seed-input" inputMode="numeric" placeholder="e.g. 2026" value={seed} onChange={e => setSeed(e.target.value)} />
            <button className="button button-primary full-button" onClick={handleGenerate} disabled={busy}>
              {busy ? <LoaderCircle className="spin" size={17} /> : <Shuffle size={16} />} Generate maze
            </button>
            <div className="or-divider"><span>OR</span></div>
            <input ref={fileInput} className="visually-hidden" type="file" accept=".csv,text/csv" onChange={e => void handleUpload(e.target.files?.[0])} />
            <button className="button button-secondary full-button" onClick={() => fileInput.current?.click()} disabled={busy}><Upload size={16} /> Upload maze CSV</button>
            <div className="field-hint"><CircleHelp size={13} /> CSV cells use comma-separated maze symbols.</div>
          </section>

          <section className="panel legend-panel">
            <div className="panel-heading compact-heading"><span className="heading-icon heading-icon-quiet"><CircleHelp size={16} /></span><div><h2>Cell legend</h2></div></div>
            <div className="legend-grid">
              <LegendItem symbol="S" label="Start" className="legend-start" />
              <LegendItem symbol="E" label="Exit" className="legend-exit" />
              <LegendItem symbol="·" label="Open" className="legend-open" />
              <LegendItem symbol="" label="Wall" className="legend-wall" />
              <LegendItem symbol="a" label="Key" className="legend-key" />
              <LegendItem symbol="A" label="Locked door" className="legend-door" />
              <LegendItem symbol="" label="Shortest path" className="legend-path" />
              <LegendItem symbol="●" label="Player" className="legend-player" />
            </div>
          </section>
        </aside>

        <section className="panel maze-panel">
          <div className="maze-panel-head">
            <div><div className="section-kicker">YOUR PUZZLE</div><h2>{maze ? 'Maze board' : 'Ready for a maze?'}</h2></div>
            <div className="board-meta">{maze ? <><span className="meta-dot" /> {maze.size} × {maze.size} <span className="meta-separator">/</span> {maze.keyTypes} key types</> : <span>Generate or upload to begin</span>}</div>
          </div>
          <div className={`board-stage ${maze ? '' : 'board-empty'}`}>
            {maze ? <div className="maze-scroll"><div className="maze-grid" style={{ '--grid-size': maze.grid.length, '--cell-font': `${Math.max(8, Math.min(17, 420 / maze.grid.length))}px` } as React.CSSProperties}>
              {maze.grid.flatMap((row, rowIndex) => [...row].map((cell, colIndex) => {
                const position = { row: rowIndex, col: colIndex }
                const isExit = samePosition(maze.exit, position)
                const isStart = samePosition(maze.start, position)
                const isKey = cell >= 'a' && cell <= 'f'
                const isDoor = cell >= 'A' && cell <= 'F' && !isExit
                const keyIndex = isKey ? cell.charCodeAt(0) - 97 : isDoor ? cell.charCodeAt(0) - 65 : 0
                const cellName = isStart ? 'start' : isExit ? 'exit' : cell === '#' ? 'wall' : isKey ? 'key' : isDoor ? 'door' : 'open'
                const onPath = pathCells.has(`${rowIndex}:${colIndex}`)
                const isPlayer = samePosition(currentPosition, position)
                const label = isStart ? 'S' : isExit ? 'E' : isDoor ? cell : isKey ? cell : cell === '#' ? '' : '·'
                return <div key={`${rowIndex}-${colIndex}`} className={`cell cell-${cellName}${onPath ? ' on-path' : ''}${isPlayer ? ' is-player' : ''}`} style={isKey || isDoor ? { '--cell-accent': keyColors[keyIndex] } as React.CSSProperties : undefined} title={isDoor ? `Door ${cell}${inventory.includes(cell.toLowerCase()) ? ' · unlocked' : ' · locked'}` : isKey ? `Key ${cell}` : cellName}>
                  {label}{isPlayer && !isStart && !isExit && <span className="player-token" aria-label="Player">●</span>}
                </div>
              }))}
            </div></div> : <div className="empty-state"><div className="empty-maze-icon"><Waypoints size={26} /></div><h3>Your next move starts here</h3><p>Generate a seeded maze or upload a CSV to see the board.</p><span>JAVA-POWERED · DETERMINISTIC · INTERACTIVE</span></div>}
          </div>
          <div className="board-footer">
            <div className="inventory-area"><span className="footer-label">KEY RING</span><div className="key-ring">
              {Array.from({ length: maze?.keyTypes ?? keyTypes }, (_, i) => {
                const key = String.fromCharCode(97 + i), collected = inventory.includes(key)
                return <span key={key} className={`inventory-key${collected ? ' collected' : ''}`} style={{ '--cell-accent': keyColors[i] } as React.CSSProperties} title={collected ? `Key ${key} collected` : `Key ${key} not collected`}><KeyRound size={12} />{key}</span>
              })}
            </div></div>
            <div className="position-readout"><span className="footer-label">PLAYER</span><b>{currentPosition ? `R${currentPosition.row + 1} · C${currentPosition.col + 1}` : maze ? `R${maze.start.row + 1} · C${maze.start.col + 1}` : '—'}</b></div>
            <div className="position-readout step-readout"><span className="footer-label">STEP</span><b>{solution?.solvable ? `${step} / ${solution.shortestPathLength}` : '—'}</b></div>
          </div>
        </section>
      </div>

      <div className="lower-grid">
        <section className="panel playback-panel">
          <div className="panel-heading playback-heading"><span className="heading-icon"><Play size={16} /></span><div><h2>Path playback</h2><p>Animate the shortest route step by step</p></div><span className={`status-pill ${solution?.solvable ? 'status-ready' : ''}`}>{solution ? solution.solvable ? completed ? 'COMPLETE' : 'PATH READY' : 'NO ROUTE' : 'WAITING'}</span></div>
          <div className="playback-controls">
            <button className="icon-button" onClick={() => moveStep(-1)} disabled={!solution?.solvable || step <= 0} title="Previous step"><ArrowLeft size={17} /></button>
            <button className="play-button" onClick={() => {
              if (!solution?.solvable) return
              if (completed) setStep(0)
              setRunning(true)
            }} disabled={!solution?.solvable || running} title="Play path"><Play size={16} fill="currentColor" /></button>
            <button className="icon-button" onClick={() => setRunning(false)} disabled={!running} title="Pause"><Pause size={17} /></button>
            <button className="icon-button" onClick={() => moveStep(1)} disabled={!solution?.solvable || completed} title="Next step"><ArrowRight size={17} /></button>
            <button className="icon-button reset-button" onClick={resetPlayback} disabled={!solution} title="Reset playback"><RotateCcw size={16} /></button>
            <div className="speed-control"><span>SPEED</span><input aria-label="Animation speed" type="range" min="1" max="6" value={speed} onChange={e => setSpeed(Number(e.target.value))} /><b>{speed}×</b></div>
          </div>
          <div className="scrub-row"><span>START</span><input aria-label="Path step" type="range" min="0" max={Math.max(0, (solution?.pathSteps.length ?? 1) - 1)} value={step} onChange={e => { setRunning(false); setStep(Number(e.target.value)) }} disabled={!solution?.solvable} /><span>EXIT</span></div>
          {currentStep?.keyPickedUp && <div className="event-note event-key"><KeyRound size={14} /> Picked up key <b>{currentStep.keyPickedUp}</b></div>}
          {currentStep?.doorOpened && <div className="event-note event-door"><DoorClosed size={14} /> Unlocked door <b>{currentStep.doorOpened}</b></div>}
        </section>

        <section className="panel results-panel">
          <div className="panel-heading results-heading"><span className="heading-icon heading-icon-quiet"><Sparkles size={16} /></span><div><h2>Solver results</h2><p>Measured by the Java backend</p></div></div>
          <div className="result-primary"><div><span className="result-label">SHORTEST PATH</span><div className="result-value">{solution?.solvable ? <>{solution.shortestPathLength}<small> moves</small></> : '—'}</div></div><span className={`result-badge ${solution?.solvable ? 'result-success' : ''}`}>{solution?.solvable ? <><Check size={13} /> SOLVABLE</> : solution ? 'UNSOLVABLE' : 'NOT RUN'}</span></div>
          <div className="stat-grid">
            <Stat label="States explored" value={solution?.statesExplored.toLocaleString() ?? '—'} />
            <Stat label="Unique states" value={solution?.uniqueStatesVisited.toLocaleString() ?? '—'} />
            <Stat label="Keys collected" value={solution ? `${solution.keysCollected.length} / ${maze?.keyTypes ?? keyTypes}` : '—'} />
            <Stat label="Doors traversed" value={solution?.doorsOpened.length.toString() ?? '—'} />
            <Stat label="Solve time" value={solution ? `${(solution.executionTimeNanos / 1_000_000).toFixed(3)} ms` : '—'} />
            <Stat label="Grid dimensions" value={maze ? `${maze.size} × ${maze.size}` : '—'} />
          </div>
          <div className="result-actions">
            <button className="button button-secondary" onClick={handleSolve} disabled={!maze || busy}>{busy ? <LoaderCircle className="spin" size={15} /> : <Waypoints size={15} />} Solve maze</button>
            <button className="button button-export" onClick={handleExport} disabled={!maze || !solution?.solvable || busy}><ArrowDownToLine size={15} /> Export CSV</button>
          </div>
        </section>
      </div>

      {(error || notice) && <div className={`message-bar ${error ? 'message-error' : 'message-success'}`} role={error ? 'alert' : 'status'}>{error || notice}<button onClick={() => { setError(''); setNotice('') }} aria-label="Dismiss">×</button></div>}

      <section className="panel explanation-panel">
        <div className="explanation-title"><span className="heading-icon heading-icon-quiet"><CircleHelp size={16} /></span><div><h2>How the solver finds the way</h2><p>Every move has equal cost, so a breadth-first search guarantees the shortest valid route.</p></div></div>
        <div className="explanation-grid">
          <article><span className="explanation-number">01</span><h3>State = position + keys</h3><p>The Java solver models each visit as <code>(row, column, keyMask)</code>. A bitmask records which keys have been collected.</p></article>
          <article><span className="explanation-number">02</span><h3>Legal transitions only</h3><p>Walls block movement. A door opens only if its key bit is already set; entering a key cell updates the inventory immediately.</p></article>
          <article><span className="explanation-number">03</span><h3>First exit is shortest</h3><p>FIFO BFS explores states by distance. Parent pointers reconstruct the first valid exit path without copying paths during search.</p></article>
          <article><span className="explanation-number">04</span><h3>Bounded state space</h3><p>At most <code>N² × 2ᵀ</code> states, with four moves each. For up to six key types, BFS stays practical.</p></article>
        </div>
        <div className="proof-strip"><b>Why it is optimal:</b> unit-cost transitions + breadth-first order + distinct inventory states mean the first reachable exit state has the minimum move count. Parent pointers preserve that legal route. <span>Compared with DFS, BFS is optimal; Dijkstra is unnecessary for unit costs, and A* needs a heuristic while keeping the same augmented state.</span></div>
      </section>

      <footer className="page-footer"><span>PATHFINDER LAB <span className="footer-muted">· MAZE WITH KEYS &amp; DOORS</span></span><span>JAVA 17+ <i /> SPRING BOOT <i /> REACT</span></footer>
    </div>
  </main>
}

function LegendItem({ symbol, label, className }: { symbol: string; label: string; className: string }) {
  return <div className="legend-item"><span className={`legend-swatch ${className}`}>{symbol}</span><span>{label}</span></div>
}

function Stat({ label, value }: { label: string; value: string }) {
  return <div className="stat-item"><span>{label}</span><b>{value}</b></div>
}

export default App
