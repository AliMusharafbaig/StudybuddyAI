import { useState, useEffect } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
    CheckCircle, XCircle, ArrowRight, Trophy, RotateCcw,
    Brain, Clock, Home, Target, BookOpen, Lightbulb, FileText
} from 'lucide-react'
import api from '../api'
import toast from 'react-hot-toast'

export default function Quiz() {
    const { id } = useParams()
    const [searchParams] = useSearchParams()
    const navigate = useNavigate()
    const [quiz, setQuiz] = useState(null)
    const [currentIndex, setCurrentIndex] = useState(0)
    const [selectedAnswer, setSelectedAnswer] = useState(null)
    const [result, setResult] = useState(null)
    const [finished, setFinished] = useState(false)
    const [loading, setLoading] = useState(true)
    const [startTime] = useState(Date.now())
    const [answers, setAnswers] = useState([])

    useEffect(() => {
        if (searchParams.get('generate')) generateQuiz()
        else loadQuiz()
    }, [id])

    const generateQuiz = async () => {
        try {
            const { data } = await api.post('/quiz/generate', {
                course_id: id,
                num_questions: 10,
                difficulty: 'medium'
            })
            setQuiz(data)
        } catch (e) {
            toast.error('Failed to generate quiz. Make sure you have processed materials.')
            navigate('/app')
        } finally {
            setLoading(false)
        }
    }

    const loadQuiz = async () => {
        try {
            const { data } = await api.get(`/quiz/${id}`)
            setQuiz(data)
        } catch (e) {
            toast.error('Quiz not found')
            navigate('/app')
        } finally {
            setLoading(false)
        }
    }

    const submitAnswer = async () => {
        if (!selectedAnswer) return

        const question = quiz.questions[currentIndex]
        try {
            const { data } = await api.post(`/quiz/${quiz.id}/questions/${question.id}/answer`, {
                answer: selectedAnswer
            })
            setResult(data)
            setAnswers([...answers, { question: question.question_text, answer: selectedAnswer, correct: data.is_correct }])

            if (data.is_correct) {
                setQuiz({ ...quiz, correct_answers: (quiz.correct_answers || 0) + 1 })
            }
        } catch (e) {
            toast.error('Failed to submit')
        }
    }

    const nextQuestion = () => {
        if (currentIndex + 1 >= quiz.questions.length) {
            setFinished(true)
        } else {
            setCurrentIndex(currentIndex + 1)
            setSelectedAnswer(null)
            setResult(null)
        }
    }

    // Loading state
    if (loading) {
        return (
            <div style={{
                minHeight: '80vh',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                padding: '40px 20px'
            }}>
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    style={{ marginBottom: '32px' }}
                >
                    <div style={{
                        width: '100px',
                        height: '100px',
                        background: 'var(--gradient-primary)',
                        borderRadius: '24px',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                    }}>
                        <Brain size={50} color="white" />
                    </div>
                </motion.div>
                <h2 style={{ marginBottom: '12px' }}>Generating Your Quiz</h2>
                <p style={{ color: 'var(--text-secondary)', textAlign: 'center', maxWidth: '400px' }}>
                    AI is analyzing your course materials to create personalized questions...
                </p>
                <div style={{ display: 'flex', gap: '8px', marginTop: '24px' }}>
                    {[0, 1, 2].map(i => (
                        <motion.div
                            key={i}
                            animate={{ scale: [1, 1.4, 1], opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 1, repeat: Infinity, delay: i * 0.2 }}
                            style={{
                                width: '12px',
                                height: '12px',
                                borderRadius: '50%',
                                background: 'var(--primary)'
                            }}
                        />
                    ))}
                </div>
            </div>
        )
    }

    if (!quiz) return null

    // Results screen
    if (finished) {
        const score = Math.round(((quiz.correct_answers || answers.filter(a => a.correct).length) / quiz.total_questions) * 100)
        const timeTaken = Math.round((Date.now() - startTime) / 1000 / 60)
        const correctCount = quiz.correct_answers || answers.filter(a => a.correct).length

        const getMessage = () => {
            if (score >= 90) return { text: "🏆 Outstanding! You've mastered this material!", emoji: "🎉" }
            if (score >= 70) return { text: "⭐ Great job! You're on the right track!", emoji: "💪" }
            if (score >= 50) return { text: "📚 Good effort! Keep reviewing the material.", emoji: "💡" }
            return { text: "🌱 Don't give up! Review and try again.", emoji: "📖" }
        }
        const message = getMessage()

        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                style={{ maxWidth: '700px', margin: '0 auto', padding: '40px 24px' }}
            >
                {/* Header Card */}
                <div className="card" style={{
                    textAlign: 'center',
                    padding: '48px 32px',
                    marginBottom: '24px',
                    background: score >= 70
                        ? 'linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(52, 211, 153, 0.05))'
                        : 'linear-gradient(135deg, rgba(245, 158, 11, 0.1), rgba(251, 191, 36, 0.05))',
                    border: `1px solid ${score >= 70 ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)'}`
                }}>
                    <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', duration: 0.6 }}
                    >
                        <div style={{
                            width: '100px',
                            height: '100px',
                            background: score >= 70
                                ? 'linear-gradient(135deg, #10b981, #34d399)'
                                : 'linear-gradient(135deg, #f59e0b, #fbbf24)',
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 24px',
                            boxShadow: `0 0 50px ${score >= 70 ? 'rgba(16, 185, 129, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`
                        }}>
                            <Trophy size={50} color="white" />
                        </div>
                    </motion.div>

                    <h1 style={{ marginBottom: '12px', fontSize: '2rem' }}>Quiz Complete!</h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem', marginBottom: '32px' }}>
                        {message.text}
                    </p>

                    {/* Score Display */}
                    <div style={{
                        fontSize: '5rem',
                        fontWeight: 800,
                        background: score >= 70
                            ? 'linear-gradient(135deg, #10b981, #34d399)'
                            : 'linear-gradient(135deg, #f59e0b, #fbbf24)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        lineHeight: 1
                    }}>
                        {score}%
                    </div>
                    <p style={{ color: 'var(--text-muted)', marginTop: '8px' }}>
                        {correctCount} of {quiz.total_questions} correct
                    </p>
                </div>

                {/* Stats Grid */}
                <div style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(3, 1fr)',
                    gap: '16px',
                    marginBottom: '32px'
                }}>
                    <div className="card" style={{ padding: '24px', textAlign: 'center' }}>
                        <CheckCircle size={32} color="var(--success)" style={{ marginBottom: '12px' }} />
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--success)' }}>{correctCount}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Correct</div>
                    </div>
                    <div className="card" style={{ padding: '24px', textAlign: 'center' }}>
                        <XCircle size={32} color="var(--error)" style={{ marginBottom: '12px' }} />
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--error)' }}>{quiz.total_questions - correctCount}</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Incorrect</div>
                    </div>
                    <div className="card" style={{ padding: '24px', textAlign: 'center' }}>
                        <Clock size={32} color="var(--primary)" style={{ marginBottom: '12px' }} />
                        <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--primary)' }}>{timeTaken || '<1'}m</div>
                        <div style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Time</div>
                    </div>
                </div>

                {/* Actions */}
                <div style={{ display: 'flex', gap: '16px' }}>
                    <button
                        className="btn btn-secondary"
                        onClick={() => navigate('/app')}
                        style={{ flex: 1, padding: '16px', justifyContent: 'center' }}
                    >
                        <Home size={20} /> Dashboard
                    </button>
                    <button
                        className="btn btn-primary"
                        onClick={() => window.location.reload()}
                        style={{ flex: 1, padding: '16px', justifyContent: 'center' }}
                    >
                        <RotateCcw size={20} /> Try Again
                    </button>
                </div>
            </motion.div>
        )
    }

    const question = quiz.questions[currentIndex]
    const progress = ((currentIndex + 1) / quiz.questions.length) * 100

    return (
        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
            {/* Header Bar */}
            <div className="card" style={{
                marginBottom: '24px',
                padding: '20px 24px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                flexWrap: 'wrap',
                gap: '16px'
            }}>
                <div>
                    <h2 style={{ margin: '0 0 4px', fontSize: '1.3rem' }}>📝 Knowledge Check</h2>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
                        Question {currentIndex + 1} of {quiz.questions.length}
                    </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{
                        padding: '10px 20px',
                        background: 'rgba(16, 185, 129, 0.15)',
                        borderRadius: '12px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                    }}>
                        <CheckCircle size={18} color="var(--success)" />
                        <span style={{ fontWeight: 600, color: 'var(--success)' }}>
                            {quiz.correct_answers || answers.filter(a => a.correct).length} correct
                        </span>
                    </div>
                </div>
            </div>

            {/* Progress Bar */}
            <div style={{ marginBottom: '32px' }}>
                <div style={{
                    height: '8px',
                    background: 'var(--bg-card)',
                    borderRadius: '8px',
                    overflow: 'hidden'
                }}>
                    <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.4 }}
                        style={{
                            height: '100%',
                            background: 'var(--gradient-primary)',
                            borderRadius: '8px'
                        }}
                    />
                </div>
            </div>

            {/* Question Card */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentIndex}
                    initial={{ opacity: 0, x: 30 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -30 }}
                    transition={{ duration: 0.3 }}
                    className="card"
                    style={{ marginBottom: '24px', padding: '32px' }}
                >
                    {/* Question Type & Difficulty Badge */}
                    <div style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '10px',
                        marginBottom: '20px'
                    }}>
                        <span style={{
                            padding: '6px 14px',
                            background: 'rgba(99, 102, 241, 0.15)',
                            borderRadius: '20px',
                            fontSize: '0.8rem',
                            color: 'var(--primary-light)',
                            fontWeight: 500,
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px'
                        }}>
                            <Target size={14} />
                            {question.question_type === 'mcq' ? 'Multiple Choice' :
                                question.question_type === 'true_false' ? 'True or False' : 'Short Answer'}
                        </span>
                    </div>

                    {/* Question Text */}
                    <h2 style={{
                        marginBottom: 0,
                        lineHeight: 1.6,
                        fontSize: '1.25rem',
                        fontWeight: 500
                    }}>
                        {question.question_text}
                    </h2>
                </motion.div>
            </AnimatePresence>

            {/* Options - Clean Card Layout */}
            {question.options ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
                    {question.options.map((option, i) => {
                        const isSelected = selectedAnswer === option
                        const isCorrect = result && option === result.correct_answer
                        const isWrong = result && isSelected && !result.is_correct
                        const optionLetter = String.fromCharCode(65 + i)

                        return (
                            <motion.button
                                key={i}
                                whileHover={{ scale: result ? 1 : 1.01 }}
                                whileTap={{ scale: result ? 1 : 0.99 }}
                                onClick={() => !result && setSelectedAnswer(option)}
                                disabled={!!result}
                                style={{
                                    padding: '20px 24px',
                                    background: isCorrect
                                        ? 'rgba(16, 185, 129, 0.12)'
                                        : isWrong
                                            ? 'rgba(239, 68, 68, 0.12)'
                                            : isSelected
                                                ? 'rgba(99, 102, 241, 0.15)'
                                                : 'var(--bg-card)',
                                    border: `2px solid ${isCorrect ? 'var(--success)' :
                                            isWrong ? 'var(--error)' :
                                                isSelected ? 'var(--primary)' : 'transparent'
                                        }`,
                                    borderRadius: '16px',
                                    textAlign: 'left',
                                    cursor: result ? 'default' : 'pointer',
                                    color: 'var(--text-primary)',
                                    display: 'flex',
                                    alignItems: 'flex-start',
                                    gap: '16px',
                                    transition: 'all 0.2s'
                                }}
                            >
                                {/* Option Letter Circle */}
                                <div style={{
                                    width: '40px',
                                    height: '40px',
                                    borderRadius: '12px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontWeight: 700,
                                    fontSize: '1rem',
                                    flexShrink: 0,
                                    background: isCorrect
                                        ? 'var(--success)'
                                        : isWrong
                                            ? 'var(--error)'
                                            : isSelected
                                                ? 'var(--primary)'
                                                : 'var(--bg-input)',
                                    color: isSelected || isCorrect || isWrong ? 'white' : 'var(--text-secondary)'
                                }}>
                                    {isCorrect ? <CheckCircle size={20} /> :
                                        isWrong ? <XCircle size={20} /> : optionLetter}
                                </div>

                                {/* Option Text */}
                                <span style={{
                                    flex: 1,
                                    lineHeight: 1.5,
                                    paddingTop: '8px'
                                }}>
                                    {option}
                                </span>
                            </motion.button>
                        )
                    })}
                </div>
            ) : (
                <div className="card" style={{ marginBottom: '24px', padding: '24px' }}>
                    <label style={{ display: 'block', marginBottom: '12px', fontWeight: 500 }}>
                        Your Answer:
                    </label>
                    <textarea
                        className="input"
                        rows={4}
                        placeholder="Type your answer here..."
                        value={selectedAnswer || ''}
                        onChange={(e) => setSelectedAnswer(e.target.value)}
                        disabled={!!result}
                        style={{ resize: 'vertical' }}
                    />
                </div>
            )}

            {/* Feedback Card */}
            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, height: 0 }}
                        animate={{ opacity: 1, y: 0, height: 'auto' }}
                        exit={{ opacity: 0, y: -20, height: 0 }}
                        className="card"
                        style={{
                            padding: '24px',
                            marginBottom: '24px',
                            background: result.is_correct
                                ? 'rgba(16, 185, 129, 0.08)'
                                : 'rgba(239, 68, 68, 0.08)',
                            borderLeft: `5px solid ${result.is_correct ? 'var(--success)' : 'var(--error)'}`
                        }}
                    >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
                            {result.is_correct
                                ? <CheckCircle size={28} color="var(--success)" />
                                : <XCircle size={28} color="var(--error)" />
                            }
                            <span style={{ fontWeight: 700, fontSize: '1.2rem' }}>
                                {result.is_correct ? '✓ Correct!' : '✗ Incorrect'}
                            </span>
                        </div>

                        {!result.is_correct && result.correct_answer && (
                            <div style={{
                                padding: '14px 18px',
                                background: 'rgba(16, 185, 129, 0.1)',
                                borderRadius: '10px',
                                marginBottom: '16px',
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: '12px'
                            }}>
                                <Lightbulb size={20} color="var(--success)" style={{ flexShrink: 0, marginTop: '2px' }} />
                                <div>
                                    <div style={{ fontWeight: 600, color: 'var(--success)', marginBottom: '4px' }}>
                                        Correct Answer:
                                    </div>
                                    <div style={{ color: 'var(--text-secondary)' }}>
                                        {result.correct_answer}
                                    </div>
                                </div>
                            </div>
                        )}

                        {result.explanation && (
                            <div style={{
                                display: 'flex',
                                alignItems: 'flex-start',
                                gap: '12px',
                                padding: '14px 18px',
                                background: 'var(--bg-input)',
                                borderRadius: '10px'
                            }}>
                                <BookOpen size={20} color="var(--primary-light)" style={{ flexShrink: 0, marginTop: '2px' }} />
                                <div>
                                    <div style={{ fontWeight: 600, color: 'var(--primary-light)', marginBottom: '4px' }}>
                                        Explanation:
                                    </div>
                                    <div style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                                        {result.explanation}
                                    </div>
                                </div>
                            </div>
                        )}
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Action Buttons */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <button
                    className="btn btn-secondary"
                    onClick={() => navigate('/app')}
                    style={{ padding: '14px 24px' }}
                >
                    Exit Quiz
                </button>
                {!result ? (
                    <button
                        className="btn btn-primary"
                        onClick={submitAnswer}
                        disabled={!selectedAnswer}
                        style={{ padding: '14px 32px' }}
                    >
                        <Target size={18} /> Submit Answer
                    </button>
                ) : (
                    <button
                        className="btn btn-primary"
                        onClick={nextQuestion}
                        style={{ padding: '14px 32px' }}
                    >
                        {currentIndex + 1 >= quiz.questions.length ? (
                            <>View Results <Trophy size={18} /></>
                        ) : (
                            <>Next Question <ArrowRight size={18} /></>
                        )}
                    </button>
                )}
            </div>
        </div>
    )
}
