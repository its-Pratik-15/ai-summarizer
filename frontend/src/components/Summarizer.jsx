import { useState, useRef } from 'react'
import './Summarizer.css'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

function Summarizer({ onBack }) {
    const [text, setText] = useState('')
    const [file, setFile] = useState(null)
    const [style, setStyle] = useState('standard')
    const [customPrompt, setCustomPrompt] = useState('')
    const [summary, setSummary] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [wordCount, setWordCount] = useState(0)
    const [loadingDots, setLoadingDots] = useState('')
    const fileInputRef = useRef(null)

    // Update word count
    const handleTextChange = (e) => {
        const newText = e.target.value
        setText(newText)
        setWordCount(newText.trim().split(/\s+/).filter(Boolean).length)
        setError('')
    }

    // Handle file upload
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0]
        if (selectedFile) {
            setFile(selectedFile)
            const reader = new FileReader()
            reader.onload = (event) => {
                const content = event.target.result
                setText(content)
                setWordCount(content.trim().split(/\s+/).filter(Boolean).length)
            }
            reader.readAsText(selectedFile)
            setError('')
        }
    }

    // Animated loading dots
    useState(() => {
        let interval
        if (loading) {
            interval = setInterval(() => {
                setLoadingDots(prev => {
                    if (prev === '...') return ''
                    return prev + '.'
                })
            }, 500)
        }
        return () => clearInterval(interval)
    }, [loading])

    // Handle summarization
    const handleSummarize = async () => {
        if (!text.trim()) {
            setError('Please enter some text or upload a file')
            return
        }

        if (style === 'custom' && !customPrompt.trim()) {
            setError('Please provide a custom prompt')
            return
        }

        setLoading(true)
        setError('')
        setSummary('')
        setLoadingDots('')

        try {
            const endpoint = file ? '/summarize-file' : '/summarize'
            let response

            if (file) {
                const formData = new FormData()
                formData.append('file', file)
                formData.append('style', style)
                if (style === 'custom') {
                    formData.append('custom_prompt', customPrompt)
                }

                response = await fetch(`${API_BASE_URL}${endpoint}`, {
                    method: 'POST',
                    body: formData,
                })
            } else {
                response = await fetch(`${API_BASE_URL}${endpoint}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text,
                        style,
                        custom_prompt: style === 'custom' ? customPrompt : undefined,
                    }),
                })
            }

            const data = await response.json()

            if (!response.ok) {
                throw new Error(data.detail || 'Failed to generate summary')
            }

            setSummary(data.summary)
        } catch (err) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    // Clear all
    const handleClear = () => {
        setText('')
        setFile(null)
        setSummary('')
        setError('')
        setWordCount(0)
        setCustomPrompt('')
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    return (
        <div className="summarizer">
            <div className="summarizer-header">
                <button className="back-button" onClick={onBack}>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 17l-7-7 7-7M3 10h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                    </svg>
                    Back
                </button>
                <h2>AI Summarizer</h2>
                <div></div>
            </div>

            <div className="summarizer-content">
                <div className="input-section">
                    <div className="section-header">
                        <h3>Input Text</h3>
                        <span className="word-count">{wordCount} words</span>
                    </div>

                    <textarea
                        className="text-input"
                        placeholder="Paste your text here (150-1500 words for text area, 300-4000 words for file upload)..."
                        value={text}
                        onChange={handleTextChange}
                        disabled={loading}
                    />

                    <div className="file-upload-section">
                        <input
                            ref={fileInputRef}
                            type="file"
                            accept=".txt,.md,.csv,.json"
                            onChange={handleFileChange}
                            disabled={loading}
                            style={{ display: 'none' }}
                        />
                        <button
                            className="upload-button"
                            onClick={() => fileInputRef.current?.click()}
                            disabled={loading}
                        >
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                                <path d="M10 3v10M6 9l4-4 4 4M3 17h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                            </svg>
                            {file ? file.name : 'Upload File'}
                        </button>
                        {file && (
                            <button className="clear-file-button" onClick={() => {
                                setFile(null)
                                if (fileInputRef.current) fileInputRef.current.value = ''
                            }}>
                                ✕
                            </button>
                        )}
                    </div>

                    <div className="style-section">
                        <label>Summarization Style:</label>
                        <select value={style} onChange={(e) => setStyle(e.target.value)} disabled={loading}>
                            <option value="standard">Standard (direct summary)</option>
                            <option value="brief">Brief (concise with key info)</option>
                            <option value="detailed">Detailed (comprehensive)</option>
                            <option value="bullet_points">Bullet Points</option>
                            <option value="custom">Custom</option>
                        </select>
                    </div>

                    {style === 'custom' && (
                        <div className="custom-prompt-section">
                            <label>Custom Prompt:</label>
                            <input
                                type="text"
                                className="custom-prompt-input"
                                placeholder="e.g., 'Rewrite as a tweet' or 'Explain like I'm 5'"
                                value={customPrompt}
                                onChange={(e) => setCustomPrompt(e.target.value)}
                                disabled={loading}
                            />
                        </div>
                    )}

                    <div className="action-buttons">
                        <button
                            className="summarize-button"
                            onClick={handleSummarize}
                            disabled={loading || !text.trim()}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    Summarizing{loadingDots}
                                </>
                            ) : (
                                <>
                                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                                        <path d="M10 3l7 7-7 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                                    </svg>
                                    Generate Summary
                                </>
                            )}
                        </button>
                        <button className="clear-button" onClick={handleClear} disabled={loading}>
                            Clear
                        </button>
                    </div>

                    {error && (
                        <div className="error-message">
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                                <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="2" fill="none" />
                                <path d="M10 6v4M10 14h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
                            </svg>
                            {error}
                        </div>
                    )}
                </div>

                <div className="output-section">
                    <div className="section-header">
                        <h3>Summary</h3>
                        {summary && (
                            <button
                                className="copy-button"
                                onClick={() => {
                                    navigator.clipboard.writeText(summary)
                                    alert('Copied to clipboard!')
                                }}
                            >
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                                    <path d="M4 2h8a2 2 0 012 2v8M2 6h8a2 2 0 012 2v6a2 2 0 01-2 2H4a2 2 0 01-2-2V8a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5" fill="none" />
                                </svg>
                                Copy
                            </button>
                        )}
                    </div>

                    <div className="summary-output">
                        {loading ? (
                            <div className="loading-animation">
                                <div className="loading-line"></div>
                                <div className="loading-line"></div>
                                <div className="loading-line"></div>
                                <div className="loading-text">
                                    Analyzing your text{loadingDots}
                                </div>
                            </div>
                        ) : summary ? (
                            <div className="summary-text">{summary}</div>
                        ) : (
                            <div className="empty-state">
                                <svg width="60" height="60" viewBox="0 0 60 60" fill="none">
                                    <circle cx="30" cy="30" r="28" stroke="#e0e0e0" strokeWidth="2" />
                                    <path d="M20 25h20M20 30h15M20 35h18" stroke="#e0e0e0" strokeWidth="2" strokeLinecap="round" />
                                </svg>
                                <p>Your summary will appear here</p>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default Summarizer
