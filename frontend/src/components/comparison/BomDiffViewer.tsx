interface BomDiff {
  added: Record<string, string>[]
  removed: Record<string, string>[]
  changed: Record<string, string>[]
  unchanged_count: number
  total_old: number
  total_new: number
}

export default function BomDiffViewer({ diffData }: { diffData: BomDiff; summary?: string }) {
  const allColumns = Array.from(new Set([
    ...diffData.added.flatMap(Object.keys),
    ...diffData.removed.flatMap(Object.keys),
    ...diffData.changed.flatMap(Object.keys),
  ])).filter(c => !c.endsWith('_old') && !c.endsWith('_new') && c !== '_merge')

  return (
    <div>
      {/* Summary badges */}
      <div className="flex gap-3 mb-4">
        {diffData.added.length > 0 && (
          <span className="inline-flex items-center gap-1 bg-green-100 text-green-700 text-sm font-medium px-3 py-1 rounded-full">
            +{diffData.added.length} Teile neu
          </span>
        )}
        {diffData.removed.length > 0 && (
          <span className="inline-flex items-center gap-1 bg-red-100 text-red-700 text-sm font-medium px-3 py-1 rounded-full">
            -{diffData.removed.length} Teile entfernt
          </span>
        )}
        {diffData.changed.length > 0 && (
          <span className="inline-flex items-center gap-1 bg-yellow-100 text-yellow-700 text-sm font-medium px-3 py-1 rounded-full">
            ~{diffData.changed.length} geändert
          </span>
        )}
        <span className="text-sm text-gray-500 ml-auto">{diffData.unchanged_count} unverändert</span>
      </div>

      {/* Stückliste diff table */}
      <div className="overflow-x-auto rounded-lg border border-gray-200">
        <table className="w-full text-xs">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="px-3 py-2 text-left font-medium text-gray-600 w-20">Status</th>
              {allColumns.map(col => (
                <th key={col} className="px-3 py-2 text-left font-medium text-gray-600">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {diffData.added.map((row, i) => (
              <tr key={`add-${i}`} className="bg-green-50 border-l-4 border-green-400">
                <td className="px-3 py-2 font-medium text-green-700">NEU</td>
                {allColumns.map(col => <td key={col} className="px-3 py-2 text-gray-800">{row[col] ?? ''}</td>)}
              </tr>
            ))}
            {diffData.removed.map((row, i) => (
              <tr key={`rm-${i}`} className="bg-red-50 border-l-4 border-red-400 opacity-70">
                <td className="px-3 py-2 font-medium text-red-700">ENTFERNT</td>
                {allColumns.map(col => <td key={col} className="px-3 py-2 text-gray-600 line-through">{row[col] ?? ''}</td>)}
              </tr>
            ))}
            {diffData.changed.map((row, i) => (
              <tr key={`chg-${i}`} className="bg-yellow-50 border-l-4 border-yellow-400">
                <td className="px-3 py-2 font-medium text-yellow-700">GEÄNDERT</td>
                {allColumns.map(col => {
                  const oldVal = row[`${col}_old`] ?? row[col] ?? ''
                  const newVal = row[`${col}_new`] ?? row[col] ?? ''
                  const changed = oldVal !== newVal && (row[`${col}_old`] !== undefined)
                  return (
                    <td key={col} className="px-3 py-2">
                      {changed ? (
                        <span>
                          <span className="line-through text-red-500 mr-1">{oldVal}</span>
                          <span className="text-green-600 font-medium">{newVal}</span>
                        </span>
                      ) : (
                        <span className="text-gray-700">{newVal || oldVal}</span>
                      )}
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
        {diffData.added.length === 0 && diffData.removed.length === 0 && diffData.changed.length === 0 && (
          <div className="py-8 text-center text-gray-400 text-sm">Keine Änderungen gefunden</div>
        )}
      </div>

      <p className="text-xs text-gray-400 mt-2">{diffData.unchanged_count} weitere unveränderte Teile nicht angezeigt</p>
    </div>
  )
}
