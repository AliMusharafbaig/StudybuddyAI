import { useState, useEffect, useRef } from 'react'
import { useParams, Link } from 'react-router-dom'
import { Upload, FileText, Play, Brain, Target, ArrowLeft, Trash2, RefreshCw, CheckCircle, AlertCircle, Loader } from 'lucide-react'
import api from '../api'
import toast from 'react-hot-toast'

export default function CourseDetail() {
    const { id } = useParams()
    const [course, setCourse] = useState(null)
    const [materials, setMaterials] = useState([])
    const [concepts, setConcepts] = useState([])
    const [uploading, setUploading] = useState(false)
    const [polling, setPolling] = useState(false)
    const fileRef = useRef()
    const pollIntervalRef = useRef(null)

    useEffect(() => {
        loadData()
        return () => {
            if (pollIntervalRef.current) {
                clearInterval(pollIntervalRef.current)
            }
        }
    }, [id])

    // Start polling when there are pending materials
    useEffect(() => {
        const hasPending = materials.some(m => !m.is_processed && m.processing_status !== 'failed')

        if (hasPending && !pollIntervalRef.current) {
            setPolling(true)
            pollIntervalRef.current = setInterval(async () => {
                try {
                    const [materialsRes, conceptsRes] = await Promise.all([
                        api.get(`/courses/${id}/materials`),
                        api.get(`/courses/${id}/concepts`)
                    ])
                    setMaterials(materialsRes.data)
                    setConcepts(conceptsRes.data)

                    // Check if all done
                    const stillPending = materialsRes.data.some(m => !m.is_processed && m.processing_status !== 'failed')
                    if (!stillPending) {
                        clearInterval(pollIntervalRef.current)
                        pollIntervalRef.current = null
                        setPolling(false)
                        toast.success('All materials processed!')
                    }
                } catch (e) {
                    console.error('Poll error:', e)
                }
            }, 3000) // Poll every 3 seconds
        } else if (!hasPending && pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current)
            pollIntervalRef.current = null
            setPolling(false)
        }
    }, [materials, id])

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
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 300000 // 5 min timeout for large files
            })
            toast.success('File uploaded! Processing started...')
            loadData()
        } catch (e) {
            toast.error(e.response?.data?.detail || 'Upload failed')
        } finally {
            setUploading(false)
            if (fileRef.current) fileRef.current.value = ''
        }
    }

    const triggerReprocess = async () => {
        try {
            await api.post(`/courses/${id}/process`)
            toast.success('Reprocessing started...')
            loadData()
        } catch (e) {
            toast.error('Failed to trigger processing')
        }
    }

    const getStatusIcon = (material) => {
        if (material.is_processed) {
            return <CheckCircle size={16} color="var(--success)" />
        } else if (material.processing_status === 'failed') {
            return <AlertCircle size={16} color="var(--error)" />
        } else {
            return <Loader size={16} color="var(--warning)" className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
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
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <h2 style={{ margin: 0 }}>📚 Materials</h2>
                        {polling && (
                            <span style={{
                                padding: '4px 10px',
                                background: 'rgba(245, 158, 11, 0.2)',
                                borderRadius: '12px',
                                fontSize: '0.75rem',
                                color: 'var(--warning)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px'
                            }}>
                                <Loader size={12} style={{ animation: 'spin 1s linear infinite' }} />
                                Processing...
                            </span>
                        )}
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        {materials.some(m => m.processing_status === 'failed') && (
                            <button className="btn btn-secondary" onClick={triggerReprocess} style={{ padding: '10px 16px' }}>
                                <RefreshCw size={16} /> Retry Failed
                            </button>
                        )}
                        <input type="file" ref={fileRef} onChange={handleUpload} hidden accept=".pdf,.docx,.pptx,.mp4,.mp3" />
                        <button className="btn btn-primary" onClick={() => fileRef.current?.click()} disabled={uploading}>
                            <Upload size={18} /> {uploading ? 'Uploading...' : 'Upload'}
                        </button>
                    </div>
                </div>

                {materials.length === 0 ? (
                    <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
                        <FileText size={48} color="var(--text-muted)" style={{ marginBottom: '16px' }} />
                        <h3 style={{ marginBottom: '8px' }}>No materials yet</h3>
                        <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
                            Upload PDFs, videos, or audio files to get started
                        </p>
                        <button className="btn btn-primary" onClick={() => fileRef.current?.click()}>
                            <Upload size={18} /> Upload Your First File
                        </button>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gap: '12px' }}>
                        {materials.map(m => (
                            <div key={m.id} className="card" style={{
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'space-between',
                                padding: '16px',
                                borderLeft: `4px solid ${m.is_processed ? 'var(--success)' : m.processing_status === 'failed' ? 'var(--error)' : 'var(--warning)'}`
                            }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                    <div style={{
                                        width: '44px',
                                        height: '44px',
                                        background: 'rgba(99, 102, 241, 0.2)',
                                        borderRadius: '10px',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center'
                                    }}>
                                        <FileText size={22} color="var(--primary)" />
                                    </div>
                                    <div>
                                        <div style={{ fontWeight: 600, marginBottom: '4px' }}>{m.original_filename}</div>
                                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', display: 'flex', gap: '12px' }}>
                                            <span>{m.file_type.toUpperCase()}</span>
                                            <span>{(m.file_size / 1024 / 1024).toFixed(1)} MB</span>
                                        </div>
                                    </div>
                                </div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                    {getStatusIcon(m)}
                                    <span style={{
                                        padding: '6px 14px',
                                        borderRadius: '20px',
                                        fontSize: '0.8rem',
                                        fontWeight: 500,
                                        background: m.is_processed ? 'rgba(16, 185, 129, 0.15)' :
                                            m.processing_status === 'failed' ? 'rgba(239, 68, 68, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                                        color: m.is_processed ? 'var(--success)' :
                                            m.processing_status === 'failed' ? 'var(--error)' : 'var(--warning)'
                                    }}>
                                        {m.is_processed ? '✓ Processed' :
                                            m.processing_status === 'failed' ? '✗ Failed' :
                                                m.processing_status === 'processing' ? 'Processing...' : 'Pending'}
                                    </span>
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
