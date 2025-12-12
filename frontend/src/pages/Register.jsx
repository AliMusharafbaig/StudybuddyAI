import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import { Brain, Mail, Lock, User, ArrowRight } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Register() {
    const [fullName, setFullName] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const { register, isLoading } = useAuthStore()
    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        const result = await register(email, password, fullName)
        if (result.success) {
            toast.success('Account created! Please sign in.')
            // Mark as new user so walkthrough shows after first login
            localStorage.setItem('studybuddy_new_user', 'true')
            localStorage.removeItem('studybuddy_walkthrough')
            // Redirect to login page - user must sign in first
            navigate('/login')
        } else {
            toast.error(result.error)
        }
    }

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '24px'
        }}>
            <div style={{
                width: '100%',
                maxWidth: '420px',
                background: 'var(--bg-card)',
                borderRadius: '24px',
                padding: '48px',
                border: '1px solid rgba(255,255,255,0.05)'
            }}>
                <div style={{ textAlign: 'center', marginBottom: '32px' }}>
                    <div style={{
                        width: '64px',
                        height: '64px',
                        background: 'var(--gradient-primary)',
                        borderRadius: '18px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 16px'
                    }}>
                        <Brain size={32} color="white" />
                    </div>
                    <h1 style={{ marginBottom: '8px' }}>Create Account</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>Start your AI-powered learning journey</p>
                </div>

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                            Full Name
                        </label>
                        <div style={{ position: 'relative' }}>
                            <User size={20} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="text"
                                value={fullName}
                                onChange={(e) => setFullName(e.target.value)}
                                className="input"
                                style={{ paddingLeft: '44px' }}
                                placeholder="John Doe"
                            />
                        </div>
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                            Email
                        </label>
                        <div style={{ position: 'relative' }}>
                            <Mail size={20} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                className="input"
                                style={{ paddingLeft: '44px' }}
                                placeholder="you@example.com"
                                required
                            />
                        </div>
                    </div>

                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                            Password
                        </label>
                        <div style={{ position: 'relative' }}>
                            <Lock size={20} style={{ position: 'absolute', left: '14px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="input"
                                style={{ paddingLeft: '44px' }}
                                placeholder="••••••••"
                                required
                                minLength={6}
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        className="btn btn-primary w-full"
                        disabled={isLoading}
                        style={{ padding: '14px' }}
                    >
                        {isLoading ? 'Creating...' : 'Create Account'} <ArrowRight size={20} />
                    </button>
                </form>

                <p style={{ textAlign: 'center', marginTop: '24px', color: 'var(--text-secondary)' }}>
                    Already have an account? <Link to="/login" style={{ fontWeight: 600 }}>Sign in</Link>
                </p>
            </div>
        </div>
    )
}
