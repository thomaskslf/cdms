import { create } from 'zustand'
import type { User } from '../types'

interface AuthState {
  token: string | null
  user: User | null
  setAuth: (token: string, user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  token: localStorage.getItem('cdms_token'),
  user: (() => {
    try { return JSON.parse(localStorage.getItem('cdms_user') || 'null') } catch { return null }
  })(),
  setAuth: (token, user) => {
    localStorage.setItem('cdms_token', token)
    localStorage.setItem('cdms_user', JSON.stringify(user))
    set({ token, user })
  },
  logout: () => {
    localStorage.removeItem('cdms_token')
    localStorage.removeItem('cdms_user')
    set({ token: null, user: null })
  },
}))
