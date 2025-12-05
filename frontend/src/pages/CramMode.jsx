import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Zap, Clock, Target, Lightbulb, Play, CheckCircle } from 'lucide-react'
import api from '../api'
import toast from 'react-hot-toast'

export default function CramMode() {
    const [courses, setCourses] = useState([])
    const [selectedCourse, setSelectedCourse] = useState('')
    const [hours, setHours] = useState(3)
    const [plan, setPlan] = useState(null)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        api.get('/courses').then(r => setCourses(r.data)).catch(() => { })
    }, [])

    const generatePlan = async () => {
        if (!selectedCourse) return toast.error('Select a course')
        setLoading(true)
        try {
            const { data } = await api.post('/cram/generate', {
                course_id: selectedCourse,
                available_hours: hours
            })
            setPlan(data)
        } catch (e) {
            toast.error('Failed to generate plan')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} style={{
                    width: '80px', height: '80px', background: 'linear-gradient(135deg, #ef4444, #f97316)',
                    borderRadius: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    margin: '0 auto 20px', boxShadow: '0 0 40px rgba(239, 68, 68, 0.3)'
                }}>
                    <Zap size={40} color="white" />
                </motion.div>
                <h1>🚨 Emergency Cram Mode</h1>
                <p style={{ color: 'var(--text-secondary)', maxWidth: '500px', margin: '0 auto' }}>
                    Exam tomorrow? We'll create an optimized study plan based on your available time.
                </p>
            </div>

            {!plan ? (
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="card" style={{ maxWidth: '500px', margin: '0 auto', padding: '32px' }}>
                    <div style={{ marginBottom: '24px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>📚 Select Course</label>
                        <select className="input" value={selectedCourse} onChange={e => setSelectedCourse(e.target.value)}>
                            <option value="">Choose a course...</option>
                            {courses.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                    </div>

                    <div style={{ marginBottom: '32px' }}>
                        <label style={{ display: 'block', marginBottom: '8px', fontWeight: 500 }}>
                            ⏰ Available Hours: <span style={{ color: 'var(--primary)' }}>{hours}h</span>
                        </label>
                        <input type="range" min="1" max="12" value={hours} onChange={e => setHours(+e.target.value)}
                            style={{ width: '100%', accentColor: 'var(--primary)' }} />
                        <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
                            <span>1 hour</span><span>12 hours</span>
                        </div>
                    </div>

                    <button className="btn btn-primary w-full" onClick={generatePlan} disabled={loading} style={{ padding: '16px' }}>
                        {loading ? 'Generating...' : <><Play size={20} /> Generate Cram Plan</>}
                    </button>
                </motion.div>
            ) : (
                <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                    <div className="card" style={{ marginBottom: '24px', background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(249, 115, 22, 0.1))' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <h2 style={{ margin: 0 }}>Your {hours}-Hour Cram Plan</h2>
                                <p style={{ color: 'var(--text-secondary)', margin: '8px 0 0' }}>{plan.topic_count} topics • {plan.sessions?.length || 0} study sessions</p>
                            </div>
                            <button className="btn btn-secondary" onClick={() => setPlan(null)}>New Plan</button>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gap: '16px' }}>
                        {plan.sessions?.map((session, i) => (
                            <motion.div key={i} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.1 }} className="card">
                                <div style={{ display: 'flex', gap: '16px' }}>
                                    <div style={{
                                        width: '48px', height: '48px', background: 'var(--gradient-primary)', borderRadius: '12px',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, flexShrink: 0
                                    }}>
                                        {i + 1}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                            <h3 style={{ margin: 0 }}>{session.topic}</h3>
                                            <span style={{ color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                                <Clock size={16} /> {session.duration_minutes}m
                                            </span>
                                        </div>
                                        <p style={{ color: 'var(--text-secondary)', margin: 0, fontSize: '0.9rem' }}>{session.description}</p>
                                        <div style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
                                            {session.activities?.map((a, j) => (
                                                <span key={j} style={{ padding: '4px 10px', background: 'var(--bg-input)', borderRadius: '8px', fontSize: '0.8rem' }}>
                                                    {a}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </div>

                    {plan.tips && (
                        <div className="card" style={{ marginTop: '24px' }}>
                            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}><Lightbulb size={20} color="var(--warning)" /> Pro Tips</h3>
                            <ul style={{ color: 'var(--text-secondary)', paddingLeft: '20px', margin: 0 }}>
                                {plan.tips.map((t, i) => <li key={i} style={{ marginBottom: '8px' }}>{t}</li>)}
                            </ul>
                        </div>
                    )}
                </div>
            )}
        </div>
    )
}
