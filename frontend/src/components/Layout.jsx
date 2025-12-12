import { useState, useEffect } from 'react'
import { Outlet, NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../store/authStore'
import {
    LayoutDashboard, BookOpen, Brain, MessageCircle,
    BarChart3, Zap, LogOut, User, Sparkles, Palette, Type
} from 'lucide-react'
import Walkthrough from './Walkthrough'
import ThemeSettings, { initializeTheme } from './ThemeSettings'

const navItems = [
    { path: '/app', icon: LayoutDashboard, label: 'Dashboard', end: true },
    { path: '/app/courses', icon: BookOpen, label: 'Courses' },
    { path: '/app/cram', icon: Zap, label: 'Cram Mode' },
    { path: '/app/chat', icon: MessageCircle, label: 'AI Chat' },
    { path: '/app/analytics', icon: BarChart3, label: 'Analytics' },
]

export default function Layout() {
    const { user, logout } = useAuthStore()
    const navigate = useNavigate()
    const [showThemeSettings, setShowThemeSettings] = useState(false)

    // Initialize theme on component mount
    useEffect(() => {
        initializeTheme()
    }, [])

    const handleLogout = () => {
        // Clear chat-related localStorage items
        localStorage.removeItem('studybuddy_current_chat')
        logout()
        navigate('/login')
    }

    return (
        <div style={{ display: 'flex', minHeight: '100vh', position: 'relative' }}>
            <Walkthrough />
            {/* Sidebar */}
            <aside style={{
                width: '260px',
                background: 'var(--bg-card)',
                borderRight: '1px solid rgba(255,255,255,0.05)',
                padding: '24px 16px',
                display: 'flex',
                flexDirection: 'column'
            }}>
                {/* Logo */}
                <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    marginBottom: '32px',
                    paddingLeft: '8px'
                }}>
                    <div style={{
                        width: '40px',
                        height: '40px',
                        background: 'var(--gradient-primary)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <Brain size={24} color="white" />
                    </div>
                    <div>
                        <h1 style={{ fontSize: '1.25rem', margin: 0 }}>StudyBuddy</h1>
                        <span style={{ fontSize: '0.75rem', color: 'var(--primary-light)' }}>AI Platform</span>
                    </div>
                </div>

                {/* Navigation */}
                <nav style={{ flex: 1 }}>
                    {navItems.map(({ path, icon: Icon, label, end }) => (
                        <NavLink
                            key={path}
                            to={path}
                            end={end}
                            style={({ isActive }) => ({
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px',
                                padding: '12px 16px',
                                borderRadius: '12px',
                                marginBottom: '4px',
                                color: isActive ? 'white' : 'var(--text-secondary)',
                                background: isActive ? 'var(--gradient-primary)' : 'transparent',
                                transition: 'all 0.2s',
                                textDecoration: 'none'
                            })}
                        >
                            <Icon size={20} />
                            {label}
                        </NavLink>
                    ))}

                    {/* Divider */}
                    <div style={{
                        height: '1px',
                        background: 'rgba(255,255,255,0.1)',
                        margin: '16px 0'
                    }} />

                    {/* UI Customization Section */}
                    <div style={{
                        fontSize: '0.7rem',
                        color: 'var(--text-muted)',
                        padding: '0 16px 8px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em'
                    }}>
                        Customize
                    </div>

                    {/* Theme Button */}
                    <button
                        onClick={() => setShowThemeSettings(true)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '12px 16px',
                            borderRadius: '12px',
                            marginBottom: '4px',
                            color: 'var(--text-secondary)',
                            background: 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            width: '100%',
                            textAlign: 'left',
                            transition: 'all 0.2s',
                            fontSize: '1rem'
                        }}
                        onMouseEnter={e => {
                            e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)'
                            e.currentTarget.style.color = 'var(--primary-light)'
                        }}
                        onMouseLeave={e => {
                            e.currentTarget.style.background = 'transparent'
                            e.currentTarget.style.color = 'var(--text-secondary)'
                        }}
                    >
                        <Palette size={20} />
                        🎨 Theme
                    </button>

                    {/* Font Size Button */}
                    <button
                        onClick={() => setShowThemeSettings(true)}
                        style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '12px 16px',
                            borderRadius: '12px',
                            marginBottom: '4px',
                            color: 'var(--text-secondary)',
                            background: 'transparent',
                            border: 'none',
                            cursor: 'pointer',
                            width: '100%',
                            textAlign: 'left',
                            transition: 'all 0.2s',
                            fontSize: '1rem'
                        }}
                        onMouseEnter={e => {
                            e.currentTarget.style.background = 'rgba(99, 102, 241, 0.1)'
                            e.currentTarget.style.color = 'var(--primary-light)'
                        }}
                        onMouseLeave={e => {
                            e.currentTarget.style.background = 'transparent'
                            e.currentTarget.style.color = 'var(--text-secondary)'
                        }}
                    >
                        <Type size={20} />
                        🔤 Font Size
                    </button>
                </nav>

                {/* User */}
                <div style={{
                    padding: '16px',
                    background: 'var(--bg-input)',
                    borderRadius: '12px',
                    marginBottom: '8px'
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <div style={{
                            width: '40px',
                            height: '40px',
                            background: 'var(--gradient-primary)',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center'
                        }}>
                            <User size={20} color="white" />
                        </div>
                        <div>
                            <div style={{ fontWeight: 600 }}>{user?.full_name || 'Student'}</div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{user?.email}</div>
                        </div>
                    </div>
                </div>

                <button
                    onClick={handleLogout}
                    style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '12px',
                        padding: '12px 16px',
                        background: 'transparent',
                        border: '1px solid rgba(239, 68, 68, 0.3)',
                        borderRadius: '12px',
                        color: 'var(--error)',
                        cursor: 'pointer',
                        transition: 'all 0.2s'
                    }}
                >
                    <LogOut size={20} />
                    Logout
                </button>
            </aside>

            {/* Main Content */}
            <main style={{ flex: 1, padding: '32px', overflowY: 'auto' }}>
                <Outlet />
            </main>

            {/* Theme Settings Modal */}
            <ThemeSettings
                isOpen={showThemeSettings}
                onClose={() => setShowThemeSettings(false)}
            />
        </div>
    )
}

