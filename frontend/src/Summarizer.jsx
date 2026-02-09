import React, { useState } from 'react';
import axios from 'axios';
import './Summarizer.css';

const Summarizer = () => {
    const [text, setText] = useState('');
    const [file, setFile] = useState(null);
    const [style, setStyle] = useState('brief');
    const [summary, setSummary] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [charCount, setCharCount] = useState(0);

    const handleTextChange = (e) => {
        setText(e.target.value);
        setCharCount(e.target.value.length);
        if (file) setFile(null); // Clear file if text is entered
    };

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setText(''); // Clear text if file is selected
            setCharCount(0);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSummary('');

        try {
            let response;
            const config = {
                headers: {
                    'Content-Type': 'application/json' // Default
                }
            };

            if (file) {
                const formData = new FormData();
                formData.append('file', file);
                config.headers['Content-Type'] = 'multipart/form-data';

                // Add style param to query string or formData depending on backend implementation
                // Based on router: style is a query param default BRIEF
                response = await axios.post(`http://127.0.0.1:8000/api/summarize-file?style=${style}`, formData, config);
            } else {
                response = await axios.post('http://127.0.0.1:8000/api/summarize', {
                    text,
                    style
                }, config);
            }

            setSummary(response.data.summary);
        } catch (err) {
            console.error('Error fetching summary:', err);
            setError(err.response?.data?.detail || 'Failed to generate summary. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="summarizer-container">
            <header className="app-header">
                <h1>AI Document Summarizer</h1>
                <p>Upload a file or paste text to get a quick summary.</p>
            </header>

            <main className="main-content">
                <form onSubmit={handleSubmit} className="summary-form">
                    <div className="input-group">
                        <label>Input Method</label>
                        <div className="tabs">
                            <button
                                type="button"
                                className={!file ? 'active' : ''}
                                onClick={() => { setFile(null); setText(''); }}
                            >
                                Text Input
                            </button>
                            <button
                                type="button"
                                className={file ? 'active' : ''}
                                onClick={() => { setText(''); }}
                            >
                                File Upload
                            </button>
                        </div>

                        {!file ? (
                            <textarea
                                value={text}
                                onChange={handleTextChange}
                                placeholder="Paste your text here..."
                                rows={10}
                                disabled={loading}
                            />
                        ) : (
                            <div className="file-upload-area">
                                <input
                                    type="file"
                                    onChange={handleFileChange}
                                    accept=".txt,.pdf"
                                    disabled={loading}
                                />
                                {file && <p>Selected: {file.name}</p>}
                            </div>
                        )}
                        <div className="char-counter">
                            {charCount} characters
                        </div>
                    </div>

                    <div className="controls-group">
                        <label>Detail Level</label>
                        <select
                            value={style}
                            onChange={(e) => setStyle(e.target.value)}
                            disabled={loading}
                        >
                            <option value="brief">Brief (1-2 sentences)</option>
                            <option value="detailed">Detailed (Comprehensive)</option>
                            <option value="bullet_points">Bullet Points</option>
                        </select>
                    </div>

                    <button type="submit" className="submit-btn" disabled={loading || (!text && !file)}>
                        {loading ? 'Summarizing...' : 'Summarize Text'}
                    </button>
                </form>

                {error && <div className="error-message">{error}</div>}

                {summary && (
                    <div className="result-section">
                        <h2>Summary Result</h2>
                        <div className="summary-content">
                            {style === 'bullet_points' ? (
                                <ul>
                                    {summary.split('\n').map((line, index) =>
                                        line.trim() && <li key={index}>{line.replace(/^- /, '')}</li>
                                    )}
                                </ul>
                            ) : (
                                <p>{summary}</p>
                            )}
                        </div>
                    </div>
                )}
            </main>
        </div>
    );
};

export default Summarizer;
