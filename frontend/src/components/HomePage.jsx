import React from 'react'
import './HomePage.css'

function HomePage({ onStartSummarizing }) {
    return (
        <div className="homepage">
            <div className="homepage-content">
                <div className="logo-section">
                    <div className="logo-icon">
                        <svg width="60" height="60" viewBox="0 0 60 60" fill="none">
                            <rect width="60" height="60" rx="12" fill="url(#gradient)" />
                            <path d="M20 25h20M20 30h15M20 35h18" stroke="white" strokeWidth="3" strokeLinecap="round" />
                            <defs>
                                <linearGradient id="gradient" x1="0" y1="0" x2="60" y2="60">
                                    <stop offset="0%" stopColor="#667eea" />
                                    <stop offset="100%" stopColor="#764ba2" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <h1 className="title">AI Summarizer</h1>
                    <p className="subtitle">Transform long texts into concise summaries with AI</p>
                </div>

                <div className="features">
                    <div className="feature-card">
                        <div className="feature-icon">📝</div>
                        <h3>Smart Summarization</h3>
                        <p>Powered by BART-CNN and FLAN-T5 models</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">🎨</div>
                        <h3>Multiple Styles</h3>
                        <p>Brief, detailed, bullet points, or custom</p>
                    </div>
                    <div className="feature-card">
                        <div className="feature-icon">⚡</div>
                        <h3>Fast Processing</h3>
                        <p>Token-based chunking for efficient results</p>
                    </div>
                </div>

                <button className="start-button" onClick={onStartSummarizing}>
                    <span>Start Summarizing</span>
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                        <path d="M10 3l7 7-7 7M3 10h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" fill="none" />
                    </svg>
                </button>

                <div className="info-section">
                    <div className="info-item">
                        <span className="info-label">Text Area:</span>
                        <span className="info-value">150-1500 words</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">File Upload:</span>
                        <span className="info-value">300-4000 words</span>
                    </div>
                </div>
            </div>
        </div>
    )
}

export default HomePage
