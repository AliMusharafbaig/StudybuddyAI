import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Zap, Clock, Target, BookOpen, CheckCircle, Brain, ArrowRight, Sparkles, AlertTriangle, Coffee, MessageCircle } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import api from '../api'
import toast from 'react-hot-toast'

export default function CramMode() {
    const [courses, setCourses] = useState([])
    const [selectedCourse, setSelectedCourse] = useState('')
    const [hours, setHours] = useState(4)
    const [loading, setLoading] = useState(false)
    const [plan, setPlan] = useState(null)
    const [step, setStep] = useState(0) // 0: setup, 1: generating, 2: plan ready
    const navigate = useNavigate()

    useEffect(() => {
        loadCourses()
    }, [])

    const loadCourses = async () => {
        try {
            const { data } = await api.get('/courses')
            // Filter to courses that are processed AND have concepts extracted
            setCourses(data.filter(c => c.is_processed && c.total_concepts > 0))
        } catch (e) {
            console.error('Failed to load courses', e)
        }
    }

    const generatePlan = async () => {
        if (!selectedCourse) {
            toast.error('Please select a course first!')
            return
        }

        setLoading(true)
        setStep(1)

        try {
            const { data } = await api.post('/cram/generate', {
                course_id: selectedCourse,
                hours_available: hours
            })
            setPlan(data)
            setStep(2)
            toast.success('Cram plan generated!')
        } catch (e) {
            console.error('Failed to generate plan', e)
            // Show the actual error message from backend
            const errorMsg = e.response?.data?.detail || 'Failed to generate cram plan. Make sure you have uploaded and processed materials.'
            toast.error(errorMsg)
            setStep(0)
        } finally {
            setLoading(false)
        }
    }

    const hourOptions = [
        { value: 1, label: '1 Hour', emoji: '⚡', desc: 'Quick review' },
        { value: 2, label: '2 Hours', emoji: '🏃', desc: 'Focused sprint' },
        { value: 4, label: '4 Hours', emoji: '💪', desc: 'Solid session' },
        { value: 6, label: '6 Hours', emoji: '🚀', desc: 'Deep dive' },
        { value: 8, label: '8+ Hours', emoji: '🏆', desc: 'Full marathon' }
    ]

    const selectedCourseData = courses.find(c => c.id === selectedCourse)

    return (
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            {/* Header */}
            <motion.div
                initial={{ opacity: 0, y: -20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{
                    textAlign: 'center',
                    marginBottom: '40px',
                    padding: '40px',
                    background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(249, 115, 22, 0.1) 100%)',
                    borderRadius: '24px',
                    border: '1px solid rgba(239, 68, 68, 0.2)'
                }}
            >
                <div style={{
                    width: '80px',
                    height: '80px',
                    background: 'linear-gradient(135deg, #ef4444, #f97316)',
                    borderRadius: '20px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    margin: '0 auto 20px',
                    boxShadow: '0 0 40px rgba(239, 68, 68, 0.3)'
                }}>
                    <Zap size={40} color="white" />
                </div>
                <h1 style={{ fontSize: '2.5rem', marginBottom: '12px' }}>
                    🚨 Emergency Cram Mode
                </h1>
                <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto', fontSize: '1.1rem' }}>
                    Exam tomorrow? Don't panic! Our AI will create an optimized study plan
                    that focuses on high-value topics to maximize your score.
                </p>
            </motion.div>

            <AnimatePresence mode="wait">
                {step === 0 && (
                    <motion.div
                        key="setup"
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: 20 }}
                    >
                        {/* Course Selection */}
                        <div className="card" style={{ marginBottom: '24px' }}>
                            <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <BookOpen size={24} color="var(--primary)" /> Select Your Course
                            </h2>

                            {courses.length === 0 ? (
                                <div style={{ textAlign: 'center', padding: '40px' }}>
                                    <AlertTriangle size={40} color="var(--warning)" style={{ marginBottom: '16px' }} />
                                    <p style={{ color: 'var(--text-secondary)' }}>
                                        No processed courses found. Upload and process materials first!
                                    </p>
                                </div>
                            ) : (
                                <div style={{ display: 'grid', gap: '12px' }}>
                                    {courses.map(course => (
                                        <motion.div
                                            key={course.id}
                                            whileHover={{ scale: 1.01 }}
                                            onClick={() => setSelectedCourse(course.id)}
                                            style={{
                                                padding: '16px 20px',
                                                borderRadius: '12px',
                                                border: selectedCourse === course.id
                                                    ? '2px solid var(--primary)'
                                                    : '1px solid rgba(255,255,255,0.1)',
                                                background: selectedCourse === course.id
                                                    ? 'rgba(99, 102, 241, 0.1)'
                                                    : 'var(--bg-input)',
                                                cursor: 'pointer',
                                                transition: 'all 0.2s',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'space-between'
                                            }}
                                        >
                                            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                                                <div style={{
                                                    width: '8px',
                                                    height: '40px',
                                                    background: course.color || 'var(--primary)',
                                                    borderRadius: '4px'
                                                }} />
                                                <div>
                                                    <div style={{ fontWeight: 600 }}>{course.name}</div>
                                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                                        {course.total_concepts || 0} concepts
                                                    </div>
                                                </div>
                                            </div>
                                            {selectedCourse === course.id && (
                                                <CheckCircle size={24} color="var(--primary)" />
                                            )}
                                        </motion.div>
                                    ))}
                                </div>
                            )}
                        </div>

                        {/* Time Selection */}
                        <div className="card" style={{ marginBottom: '24px' }}>
                            <h2 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <Clock size={24} color="var(--secondary)" /> How Much Time Do You Have?
                            </h2>

                            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '12px' }}>
                                {hourOptions.map(option => (
                                    <motion.div
                                        key={option.value}
                                        whileHover={{ scale: 1.05 }}
                                        whileTap={{ scale: 0.98 }}
                                        onClick={() => setHours(option.value)}
                                        style={{
                                            padding: '20px 16px',
                                            borderRadius: '16px',
                                            border: hours === option.value
                                                ? '2px solid var(--secondary)'
                                                : '1px solid rgba(255,255,255,0.1)',
                                            background: hours === option.value
                                                ? 'rgba(139, 92, 246, 0.15)'
                                                : 'var(--bg-input)',
                                            cursor: 'pointer',
                                            textAlign: 'center',
                                            transition: 'all 0.2s'
                                        }}
                                    >
                                        <div style={{ fontSize: '1.5rem', marginBottom: '6px' }}>{option.emoji}</div>
                                        <div style={{ fontWeight: 600 }}>{option.label}</div>
                                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{option.desc}</div>
                                    </motion.div>
                                ))}
                            </div>
                        </div>

                        {/* Generate Button */}
                        <motion.button
                            whileHover={{ scale: 1.02 }}
                            whileTap={{ scale: 0.98 }}
                            className="btn btn-primary"
                            onClick={generatePlan}
                            disabled={!selectedCourse}
                            style={{
                                width: '100%',
                                padding: '18px',
                                fontSize: '1.1rem',
                                background: 'linear-gradient(135deg, #ef4444, #f97316)',
                                justifyContent: 'center'
                            }}
                        >
                            <Zap size={22} /> Generate My Cram Plan <ArrowRight size={22} />
                        </motion.button>
                    </motion.div>
                )}

                {step === 1 && (
                    <motion.div
                        key="generating"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        style={{ textAlign: 'center', padding: '60px 20px' }}
                    >
                        <motion.div
                            animate={{ rotate: 360 }}
                            transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                            style={{ display: 'inline-block', marginBottom: '24px' }}
                        >
                            <Brain size={60} color="var(--primary)" />
                        </motion.div>
                        <h2>AI is analyzing your course...</h2>
                        <p style={{ color: 'var(--text-secondary)' }}>
                            Identifying high-value topics and creating your optimized study plan
                        </p>
                        <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginTop: '20px' }}>
                            {[0, 1, 2].map(i => (
                                <motion.div
                                    key={i}
                                    animate={{ scale: [1, 1.3, 1] }}
                                    transition={{ duration: 0.6, repeat: Infinity, delay: i * 0.2 }}
                                    style={{
                                        width: '12px',
                                        height: '12px',
                                        borderRadius: '50%',
                                        background: 'var(--primary)'
                                    }}
                                />
                            ))}
                        </div>
                    </motion.div>
                )}

                {step === 2 && plan && (
                    <motion.div
                        key="plan"
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                    >
                        {/* Plan Header */}
                        <div className="card" style={{
                            marginBottom: '24px',
                            background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(52, 211, 153, 0.05))',
                            border: '1px solid rgba(16, 185, 129, 0.2)'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
                                <div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                                        <CheckCircle size={28} color="var(--success)" />
                                        <h2 style={{ margin: 0 }}>Your Cram Plan is Ready!</h2>
                                    </div>
                                    <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
                                        {selectedCourseData?.name} • {hours} hour study session
                                    </p>
                                </div>
                                <div style={{ display: 'flex', gap: '12px' }}>
                                    <button className="btn btn-secondary" onClick={() => { setStep(0); setPlan(null); }}>
                                        New Plan
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Priority Topics from high_priority_concepts */}
                        <div className="card" style={{ marginBottom: '24px' }}>
                            <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <Target size={22} color="var(--error)" /> Priority Topics (Focus 80% here)
                            </h3>
                            <div style={{ display: 'grid', gap: '12px' }}>
                                {(plan.high_priority_concepts || []).slice(0, 5).map((topic, i) => (
                                    <div
                                        key={i}
                                        style={{
                                            padding: '16px',
                                            background: 'rgba(239, 68, 68, 0.1)',
                                            borderRadius: '12px',
                                            borderLeft: '4px solid var(--error)',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '14px'
                                        }}
                                    >
                                        <div style={{
                                            width: '32px',
                                            height: '32px',
                                            background: 'var(--error)',
                                            borderRadius: '50%',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            fontSize: '0.85rem',
                                            fontWeight: 700
                                        }}>
                                            {i + 1}
                                        </div>
                                        <div style={{ fontWeight: 600 }}>{topic}</div>
                                    </div>
                                ))}
                                {(!plan.high_priority_concepts || plan.high_priority_concepts.length === 0) && (
                                    <p style={{ color: 'var(--text-muted)' }}>No high priority concepts found.</p>
                                )}
                            </div>
                        </div>

                        {/* Study Schedule from topics */}
                        {plan.topics && plan.topics.length > 0 && (
                            <div className="card" style={{ marginBottom: '24px' }}>
                                <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                    <Clock size={22} color="var(--secondary)" /> Your Study Schedule
                                </h3>
                                <div style={{ display: 'grid', gap: '12px' }}>
                                    {plan.topics.slice(0, 10).map((topicPlan, i) => (
                                        <div
                                            key={i}
                                            style={{
                                                padding: '16px',
                                                background: 'var(--bg-input)',
                                                borderRadius: '12px',
                                                display: 'flex',
                                                alignItems: 'center',
                                                gap: '16px'
                                            }}
                                        >
                                            <div style={{
                                                padding: '8px 14px',
                                                background: 'rgba(139, 92, 246, 0.2)',
                                                borderRadius: '8px',
                                                fontWeight: 600,
                                                color: 'var(--secondary)',
                                                minWidth: '70px',
                                                textAlign: 'center'
                                            }}>
                                                {topicPlan.allocated_minutes} min
                                            </div>
                                            <div style={{ flex: 1 }}>
                                                <div style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    {topicPlan.topic}
                                                    <span style={{
                                                        fontSize: '0.75rem',
                                                        padding: '3px 8px',
                                                        background: topicPlan.priority >= 8 ? 'rgba(239, 68, 68, 0.2)' : 'rgba(99, 102, 241, 0.2)',
                                                        borderRadius: '6px',
                                                        color: topicPlan.priority >= 8 ? 'var(--error)' : 'var(--primary-light)'
                                                    }}>
                                                        Priority {topicPlan.priority}/10
                                                    </span>
                                                </div>
                                                {topicPlan.key_points && topicPlan.key_points.length > 0 && (
                                                    <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                                                        {topicPlan.key_points[0]}
                                                    </div>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div style={{ marginTop: '16px', padding: '12px', background: 'rgba(16, 185, 129, 0.1)', borderRadius: '8px', textAlign: 'center' }}>
                                    <strong style={{ color: 'var(--success)' }}>Total Study Time:</strong> {plan.total_minutes} minutes ({(plan.total_minutes / 60).toFixed(1)} hours)
                                </div>
                            </div>
                        )}

                        {/* Skip Topics */}
                        {plan.skip_topics && plan.skip_topics.length > 0 && (
                            <div className="card" style={{ marginBottom: '24px', background: 'rgba(156, 163, 175, 0.1)' }}>
                                <h3 style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--text-muted)' }}>
                                    ⏭️ Topics to Skip (Low Priority)
                                </h3>
                                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                                    {plan.skip_topics.join(', ')}
                                </p>
                            </div>
                        )}

                        {/* Tips */}
                        <div className="card" style={{ background: 'rgba(99, 102, 241, 0.1)', border: '1px solid rgba(99, 102, 241, 0.2)', marginBottom: '24px' }}>
                            <h3 style={{ marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '10px' }}>
                                <Sparkles size={22} color="var(--primary-light)" /> Pro Tips
                            </h3>
                            <ul style={{ margin: 0, paddingLeft: '20px', color: 'var(--text-secondary)' }}>
                                <li style={{ marginBottom: '8px' }}>Take a 5-minute break every 25 minutes (Pomodoro technique)</li>
                                <li style={{ marginBottom: '8px' }}>Stay hydrated and have healthy snacks ready</li>
                                <li style={{ marginBottom: '8px' }}>Put your phone on Do Not Disturb mode</li>
                                <li style={{ marginBottom: '8px' }}>Focus on understanding concepts, not just memorizing</li>
                                <li>Get at least 6 hours of sleep before your exam!</li>
                            </ul>
                        </div>

                        {/* Start Learning Button */}
                        <motion.div
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            className="card"
                            style={{
                                background: 'linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 182, 212, 0.1))',
                                border: '2px solid rgba(16, 185, 129, 0.3)',
                                textAlign: 'center',
                                padding: '32px'
                            }}
                        >
                            <h3 style={{ marginBottom: '12px', color: 'var(--success)' }}>
                                🚀 Ready to Start Learning?
                            </h3>
                            <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', maxWidth: '500px', margin: '0 auto 24px' }}>
                                Let me teach you these topics one by one in an interactive chat session.
                                I'll explain each concept and answer any questions you have!
                            </p>
                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                className="btn btn-primary"
                                onClick={() => {
                                    // Store the cram topics in localStorage
                                    const topicsToLearn = plan.high_priority_concepts || [];
                                    const topicsList = topicsToLearn.join(', ');
                                    localStorage.setItem('studybuddy_cram_topics', JSON.stringify({
                                        courseId: selectedCourse,
                                        courseName: selectedCourseData?.name,
                                        topics: topicsToLearn
                                    }));

                                    // Navigate to chat with a cram mode flag
                                    navigate(`/app/chat?mode=cram&topics=${encodeURIComponent(topicsList)}&course=${selectedCourse}`);
                                    toast.success('Starting your cram session!');
                                }}
                                style={{
                                    padding: '16px 32px',
                                    fontSize: '1.1rem',
                                    background: 'linear-gradient(135deg, #10b981, #06b6d4)',
                                    justifyContent: 'center',
                                    gap: '10px'
                                }}
                            >
                                <MessageCircle size={22} /> Start Learning with AI Chat <ArrowRight size={22} />
                            </motion.button>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}

