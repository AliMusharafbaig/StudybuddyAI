import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import api from '../api'

export default function Chat() {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: "Hi! I'm your AI Study Buddy 🎓 Ask me anything about your courses, concepts, or studying strategies!" }
    ])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [courses, setCourses] = useState([])
    const [selectedCourse, setSelectedCourse] = useState('')
    const bottomRef = useRef()

    useEffect(() => {
        api.get('/courses').then(r => setCourses(r.data)).catch(() => { })
    }, [])

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const sendMessage = async () => {
        if (!input.trim() || loading) return

        const userMsg = { role: 'user', content: input }
        setMessages(m => [...m, userMsg])
        setInput('')
        setLoading(true)

        try {
            const { data } = await api.post('/chat/message', {
                message: input,
                course_id: selectedCourse || undefined
            })
            setMessages(m => [...m, { role: 'assistant', content: data.content, sources: data.sources }])
        } catch {
            setMessages(m => [...m, { role: 'assistant', content: "Sorry, I couldn't process that. Please try again!" }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ height: 'calc(100vh - 64px)', display: 'flex', flexDirection: 'column' }}>
            {/* Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ width: '48px', height: '48px', background: 'var(--gradient-primary)', borderRadius: '14px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <Sparkles size={24} color="white" />
                    </div>
                    <div>
                        <h2 style={{ margin: 0 }}>AI Study Buddy</h2>
                        <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Ask anything about your courses</span>
                    </div>
                </div>
                <select className="input" style={{ width: '200px' }} value={selectedCourse} onChange={e => setSelectedCourse(e.target.value)}>
                    <option value="">All Courses</option>
                    {courses.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflowY: 'auto', paddingRight: '8px', marginBottom: '20px' }}>
                {messages.map((msg, i) => (
                    <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                        style={{ display: 'flex', gap: '12px', marginBottom: '20px', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                        <div style={{
                            width: '40px', height: '40px', borderRadius: '12px', flexShrink: 0,
                            background: msg.role === 'user' ? 'var(--secondary)' : 'var(--gradient-primary)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center'
                        }}>
                            {msg.role === 'user' ? <User size={20} color="white" /> : <Bot size={20} color="white" />}
                        </div>
                        <div style={{
                            maxWidth: '70%', padding: '14px 18px', borderRadius: '16px',
                            background: msg.role === 'user' ? 'var(--secondary)' : 'var(--bg-card)',
                            borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                            borderBottomLeftRadius: msg.role === 'user' ? '16px' : '4px'
                        }}>
                            <p style={{ margin: 0, lineHeight: 1.5 }}>{msg.content}</p>
                            {msg.sources?.length > 0 && (
                                <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Sources:</span>
                                    <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                                        {msg.sources.map((s, j) => (
                                            <span key={j} style={{ padding: '2px 8px', background: 'var(--bg-input)', borderRadius: '6px', fontSize: '0.75rem' }}>
                                                {s.source} {s.page && `p.${s.page}`}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </motion.div>
                ))}
                {loading && (
                    <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
                        <div style={{ width: '40px', height: '40px', background: 'var(--gradient-primary)', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                            <Bot size={20} color="white" />
                        </div>
                        <div style={{ padding: '14px 18px', background: 'var(--bg-card)', borderRadius: '16px' }}>
                            <div style={{ display: 'flex', gap: '4px' }}>
                                <span className="animate-pulse" style={{ width: '8px', height: '8px', background: 'var(--primary)', borderRadius: '50%' }} />
                                <span className="animate-pulse" style={{ width: '8px', height: '8px', background: 'var(--primary)', borderRadius: '50%', animationDelay: '0.2s' }} />
                                <span className="animate-pulse" style={{ width: '8px', height: '8px', background: 'var(--primary)', borderRadius: '50%', animationDelay: '0.4s' }} />
                            </div>
                        </div>
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div style={{ display: 'flex', gap: '12px' }}>
                <input
                    className="input"
                    placeholder="Ask a question..."
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    onKeyDown={e => e.key === 'Enter' && sendMessage()}
                    style={{ flex: 1 }}
                />
                <button className="btn btn-primary" onClick={sendMessage} disabled={loading || !input.trim()}>
                    <Send size={20} />
                </button>
            </div>
        </div>
    )
}
