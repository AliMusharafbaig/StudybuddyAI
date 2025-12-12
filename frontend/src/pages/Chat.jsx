import { useState, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
    Send, Bot, User, Sparkles, Plus, MessageCircle,
    ChevronRight, FileText, Zap, Brain, Trash2,
    BookOpen, Target, Clock, Info, AlertCircle, Loader
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import api from '../api'
import toast from 'react-hot-toast'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import CourseSelectionModal from '../components/CourseSelectionModal'
import TopicSelectionModal from '../components/TopicSelectionModal'

export default function Chat() {
    const [messages, setMessages] = useState([])
    const [input, setInput] = useState('')
    const [loading, setLoading] = useState(false)
    const [courses, setCourses] = useState([])
    const [selectedCourse, setSelectedCourse] = useState('')
    const [conversationId, setConversationId] = useState(null)
    const [conversations, setConversations] = useState([])
    const [showSidebar, setShowSidebar] = useState(true)
    const [materials, setMaterials] = useState([])
    const [showCourseModal, setShowCourseModal] = useState(false)
    const [showTopicModal, setShowTopicModal] = useState(false)
    const [selectedCourseForAction, setSelectedCourseForAction] = useState(null)
    const [pendingAction, setPendingAction] = useState(null)
    const pendingActionRef = useRef(null) // Store action in ref for reliable access
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const bottomRef = useRef()

    // Load courses and chat history on mount
    useEffect(() => {
        loadCourses()
        loadConversations()

        // Check for saved conversation
        const saved = localStorage.getItem('studybuddy_current_chat')
        if (saved) {
            const { conversationId: savedId, courseId } = JSON.parse(saved)
            if (savedId) {
                setConversationId(savedId)
                if (courseId) setSelectedCourse(courseId)
            }
        }
    }, [])

    // Handle cram mode from URL params
    useEffect(() => {
        const mode = searchParams.get('mode')
        const topics = searchParams.get('topics')
        const courseParam = searchParams.get('course')

        if (mode === 'cram' && topics && courseParam) {
            // Start a cram learning session
            setSelectedCourse(courseParam)

            // Create the initial cram message
            const cramMessage = `I'm ready for my cram session! Please teach me these topics one by one, starting with the first one. After each topic, wait for me to say "next" before moving on.\n\nTopics to learn:\n${topics}\n\nLet's start with the first topic. Give me a clear explanation.`

            // Set input and auto-send after a delay
            setTimeout(() => {
                setInput(cramMessage)
                setTimeout(() => {
                    document.getElementById('chat-send-btn')?.click()
                }, 200)
            }, 500)

            // Clear the URL params
            navigate('/app/chat', { replace: true })
        }
    }, [searchParams, courses])

    // Load chat history when conversation changes
    useEffect(() => {
        if (conversationId) {
            loadHistory()
            localStorage.setItem('studybuddy_current_chat', JSON.stringify({
                conversationId,
                courseId: selectedCourse
            }))
        }
    }, [conversationId])

    // Load materials when course changes
    useEffect(() => {
        if (selectedCourse) {
            loadMaterials()
        } else {
            setMaterials([])
        }
    }, [selectedCourse])

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
    }, [messages])

    const loadCourses = async () => {
        try {
            const { data } = await api.get('/courses')
            setCourses(data)
        } catch (e) {
            console.error('Failed to load courses', e)
        }
    }

    const loadMaterials = async () => {
        try {
            const { data } = await api.get(`/courses/${selectedCourse}/materials`)
            setMaterials(data.filter(m => m.is_processed))
        } catch (e) {
            console.error('Failed to load materials', e)
        }
    }

    const loadConversations = async () => {
        // Load unique conversations from history
        try {
            const { data } = await api.get('/chat/history')
            // Group by conversation_id
            const convMap = {}
            data.forEach(msg => {
                if (msg.conversation_id && !convMap[msg.conversation_id]) {
                    convMap[msg.conversation_id] = {
                        id: msg.conversation_id,
                        preview: msg.content.slice(0, 50) + '...',
                        timestamp: msg.timestamp
                    }
                }
            })
            setConversations(Object.values(convMap).slice(0, 10))
        } catch (e) {
            console.error('Failed to load conversations', e)
        }
    }

    const loadHistory = async () => {
        try {
            const { data } = await api.get('/chat/history')
            // Filter by current conversation
            const filtered = data.filter(m => m.conversation_id === conversationId)
            if (filtered.length > 0) {
                setMessages(filtered)
            } else {
                setMessages([getWelcomeMessage()])
            }
        } catch (e) {
            console.error("Failed to load history", e)
            setMessages([getWelcomeMessage()])
        }
    }

    const getWelcomeMessage = () => {
        // Get list of course names for the welcome message
        const courseNames = courses.map(c => c.name)
        const courseList = courseNames.length > 0
            ? courseNames.slice(0, 5).join(', ') + (courseNames.length > 5 ? ` and ${courseNames.length - 5} more` : '')
            : null

        return {
            id: 'welcome',
            role: 'assistant',
            content: courseNames.length > 0
                ? `👋 **Hey there!** I'm your AI Study Buddy with complete memory of all your uploaded courses!\n\n📚 **Your courses:** ${courseList}\n\nI can help you with:\n• **Quiz me** - Practice questions on any topic\n• **Summarize** - Get key takeaways from your materials\n• **Key Topics** - Identify important concepts to focus on\n• **Cram Mode** - Generate an optimized study plan\n• **Predict Exam** - See likely exam questions\n\n**Ask me anything** about your study materials, or click the buttons above to get started!`
                : "👋 **Welcome!** I'm your AI Study Buddy. I can help you study, create quizzes, summarize content, and explain concepts.\n\n📤 **Get started:** Upload some materials to a course first, then come back here for personalized help!\n\n💡 I can also answer general questions about topics you want to learn, even without uploaded materials.",
            timestamp: new Date()
        }
    }

    const startNewChat = () => {
        // Generate a new unique conversation ID
        const newConversationId = crypto.randomUUID ? crypto.randomUUID() : `chat-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
        setConversationId(newConversationId)
        setMessages([getWelcomeMessage()])
        localStorage.setItem('studybuddy_current_chat', JSON.stringify({
            conversationId: newConversationId,
            courseId: selectedCourse
        }))
        toast.success('New chat started!')
    }

    // Quick action handlers - open course/topic selection modals
    const handleQuickAction = (actionType) => {
        setPendingAction(actionType)
        pendingActionRef.current = actionType // Store in ref for reliable access
        if (courses.length === 0) {
            toast.error('Please add a course first')
            return
        }
        setShowCourseModal(true)
    }

    const handleCramMode = () => {
        if (!selectedCourse) {
            setPendingAction('cram')
            setShowCourseModal(true)
        } else {
            navigate(`/app/cram?course=${selectedCourse}`)
        }
    }

    const handleCourseSelect = (course) => {
        setSelectedCourse(course.id)
        setSelectedCourseForAction(course.id)

        // Handle different pending actions
        if (pendingAction === 'cram') {
            navigate(`/app/cram?course=${course.id}`)
            setPendingAction(null)
        } else if (['quiz', 'summarize', 'exam', 'keytopics'].includes(pendingAction)) {
            // For these actions, show topic selection modal
            setShowCourseModal(false)
            setShowTopicModal(true)
        } else {
            setPendingAction(null)
        }
    }

    const handleTopicSelect = async ({ topic, courseName, courseId, allTopics }) => {
        const topicName = allTopics ? 'all topics' : (topic?.name || 'this topic')

        // Use ref value for reliable action detection
        const action = pendingActionRef.current || pendingAction

        let message = ''
        switch (action) {
            case 'quiz':
                message = `Quiz me on ${topicName} from ${courseName}. Create 5 MCQ questions to test my understanding.`
                break
            case 'summarize':
                message = `Please summarize ${topicName} from ${courseName}. Give me the key points and important concepts.`
                break
            case 'exam':
                message = `Based on ${topicName} from ${courseName}, predict the most likely exam questions. What questions might appear on an exam covering this material? Generate 5-10 potential exam questions with varying difficulty.`
                break
            case 'keytopics':
                message = `What are the most important concepts and key topics I should focus on from ${courseName}?`
                break
            default:
                message = `Tell me about ${topicName} from ${courseName}`
        }

        setSelectedCourse(courseId)
        setPendingAction(null)
        pendingActionRef.current = null // Clear ref
        setShowTopicModal(false)

        // Send the message
        setInput(message)
        // Trigger send with a small delay to allow state update
        setTimeout(() => {
            document.getElementById('chat-send-btn')?.click()
        }, 100)
    }

    const sendMessage = async () => {
        if (!input.trim() || loading) return

        const userMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: input.trim(),
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInput('')
        setLoading(true)

        try {
            const { data } = await api.post('/chat/message', {
                message: userMessage.content,
                course_id: selectedCourse || null,
                conversation_id: conversationId
            })

            // Set conversation ID if new
            if (data.conversation_id && !conversationId) {
                setConversationId(data.conversation_id)
            }

            const assistantMessage = {
                id: data.id || Date.now().toString(),
                role: 'assistant',
                content: data.content,
                sources: data.sources || [],
                timestamp: new Date(),
                conversation_id: data.conversation_id
            }

            setMessages(prev => [...prev, assistantMessage])
        } catch (error) {
            console.error('Chat error:', error)
            toast.error('Failed to send message')

            // Add error message
            setMessages(prev => [...prev, {
                id: Date.now().toString(),
                role: 'assistant',
                content: '❌ Sorry, I encountered an error. Please try again.',
                timestamp: new Date()
            }])
        } finally {
            setLoading(false)
        }
    }

    return (
        <div style={{ height: 'calc(100vh - 64px)', display: 'flex' }}>
            {/* Sidebar - Chat History */}
            <AnimatePresence>
                {showSidebar && (
                    <motion.aside
                        initial={{ width: 0, opacity: 0 }}
                        animate={{ width: 280, opacity: 1 }}
                        exit={{ width: 0, opacity: 0 }}
                        style={{
                            background: 'var(--bg-card)',
                            borderRight: '1px solid rgba(255,255,255,0.05)',
                            display: 'flex',
                            flexDirection: 'column',
                            overflow: 'hidden'
                        }}
                    >
                        <div style={{ padding: '16px' }}>
                            <button
                                className="btn btn-primary w-full"
                                onClick={startNewChat}
                                style={{ justifyContent: 'center' }}
                            >
                                <Plus size={18} /> New Chat
                            </button>
                        </div>

                        <div style={{ flex: 1, overflowY: 'auto', padding: '0 12px' }}>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', padding: '8px', textTransform: 'uppercase' }}>
                                Recent Chats
                            </div>
                            {conversations.map(conv => (
                                <div
                                    key={conv.id}
                                    onClick={() => setConversationId(conv.id)}
                                    style={{
                                        padding: '12px',
                                        borderRadius: '8px',
                                        cursor: 'pointer',
                                        marginBottom: '4px',
                                        background: conversationId === conv.id ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                                        transition: 'background 0.2s'
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <MessageCircle size={14} color="var(--text-muted)" />
                                        <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                                            {conv.preview}
                                        </span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </motion.aside>
                )}
            </AnimatePresence>

            {/* Main Chat Area */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                {/* Header with context */}
                <div style={{
                    padding: '16px 24px',
                    borderBottom: '1px solid rgba(255,255,255,0.05)',
                    background: 'rgba(0,0,0,0.2)'
                }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                            <div style={{
                                width: '48px',
                                height: '48px',
                                background: 'var(--gradient-primary)',
                                borderRadius: '14px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}>
                                <Sparkles size={24} color="white" />
                            </div>
                            <div>
                                <h2 style={{ margin: 0, fontSize: '1.25rem' }}>AI Study Buddy</h2>
                                <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                                    {selectedCourse ? courses.find(c => c.id === selectedCourse)?.name : 'All Courses'}
                                    {materials.length > 0 && ` • ${materials.length} materials loaded`}
                                </span>
                            </div>
                        </div>
                        <select
                            className="input"
                            style={{ width: '220px' }}
                            value={selectedCourse}
                            onChange={e => setSelectedCourse(e.target.value)}
                        >
                            <option value="">All Courses</option>
                            {courses.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                        </select>
                    </div>

                    {/* Context Banner */}
                    {materials.length > 0 && (
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            style={{
                                marginTop: '12px',
                                padding: '10px 14px',
                                background: 'rgba(99, 102, 241, 0.1)',
                                borderRadius: '10px',
                                border: '1px solid rgba(99, 102, 241, 0.2)',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '12px'
                            }}
                        >
                            <FileText size={18} color="var(--primary-light)" />
                            <div style={{ flex: 1 }}>
                                <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                    <strong style={{ color: 'var(--primary-light)' }}>Context loaded:</strong>{' '}
                                    {materials.slice(0, 3).map(m => m.original_filename).join(', ')}
                                    {materials.length > 3 && ` +${materials.length - 3} more`}
                                </span>
                            </div>
                            <Info size={16} color="var(--text-muted)" />
                        </motion.div>
                    )}

                    {/* Quick Actions */}
                    <div style={{ display: 'flex', gap: '8px', marginTop: '12px', flexWrap: 'wrap' }}>
                        <button
                            onClick={() => handleQuickAction('quiz')}
                            style={{
                                padding: '6px 12px',
                                background: 'rgba(139, 92, 246, 0.2)',
                                border: '1px solid rgba(139, 92, 246, 0.3)',
                                borderRadius: '20px',
                                color: 'var(--secondary)',
                                cursor: 'pointer',
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.05)'}
                            onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                        >
                            <Target size={14} /> Quiz Me
                        </button>
                        <button
                            onClick={() => handleQuickAction('summarize')}
                            style={{
                                padding: '6px 12px',
                                background: 'rgba(16, 185, 129, 0.2)',
                                border: '1px solid rgba(16, 185, 129, 0.3)',
                                borderRadius: '20px',
                                color: 'var(--success)',
                                cursor: 'pointer',
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.05)'}
                            onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                        >
                            <BookOpen size={14} /> Summarize
                        </button>
                        <button
                            onClick={handleCramMode}
                            style={{
                                padding: '6px 12px',
                                background: 'rgba(239, 68, 68, 0.2)',
                                border: '1px solid rgba(239, 68, 68, 0.3)',
                                borderRadius: '20px',
                                color: 'var(--error)',
                                cursor: 'pointer',
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.05)'}
                            onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                        >
                            <Zap size={14} /> Cram Mode
                        </button>
                        <button
                            onClick={() => handleQuickAction('exam')}
                            style={{
                                padding: '6px 12px',
                                background: 'rgba(245, 158, 11, 0.2)',
                                border: '1px solid rgba(245, 158, 11, 0.3)',
                                borderRadius: '20px',
                                color: '#fbbf24',
                                cursor: 'pointer',
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.05)'}
                            onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                        >
                            <AlertCircle size={14} /> Predict Exam
                        </button>
                        <button
                            onClick={() => handleQuickAction('keytopics')}
                            style={{
                                padding: '6px 12px',
                                background: 'rgba(99, 102, 241, 0.2)',
                                border: '1px solid rgba(99, 102, 241, 0.3)',
                                borderRadius: '20px',
                                color: 'var(--primary-light)',
                                cursor: 'pointer',
                                fontSize: '0.8rem',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '6px',
                                transition: 'all 0.2s'
                            }}
                            onMouseEnter={e => e.currentTarget.style.transform = 'scale(1.05)'}
                            onMouseLeave={e => e.currentTarget.style.transform = 'scale(1)'}
                        >
                            <Brain size={14} /> Key Topics
                        </button>
                    </div>
                </div>

                {/* Messages */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
                    {messages.length === 0 ? (
                        <div style={{ textAlign: 'center', padding: '60px 20px' }}>
                            <div style={{
                                width: '80px',
                                height: '80px',
                                background: 'var(--gradient-primary)',
                                borderRadius: '20px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                margin: '0 auto 24px'
                            }}>
                                <Sparkles size={40} color="white" />
                            </div>
                            <h2>Start a Conversation</h2>
                            <p style={{ color: 'var(--text-secondary)', maxWidth: '400px', margin: '0 auto' }}>
                                Ask me anything about your courses! I can help you study, explain concepts, create quizzes, and more.
                            </p>
                        </div>
                    ) : (
                        messages.map((msg, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                style={{
                                    display: 'flex',
                                    gap: '12px',
                                    marginBottom: '20px',
                                    flexDirection: msg.role === 'user' ? 'row-reverse' : 'row'
                                }}
                            >
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    borderRadius: '12px',
                                    flexShrink: 0,
                                    background: msg.role === 'user' ? 'var(--secondary)' : 'var(--gradient-primary)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    {msg.role === 'user' ? <User size={20} color="white" /> : <Bot size={20} color="white" />}
                                </div>
                                <div style={{
                                    maxWidth: '70%',
                                    padding: '14px 18px',
                                    borderRadius: '16px',
                                    background: msg.role === 'user' ? 'var(--secondary)' : 'var(--bg-card)',
                                    borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                                    borderBottomLeftRadius: msg.role === 'user' ? '16px' : '4px'
                                }}>
                                    <div style={{ lineHeight: 1.6, fontSize: '0.95rem' }}>
                                        <ReactMarkdown
                                            components={{
                                                p: ({ node, ...props }) => <p style={{ margin: '0 0 10px 0' }} {...props} />,
                                                ul: ({ node, ...props }) => <ul style={{ margin: '0 0 10px 20px', paddingLeft: 0 }} {...props} />,
                                                li: ({ node, ...props }) => <li style={{ marginBottom: '4px' }} {...props} />,
                                                strong: ({ node, ...props }) => <strong style={{ color: 'var(--primary-light)', fontWeight: 600 }} {...props} />,
                                                code: ({ node, ...props }) => <code style={{ background: 'rgba(0,0,0,0.3)', padding: '2px 6px', borderRadius: '4px' }} {...props} />
                                            }}
                                        >
                                            {msg.content}
                                        </ReactMarkdown>
                                    </div>
                                    {msg.sources?.length > 0 && (
                                        <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                                            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>📚 Sources:</span>
                                            <div style={{ display: 'flex', gap: '6px', flexWrap: 'wrap', marginTop: '6px' }}>
                                                {msg.sources.map((s, j) => (
                                                    <span key={j} style={{
                                                        padding: '4px 10px',
                                                        background: 'var(--bg-input)',
                                                        borderRadius: '6px',
                                                        fontSize: '0.75rem'
                                                    }}>
                                                        {s.title || s.source}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            </motion.div>
                        ))
                    )}
                    {loading && (
                        <div style={{ display: 'flex', gap: '12px', marginBottom: '20px' }}>
                            <div style={{
                                width: '40px',
                                height: '40px',
                                background: 'var(--gradient-primary)',
                                borderRadius: '12px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center'
                            }}>
                                <Bot size={20} color="white" />
                            </div>
                            <div style={{ padding: '14px 18px', background: 'var(--bg-card)', borderRadius: '16px' }}>
                                <div style={{ display: 'flex', gap: '6px' }}>
                                    <span style={{
                                        width: '8px',
                                        height: '8px',
                                        background: 'var(--primary)',
                                        borderRadius: '50%',
                                        animation: 'pulse 1s infinite'
                                    }} />
                                    <span style={{
                                        width: '8px',
                                        height: '8px',
                                        background: 'var(--primary)',
                                        borderRadius: '50%',
                                        animation: 'pulse 1s infinite 0.2s'
                                    }} />
                                    <span style={{
                                        width: '8px',
                                        height: '8px',
                                        background: 'var(--primary)',
                                        borderRadius: '50%',
                                        animation: 'pulse 1s infinite 0.4s'
                                    }} />
                                </div>
                            </div>
                        </div>
                    )}
                    <div ref={bottomRef} />
                </div>

                {/* Input */}
                <div style={{ padding: '16px 24px', borderTop: '1px solid rgba(255,255,255,0.05)' }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <input
                            className="input"
                            placeholder={selectedCourse ? "Ask about your course materials..." : "Ask any study question..."}
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                            style={{ flex: 1 }}
                        />
                        <button
                            id="chat-send-btn"
                            className="btn btn-primary"
                            onClick={sendMessage}
                            disabled={loading || !input.trim()}
                            style={{ padding: '12px 24px' }}
                        >
                            <Send size={20} />
                        </button>
                    </div>
                    <div style={{
                        marginTop: '8px',
                        fontSize: '0.75rem',
                        color: 'var(--text-muted)',
                        textAlign: 'center'
                    }}>
                        Press Enter to send • Answers are based on your uploaded materials
                    </div>
                </div>
            </div>

            {/* Course Selection Modal */}
            <CourseSelectionModal
                isOpen={showCourseModal}
                onClose={() => { setShowCourseModal(false); setPendingAction(null); }}
                onSelect={handleCourseSelect}
                courses={courses}
                title={
                    pendingAction === 'quiz' ? 'Select Course for Quiz' :
                        pendingAction === 'summarize' ? 'Select Course to Summarize' :
                            pendingAction === 'exam' ? 'Select Course for Exam Prediction' :
                                pendingAction === 'keytopics' ? 'Select Course for Key Topics' :
                                    pendingAction === 'cram' ? 'Select Course for Cram Mode' :
                                        'Select a Course'
                }
            />

            {/* Topic Selection Modal */}
            <TopicSelectionModal
                isOpen={showTopicModal}
                onClose={() => { setShowTopicModal(false); setPendingAction(null); }}
                onSelect={handleTopicSelect}
                courseId={selectedCourseForAction}
                title={
                    pendingAction === 'quiz' ? 'Select Topic to Quiz On' :
                        pendingAction === 'summarize' ? 'Select Topic to Summarize' :
                            pendingAction === 'exam' ? 'Select Topic for Exam Prediction' :
                                pendingAction === 'keytopics' ? 'Select Topic for Key Topics' :
                                    'Select a Topic'
                }
            />
        </div>
    )
}
