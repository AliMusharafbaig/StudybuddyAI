import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Plus, Upload, BookOpen, X } from 'lucide-react'
import api from '../api'
import toast from 'react-hot-toast'

export default function Courses() {
    const [courses, setCourses] = useState([])
    const [showModal, setShowModal] = useState(false)
    const [form, setForm] = useState({ name: '', description: '', code: '', color: '#6366f1' })
    const [loading, setLoading] = useState(true)

    useEffect(() => { loadCourses() }, [])

    const loadCourses = async () => {
        try {
            const { data } = await api.get('/courses')
            setCourses(data)
        } catch (e) {
            toast.error('Failed to load courses')
        } finally {
            setLoading(false)
        }
    }

    const createCourse = async (e) => {
        e.preventDefault()
        try {
            await api.post('/courses', form)
            toast.success('Course created!')
            setShowModal(false)
            setForm({ name: '', description: '', code: '', color: '#6366f1' })
            loadCourses()
        } catch (e) {
            toast.error('Failed to create course')
        }
    }

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <h1>Your Courses</h1>
                <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                    <Plus size={20} /> New Course
                </button>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '60px' }}>Loading...</div>
            ) : courses.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '80px' }}>
                    <BookOpen size={64} color="var(--text-muted)" style={{ marginBottom: '20px' }} />
                    <h2>No courses yet</h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '24px' }}>
                        Create your first course to start learning with AI
                    </p>
                    <button className="btn btn-primary" onClick={() => setShowModal(true)}>
                        <Plus size={20} /> Create Your First Course
                    </button>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px' }}>
                    {courses.map(course => (
                        <Link key={course.id} to={`/app/courses/${course.id}`} style={{ textDecoration: 'none' }}>
                            <motion.div whileHover={{ scale: 1.02 }} className="card" style={{ height: '100%' }}>
                                <div style={{ width: '100%', height: '10px', background: course.color, borderRadius: '5px', marginBottom: '20px' }} />
                                <h3>{course.name}</h3>
                                {course.code && <div style={{ color: 'var(--primary-light)', marginBottom: '8px' }}>{course.code}</div>}
                                <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '20px' }}>
                                    {course.description || 'No description'}
                                </p>
                                <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    <span>📚 {course.total_materials || 0} materials</span>
                                    <span>🧠 {course.total_concepts || 0} concepts</span>
                                </div>
                                <div style={{ marginTop: '16px', background: 'var(--bg-input)', borderRadius: '8px', padding: '12px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                                        <span style={{ fontSize: '0.875rem' }}>Mastery</span>
                                        <span style={{ fontSize: '0.875rem', color: 'var(--primary-light)' }}>{course.mastery_percentage || 0}%</span>
                                    </div>
                                    <div style={{ height: '6px', background: 'var(--bg-dark)', borderRadius: '3px', overflow: 'hidden' }}>
                                        <div style={{ width: `${course.mastery_percentage || 0}%`, height: '100%', background: 'var(--gradient-primary)', borderRadius: '3px' }} />
                                    </div>
                                </div>
                            </motion.div>
                        </Link>
                    ))}
                </div>
            )}

            {/* Create Modal */}
            {showModal && (
                <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
                    <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="card" style={{ width: '100%', maxWidth: '480px', margin: '24px' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '24px' }}>
                            <h2>Create Course</h2>
                            <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                                <X size={24} />
                            </button>
                        </div>
                        <form onSubmit={createCourse}>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-secondary)' }}>Course Name *</label>
                                <input className="input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required placeholder="e.g., Natural Language Processing" />
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-secondary)' }}>Course Code</label>
                                <input className="input" value={form.code} onChange={e => setForm({ ...form, code: e.target.value })} placeholder="e.g., CS4063" />
                            </div>
                            <div style={{ marginBottom: '16px' }}>
                                <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-secondary)' }}>Description</label>
                                <textarea className="input" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="What is this course about?" rows={3} />
                            </div>
                            <div style={{ marginBottom: '24px' }}>
                                <label style={{ display: 'block', marginBottom: '6px', color: 'var(--text-secondary)' }}>Color</label>
                                <input type="color" value={form.color} onChange={e => setForm({ ...form, color: e.target.value })} style={{ width: '60px', height: '40px', border: 'none', borderRadius: '8px', cursor: 'pointer' }} />
                            </div>
                            <button type="submit" className="btn btn-primary w-full">Create Course</button>
                        </form>
                    </motion.div>
                </div>
            )}
        </div>
    )
}
