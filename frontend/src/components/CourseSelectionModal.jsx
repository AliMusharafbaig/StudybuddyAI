import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Search, ChevronRight } from 'lucide-react'

export default function CourseSelectionModal({ isOpen, onClose, onSelect, courses, title = "Select a Course" }) {
    const [searchQuery, setSearchQuery] = useState('')

    if (!isOpen) return null

    const filteredCourses = courses.filter(c =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (c.code && c.code.toLowerCase().includes(searchQuery.toLowerCase()))
    )

    const handleSelect = (course) => {
        onSelect(course)
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
                                {filteredCourses.length} course{filteredCourses.length !== 1 ? 's' : ''} available
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
                            placeholder="Search courses..."
                            value={searchQuery}
                            onChange={e => setSearchQuery(e.target.value)}
                            style={{ paddingLeft: '44px' }}
                            autoFocus
                        />
                    </div>

                    {/* Course List */}
                    <div style={{
                        flex: 1,
                        overflowY: 'auto',
                        marginRight: '-8px',
                        paddingRight: '8px'
                    }}>
                        {filteredCourses.length === 0 ? (
                            <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
                                <p>No courses found</p>
                            </div>
                        ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                {filteredCourses.map(course => (
                                    <motion.div
                                        key={course.id}
                                        whileHover={{ scale: 1.01, x: 4 }}
                                        whileTap={{ scale: 0.99 }}
                                        onClick={() => handleSelect(course)}
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
                                        {/* Color Bar */}
                                        <div style={{
                                            width: '4px',
                                            height: '40px',
                                            background: course.color || '#6366f1',
                                            borderRadius: '2px',
                                            flexShrink: 0
                                        }} />

                                        {/* Course Info */}
                                        <div style={{ flex: 1, minWidth: 0 }}>
                                            <div style={{ fontWeight: 600, marginBottom: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                {course.name}
                                            </div>
                                            <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', display: 'flex', gap: '12px' }}>
                                                {course.code && <span>{course.code}</span>}
                                                <span>📚 {course.total_materials || 0} materials</span>
                                                <span>🧠 {course.total_concepts || 0} concepts</span>
                                            </div>
                                        </div>

                                        {/* Arrow */}
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
