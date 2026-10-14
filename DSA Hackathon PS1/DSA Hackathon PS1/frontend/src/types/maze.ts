export type Position = { row: number; col: number }

export type MazeResponse = {
  grid: string[]
  size: number
  keyTypes: number
  seed: number | null
  start: Position
  exit: Position
}

export type PathStep = {
  position: Position
  cellType: string
  keyMask: number
  inventory: string[]
  keyPickedUp: string | null
  doorOpened: string | null
}

export type SolverResult = {
  solvable: boolean
  shortestPathLength: number
  path: Position[]
  pathSteps: PathStep[]
  keysCollected: string[]
  doorsOpened: string[]
  statesExplored: number
  uniqueStatesVisited: number
  executionTimeNanos: number
}

export type ApiError = { message?: string }
