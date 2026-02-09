import { useState, useRef } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

function Home() {
    const [text, setText] = useState('')
    const [file, setFile] = useState(null)
    const [style, setStyle] = useState('standard')
    const [summary, setSummary] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')
    const [showToast, setShowToast] = useState(false)
    const fileInputRef = useRef(null)

    // Handle text input change
    const handleTextChange = (e) => {
        setText(e.target.value)
        setError('')
    }

    // Handle file upload
    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0]
        if (selectedFile) {
            // Check file type
            const validTypes = ['.txt', '.md', '.csv', '.json', '.pdf']
            const fileExt = '.' + selectedFile.name.split('.').pop().toLowerCase()

            if (!validTypes.includes(fileExt)) {
                setError('Invalid file type. Please upload .txt, .md, .csv, .json, or .pdf files.')
                return
            }

            setFile(selectedFile)

            // Read file content for text files only (not PDF)
            if (fileExt !== '.pdf') {
                const reader = new FileReader()
                reader.onload = (event) => {
                    const content = event.target.result
                    setText(content)
                }
                reader.readAsText(selectedFile)
            } else {
                // For PDF, just show a message
                setText(`PDF file selected: ${selectedFile.name}\n\nClick "Generate Summary" to process the PDF.`)
            }
            setError('')
        }
    }

    // Clear file selection
    const handleClearFile = () => {
        setFile(null)
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    // Handle summarization
    const handleSummarize = async () => {
        if (!text.trim()) {
            setError('Please enter some text or upload a file to summarize')
            return
        }

        setLoading(true)
        setError('')
        setSummary('')

        try {
            let response

            if (file) {
                // Use file upload endpoint
                const formData = new FormData()
                formData.append('file', file)
                formData.append('style', style)

                response = await fetch(`${API_BASE_URL}/summarize-file`, {
                    method: 'POST',
                    body: formData,
                })
            } else {
                // Use text endpoint
                response = await fetch(`${API_BASE_URL}/summarize`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text,
                        style,
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

    // Clear all fields
    const handleClear = () => {
        setText('')
        setFile(null)
        setSummary('')
        setError('')
        if (fileInputRef.current) {
            fileInputRef.current.value = ''
        }
    }

    // Copy to clipboard with toast notification
    const handleCopy = () => {
        navigator.clipboard.writeText(summary)
        setShowToast(true)
        setTimeout(() => setShowToast(false), 3000)
    }

    return (
        <div className="home-page">
            <h1>AI Text Summarizer</h1>
            <p className="subtitle">Powered by BART-CNN</p>

            <div className="input-section">
                <label htmlFor="text-input">Enter Text or Upload File:</label>

                {/* File Upload Section */}
                <div className="file-upload-area">
                    <input
                        ref={fileInputRef}
                        type="file"
                        accept=".txt,.md,.csv,.json,.pdf"
                        onChange={handleFileChange}
                        disabled={loading}
                        style={{ display: 'none' }}
                        id="file-input"
                    />
                    <label htmlFor="file-input" className="file-upload-label">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                            <polyline points="17 8 12 3 7 8" />
                            <line x1="12" y1="3" x2="12" y2="15" />
                        </svg>
                        {file ? file.name : 'Choose File (.txt, .md, .csv, .json, .pdf)'}
                    </label>
                    {file && (
                        <button
                            className="clear-file-btn"
                            onClick={handleClearFile}
                            disabled={loading}
                            type="button"
                        >
                            ✕
                        </button>
                    )}
                </div>

                <div className="divider">
                    <span>OR</span>
                </div>

                <textarea
                    id="text-input"
                    value={text}
                    onChange={handleTextChange}
                    placeholder="Paste your text here (50-1500 words, minimum 3 sentences)..."
                    rows={10}
                    disabled={loading}
                />

                <div className="word-count">
                    {text.split(/\s+/).filter(Boolean).length} words
                </div>

                <div className="controls">
                    <div className="style-selector">
                        <label htmlFor="style-select">Summarization Style:</label>
                        <select
                            id="style-select"
                            value={style}
                            onChange={(e) => setStyle(e.target.value)}
                            disabled={loading}
                        >
                            <option value="standard">Standard (balanced)</option>
                            <option value="brief">Brief (concise)</option>
                            <option value="detailed">Detailed (comprehensive)</option>
                            <option value="bullet_points">Bullet Points</option>
                        </select>
                    </div>

                    <div className="buttons">
                        <button
                            onClick={handleSummarize}
                            disabled={loading || !text.trim()}
                            className="btn-primary"
                        >
                            {loading ? 'Summarizing...' : 'Generate Summary'}
                        </button>
                        <button
                            onClick={handleClear}
                            disabled={loading}
                            className="btn-secondary"
                        >
                            Clear
                        </button>
                    </div>
                </div>

                {error && (
                    <div className="error-message">
                        <strong>Error:</strong> {error}
                    </div>
                )}
            </div>

            {summary && (
                <div className="output-section">
                    <h2>Summary:</h2>
                    <pre className="summary-output">{summary}</pre>
                    <button
                        className="btn-copy"
                        onClick={handleCopy}
                    >
                        📋 Copy to Clipboard
                    </button>
                </div>
            )}

            {showToast && (
                <div className="toast">
                    ✓ Copied to clipboard!
                </div>
            )}
        </div>
    )
}

export default Home
