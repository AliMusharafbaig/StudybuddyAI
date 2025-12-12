import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Plus, Upload, BookOpen, X, Trash2, AlertTriangle, ChevronRight, Target } from 'lucide-react'
import api from '../api'
import toast from 'react-hot-toast'

export default function Courses() {
    const [courses, setCourses] = useState([])
    const [showModal, setShowModal] = useState(false)
    const [deleteModal, setDeleteModal] = useState(null) // course id to delete
    const [form, setForm] = useState({ name: '', description: '', code: '', color: '#6366f1' })
    const [loading, setLoading] = useState(true)

    const colorOptions = [
        '#6366f1', // Indigo
        '#8b5cf6', // Purple
        '#ec4899', // Pink
        '#ef4444', // Red
        '#f59e0b', // Amber  
        '#10b981', // Emerald
        '#06b6d4', // Cyan
        '#3b82f6', // Blue
    ]

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

    const deleteCourse = async () => {
        if (!deleteModal) return

        try {
            await api.delete(`/courses/${deleteModal}`)
            toast.success('Course deleted')
            setCourses(courses.filter(c => c.id !== deleteModal))
            setDeleteModal(null)
        } catch (e) {
            toast.error('Failed to delete course')
        }
    }

    const courseToDelete = courses.find(c => c.id === deleteModal)

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
                <div>
                    <h1 style={{ marginBottom: '8px' }}>📚 Your Courses</h1>
                    <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
                        {courses.length} {courses.length === 1 ? 'course' : 'courses'} • Upload materials to start learning
                    </p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowModal(true)} style={{ padding: '12px 20px' }}>
                    <Plus size={20} /> New Course
                </button>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: '60px' }}>Loading...</div>
            ) : courses.length === 0 ? (
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="card"
                    style={{ textAlign: 'center', padding: '80px' }}
                >
                    <div style={{
                        width: '100px',
                        height: '100px',
                        background: 'var(--gradient-primary)',
                        borderRadius: '24px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 24px'
                    }}>
                        <BookOpen size={50} color="white" />
                    </div>
                    <h2>No courses yet</h2>
                    <p style={{ color: 'var(--text-secondary)', marginBottom: '24px', maxWidth: '400px', margin: '0 auto 24px' }}>
                        Create your first course, upload your study materials, and let AI help you master the content!
                    </p>
                    <button className="btn btn-primary" onClick={() => setShowModal(true)} style={{ padding: '14px 28px' }}>
                        <Plus size={20} /> Create Your First Course
                    </button>
                </motion.div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px' }}>
                    {courses.map((course, i) => (
                        <motion.div
                            key={course.id}
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.05 }}
                        >
                            <Link to={`/app/courses/${course.id}`} style={{ textDecoration: 'none' }}>
                                <motion.div
                                    whileHover={{ scale: 1.02, y: -4 }}
                                    className="card"
                                    style={{ height: '100%', position: 'relative', overflow: 'hidden' }}
                                >
                                    {/* Delete Button */}
                                    <button
                                        onClick={(e) => {
                                            e.preventDefault()
                                            e.stopPropagation()
                                            setDeleteModal(course.id)
                                        }}
                                        style={{
                                            position: 'absolute',
                                            top: '12px',
                                            right: '12px',
                                            padding: '10px',
                                            background: 'rgba(0,0,0,0.3)',
                                            border: 'none',
                                            borderRadius: '10px',
                                            color: 'white',
                                            cursor: 'pointer',
                                            zIndex: 10,
                                            transition: 'all 0.2s',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center'
                                        }}
                                        onMouseEnter={e => {
                                            e.currentTarget.style.background = 'rgba(239, 68, 68, 0.9)'
                                            e.currentTarget.style.transform = 'scale(1.1)'
                                        }}
                                        onMouseLeave={e => {
                                            e.currentTarget.style.background = 'rgba(0,0,0,0.3)'
                                            e.currentTarget.style.transform = 'scale(1)'
                                        }}
                                    >
                                        <Trash2 size={16} />
                                    </button>

                                    {/* Color Bar */}
                                    <div style={{
                                        width: '100%',
                                        height: '8px',
                                        background: course.color,
                                        borderRadius: '4px',
                                        marginBottom: '20px'
                                    }} />

                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div style={{ flex: 1 }}>
                                            <h3 style={{ marginBottom: '4px' }}>{course.name}</h3>
                                            {course.code && (
                                                <div style={{ color: 'var(--primary-light)', marginBottom: '8px', fontSize: '0.9rem' }}>
                                                    {course.code}
                                                </div>
                                            )}
                                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '16px' }}>
                                                {course.description?.slice(0, 80) || 'No description'}
                                                {(course.description?.length || 0) > 80 && '...'}
                                            </p>
                                        </div>
                                        <ChevronRight size={20} color="var(--text-muted)" style={{ marginTop: '4px' }} />
                                    </div>

                                    {/* Stats */}
                                    <div style={{
                                        display: 'flex',
                                        gap: '16px',
                                        color: 'var(--text-muted)',
                                        fontSize: '0.85rem',
                                        marginBottom: '16px'
                                    }}>
                                        <span>📚 {course.total_materials || 0} materials</span>
                                        <span>🧠 {course.total_concepts || 0} concepts</span>
                                    </div>

                                    {/* Mastery Bar */}
                                    <div style={{
                                        background: 'var(--bg-input)',
                                        borderRadius: '10px',
                                        padding: '14px'
                                    }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>Mastery Progress</span>
                                            <span style={{
                                                fontSize: '0.85rem',
                                                fontWeight: 600,
                                                color: (course.mastery_percentage || 0) >= 80 ? 'var(--success)' : 'var(--primary-light)'
                                            }}>
                                                {course.mastery_percentage || 0}%
                                            </span>
                                        </div>
                                        <div style={{
                                            height: '8px',
                                            background: 'var(--bg-dark)',
                                            borderRadius: '4px',
                                            overflow: 'hidden'
                                        }}>
                                            <motion.div
                                                initial={{ width: 0 }}
                                                animate={{ width: `${course.mastery_percentage || 0}%` }}
                                                transition={{ duration: 0.8, delay: i * 0.1 }}
                                                style={{
                                                    height: '100%',
                                                    background: (course.mastery_percentage || 0) >= 80
                                                        ? 'linear-gradient(90deg, #10b981, #34d399)'
                                                        : 'var(--gradient-primary)',
                                                    borderRadius: '4px'
                                                }}
                                            />
                                        </div>
                                    </div>

                                    {/* Quick Quiz Button */}
                                    {course.is_processed && (
                                        <Link
                                            to={`/app/quiz/${course.id}?generate=true`}
                                            onClick={e => e.stopPropagation()}
                                            style={{
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                gap: '8px',
                                                marginTop: '16px',
                                                padding: '10px',
                                                background: 'rgba(99, 102, 241, 0.15)',
                                                borderRadius: '10px',
                                                color: 'var(--primary-light)',
                                                fontSize: '0.9rem',
                                                fontWeight: 500,
                                                textDecoration: 'none',
                                                transition: 'all 0.2s'
                                            }}
                                        >
                                            <Target size={16} /> Start Quiz
                                        </Link>
                                    )}
                                </motion.div>
                            </Link>
                        </motion.div>
                    ))}
                </div>
            )}

            {/* Create Modal */}
            <AnimatePresence>
                {showModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        style={{
                            position: 'fixed',
                            inset: 0,
                            background: 'rgba(0,0,0,0.85)',
                            backdropFilter: 'blur(8px)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 100
                        }}
                        onClick={() => setShowModal(false)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="card"
                            style={{ width: '100%', maxWidth: '500px', margin: '24px' }}
                            onClick={e => e.stopPropagation()}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '28px' }}>
                                <div>
                                    <h2 style={{ margin: '0 0 4px' }}>Create New Course</h2>
                                    <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem' }}>
                                        Add a course and upload your materials
                                    </p>
                                </div>
                                <button onClick={() => setShowModal(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer', padding: '8px' }}>
                                    <X size={24} />
                                </button>
                            </div>
                            <form onSubmit={createCourse}>
                                <div style={{ marginBottom: '20px' }}>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontWeight: 500 }}>Course Name *</label>
                                    <input className="input" value={form.name} onChange={e => setForm({ ...form, name: e.target.value })} required placeholder="e.g., Natural Language Processing" />
                                </div>
                                <div style={{ marginBottom: '20px' }}>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontWeight: 500 }}>Description</label>
                                    <textarea className="input" value={form.description} onChange={e => setForm({ ...form, description: e.target.value })} placeholder="What is this course about?" rows={3} />
                                </div>
                                <div style={{ marginBottom: '28px' }}>
                                    <label style={{ display: 'block', marginBottom: '8px', color: 'var(--text-secondary)', fontWeight: 500 }}>Color Theme</label>
                                    <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                                        {colorOptions.map(color => (
                                            <button
                                                key={color}
                                                type="button"
                                                onClick={() => setForm({ ...form, color })}
                                                style={{
                                                    width: '40px',
                                                    height: '40px',
                                                    borderRadius: '10px',
                                                    background: color,
                                                    border: form.color === color ? '3px solid white' : 'none',
                                                    cursor: 'pointer',
                                                    transition: 'transform 0.2s',
                                                    boxShadow: form.color === color ? '0 0 0 2px var(--primary)' : 'none'
                                                }}
                                                onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.1)'}
                                                onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                                            />
                                        ))}
                                    </div>
                                </div>
                                <button type="submit" className="btn btn-primary" style={{ width: '100%', padding: '14px', justifyContent: 'center' }}>
                                    <Plus size={20} /> Create Course
                                </button>
                            </form>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Delete Confirmation Modal */}
            <AnimatePresence>
                {deleteModal && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        style={{
                            position: 'fixed',
                            inset: 0,
                            background: 'rgba(0,0,0,0.85)',
                            backdropFilter: 'blur(8px)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 100
                        }}
                        onClick={() => setDeleteModal(null)}
                    >
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0, y: 20 }}
                            animate={{ scale: 1, opacity: 1, y: 0 }}
                            exit={{ scale: 0.9, opacity: 0, y: 20 }}
                            className="card"
                            style={{ width: '100%', maxWidth: '420px', margin: '24px', textAlign: 'center' }}
                            onClick={e => e.stopPropagation()}
                        >
                            <div style={{
                                width: '70px',
                                height: '70px',
                                background: 'rgba(239, 68, 68, 0.15)',
                                borderRadius: '50%',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                margin: '0 auto 20px'
                            }}>
                                <AlertTriangle size={36} color="var(--error)" />
                            </div>
                            <h2 style={{ marginBottom: '12px' }}>Delete Course?</h2>
                            <p style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>
                                You're about to delete <strong style={{ color: 'white' }}>{courseToDelete?.name}</strong>
                            </p>
                            <p style={{ color: 'var(--error)', fontSize: '0.9rem', marginBottom: '28px' }}>
                                ⚠️ All materials, concepts, and quiz history will be permanently lost.
                            </p>
                            <div style={{ display: 'flex', gap: '12px' }}>
                                <button
                                    className="btn btn-secondary"
                                    onClick={() => setDeleteModal(null)}
                                    style={{ flex: 1, justifyContent: 'center' }}
                                >
                                    Cancel
                                </button>
                                <button
                                    className="btn"
                                    onClick={deleteCourse}
                                    style={{
                                        flex: 1,
                                        justifyContent: 'center',
                                        background: 'var(--error)',
                                        color: 'white'
                                    }}
                                >
                                    <Trash2 size={18} /> Delete
                                </button>
                            </div>
                        </motion.div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    )
}
