import { useState, useEffect } from 'react'
import { useParams, useSearchParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { CheckCircle, XCircle, ArrowRight, Trophy, RotateCcw } from 'lucide-react'
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
            toast.error('Failed to generate quiz')
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

    if (loading) return <div style={{ textAlign: 'center', padding: '100px' }}>Generating quiz...</div>
    if (!quiz) return null

    if (finished) {
        const score = Math.round((quiz.correct_answers / quiz.total_questions) * 100)
        return (
            <div style={{ maxWidth: '600px', margin: '0 auto', textAlign: 'center', padding: '60px 24px' }}>
                <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }}>
                    <Trophy size={80} color={score >= 70 ? 'var(--success)' : 'var(--warning)'} style={{ marginBottom: '24px' }} />
                </motion.div>
                <h1>Quiz Complete!</h1>
                <div style={{ fontSize: '4rem', fontWeight: 800, color: score >= 70 ? 'var(--success)' : 'var(--warning)', margin: '24px 0' }}>
                    {score}%
                </div>
                <p style={{ color: 'var(--text-secondary)', marginBottom: '32px' }}>
                    You got {quiz.correct_answers} out of {quiz.total_questions} questions correct
                </p>
                <div style={{ display: 'flex', gap: '16px', justifyContent: 'center' }}>
                    <button className="btn btn-secondary" onClick={() => navigate('/app')}>
                        Back to Dashboard
                    </button>
                    <button className="btn btn-primary" onClick={() => window.location.reload()}>
                        <RotateCcw size={18} /> Try Again
                    </button>
                </div>
            </div>
        )
    }

    const question = quiz.questions[currentIndex]

    return (
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
            {/* Progress */}
            <div style={{ marginBottom: '32px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                    <span>Question {currentIndex + 1} of {quiz.questions.length}</span>
                    <span>{quiz.correct_answers || 0} correct</span>
                </div>
                <div style={{ height: '8px', background: 'var(--bg-card)', borderRadius: '4px' }}>
                    <div style={{ width: `${((currentIndex + 1) / quiz.questions.length) * 100}%`, height: '100%', background: 'var(--gradient-primary)', borderRadius: '4px', transition: 'width 0.3s' }} />
                </div>
            </div>

            {/* Question */}
            <motion.div key={currentIndex} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="card" style={{ marginBottom: '24px' }}>
                <div style={{ padding: '4px 12px', background: 'rgba(99, 102, 241, 0.2)', borderRadius: '8px', display: 'inline-block', marginBottom: '16px', fontSize: '0.875rem', color: 'var(--primary-light)' }}>
                    {question.question_type.toUpperCase()}
                </div>
                <h2 style={{ marginBottom: 0, lineHeight: 1.4 }}>{question.question_text}</h2>
            </motion.div>

            {/* Options */}
            {question.options ? (
                <div style={{ display: 'grid', gap: '12px', marginBottom: '24px' }}>
                    {question.options.map((option, i) => {
                        const isSelected = selectedAnswer === option
                        const isCorrect = result && option === result.correct_answer
                        const isWrong = result && isSelected && !result.is_correct

                        return (
                            <motion.button
                                key={i}
                                whileHover={{ scale: result ? 1 : 1.01 }}
                                onClick={() => !result && setSelectedAnswer(option)}
                                disabled={!!result}
                                style={{
                                    padding: '16px 20px',
                                    background: isCorrect ? 'rgba(16, 185, 129, 0.2)' : isWrong ? 'rgba(239, 68, 68, 0.2)' : isSelected ? 'rgba(99, 102, 241, 0.3)' : 'var(--bg-card)',
                                    border: `2px solid ${isCorrect ? 'var(--success)' : isWrong ? 'var(--error)' : isSelected ? 'var(--primary)' : 'transparent'}`,
                                    borderRadius: '12px',
                                    textAlign: 'left',
                                    cursor: result ? 'default' : 'pointer',
                                    color: 'var(--text-primary)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '12px'
                                }}
                            >
                                {isCorrect && <CheckCircle size={20} color="var(--success)" />}
                                {isWrong && <XCircle size={20} color="var(--error)" />}
                                {option}
                            </motion.button>
                        )
                    })}
                </div>
            ) : (
                <textarea
                    className="input"
                    rows={4}
                    placeholder="Type your answer..."
                    value={selectedAnswer || ''}
                    onChange={(e) => setSelectedAnswer(e.target.value)}
                    disabled={!!result}
                    style={{ marginBottom: '24px' }}
                />
            )}

            {/* Result */}
            {result && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="card" style={{ padding: '20px', marginBottom: '24px', background: result.is_correct ? 'rgba(16, 185, 129, 0.1)' : 'rgba(239, 68, 68, 0.1)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                        {result.is_correct ? <CheckCircle size={24} color="var(--success)" /> : <XCircle size={24} color="var(--error)" />}
                        <strong>{result.is_correct ? 'Correct!' : 'Incorrect'}</strong>
                    </div>
                    {result.explanation && <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{result.explanation}</p>}
                </motion.div>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                {!result ? (
                    <button className="btn btn-primary" onClick={submitAnswer} disabled={!selectedAnswer}>
                        Submit Answer
                    </button>
                ) : (
                    <button className="btn btn-primary" onClick={nextQuestion}>
                        {currentIndex + 1 >= quiz.questions.length ? 'Finish Quiz' : 'Next Question'} <ArrowRight size={18} />
                    </button>
                )}
            </div>
        </div>
    )
}
