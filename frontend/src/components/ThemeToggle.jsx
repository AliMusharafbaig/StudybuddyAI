import { useState, useEffect } from 'react'
import { Sun, Moon } from 'lucide-react'
import { motion } from 'framer-motion'

export default function ThemeToggle() {
    const [theme, setTheme] = useState('dark')

    useEffect(() => {
        // Load theme from localStorage
        const saved = localStorage.getItem('studybuddy-theme') || 'dark'
        setTheme(saved)
        document.documentElement.setAttribute('data-theme', saved)
    }, [])

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark'
        setTheme(newTheme)
        localStorage.setItem('studybuddy-theme', newTheme)
        document.documentElement.setAttribute('data-theme', newTheme)
    }

    return (
        <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={toggleTheme}
            style={{
                background: 'var(--bg-input)',
                border: '1px solid rgba(255,255,255,0.1)',
                borderRadius: '12px',
                padding: '10px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all 0.3s ease'
            }}
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
        >
            <motion.div
                initial={false}
                animate={{ rotate: theme === 'dark' ? 0 : 180 }}
                transition={{ duration: 0.3 }}
            >
                {theme === 'dark' ? (
                    <Sun size={20} color="var(--primary-light)" />
                ) : (
                    <Moon size={20} color="var(--primary-light)" />
                )}
            </motion.div>
        </motion.button>
    )
}
