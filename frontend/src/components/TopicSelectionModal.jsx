import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Search, ChevronRight, BookOpen, Loader, FileText } from 'lucide-react'
import api from '../api'

export default function TopicSelectionModal({
    isOpen,
    onClose,
    onSelect,
    courseId,
    title = "Select a Topic",
    allowAllTopics = true
}) {
    const [searchQuery, setSearchQuery] = useState('')
    const [topics, setTopics] = useState([])
    const [loading, setLoading] = useState(false)
    const [courseName, setCourseName] = useState('')

    useEffect(() => {
        if (isOpen && courseId) {
            loadTopics()
        }
    }, [isOpen, courseId])

    const loadTopics = async () => {
        setLoading(true)
        try {
            // Load course details
            const courseRes = await api.get(`/courses/${courseId}`)
            setCourseName(courseRes.data.name)

            // Load MATERIALS (PDFs) as topics - each uploaded file is a topic
            const { data } = await api.get(`/courses/${courseId}/materials`)
            // Filter to only processed materials and format them as topics
            const materialsAsTopics = (data || [])
                .filter(m => m.is_processed)
                .map(m => ({
                    id: m.id,
                    name: m.original_filename.replace(/\.(pdf|docx|pptx|txt)$/i, ''), // Remove file extension
                    fullName: m.original_filename,
                    type: 'material'
                }))
            setTopics(materialsAsTopics)
        } catch (e) {
            console.error('Failed to load topics', e)
            setTopics([])
        } finally {
            setLoading(false)
        }
    }

    if (!isOpen) return null

    const filteredTopics = topics.filter(t =>
        t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (t.category && t.category.toLowerCase().includes(searchQuery.toLowerCase()))
    )

    const handleSelect = (topic) => {
        onSelect({ topic, courseName, courseId })
        onClose()
        setSearchQuery('')
    }

    const handleSelectAll = () => {
        onSelect({ topic: null, courseName, courseId, allTopics: true })
        onClose()
        setSearchQuery('')
    }

    return (
        <AnimatePresence>
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
                    zIndex: 1000
                }}
                onClick={onClose}
            >
                <motion.div
                    initial={{ scale: 0.9, opacity: 0, y: 20 }}
                    animate={{ scale: 1, opacity: 1, y: 0 }}
                    exit={{ scale: 0.9, opacity: 0, y: 20 }}
                    className="card"
                    style={{
                        width: '100%',
                        maxWidth: '500px',
                        margin: '24px',
                        maxHeight: '80vh',
                        display: 'flex',
                        flexDirection: 'column'
                    }}
                    onClick={e => e.stopPropagation()}
                >
                    {/* Header */}
                    <div style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '24px',
                        paddingBottom: '16px',
                        borderBottom: '1px solid rgba(255,255,255,0.1)'
                    }}>
                        <div>
                            <h2 style={{ margin: '0 0 4px' }}>{title}</h2>
                            <p style={{ color: 'var(--text-muted)', margin: 0, fontSize: '0.9rem' }}>
                                {courseName && `Course: ${courseName}`}
                            </p>
                        </div>
                        <button
                            onClick={onClose}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: 'var(--text-muted)',
                                cursor: 'pointer',
                                padding: '8px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}
                        >
                            <X size={24} />
                        </button>
                    </div>

                    {/* Search */}
                    <div style={{ marginBottom: '20px', position: 'relative' }}>
                        <Search size={18} style={{
                            position: 'absolute',
                            left: '14px',
                            top: '50%',
                            transform: 'translateY(-50%)',
                            color: 'var(--text-muted)'
                        }} />
                        <input
                            className="input"
                            type="text"
                            placeholder="Search topics..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            style={{ paddingLeft: '44px' }}
                            autoFocus
                        />
                    </div>

                    {/* All Topics Option */}
                    {allowAllTopics && !loading && topics.length > 0 && (
                        <motion.div
                            whileHover={{ scale: 1.01, x: 4 }}
                            whileTap={{ scale: 0.99 }}
                            onClick={handleSelectAll}
                            style={{
                                padding: '14px 16px',
                                background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.1))',
                                borderRadius: '12px',
                                cursor: 'pointer',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '14px',
                                marginBottom: '16px',
                                border: '1px solid rgba(99, 102, 241, 0.3)'
                            }}
                        >
                            <BookOpen size={20} color="var(--primary-light)" />
                            <div style={{ flex: 1 }}>
                                <div style={{ fontWeight: 600, color: 'var(--primary-light)' }}>
                                    All Topics
                                </div>
                                <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                    Include all {topics.length} topics from this course
                                </div>
                            </div>
                            <ChevronRight size={20} color="var(--primary-light)" />
                        </motion.div>
                    )}

                    {/* Topic List */}
                    <div style={{
                        flex: 1,
                        overflowY: 'auto',
                        marginRight: '-8px',
                        paddingRight: '8px'
                    }}>
                        {loading ? (
                            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
                                <Loader size={24} className="animate-spin" style={{ marginBottom: '12px' }} />
                                <p>Loading topics...</p>
                            </div>
                        ) : filteredTopics.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
                                <p>No topics found</p>
                                {topics.length === 0 && (
                                    <p style={{ fontSize: '0.85rem' }}>
                                        Upload and process materials to extract topics
                                    </p>
                                )}
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {filteredTopics.map(topic => (
                                    <motion.div
                                        key={topic.id}
                                        whileHover={{ scale: 1.01, x: 4 }}
                                        whileTap={{ scale: 0.99 }}
                                        onClick={() => handleSelect(topic)}
                                        style={{
                                            padding: '14px 16px',
                                            background: 'var(--bg-input)',
                                            borderRadius: '12px',
                                            cursor: 'pointer',
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: '14px',
                                            transition: 'all 0.2s',
                                            border: '1px solid transparent'
                                        }}
                                        onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--primary)'}
                                        onMouseLeave={e => e.currentTarget.style.borderColor = 'transparent'}
                                    >
                                        {/* File icon */}
                                        <div style={{
                                            width: '40px',
                                            height: '40px',
                                            background: 'rgba(99, 102, 241, 0.2)',
                                            borderRadius: '10px',
                                            display: 'flex',
                                            alignItems: 'center',
                                            justifyContent: 'center',
                                            flexShrink: 0
                                        }}>
                                            <FileText size={20} color="var(--primary-light)" />
                                        </div>

                                        {/* Topic Info */}
                                        <div style={{ flex: 1, minWidth: 0 }}>
                                            <div style={{
                                                fontWeight: 600,
                                                marginBottom: '2px',
                                                whiteSpace: 'nowrap',
                                                overflow: 'hidden',
                                                textOverflow: 'ellipsis'
                                            }}>
                                                {topic.name}
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                                                📄 Uploaded material
                                            </div>
                                        </div>

                                        <ChevronRight size={20} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                                    </motion.div>
                                ))}
                            </div>
                        )}
                    </div>
                </motion.div>
            </motion.div>
        </AnimatePresence>
    )
}
