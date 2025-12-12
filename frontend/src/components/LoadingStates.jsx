import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Brain, Zap, AlertCircle, CheckCircle } from 'lucide-react'

/**
 * Beautiful loading states for various operations
 */

export const LoadingSpinner = ({ size = 40, message = "Loading..." }) => (
    <div style={{ textAlign: 'center', padding: '40px' }}>
        <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            style={{
                width: `${size}px`,
                height: `${size}px`,
                border: `4px solid rgba(99, 102, 241, 0.2)`,
                borderTop: '4px solid var(--primary)',
                borderRadius: '50%',
                margin: '0 auto 16px'
            }}
        />
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{message}</p>
    </div>
)

export const LoadingDots = () => (
    <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', alignItems: 'center', padding: '20px' }}>
        {[0, 1, 2].map(i => (
            <motion.div
                key={i}
                animate={{ scale: [1, 1.4, 1], opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '50%',
                    background: 'var(--primary)'
                }}
            />
        ))}
    </div>
)

export const LoadingPulse = ({ icon: Icon = Brain }) => (
    <motion.div
        animate={{ scale: [1, 1.1, 1], opacity: [0.7, 1, 0.7] }}
        transition={{ duration: 2, repeat: Infinity }}
        style={{
            width: '80px',
            height: '80px',
            background: 'var(--gradient-primary)',
            borderRadius: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            margin: '0 auto'
        }}
    >
        <Icon size={40} color="white" />
    </motion.div>
)

export const ProcessingAnimation = ({ message = "Processing your request..." }) => (
    <div style={{ textAlign: 'center', padding: '60px 20px' }}>
        <div style={{ position: 'relative', marginBottom: '24px' }}>
            {/* Outer ring */}
            <motion.div
                animate={{ rotate: 360 }}
                transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                style={{
                    width: '100px',
                    height: '100px',
                    border: '3px solid transparent',
                    borderTop: '3px solid var(--primary)',
                    borderRight: '3px solid var(--secondary)',
                    borderRadius: '50%',
                    margin: '0 auto',
                    position: 'absolute',
                    left: '50%',
                    transform: 'translateX(-50%)'
                }}
            />
            {/* Inner pulse */}
            <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                style={{
                    width: '80px',
                    height: '80px',
                    background: 'var(--gradient-primary)',
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '10px auto 0',
                    boxShadow: '0 0 40px rgba(99, 102, 241, 0.4)'
                }}
            >
                <Sparkles size={35} color="white" />
            </motion.div>
        </div>
        <p style={{ color: 'var(--text-primary)', fontWeight: 600, marginTop: '48px' }}>{message}</p>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: '8px' }}>
            This may take a moment...
        </p>
    </div>
)

export const SuccessAnimation = ({ message = "Success!" }) => (
    <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: 'spring', duration: 0.6 }}
        style={{ textAlign: 'center', padding: '40px' }}
    >
        <motion.div
            animate={{ scale: [1, 1.1, 1] }}
            transition={{ duration: 0.5 }}
            style={{
                width: '100px',
                height: '100px',
                background: 'linear-gradient(135deg, #10b981, #34d399)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px',
                boxShadow: '0 0 50px rgba(16, 185, 129, 0.4)'
            }}
        >
            <CheckCircle size={50} color="white" />
        </motion.div>
        <h3 style={{ color: 'var(--success)', margin: '0 0 8px' }}>{message}</h3>
    </motion.div>
)

export const ErrorAnimation = ({ message = "Oops! Something went wrong" }) => (
    <motion.div
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        style={{ textAlign: 'center', padding: '40px' }}
    >
        <motion.div
            animate={{ rotate: [0, -10, 10, -10, 0] }}
            transition={{ duration: 0.5 }}
            style={{
                width: '100px',
                height: '100px',
                background: 'linear-gradient(135deg, #ef4444, #f97316)',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 20px'
            }}
        >
            <AlertCircle size={50} color="white" />
        </motion.div>
        <h3 style={{ color: 'var(--error)', margin: '0 0 8px' }}>{message}</h3>
    </motion.div>
)
