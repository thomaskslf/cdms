import { useCallback, useRef, useState } from 'react'
import { Upload } from 'lucide-react'
import type { DocType } from '../../types'
import { ALL_DOC_TYPES, DOC_TYPE_LABELS } from '../../types'
import { useUploadDocument, useUploadBatch } from '../../hooks'

interface Props {
  projectId: number
  onSuccess: () => void
}

const SUPPORTED_EXT = ['.pdf', '.xlsx', '.xls', '.csv', '.dxf', '.dwg', '.jpg', '.jpeg', '.png', '.tiff', '.tif']

export default function DropZone({ projectId, onSuccess }: Props) {
  const [dragOver, setDragOver] = useState(false)
  const [files, setFiles] = useState<File[]>([])
  const [folderPaths, setFolderPaths] = useState<string[]>([])
  const [overrides, setOverrides] = useState<Record<number, DocType | ''>>({})
  const [changeSummary, setChangeSummary] = useState('')
  const [pathInput, setPathInput] = useState('')
  const [mode, setMode] = useState<'upload' | 'path'>('upload')
  const [results, setResults] = useState<string[]>([])
  const [loading, setLoading] = useState(false)

  const fileInputRef = useRef<HTMLInputElement>(null)
  const uploadDoc = useUploadDocument()
  const uploadBatch = useUploadBatch()

  const addFiles = (newFiles: FileList | File[]) => {
    const supported = Array.from(newFiles).filter(f =>
      SUPPORTED_EXT.some(ext => f.name.toLowerCase().endsWith(ext))
    )
    const paths = Array.from(newFiles).map(f => {
      const rel = (f as { webkitRelativePath?: string }).webkitRelativePath || ''
      return rel.includes('/') ? rel.split('/').slice(0, -1).join('/') : ''
    })
    setFiles(prev => [...prev, ...supported])
    setFolderPaths(prev => [...prev, ...paths.slice(0, supported.length)])
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)
    addFiles(e.dataTransfer.files)
  }, [])

  const handleSubmit = async () => {
    if (!files.length) return
    setLoading(true)
    setResults([])
    try {
      if (files.length === 1) {
        const formData = new FormData()
        formData.append('file', files[0])
        formData.append('project_id', String(projectId))
        if (changeSummary) formData.append('change_summary', changeSummary)
        if (folderPaths[0]) formData.append('folder_path', folderPaths[0])
        if (overrides[0]) formData.append('doc_type_override', overrides[0])
        const result = await uploadDoc.mutateAsync(formData)
        setResults([`${result.document.name} — v${result.version.version_number} ${result.is_duplicate ? '(Duplikat)' : 'hochgeladen'}`])
      } else {
        const formData = new FormData()
        files.forEach(f => formData.append('files', f))
        formData.append('project_id', String(projectId))
        formData.append('folder_paths', JSON.stringify(folderPaths))
        if (changeSummary) formData.append('change_summary', changeSummary)
        const batchResults = await uploadBatch.mutateAsync(formData)
        setResults(batchResults.map(r => `${r.document.name} — v${r.version.version_number}`))
      }
      setFiles([])
      setFolderPaths([])
      setOverrides({})
      onSuccess()
    } catch (err) {
      setResults(['Fehler beim Upload. Bitte prüfe die Dateien.'])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex gap-2 mb-3">
        <button
          onClick={() => setMode('upload')}
          className={`text-sm px-3 py-1 rounded-full ${mode === 'upload' ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-500 hover:text-gray-700'}`}
        >
          Dateien hochladen
        </button>
        <button
          onClick={() => setMode('path')}
          className={`text-sm px-3 py-1 rounded-full ${mode === 'path' ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-500 hover:text-gray-700'}`}
        >
          Lokalen Pfad scannen
        </button>
      </div>

      {mode === 'upload' ? (
        <>
          <div
            onDrop={handleDrop}
            onDragOver={e => { e.preventDefault(); setDragOver(true) }}
            onDragLeave={() => setDragOver(false)}
            onClick={() => fileInputRef.current?.click()}
            className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors ${
              dragOver ? 'border-blue-400 bg-blue-50' : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
            <p className="text-sm text-gray-600">Dateien oder Ordner hier ablegen</p>
            <p className="text-xs text-gray-400 mt-1">PDF, Excel, CSV, DXF, DWG, Bilder</p>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              // @ts-ignore - webkitdirectory is non-standard but widely supported
              webkitdirectory=""
              className="hidden"
              onChange={e => e.target.files && addFiles(e.target.files)}
            />
          </div>

          {files.length > 0 && (
            <div className="space-y-2">
              <p className="text-sm font-medium text-gray-700">{files.length} Datei(en) ausgewählt</p>
              <div className="max-h-48 overflow-y-auto space-y-1">
                {files.map((f, i) => (
                  <div key={i} className="flex items-center gap-2 text-sm">
                    <span className="flex-1 text-gray-700 truncate">{folderPaths[i] ? `${folderPaths[i]}/` : ''}{f.name}</span>
                    <select
                      value={overrides[i] || ''}
                      onChange={e => setOverrides(prev => ({ ...prev, [i]: e.target.value as DocType | '' }))}
                      className="text-xs border border-gray-200 rounded px-1 py-0.5 text-gray-600"
                    >
                      <option value="">Auto-Erkennung</option>
                      {ALL_DOC_TYPES.map(t => (
                        <option key={t} value={t}>{DOC_TYPE_LABELS[t]}</option>
                      ))}
                    </select>
                    <button onClick={() => setFiles(prev => prev.filter((_, j) => j !== i))} className="text-gray-400 hover:text-red-500 text-xs">✕</button>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Lokaler Ordnerpfad</label>
            <div className="flex gap-2">
              <input
                type="text"
                value={pathInput}
                onChange={e => setPathInput(e.target.value)}
                placeholder="C:\Kunden\Firma_AG\Projekt_2024"
                className="flex-1 text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <p className="text-xs text-gray-400 mt-1">Alle unterstützten Dateien im Ordner werden rekursiv importiert.</p>
          </div>
        </div>
      )}

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Änderungsnotiz (optional)</label>
        <input
          type="text"
          value={changeSummary}
          onChange={e => setChangeSummary(e.target.value)}
          placeholder="z.B. Rev. B – Stückliste aktualisiert"
          className="w-full text-sm border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || (mode === 'upload' ? files.length === 0 : !pathInput.trim())}
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 rounded-lg text-sm disabled:opacity-40"
      >
        {loading ? 'Verarbeite...' : mode === 'upload' ? `${files.length || ''} Datei(en) hochladen` : 'Ordner scannen'}
      </button>

      {results.length > 0 && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-3 space-y-1">
          {results.map((r, i) => (
            <p key={i} className="text-xs text-green-700">{r}</p>
          ))}
        </div>
      )}
    </div>
  )
}
