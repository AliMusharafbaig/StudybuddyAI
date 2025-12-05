import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import api from '../api'

export const useAuthStore = create(
    persist(
        (set, get) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,

            login: async (email, password) => {
                set({ isLoading: true })
                try {
                    const { data } = await api.post('/auth/login', { email, password })
                    set({
                        user: data.user,
                        token: data.access_token,
                        isAuthenticated: true,
                        isLoading: false
                    })
                    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
                    return { success: true }
                } catch (error) {
                    set({ isLoading: false })
                    return { success: false, error: error.response?.data?.message || 'Login failed' }
                }
            },

            register: async (email, password, fullName) => {
                set({ isLoading: true })
                try {
                    const { data } = await api.post('/auth/register', {
                        email,
                        password,
                        full_name: fullName
                    })
                    set({
                        user: data.user,
                        token: data.access_token,
                        isAuthenticated: true,
                        isLoading: false
                    })
                    api.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
                    return { success: true }
                } catch (error) {
                    set({ isLoading: false })
                    return { success: false, error: error.response?.data?.message || 'Registration failed' }
                }
            },

            logout: () => {
                set({ user: null, token: null, isAuthenticated: false })
                delete api.defaults.headers.common['Authorization']
            },

            initAuth: () => {
                const { token } = get()
                if (token) {
                    api.defaults.headers.common['Authorization'] = `Bearer ${token}`
                }
            }
        }),
        { name: 'studybuddy-auth' }
    )
)
