import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Brain, Sparkles, Zap, BookOpen, Target, MessageCircle, ArrowRight } from 'lucide-react'

const features = [
    { icon: Brain, title: '6 AI Agents', desc: 'Specialized agents work together to optimize your learning' },
    { icon: BookOpen, title: 'Smart Content', desc: 'Upload PDFs, videos, audio - we extract everything' },
    { icon: Target, title: 'Adaptive Quizzes', desc: 'Questions adjust to your learning level' },
    { icon: Zap, title: 'Cram Mode', desc: 'Last-minute study plans optimized for exams' },
    { icon: MessageCircle, title: 'AI Chat', desc: 'Ask questions, get instant explanations' },
    { icon: Sparkles, title: 'Exam Predictions', desc: 'Know what topics will be on your test' },
]

export default function Landing() {
    return (
        <div style={{ minHeight: '100vh' }}>
            {/* Hero */}
            <header style={{
                padding: '24px 48px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                        width: '48px',
                        height: '48px',
                        background: 'var(--gradient-primary)',
                        borderRadius: '14px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <Brain size={28} color="white" />
                    </div>
                    <span style={{ fontSize: '1.5rem', fontWeight: 700 }}>StudyBuddy AI</span>
                </div>
                <div style={{ display: 'flex', gap: '16px' }}>
                    <Link to="/login" className="btn btn-secondary">Login</Link>
                    <Link to="/register" className="btn btn-primary">Get Started</Link>
                </div>
            </header>

            {/* Hero Section */}
            <section style={{
                textAlign: 'center',
                padding: '80px 24px 120px',
                position: 'relative'
            }}>
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.6 }}
                >
                    <div style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '8px',
                        background: 'rgba(99, 102, 241, 0.15)',
                        padding: '8px 16px',
                        borderRadius: '20px',
                        marginBottom: '24px',
                        border: '1px solid rgba(99, 102, 241, 0.3)'
                    }}>
                        <Sparkles size={16} color="var(--primary-light)" />
                        <span style={{ color: 'var(--primary-light)', fontSize: '0.875rem' }}>
                            Powered by Google Gemini 2.0
                        </span>
                    </div>

                    <h1 style={{
                        fontSize: '4rem',
                        fontWeight: 800,
                        marginBottom: '24px',
                        background: 'var(--gradient-primary)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        lineHeight: 1.1
                    }}>
                        Your AI-Powered<br />Study Companion
                    </h1>

                    <p style={{
                        fontSize: '1.25rem',
                        color: 'var(--text-secondary)',
                        maxWidth: '600px',
                        margin: '0 auto 40px'
                    }}>
                        Upload your course materials. Get intelligent quizzes, exam predictions,
                        and personalized study plans. Ace your exams with AI that understands you.
                    </p>

                    <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
                        <Link to="/register" className="btn btn-primary" style={{ padding: '16px 32px', fontSize: '1.125rem' }}>
                            Start Learning Free <ArrowRight size={20} />
                        </Link>
                        <Link to="/login" className="btn btn-secondary" style={{ padding: '16px 32px', fontSize: '1.125rem' }}>
                            I Have an Account
                        </Link>
                    </div>
                </motion.div>

                {/* Glow effect */}
                <div style={{
                    position: 'absolute',
                    top: '50%',
                    left: '50%',
                    transform: 'translate(-50%, -50%)',
                    width: '600px',
                    height: '600px',
                    background: 'radial-gradient(circle, rgba(99, 102, 241, 0.2) 0%, transparent 70%)',
                    pointerEvents: 'none',
                    zIndex: -1
                }} />
            </section>

            {/* Features */}
            <section style={{ padding: '80px 48px', background: 'rgba(0,0,0,0.2)' }}>
                <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
                    <h2 style={{ textAlign: 'center', marginBottom: '16px' }}>
                        Everything You Need to Succeed
                    </h2>
                    <p style={{ textAlign: 'center', color: 'var(--text-secondary)', marginBottom: '48px' }}>
                        Six specialized AI agents working together for your success
                    </p>

                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
                        gap: '24px'
                    }}>
                        {features.map(({ icon: Icon, title, desc }, i) => (
                            <motion.div
                                key={title}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.1 }}
                                className="card"
                                style={{ padding: '32px' }}
                            >
                                <div style={{
                                    width: '56px',
                                    height: '56px',
                                    background: 'var(--gradient-primary)',
                                    borderRadius: '14px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    marginBottom: '20px'
                                }}>
                                    <Icon size={28} color="white" />
                                </div>
                                <h3 style={{ marginBottom: '8px' }}>{title}</h3>
                                <p style={{ color: 'var(--text-secondary)' }}>{desc}</p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section style={{ padding: '100px 24px', textAlign: 'center' }}>
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                >
                    <h2 style={{ fontSize: '2.5rem', marginBottom: '16px' }}>
                        Ready to Transform Your Study Game?
                    </h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
                        Join thousands of students achieving better grades with AI
                    </p>
                    <Link to="/register" className="btn btn-primary" style={{ padding: '18px 40px', fontSize: '1.25rem' }}>
                        Get Started Free <Sparkles size={20} />
                    </Link>
                </motion.div>
            </section>
        </div>
    )
}
