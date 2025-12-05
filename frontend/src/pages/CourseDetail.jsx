import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Upload, FileText, Play, Brain, Target, ArrowLeft, Trash2 } from 'lucide-react'
import api from '../api'
import toast from 'react-hot-toast'

export default function CourseDetail() {
    const { id } = useParams()
    const [course, setCourse] = useState(null)
    const [materials, setMaterials] = useState([])
    const [concepts, setConcepts] = useState([])
    const [uploading, setUploading] = useState(false)
    const fileRef = useRef()

    useEffect(() => { loadData() }, [id])

    const loadData = async () => {
        try {
            const [courseRes, materialsRes, conceptsRes] = await Promise.all([
                api.get(`/courses/${id}`),
                api.get(`/courses/${id}/materials`),
                api.get(`/courses/${id}/concepts`)
            ])
            setCourse(courseRes.data)
            setMaterials(materialsRes.data)
            setConcepts(conceptsRes.data)
        } catch (e) {
            toast.error('Failed to load course')
        }
    }

    const handleUpload = async (e) => {
        const file = e.target.files[0]
        if (!file) return

        setUploading(true)
        const formData = new FormData()
        formData.append('file', file)

        try {
            await api.post(`/courses/${id}/upload`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            })
            toast.success('File uploaded! Processing...')
            loadData()
        } catch (e) {
            toast.error('Upload failed')
        } finally {
            setUploading(false)
        }
    }

    if (!course) return <div style={{ textAlign: 'center', padding: '60px' }}>Loading...</div>

    return (
        <div>
            <Link to="/app/courses" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '24px', color: 'var(--text-secondary)' }}>
                <ArrowLeft size={20} /> Back to Courses
            </Link>

            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
                <div>
                    <div style={{ width: '60px', height: '8px', background: course.color, borderRadius: '4px', marginBottom: '16px' }} />
                    <h1>{course.name}</h1>
                    {course.code && <div style={{ color: 'var(--primary-light)', marginTop: '4px' }}>{course.code}</div>}
                    <p style={{ color: 'var(--text-secondary)', marginTop: '8px' }}>{course.description}</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <Link to={`/app/quiz/${id}?generate=true`} className="btn btn-primary">
                        <Target size={20} /> Start Quiz
                    </Link>
                </div>
            </div>

            {/* Stats */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '32px' }}>
                <div className="card" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary)' }}>{materials.length}</div>
                    <div style={{ color: 'var(--text-secondary)' }}>Materials</div>
                </div>
                <div className="card" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--secondary)' }}>{concepts.length}</div>
                    <div style={{ color: 'var(--text-secondary)' }}>Concepts</div>
                </div>
                <div className="card" style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--success)' }}>{course.mastery_percentage || 0}%</div>
                    <div style={{ color: 'var(--text-secondary)' }}>Mastery</div>
                </div>
            </div>

            {/* Materials */}
            <div style={{ marginBottom: '32px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                    <h2>📚 Materials</h2>
                    <input type="file" ref={fileRef} onChange={handleUpload} hidden accept=".pdf,.docx,.pptx,.mp4,.mp3" />
                    <button className="btn btn-secondary" onClick={() => fileRef.current?.click()} disabled={uploading}>
                        <Upload size={18} /> {uploading ? 'Uploading...' : 'Upload'}
                    </button>
                </div>

                {materials.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                        <FileText size={40} color="var(--text-muted)" style={{ marginBottom: '12px' }} />
                        <p style={{ color: 'var(--text-secondary)' }}>No materials yet. Upload PDFs, videos, or audio files.</p>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gap: '12px' }}>
                        {materials.map(m => (
                            <div key={m.id} className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '16px' }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    <FileText size={24} color="var(--primary)" />
                                    <div>
                                        <div style={{ fontWeight: 500 }}>{m.original_filename}</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                                            {m.file_type.toUpperCase()} • {(m.file_size / 1024 / 1024).toFixed(1)} MB
                                        </div>
                                    </div>
                                </div>
                                <div style={{
                                    padding: '4px 12px', borderRadius: '12px', fontSize: '0.8rem',
                                    background: m.is_processed ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)',
                                    color: m.is_processed ? 'var(--success)' : 'var(--warning)'
                                }}>
                                    {m.is_processed ? 'Processed' : m.processing_status}
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Concepts */}
            <div>
                <h2 style={{ marginBottom: '16px' }}>🧠 Key Concepts</h2>
                {concepts.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
                        <Brain size={40} color="var(--text-muted)" style={{ marginBottom: '12px' }} />
                        <p style={{ color: 'var(--text-secondary)' }}>Concepts will be extracted after materials are processed.</p>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '16px' }}>
                        {concepts.slice(0, 12).map(c => (
                            <div key={c.id} className="card" style={{ padding: '16px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                                    <h4 style={{ margin: 0 }}>{c.name}</h4>
                                    <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '8px', background: 'rgba(99, 102, 241, 0.2)', color: 'var(--primary-light)' }}>
                                        {c.importance_score}/10
                                    </span>
                                </div>
                                <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', margin: 0 }}>
                                    {c.definition?.slice(0, 100) || 'No definition'}...
                                </p>
                                <div style={{ marginTop: '12px' }}>
                                    <div style={{ height: '4px', background: 'var(--bg-input)', borderRadius: '2px' }}>
                                        <div style={{ width: `${c.mastery_level}%`, height: '100%', background: 'var(--success)', borderRadius: '2px' }} />
                                    </div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>{c.mastery_level}% mastered</div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
