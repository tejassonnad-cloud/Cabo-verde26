import type { ApiError, MazeResponse, SolverResult } from '../types/maze'

async function parseResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const body = await response.json().catch(() => ({} as ApiError)) as ApiError
    throw new Error(body.message ?? `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export async function generateMaze(size: number, keyTypes: number, seed?: number): Promise<MazeResponse> {
  return parseResponse(await fetch('/api/mazes/generate', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ size, keyTypes, ...(seed === undefined ? {} : { seed }) }),
  }))
}

export async function solveMaze(maze: MazeResponse): Promise<SolverResult> {
  return parseResponse(await fetch('/api/mazes/solve', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ grid: maze.grid, keyTypes: maze.keyTypes }),
  }))
}

export async function uploadMaze(file: File, keyTypes: number): Promise<MazeResponse> {
  const body = new FormData()
  body.append('file', file)
  body.append('keyTypes', String(keyTypes))
  return parseResponse(await fetch('/api/mazes/upload', { method: 'POST', body }))
}

export async function exportMaze(maze: MazeResponse): Promise<Blob> {
  const response = await fetch('/api/mazes/export', {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ grid: maze.grid, keyTypes: maze.keyTypes }),
  })
  if (!response.ok) {
    const body = await response.json().catch(() => ({} as ApiError)) as ApiError
    throw new Error(body.message ?? `Export failed (${response.status})`)
  }
  return response.blob()
}
