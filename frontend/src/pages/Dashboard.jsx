import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
    BookOpen, Target, Clock, Zap, TrendingUp, Plus, ArrowRight,
    Flame, Trophy, Star, MessageCircle, Brain, Sparkles, ChevronRight
} from 'lucide-react'
import api from '../api'
import { useAuthStore } from '../store/authStore'
import ProgressTracker from '../components/ProgressTracker'

export default function Dashboard() {
    const { user } = useAuthStore()
    const [courses, setCourses] = useState([])
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)
    const [streak, setStreak] = useState(0)
    const [dailyGoal, setDailyGoal] = useState({ current: 0, target: 30 })

    useEffect(() => {
        loadData()
        // Load streak from localStorage
        const savedStreak = localStorage.getItem('studybuddy_streak')
        const lastStudy = localStorage.getItem('studybuddy_last_study')
        const today = new Date().toDateString()
        const yesterday = new Date(Date.now() - 86400000).toDateString()

        if (lastStudy === today) {
            setStreak(parseInt(savedStreak) || 1)
        } else if (lastStudy === yesterday) {
            setStreak(parseInt(savedStreak) || 0)
        } else {
            setStreak(0)
        }

        // Track visit
        if (lastStudy !== today) {
            const newStreak = lastStudy === yesterday ? (parseInt(savedStreak) || 0) + 1 : 1
            localStorage.setItem('studybuddy_streak', newStreak)
            localStorage.setItem('studybuddy_last_study', today)
            setStreak(newStreak)
        }
    }, [])

    const loadData = async () => {
        try {
            const [coursesRes, statsRes] = await Promise.all([
                api.get('/courses'),
                api.get('/analytics/progress').catch(() => ({ data: null }))
            ])
            setCourses(coursesRes.data || [])
            setStats(statsRes.data)
            if (statsRes.data?.total_study_time_minutes) {
                setDailyGoal(prev => ({ ...prev, current: Math.min(statsRes.data.total_study_time_minutes, prev.target) }))
            }
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    const motivationalQuotes = [
        "Every expert was once a beginner. Keep going! 💪",
        "Small progress is still progress. You've got this! 🌟",
        "The only way to learn is to challenge yourself. 🚀",
        "Your dedication today shapes your success tomorrow. ✨",
        "Knowledge compounds. Every minute counts! 📚"
    ]
    const todayQuote = motivationalQuotes[new Date().getDate() % motivationalQuotes.length]

    const getGreeting = () => {
        const hour = new Date().getHours()
        if (hour < 12) return 'Good morning'
        if (hour < 17) return 'Good afternoon'
        return 'Good evening'
    }

    const getStreakEmoji = () => {
        if (streak >= 30) return '👑'
        if (streak >= 14) return '🔥'
        if (streak >= 7) return '⭐'
        if (streak >= 3) return '✨'
        return '💡'
    }

    const StatCard = ({ icon: Icon, label, value, color, subtext }) => (
        <motion.div
            whileHover={{ scale: 1.02, y: -4 }}
            className="card"
            style={{ padding: '24px' }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{
                    width: '52px',
                    height: '52px',
                    background: `${color}20`,
                    borderRadius: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <Icon size={26} color={color} />
                </div>
                <div>
                    <div style={{ fontSize: '2rem', fontWeight: 700 }}>{value}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{label}</div>
                    {subtext && <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{subtext}</div>}
                </div>
            </div>
        </motion.div>
    )

    return (
        <div>
            {/* Header with greeting and streak */}
            <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: '28px',
                flexWrap: 'wrap',
                gap: '20px'
            }}>
                <div>
                    <h1 style={{ marginBottom: '8px', fontSize: '2rem' }}>
                        {getGreeting()}, {user?.full_name?.split(' ')[0] || 'Student'}! 👋
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', maxWidth: '500px' }}>
                        {todayQuote}
                    </p>
                </div>

                {/* Progress Summary Card */}
                <motion.div
                    whileHover={{ scale: 1.02 }}
                    style={{
                        background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                        borderRadius: '16px',
                        padding: '16px 24px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '16px',
                        minWidth: '200px'
                    }}
                >
                    <div style={{
                        width: '50px',
                        height: '50px',
                        background: 'rgba(255,255,255,0.2)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <Trophy size={28} color="white" />
                    </div>
                    <div>
                        <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'white' }}>
                            {stats?.total_quizzes_completed || 0} Quizzes
                        </div>
                        <div style={{ opacity: 0.9, fontSize: '0.85rem', color: 'rgba(255,255,255,0.9)' }}>
                            {stats?.average_score ? `${Math.round(stats.average_score)}% avg score` : 'Start your first quiz!'}
                        </div>
                    </div>
                </motion.div>
            </div>

            {/* Daily Progress Bar */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="card"
                style={{ marginBottom: '28px', padding: '20px 24px' }}
            >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <Flame size={22} color="#f59e0b" />
                        <span style={{ fontWeight: 600 }}>Daily Study Goal</span>
                    </div>
                    <span style={{ color: 'var(--text-secondary)' }}>
                        {dailyGoal.current} / {dailyGoal.target} minutes
                    </span>
                </div>
                <div style={{
                    height: '10px',
                    background: 'var(--bg-input)',
                    borderRadius: '10px',
                    overflow: 'hidden'
                }}>
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${(dailyGoal.current / dailyGoal.target) * 100}%` }}
                        transition={{ duration: 1, ease: 'easeOut' }}
                        style={{
                            height: '100%',
                            background: dailyGoal.current >= dailyGoal.target
                                ? 'linear-gradient(90deg, #10b981, #34d399)'
                                : 'linear-gradient(90deg, #6366f1, #8b5cf6)',
                            borderRadius: '10px'
                        }}
                    />
                </div>
                {dailyGoal.current >= dailyGoal.target && (
                    <div style={{ marginTop: '8px', color: 'var(--success)', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '6px' }}>
                        <Trophy size={16} /> Goal achieved! You're a star! 🌟
                    </div>
                )}
            </motion.div>

            {/* Stats Grid */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '20px',
                marginBottom: '28px'
            }}>
                <StatCard icon={BookOpen} label="Courses" value={courses.length} color="#6366f1" />
                <StatCard icon={Target} label="Quizzes Completed" value={stats?.total_quizzes_completed || 0} color="#10b981" />
                <StatCard icon={Clock} label="Study Time" value={`${stats?.total_study_time_minutes || 0}m`} color="#f59e0b" />
                <StatCard icon={TrendingUp} label="Average Score" value={`${Math.round(stats?.average_score || 0)}%`} color="#8b5cf6" />
            </div>

            {/* Progress Tracker - XP and Achievements */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ marginBottom: '28px' }}
            >
                <ProgressTracker user={user} />
            </motion.div>

            {/* Quick Actions - More options */}
            <h2 style={{ marginBottom: '16px' }}>Quick Actions ⚡</h2>
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
                gap: '16px',
                marginBottom: '32px'
            }}>
                <Link to="/app/cram" style={{ textDecoration: 'none' }}>
                    <motion.div
                        whileHover={{ scale: 1.02, y: -4 }}
                        className="card"
                        style={{
                            background: 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)',
                            cursor: 'pointer',
                            padding: '20px',
                            color: 'white'
                        }}
                    >
                        <Zap size={28} color="white" style={{ marginBottom: '12px' }} />
                        <h3 style={{ margin: '0 0 4px', color: 'white' }}>🚨 Cram Mode</h3>
                        <p style={{ margin: 0, opacity: 0.9, fontSize: '0.85rem', color: 'white' }}>Emergency study plan</p>
                    </motion.div>
                </Link>

                <Link to="/app/chat" style={{ textDecoration: 'none' }}>
                    <motion.div
                        whileHover={{ scale: 1.02, y: -4 }}
                        className="card"
                        style={{
                            background: 'linear-gradient(135deg, #06b6d4 0%, #0891b2 100%)',
                            cursor: 'pointer',
                            padding: '20px',
                            color: 'white'
                        }}
                    >
                        <MessageCircle size={28} color="white" style={{ marginBottom: '12px' }} />
                        <h3 style={{ margin: '0 0 4px', color: 'white' }}>💬 AI Chat</h3>
                        <p style={{ margin: 0, opacity: 0.9, fontSize: '0.85rem', color: 'white' }}>Ask anything</p>
                    </motion.div>
                </Link>

                <Link to="/app/courses" style={{ textDecoration: 'none' }}>
                    <motion.div
                        whileHover={{ scale: 1.02, y: -4 }}
                        className="card"
                        style={{
                            background: 'var(--gradient-primary)',
                            cursor: 'pointer',
                            padding: '20px',
                            color: 'white'
                        }}
                    >
                        <Plus size={28} color="white" style={{ marginBottom: '12px' }} />
                        <h3 style={{ margin: '0 0 4px', color: 'white' }}>📚 Add Course</h3>
                        <p style={{ margin: 0, opacity: 0.9, fontSize: '0.85rem', color: 'white' }}>Upload materials</p>
                    </motion.div>
                </Link>

                <Link to="/app/analytics" style={{ textDecoration: 'none' }}>
                    <motion.div
                        whileHover={{ scale: 1.02, y: -4 }}
                        className="card"
                        style={{
                            background: 'linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%)',
                            cursor: 'pointer',
                            padding: '20px',
                            color: 'white'
                        }}
                    >
                        <TrendingUp size={28} color="white" style={{ marginBottom: '12px' }} />
                        <h3 style={{ margin: '0 0 4px', color: 'white' }}>📊 Analytics</h3>
                        <p style={{ margin: 0, opacity: 0.9, fontSize: '0.85rem', color: 'white' }}>Track progress</p>
                    </motion.div>
                </Link>
            </div>

            {/* Courses Section */}
            <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2>Your Courses 📚</h2>
                    <Link to="/app/courses" style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--primary-light)' }}>
                        View All <ArrowRight size={18} />
                    </Link>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                        Loading...
                    </div>
                ) : courses.length === 0 ? (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="card"
                        style={{ textAlign: 'center', padding: '60px' }}
                    >
                        <div style={{
                            width: '80px',
                            height: '80px',
                            background: 'var(--gradient-primary)',
                            borderRadius: '20px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 20px'
                        }}>
                            <BookOpen size={40} color="white" />
                        </div>
                        <h3>Start Your Learning Journey</h3>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', maxWidth: '400px', margin: '0 auto 24px' }}>
                            Create your first course, upload your study materials, and let AI help you ace your exams!
                        </p>
                        <Link to="/app/courses" className="btn btn-primary" style={{ padding: '14px 28px' }}>
                            <Plus size={20} /> Create Your First Course
                        </Link>
                    </motion.div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                        {courses.slice(0, 4).map((course, i) => (
                            <Link key={course.id} to={`/app/courses/${course.id}`} style={{ textDecoration: 'none' }}>
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    transition={{ delay: i * 0.1 }}
                                    whileHover={{ scale: 1.02, y: -4 }}
                                    className="card"
                                >
                                    <div style={{
                                        width: '100%',
                                        height: '6px',
                                        background: course.color || 'var(--primary)',
                                        borderRadius: '4px',
                                        marginBottom: '16px'
                                    }} />
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <h3 style={{ marginBottom: '8px' }}>{course.name}</h3>
                                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '16px' }}>
                                                {course.description?.slice(0, 60) || 'No description'}
                                                {(course.description?.length || 0) > 60 && '...'}
                                            </p>
                                        </div>
                                        <ChevronRight size={20} color="var(--text-muted)" />
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                                        <span>🧠 {course.total_concepts || 0} concepts</span>
                                        <span style={{ color: 'var(--success)' }}>✓ {course.mastery_percentage || 0}% mastery</span>
                                    </div>
                                </motion.div>
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
