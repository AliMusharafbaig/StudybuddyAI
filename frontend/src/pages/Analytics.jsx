import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { TrendingUp, Target, Brain, AlertTriangle, Clock, Award } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import api from '../api'

export default function Analytics() {
    const [progress, setProgress] = useState(null)
    const [mastery, setMastery] = useState([])
    const [confusion, setConfusion] = useState([])
    const [loading, setLoading] = useState(true)

    useEffect(() => { loadData() }, [])

    const loadData = async () => {
        try {
            const [p, m, c] = await Promise.all([
                api.get('/analytics/progress').catch(() => ({ data: null })),
                api.get('/analytics/mastery').catch(() => ({ data: [] })),
                api.get('/analytics/confusion').catch(() => ({ data: [] }))
            ])
            setProgress(p.data)
            setMastery(m.data)
            setConfusion(c.data)
        } finally {
            setLoading(false)
        }
    }

    const COLORS = ['#6366f1', '#8b5cf6', '#a855f7', '#d946ef', '#ec4899']

    if (loading) return <div style={{ textAlign: 'center', padding: '80px' }}>Loading analytics...</div>

    const stats = [
        { icon: Target, label: 'Quizzes Completed', value: progress?.total_quizzes_completed || 0, color: '#6366f1' },
        { icon: Clock, label: 'Study Time', value: `${progress?.total_study_time_minutes || 0}m`, color: '#8b5cf6' },
        { icon: Award, label: 'Avg Score', value: `${Math.round(progress?.average_score || 0)}%`, color: '#10b981' },
        { icon: Brain, label: 'Concepts Mastered', value: mastery.filter(m => m.level >= 80).length, color: '#f59e0b' },
    ]

    const chartData = progress?.recent_scores?.map((s, i) => ({ name: `Quiz ${i + 1}`, score: s })) || []

    return (
        <div>
            <h1 style={{ marginBottom: '8px' }}>📊 Learning Analytics</h1>
            <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>Track your progress and identify areas for improvement</p>

            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '20px', marginBottom: '32px' }}>
                {stats.map(({ icon: Icon, label, value, color }) => (
                    <motion.div key={label} whileHover={{ scale: 1.02 }} className="card" style={{ padding: '24px' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                            <div style={{ width: '48px', height: '48px', background: `${color}20`, borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Icon size={24} color={color} />
                            </div>
                            <div>
                                <div style={{ fontSize: '1.75rem', fontWeight: 700 }}>{value}</div>
                                <div style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>{label}</div>
                            </div>
                        </div>
                    </motion.div>
                ))}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
                {/* Score Chart */}
                <div className="card">
                    <h3 style={{ marginBottom: '20px' }}><TrendingUp size={20} style={{ marginRight: '8px', verticalAlign: '-4px' }} />Quiz Performance</h3>
                    {chartData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                                <XAxis dataKey="name" stroke="var(--text-muted)" />
                                <YAxis stroke="var(--text-muted)" domain={[0, 100]} />
                                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: 'none', borderRadius: '8px' }} />
                                <Line type="monotone" dataKey="score" stroke="var(--primary)" strokeWidth={3} dot={{ fill: 'var(--primary)' }} />
                            </LineChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ height: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                            Complete quizzes to see your progress
                        </div>
                    )}
                </div>

                {/* Mastery Distribution */}
                <div className="card">
                    <h3 style={{ marginBottom: '20px' }}><Brain size={20} style={{ marginRight: '8px', verticalAlign: '-4px' }} />Concept Mastery</h3>
                    {mastery.length > 0 ? (
                        <ResponsiveContainer width="100%" height={250}>
                            <PieChart>
                                <Pie data={mastery.slice(0, 5)} dataKey="level" nameKey="concept" cx="50%" cy="50%" innerRadius={60} outerRadius={100} paddingAngle={5}>
                                    {mastery.slice(0, 5).map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                                </Pie>
                                <Tooltip contentStyle={{ background: 'var(--bg-card)', border: 'none', borderRadius: '8px' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    ) : (
                        <div style={{ height: '250px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                            Study concepts to track mastery
                        </div>
                    )}
                </div>
            </div>

            {/* Confusion Patterns */}
            <div className="card" style={{ marginTop: '24px' }}>
                <h3 style={{ marginBottom: '20px' }}><AlertTriangle size={20} style={{ marginRight: '8px', verticalAlign: '-4px' }} />Confusion Patterns</h3>
                {confusion.length > 0 ? (
                    <div style={{ display: 'grid', gap: '12px' }}>
                        {confusion.slice(0, 5).map((c, i) => (
                            <div key={i} style={{ padding: '16px', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '12px', borderLeft: '4px solid var(--error)' }}>
                                <div style={{ fontWeight: 600, marginBottom: '4px' }}>{c.pattern_type}</div>
                                <p style={{ color: 'var(--text-secondary)', margin: '0 0 8px', fontSize: '0.9rem' }}>{c.description}</p>
                                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Triggered {c.trigger_count} times</div>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div style={{ textAlign: 'center', padding: '40px', color: 'var(--text-muted)' }}>
                        No confusion patterns detected. Keep learning! 🎉
                    </div>
                )}
            </div>
        </div>
    )
}
