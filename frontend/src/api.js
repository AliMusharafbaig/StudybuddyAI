import axios from 'axios'

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000/api',
    headers: { 'Content-Type': 'application/json' },
    timeout: 30000 // 30 second timeout
})

// Initialize auth token from storage on startup
const initializeAuth = () => {
    try {
        const stored = localStorage.getItem('studybuddy-auth')
        if (stored) {
            const { state } = JSON.parse(stored)
            if (state?.token) {
                api.defaults.headers.common['Authorization'] = `Bearer ${state.token}`
            }
        }
    } catch (e) {
        console.error('Failed to initialize auth:', e)
    }
}

// Call on module load
initializeAuth()

// Request interceptor to ensure token is always set
api.interceptors.request.use(
    config => {
        // Re-check token before each request
        if (!config.headers['Authorization']) {
            try {
                const stored = localStorage.getItem('studybuddy-auth')
                if (stored) {
                    const { state } = JSON.parse(stored)
                    if (state?.token) {
                        config.headers['Authorization'] = `Bearer ${state.token}`
                    }
                }
            } catch (e) {
                // Ignore
            }
        }
        return config
    },
    error => Promise.reject(error)
)

// Response interceptor with better 401 handling
api.interceptors.response.use(
    response => response,
    error => {
        // Only redirect to login for actual auth failures, not network errors
        if (error.response?.status === 401 && error.response?.data?.detail !== 'Token expired') {
            localStorage.removeItem('studybuddy-auth')
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)

export default api
