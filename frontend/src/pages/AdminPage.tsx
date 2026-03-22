import { useState } from 'react'
import { authApi } from '../api'
import { useAuthStore } from '../stores/authStore'
import { Navigate } from 'react-router-dom'

export default function AdminPage() {
  const { user } = useAuthStore()
  const [form, setForm] = useState({ username: '', email: '', password: '', is_admin: false })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  if (!user?.is_admin) return <Navigate to="/" />

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setMessage('')
    try {
      await authApi.register(form)
      setMessage(`Benutzer "${form.username}" erstellt`)
      setForm({ username: '', email: '', password: '', is_admin: false })
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Fehler beim Erstellen')
    }
  }

  return (
    <div className="space-y-6 max-w-md">
      <h1 className="text-2xl font-bold text-gray-900">Benutzerverwaltung</h1>

      <div className="bg-white border border-gray-200 rounded-xl p-5">
        <h2 className="font-semibold text-gray-800 mb-4">Neuen Benutzer erstellen</h2>
        <form onSubmit={handleCreate} className="space-y-3">
          <input
            type="text"
            placeholder="Benutzername"
            value={form.username}
            onChange={e => setForm(p => ({ ...p, username: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="email"
            placeholder="E-Mail"
            value={form.email}
            onChange={e => setForm(p => ({ ...p, email: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <input
            type="password"
            placeholder="Passwort"
            value={form.password}
            onChange={e => setForm(p => ({ ...p, password: e.target.value }))}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <label className="flex items-center gap-2 text-sm text-gray-700">
            <input
              type="checkbox"
              checked={form.is_admin}
              onChange={e => setForm(p => ({ ...p, is_admin: e.target.checked }))}
            />
            Admin-Rechte
          </label>
          {error && <p className="text-red-500 text-sm">{error}</p>}
          {message && <p className="text-green-600 text-sm">{message}</p>}
          <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 rounded-lg text-sm font-medium">
            Benutzer erstellen
          </button>
        </form>
      </div>
    </div>
  )
}
