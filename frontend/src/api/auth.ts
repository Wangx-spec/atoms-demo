import { http } from './http'
import type { TokenResponse, User } from '../types'

export async function register(email: string, password: string) {
  const { data } = await http.post<TokenResponse>('/api/auth/register', { email, password })
  return data
}

export async function login(email: string, password: string) {
  const { data } = await http.post<TokenResponse>('/api/auth/login', { email, password })
  return data
}

export async function getCurrentUser() {
  const { data } = await http.get<User>('/api/auth/me')
  return data
}
