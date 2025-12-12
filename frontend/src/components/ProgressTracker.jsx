import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Zap, Trophy, Flame, Star, TrendingUp, Target, BookOpen, Brain, Award, CheckCircle } from 'lucide-react'

export default function ProgressTracker({ user }) {
    const [stage, setStage] = useState(1)
    const [stageProgress, setStageProgress] = useState(0)

    // Calculate user stats
    const quizzesCompleted = user?.total_quizzes_completed || 0
    const studyMinutes = user?.total_study_time_minutes || 0
    const coursesCompleted = user?.courses_completed || 0

    useEffect(() => {
        // Stage calculation based on quizzes completed
        // Stage 1: 0-5 quizzes, Stage 2: 6-15, Stage 3: 16-30, Stage 4: 31-50, Stage 5: 50+
        let currentStage = 1
        let progress = 0

        if (quizzesCompleted >= 50) {
            currentStage = 5
            progress = 100
        } else if (quizzesCompleted >= 30) {
            currentStage = 4
            progress = ((quizzesCompleted - 30) / 20) * 100
        } else if (quizzesCompleted >= 15) {
            currentStage = 3
            progress = ((quizzesCompleted - 15) / 15) * 100
        } else if (quizzesCompleted >= 5) {
            currentStage = 2
            progress = ((quizzesCompleted - 5) / 10) * 100
        } else {
            currentStage = 1
            progress = (quizzesCompleted / 5) * 100
        }

        setStage(currentStage)
        setStageProgress(Math.min(100, Math.round(progress)))
    }, [user, quizzesCompleted])

    // Stage definitions with clear milestones
    const stages = [
        { num: 1, name: 'Beginner', target: 5, icon: Star, color: '#6366f1' },
        { num: 2, name: 'Learner', target: 15, icon: BookOpen, color: '#8b5cf6' },
        { num: 3, name: 'Scholar', target: 30, icon: Brain, color: '#10b981' },
        { num: 4, name: 'Expert', target: 50, icon: Award, color: '#f59e0b' },
        { num: 5, name: 'Master', target: '∞', icon: Trophy, color: '#ef4444' }
    ]

    const currentStageInfo = stages[stage - 1]
    const nextStageInfo = stages[stage] || null
    const StageIcon = currentStageInfo.icon

    // Achievements based on actual milestones
    const achievements = [
        {
            name: 'First Quiz',
            desc: 'Complete 1 quiz',
            unlocked: quizzesCompleted >= 1,
            icon: Target,
            progress: `${Math.min(quizzesCompleted, 1)}/1`
        },
        {
            name: 'Quiz Streak',
            desc: 'Complete 10 quizzes',
            unlocked: quizzesCompleted >= 10,
            icon: Zap,
            progress: `${Math.min(quizzesCompleted, 10)}/10`
        },
        {
            name: 'Quiz Master',
            desc: 'Complete 25 quizzes',
            unlocked: quizzesCompleted >= 25,
            icon: Trophy,
            progress: `${Math.min(quizzesCompleted, 25)}/25`
        },
        {
            name: 'Study Hour',
            desc: 'Study for 60 minutes',
            unlocked: studyMinutes >= 60,
            icon: Flame,
            progress: `${Math.min(studyMinutes, 60)}/60 min`
        }
    ]

    const unlockedCount = achievements.filter(a => a.unlocked).length

    return (
        <div style={{
            background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05))',
            borderRadius: '16px',
            padding: '20px',
            border: '1px solid rgba(99, 102, 241, 0.2)'
        }}>
            {/* Stage Display */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{
                        width: '52px',
                        height: '52px',
                        borderRadius: '14px',
                        background: `linear-gradient(135deg, ${currentStageInfo.color}, ${currentStageInfo.color}aa)`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        boxShadow: `0 4px 20px ${currentStageInfo.color}40`
                    }}>
                        <StageIcon size={26} color="white" />
                    </div>
                    <div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            Current Stage
                        </div>
                        <div style={{ fontWeight: 700, fontSize: '1.2rem' }}>
                            Stage {stage}: {currentStageInfo.name}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            {quizzesCompleted} quizzes completed
                        </div>
                    </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.5rem', fontWeight: 700, color: currentStageInfo.color }}>
                        {stageProgress}%
                    </div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {nextStageInfo ? `to Stage ${stage + 1}` : 'Max Stage!'}
                    </div>
                </div>
            </div>

            {/* Progress Bar */}
            <div style={{
                height: '12px',
                background: 'var(--bg-dark)',
                borderRadius: '10px',
                overflow: 'hidden',
                marginBottom: '12px'
            }}>
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${stageProgress}%` }}
                    transition={{ duration: 1, ease: 'easeOut' }}
                    style={{
                        height: '100%',
                        background: `linear-gradient(90deg, ${currentStageInfo.color}, ${currentStageInfo.color}cc)`,
                        borderRadius: '10px'
                    }}
                />
            </div>

            {/* Next Stage Info */}
            {nextStageInfo && (
                <div style={{
                    fontSize: '0.8rem',
                    color: 'var(--text-muted)',
                    marginBottom: '16px',
                    padding: '8px 12px',
                    background: 'rgba(255,255,255,0.05)',
                    borderRadius: '8px'
                }}>
                    🎯 <strong>Next:</strong> Complete {stages[stage].target} quizzes to reach <strong>Stage {stage + 1}: {nextStageInfo.name}</strong>
                </div>
            )}

            {/* Achievements */}
            <div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600, marginBottom: '12px', display: 'flex', justifyContent: 'space-between' }}>
                    <span>🏆 Achievements</span>
                    <span style={{ color: 'var(--primary-light)' }}>{unlockedCount}/{achievements.length}</span>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '8px' }}>
                    {achievements.map((achievement, i) => {
                        const Icon = achievement.icon
                        return (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: i * 0.1 }}
                                style={{
                                    padding: '12px',
                                    background: achievement.unlocked
                                        ? 'rgba(16, 185, 129, 0.15)'
                                        : 'rgba(255,255,255,0.03)',
                                    borderRadius: '10px',
                                    border: achievement.unlocked
                                        ? '1px solid rgba(16, 185, 129, 0.3)'
                                        : '1px solid rgba(255,255,255,0.05)',
                                    position: 'relative'
                                }}
                            >
                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                    <Icon
                                        size={18}
                                        color={achievement.unlocked ? 'var(--success)' : 'var(--text-muted)'}
                                    />
                                    <div style={{
                                        fontSize: '0.8rem',
                                        fontWeight: 600,
                                        color: achievement.unlocked ? 'var(--success)' : 'var(--text-primary)'
                                    }}>
                                        {achievement.name}
                                    </div>
                                    {achievement.unlocked && (
                                        <CheckCircle size={14} color="var(--success)" />
                                    )}
                                </div>
                                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                                    {achievement.desc}
                                </div>
                                <div style={{
                                    fontSize: '0.65rem',
                                    color: achievement.unlocked ? 'var(--success)' : 'var(--primary-light)',
                                    marginTop: '4px',
                                    fontWeight: 600
                                }}>
                                    {achievement.unlocked ? '✓ Completed' : achievement.progress}
                                </div>
                            </motion.div>
                        )
                    })}
                </div>
            </div>
        </div>
    )
}

