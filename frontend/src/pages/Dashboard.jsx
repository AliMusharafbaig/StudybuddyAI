import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BookOpen, Target, Clock, Zap, TrendingUp, Plus, ArrowRight } from 'lucide-react'
import api from '../api'
import { useAuthStore } from '../store/authStore'

export default function Dashboard() {
    const { user } = useAuthStore()
    const [courses, setCourses] = useState([])
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async () => {
        try {
            const [coursesRes, statsRes] = await Promise.all([
                api.get('/courses'),
                api.get('/analytics/progress').catch(() => ({ data: null }))
            ])
            setCourses(coursesRes.data || [])
            setStats(statsRes.data)
        } catch (e) {
            console.error(e)
        } finally {
            setLoading(false)
        }
    }

    const StatCard = ({ icon: Icon, label, value, color }) => (
        <div className="card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                <div style={{
                    width: '48px',
                    height: '48px',
                    background: `${color}20`,
                    borderRadius: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                }}>
                    <Icon size={24} color={color} />
                </div>
                <div>
                    <div style={{ fontSize: '1.75rem', fontWeight: 700 }}>{value}</div>
                    <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{label}</div>
                </div>
            </div>
        </div>
    )

    return (
        <div>
            {/* Header */}
            <div style={{ marginBottom: '32px' }}>
                <h1 style={{ marginBottom: '8px' }}>
                    Welcome back, {user?.full_name?.split(' ')[0] || 'Student'}! 👋
                </h1>
                <p style={{ color: 'var(--text-secondary)' }}>
                    Ready to continue your learning journey?
                </p>
            </div>

            {/* Stats */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
                gap: '20px',
                marginBottom: '32px'
            }}>
                <StatCard icon={BookOpen} label="Courses" value={courses.length} color="#6366f1" />
                <StatCard icon={Target} label="Quizzes" value={stats?.total_quizzes_completed || 0} color="#10b981" />
                <StatCard icon={Clock} label="Study Time" value={`${stats?.total_study_time_minutes || 0}m`} color="#f59e0b" />
                <StatCard icon={TrendingUp} label="Avg Score" value={`${Math.round(stats?.average_score || 0)}%`} color="#8b5cf6" />
            </div>

            {/* Quick Actions */}
            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
                gap: '20px',
                marginBottom: '32px'
            }}>
                <Link to="/app/cram" style={{ textDecoration: 'none' }}>
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        className="card"
                        style={{
                            background: 'linear-gradient(135deg, #ef4444 0%, #f97316 100%)',
                            cursor: 'pointer'
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <Zap size={32} />
                            <div>
                                <h3 style={{ margin: 0 }}>🚨 Emergency Cram Mode</h3>
                                <p style={{ margin: 0, opacity: 0.9 }}>Exam tomorrow? We got you!</p>
                            </div>
                        </div>
                    </motion.div>
                </Link>

                <Link to="/app/courses" style={{ textDecoration: 'none' }}>
                    <motion.div
                        whileHover={{ scale: 1.02 }}
                        className="card"
                        style={{
                            background: 'var(--gradient-primary)',
                            cursor: 'pointer'
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <Plus size={32} />
                            <div>
                                <h3 style={{ margin: 0 }}>Add New Course</h3>
                                <p style={{ margin: 0, opacity: 0.9 }}>Upload materials & start learning</p>
                            </div>
                        </div>
                    </motion.div>
                </Link>
            </div>

            {/* Courses */}
            <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h2>Your Courses</h2>
                    <Link to="/app/courses" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        View All <ArrowRight size={18} />
                    </Link>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-secondary)' }}>
                        Loading...
                    </div>
                ) : courses.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
                        <BookOpen size={48} color="var(--text-muted)" style={{ marginBottom: '16px' }} />
                        <h3>No courses yet</h3>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
                            Create your first course to start learning with AI
                        </p>
                        <Link to="/app/courses" className="btn btn-primary">
                            <Plus size={20} /> Create Course
                        </Link>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
                        {courses.slice(0, 4).map(course => (
                            <Link key={course.id} to={`/app/courses/${course.id}`} style={{ textDecoration: 'none' }}>
                                <motion.div whileHover={{ scale: 1.02 }} className="card">
                                    <div style={{
                                        width: '100%',
                                        height: '8px',
                                        background: course.color || 'var(--primary)',
                                        borderRadius: '4px',
                                        marginBottom: '16px'
                                    }} />
                                    <h3 style={{ marginBottom: '8px' }}>{course.name}</h3>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem', marginBottom: '16px' }}>
                                        {course.description || 'No description'}
                                    </p>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                        <span>{course.total_concepts || 0} concepts</span>
                                        <span>{course.mastery_percentage || 0}% mastery</span>
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
