import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Palette, Type, Check, Sun, Moon } from 'lucide-react'

// Theme presets
const themePresets = [
    { id: 'default', name: 'Purple Dream', primary: '#6366f1', secondary: '#8b5cf6', bg: '#0f0f1a', card: '#1a1a2e' },
    { id: 'ocean', name: 'Ocean Blue', primary: '#0ea5e9', secondary: '#06b6d4', bg: '#0c1222', card: '#162032' },
    { id: 'forest', name: 'Forest Green', primary: '#10b981', secondary: '#34d399', bg: '#0f1512', card: '#1a2520' },
    { id: 'sunset', name: 'Sunset Orange', primary: '#f59e0b', secondary: '#f97316', bg: '#1a140c', card: '#2a2018' },
    { id: 'rose', name: 'Rose Pink', primary: '#ec4899', secondary: '#f472b6', bg: '#1a0f14', card: '#2a1a22' },
    { id: 'dark', name: 'Pure Dark', primary: '#a1a1aa', secondary: '#71717a', bg: '#09090b', card: '#18181b' },
]

// Font size presets
const fontSizes = [
    { id: 'small', name: 'Small', scale: 0.875 },
    { id: 'medium', name: 'Medium', scale: 1 },
    { id: 'large', name: 'Large', scale: 1.125 },
    { id: 'xlarge', name: 'Extra Large', scale: 1.25 },
]

export default function ThemeSettings({ isOpen, onClose }) {
    const [activeTab, setActiveTab] = useState('theme')
    const [selectedTheme, setSelectedTheme] = useState('default')
    const [selectedFontSize, setSelectedFontSize] = useState('medium')

    // Load saved preferences on mount
    useEffect(() => {
        const savedTheme = localStorage.getItem('studybuddy_theme') || 'default'
        const savedFontSize = localStorage.getItem('studybuddy_fontsize') || 'medium'
        setSelectedTheme(savedTheme)
        setSelectedFontSize(savedFontSize)
        applyTheme(savedTheme)
        applyFontSize(savedFontSize)
    }, [])

    const applyTheme = (themeId) => {
        const theme = themePresets.find(t => t.id === themeId)
        if (!theme) return

        document.documentElement.style.setProperty('--primary', theme.primary)
        document.documentElement.style.setProperty('--primary-dark', theme.primary)
        document.documentElement.style.setProperty('--primary-light', theme.secondary)
        document.documentElement.style.setProperty('--secondary', theme.secondary)
        document.documentElement.style.setProperty('--bg-dark', theme.bg)
        document.documentElement.style.setProperty('--bg-card', theme.card)
        document.documentElement.style.setProperty('--bg-card-hover', theme.card)
        document.documentElement.style.setProperty('--gradient-primary', `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`)
    }

    const applyFontSize = (sizeId) => {
        const size = fontSizes.find(s => s.id === sizeId)
        if (!size) return
        document.documentElement.style.setProperty('--font-scale', size.scale)
        document.body.style.fontSize = `${size.scale}rem`
    }

    const handleThemeChange = (themeId) => {
        setSelectedTheme(themeId)
        applyTheme(themeId)
        localStorage.setItem('studybuddy_theme', themeId)
    }

    const handleFontSizeChange = (sizeId) => {
        setSelectedFontSize(sizeId)
        applyFontSize(sizeId)
        localStorage.setItem('studybuddy_fontsize', sizeId)
    }

    if (!isOpen) return null

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                style={{
                    position: 'fixed',
                    inset: 0,
                    background: 'rgba(0,0,0,0.85)',
                    backdropFilter: 'blur(8px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000
                }}
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: 20 }}
                    className="card"
                    style={{
                        width: '100%',
                        maxWidth: '500px',
                        margin: '24px',
                        maxHeight: '80vh',
                        overflow: 'hidden'
                    }}
                    onClick={e => e.stopPropagation()}
                >
                    {/* Header */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '24px'
                    }}>
                        <div>
                            <h2 style={{ margin: '0 0 4px' }}>✨ Customize UI</h2>
                            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem' }}>
                                Personalize your study experience
                            </p>
                        </div>
                        <button
                            onClick={onClose}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: 'var(--text-muted)',
                                cursor: 'pointer',
                                padding: '8px'
                            }}
                        >
                            <X size={24} />
                        </button>
                    </div>

                    {/* Tabs */}
                    <div style={{
                        display: 'flex',
                        gap: '8px',
                        marginBottom: '24px',
                        background: 'var(--bg-input)',
                        padding: '4px',
                        borderRadius: '12px'
                    }}>
                        <button
                            onClick={() => setActiveTab('theme')}
                            style={{
                                flex: 1,
                                padding: '12px',
                                border: 'none',
                                borderRadius: '10px',
                                background: activeTab === 'theme' ? 'var(--gradient-primary)' : 'transparent',
                                color: activeTab === 'theme' ? 'white' : 'var(--text-secondary)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '8px',
                                fontWeight: 600,
                                transition: 'all 0.2s'
                            }}
                        >
                            <Palette size={18} /> Theme
                        </button>
                        <button
                            onClick={() => setActiveTab('font')}
                            style={{
                                flex: 1,
                                padding: '12px',
                                border: 'none',
                                borderRadius: '10px',
                                background: activeTab === 'font' ? 'var(--gradient-primary)' : 'transparent',
                                color: activeTab === 'font' ? 'white' : 'var(--text-secondary)',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                gap: '8px',
                                fontWeight: 600,
                                transition: 'all 0.2s'
                            }}
                        >
                            <Type size={18} /> Font Size
                        </button>
                    </div>

                    {/* Content */}
                    <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                        {activeTab === 'theme' && (
                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                                {themePresets.map(theme => (
                                    <motion.div
                                        key={theme.id}
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => handleThemeChange(theme.id)}
                                        style={{
                                            padding: '16px',
                                            borderRadius: '12px',
                                            background: theme.card,
                                            border: selectedTheme === theme.id
                                                ? `2px solid ${theme.primary}`
                                                : '2px solid transparent',
                                            cursor: 'pointer',
                                            position: 'relative',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        {/* Color preview */}
                                        <div style={{
                                            display: 'flex',
                                            gap: '6px',
                                            marginBottom: '12px'
                                        }}>
                                            <div style={{
                                                width: '24px',
                                                height: '24px',
                                                borderRadius: '6px',
                                                background: theme.primary
                                            }} />
                                            <div style={{
                                                width: '24px',
                                                height: '24px',
                                                borderRadius: '6px',
                                                background: theme.secondary
                                            }} />
                                            <div style={{
                                                width: '24px',
                                                height: '24px',
                                                borderRadius: '6px',
                                                background: theme.bg,
                                                border: '1px solid rgba(255,255,255,0.2)'
                                            }} />
                                        </div>
                                        <div style={{ fontWeight: 600, color: 'white' }}>{theme.name}</div>

                                        {/* Selected indicator */}
                                        {selectedTheme === theme.id && (
                                            <div style={{
                                                position: 'absolute',
                                                top: '8px',
                                                right: '8px',
                                                width: '20px',
                                                height: '20px',
                                                borderRadius: '50%',
                                                background: theme.primary,
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}>
                                                <Check size={12} color="white" />
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </div>
                        )}

                        {activeTab === 'font' && (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                                {fontSizes.map(size => (
                                    <motion.div
                                        key={size.id}
                                        whileHover={{ scale: 1.01 }}
                                        whileTap={{ scale: 0.99 }}
                                        onClick={() => handleFontSizeChange(size.id)}
                                        style={{
                                            padding: '16px 20px',
                                            borderRadius: '12px',
                                            background: 'var(--bg-input)',
                                            border: selectedFontSize === size.id
                                                ? '2px solid var(--primary)'
                                                : '2px solid transparent',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'space-between',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                            <span style={{
                                                fontSize: `${size.scale * 1.5}rem`,
                                                fontWeight: 700,
                                                color: selectedFontSize === size.id ? 'var(--primary)' : 'var(--text-secondary)'
                                            }}>
                                                Aa
                                            </span>
                                            <div>
                                                <div style={{ fontWeight: 600 }}>{size.name}</div>
                                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                                    {size.scale === 1 ? 'Default size' : `${Math.round((size.scale - 1) * 100)}% ${size.scale > 1 ? 'larger' : 'smaller'}`}
                                                </div>
                                            </div>
                                        </div>

                                        {selectedFontSize === size.id && (
                                            <div style={{
                                                width: '24px',
                                                height: '24px',
                                                borderRadius: '50%',
                                                background: 'var(--primary)',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center'
                                            }}>
                                                <Check size={14} color="white" />
                                            </div>
                                        )}
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    )
}

// Export function to initialize theme on app load
export function initializeTheme() {
    const savedTheme = localStorage.getItem('studybuddy_theme') || 'default'
    const savedFontSize = localStorage.getItem('studybuddy_fontsize') || 'medium'

    const theme = themePresets.find(t => t.id === savedTheme)
    const size = fontSizes.find(s => s.id === savedFontSize)

    if (theme) {
        document.documentElement.style.setProperty('--primary', theme.primary)
        document.documentElement.style.setProperty('--primary-dark', theme.primary)
        document.documentElement.style.setProperty('--primary-light', theme.secondary)
        document.documentElement.style.setProperty('--secondary', theme.secondary)
        document.documentElement.style.setProperty('--bg-dark', theme.bg)
        document.documentElement.style.setProperty('--bg-card', theme.card)
        document.documentElement.style.setProperty('--bg-card-hover', theme.card)
        document.documentElement.style.setProperty('--gradient-primary', `linear-gradient(135deg, ${theme.primary} 0%, ${theme.secondary} 100%)`)
    }

    if (size) {
        document.documentElement.style.setProperty('--font-scale', size.scale)
        document.body.style.fontSize = `${size.scale}rem`
    }
}
