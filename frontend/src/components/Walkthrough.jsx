import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, ArrowRight, ArrowLeft, BookOpen, MessageSquare, Brain, Zap, Target, Sparkles, Check } from 'lucide-react'

export default function Walkthrough() {
    const [step, setStep] = useState(0)
    const [show, setShow] = useState(false)

    useEffect(() => {
        // Only show walkthrough if:
        // 1. User just registered (new_user flag is set)
        // 2. Walkthrough hasn't been seen yet
        const isNewUser = localStorage.getItem('studybuddy_new_user')
        const walkthroughSeen = localStorage.getItem('studybuddy_walkthrough')

        if (isNewUser && !walkthroughSeen) {
            setShow(true)
            // Clear the new user flag so it doesn't show on subsequent logins
            localStorage.removeItem('studybuddy_new_user')
        }
    }, [])

    const finish = () => {
        localStorage.setItem('studybuddy_walkthrough', 'true')
        setShow(false)
    }

    const steps = [
        {
            title: "Welcome to StudyBuddy AI! 🚀",
            desc: "Your personal AI-powered study companion. Let me show you how to ace your exams with the power of AI.",
            icon: <Sparkles size={56} />,
            color: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            features: ['Personalized Learning', 'AI-Powered Quizzes', 'Smart Study Plans']
        },
        {
            title: "Step 1: Create Your Course 📚",
            desc: "Start by creating a course and uploading your study materials - PDFs, lecture notes, slides. Our AI will extract all the key concepts automatically.",
            icon: <BookOpen size={56} />,
            color: 'linear-gradient(135deg, #8b5cf6, #a855f7)',
            features: ['Upload PDFs & Docs', 'Auto-extract concepts', 'Build knowledge base']
        },
        {
            title: "Step 2: Chat with Your Materials 💬",
            desc: "Ask questions and get instant answers from YOUR uploaded content. The AI understands your specific course material and gives precise answers.",
            icon: <MessageSquare size={56} />,
            color: 'linear-gradient(135deg, #06b6d4, #0891b2)',
            features: ['Context-aware answers', 'Cite sources', 'Explain concepts']
        },
        {
            title: "Step 3: Test Your Knowledge 🎯",
            desc: "Generate personalized quizzes based on your materials. The AI creates questions that match your professor's style and focuses on what matters.",
            icon: <Target size={56} />,
            color: 'linear-gradient(135deg, #10b981, #059669)',
            features: ['Adaptive difficulty', 'Instant feedback', 'Track progress']
        },
        {
            title: "Bonus: Emergency Cram Mode ⚡",
            desc: "Exam tomorrow? Panic mode activated! Our AI creates an optimized study plan that focuses on high-value topics to maximize your score in minimal time.",
            icon: <Zap size={56} />,
            color: 'linear-gradient(135deg, #ef4444, #f97316)',
            features: ['Optimized plans', 'Focus on key topics', 'Time-efficient']
        }
    ]

    if (!show) return null

    const currentStep = steps[step]

    return (
        <AnimatePresence>
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                style={{
                    position: 'fixed',
                    inset: 0,
                    zIndex: 9999,
                    background: 'rgba(0, 0, 0, 0.9)',
                    backdropFilter: 'blur(10px)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    overflow: 'hidden'
                }}
            >
                {/* Animated background particles */}
                <div style={{ position: 'absolute', inset: 0, overflow: 'hidden', pointerEvents: 'none' }}>
                    {[...Array(20)].map((_, i) => (
                        <motion.div
                            key={i}
                            initial={{
                                x: Math.random() * window.innerWidth,
                                y: Math.random() * window.innerHeight,
                                opacity: 0.3
                            }}
                            animate={{
                                y: [null, Math.random() * window.innerHeight],
                                opacity: [0.3, 0.6, 0.3]
                            }}
                            transition={{
                                duration: 10 + Math.random() * 10,
                                repeat: Infinity,
                                ease: 'linear'
                            }}
                            style={{
                                position: 'absolute',
                                width: 4 + Math.random() * 4,
                                height: 4 + Math.random() * 4,
                                borderRadius: '50%',
                                background: 'var(--primary-light)',
                                filter: 'blur(1px)'
                            }}
                        />
                    ))}
                </div>

                {/* Main card */}
                <motion.div
                    key={step}
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: -20 }}
                    transition={{ type: 'spring', duration: 0.5 }}
                    style={{
                        background: 'var(--bg-card)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        borderRadius: '28px',
                        padding: '48px',
                        maxWidth: '580px',
                        width: '90%',
                        textAlign: 'center',
                        position: 'relative',
                        boxShadow: '0 0 80px rgba(99, 102, 241, 0.2), 0 25px 50px rgba(0, 0, 0, 0.5)'
                    }}
                >
                    {/* Skip button */}
                    <button
                        onClick={finish}
                        style={{
                            position: 'absolute',
                            top: 20,
                            right: 20,
                            background: 'none',
                            border: 'none',
                            color: 'var(--text-muted)',
                            cursor: 'pointer',
                            padding: '8px',
                            borderRadius: '8px',
                            transition: 'all 0.2s'
                        }}
                        onMouseEnter={e => e.target.style.background = 'rgba(255,255,255,0.1)'}
                        onMouseLeave={e => e.target.style.background = 'none'}
                    >
                        <X size={24} />
                    </button>

                    {/* Icon with gradient background */}
                    <motion.div
                        initial={{ scale: 0, rotate: -180 }}
                        animate={{ scale: 1, rotate: 0 }}
                        transition={{ type: 'spring', delay: 0.1, duration: 0.6 }}
                        style={{
                            width: '100px',
                            height: '100px',
                            background: currentStep.color,
                            borderRadius: '24px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 28px',
                            boxShadow: '0 0 40px rgba(99, 102, 241, 0.4)',
                            color: 'white'
                        }}
                    >
                        {currentStep.icon}
                    </motion.div>

                    {/* Title */}
                    <motion.h2
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.15 }}
                        style={{
                            marginBottom: '16px',
                            fontSize: '2rem',
                            background: currentStep.color,
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent'
                        }}
                    >
                        {currentStep.title}
                    </motion.h2>

                    {/* Description */}
                    <motion.p
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.2 }}
                        style={{
                            color: 'var(--text-secondary)',
                            marginBottom: '28px',
                            fontSize: '1.1rem',
                            lineHeight: 1.7
                        }}
                    >
                        {currentStep.desc}
                    </motion.p>

                    {/* Features */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.25 }}
                        style={{
                            display: 'flex',
                            justifyContent: 'center',
                            gap: '12px',
                            marginBottom: '36px',
                            flexWrap: 'wrap'
                        }}
                    >
                        {currentStep.features.map((feature, i) => (
                            <span
                                key={i}
                                style={{
                                    padding: '8px 16px',
                                    background: 'rgba(99, 102, 241, 0.15)',
                                    borderRadius: '20px',
                                    border: '1px solid rgba(99, 102, 241, 0.2)',
                                    fontSize: '0.85rem',
                                    color: 'var(--primary-light)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '6px'
                                }}
                            >
                                <Check size={14} /> {feature}
                            </span>
                        ))}
                    </motion.div>

                    {/* Navigation */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        {/* Progress dots */}
                        <div style={{ display: 'flex', gap: '8px' }}>
                            {steps.map((_, i) => (
                                <motion.div
                                    key={i}
                                    animate={{
                                        scale: i === step ? 1.2 : 1,
                                        opacity: i === step ? 1 : 0.4
                                    }}
                                    style={{
                                        width: i === step ? '24px' : '10px',
                                        height: '10px',
                                        borderRadius: '10px',
                                        background: i <= step ? 'var(--primary)' : 'var(--bg-input)',
                                        transition: 'all 0.3s',
                                        cursor: 'pointer'
                                    }}
                                    onClick={() => setStep(i)}
                                />
                            ))}
                        </div>

                        {/* Buttons */}
                        <div style={{ display: 'flex', gap: '12px' }}>
                            {step > 0 && (
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => setStep(s => s - 1)}
                                    style={{ padding: '12px 20px' }}
                                >
                                    <ArrowLeft size={18} /> Back
                                </button>
                            )}
                            <button
                                className="btn btn-primary"
                                onClick={() => step < steps.length - 1 ? setStep(s => s + 1) : finish()}
                                style={{ padding: '12px 24px' }}
                            >
                                {step < steps.length - 1 ? (
                                    <>Next <ArrowRight size={18} /></>
                                ) : (
                                    <>Get Started <Sparkles size={18} /></>
                                )}
                            </button>
                        </div>
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    )
}
