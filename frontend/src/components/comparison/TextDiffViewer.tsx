interface TextHunk {
  type: 'insert' | 'delete' | 'replace'
  lines_a: string[]
  lines_b: string[]
  pos_a: [number, number]
  pos_b: [number, number]
}

interface TextDiff {
  hunks: TextHunk[]
  lines_a: number
  lines_b: number
}

export default function TextDiffViewer({ diffData }: { diffData: TextDiff; summary?: string }) {
  if (!diffData.hunks?.length) {
    return <div className="py-8 text-center text-gray-400 text-sm">Keine Textänderungen gefunden</div>
  }

  return (
    <div className="space-y-2">
      <p className="text-sm text-gray-500 mb-3">
        Alt: {diffData.lines_a} Zeilen → Neu: {diffData.lines_b} Zeilen
      </p>
      <div className="font-mono text-xs bg-gray-900 text-gray-100 rounded-lg overflow-auto max-h-[60vh] p-4 space-y-4">
        {diffData.hunks.map((hunk, i) => (
          <div key={i}>
            <div className="text-gray-500 mb-1 text-[10px]">
              @@ -{hunk.pos_a[0] + 1},{hunk.lines_a.length} +{hunk.pos_b[0] + 1},{hunk.lines_b.length} @@
            </div>
            {hunk.type !== 'insert' && hunk.lines_a.map((line, j) => (
              <div key={`a-${j}`} className="bg-red-900/40 text-red-300 px-2 py-0.5">
                - {line}
              </div>
            ))}
            {hunk.type !== 'delete' && hunk.lines_b.map((line, j) => (
              <div key={`b-${j}`} className="bg-green-900/40 text-green-300 px-2 py-0.5">
                + {line}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  )
}
