function About() {
    return (
        <div className="about-page">
            <h1>About This Project</h1>

            <section>
                <h2>Overview</h2>
                <p>
                    This is an AI-powered text summarization service that uses state-of-the-art
                    natural language processing to generate concise summaries of long documents.
                </p>
            </section>

            <section>
                <h2>Technology</h2>
                <p>
                    <strong>Model:</strong> facebook/bart-large-cnn
                </p>
                <p>
                    BART (Bidirectional and Auto-Regressive Transformers) is a denoising autoencoder
                    for pretraining sequence-to-sequence models. The BART-large-cnn variant is
                    specifically fine-tuned on the CNN/DailyMail dataset for summarization tasks.
                </p>
            </section>

            <section>
                <h2>Features</h2>
                <ul>
                    <li><strong>Multiple Styles:</strong> Choose between brief, standard, detailed, or bullet point summaries</li>
                    <li><strong>Optimized Parameters:</strong> Each style uses carefully tuned parameters for best results</li>
                    <li><strong>Quality Instruction:</strong> Summaries cover all major themes and key ideas</li>
                    <li><strong>Input Validation:</strong> Supports 50-1500 words for text area input</li>
                    <li><strong>File Upload:</strong> Supports .txt, .md, .csv, .json, and .pdf files (100-4000 words)</li>
                    <li><strong>PDF Support:</strong> Automatically extracts text from PDF documents</li>
                </ul>
            </section>

            <section>
                <h2>Summarization Styles</h2>
                <div className="style-info">
                    <div className="style-card">
                        <h3>Brief</h3>
                        <p>Quick overview in 20-70 tokens. Perfect for headlines and quick previews.</p>
                    </div>
                    <div className="style-card">
                        <h3>Standard</h3>
                        <p>Balanced summary in 50-150 tokens. Best for general use and most natural output.</p>
                    </div>
                    <div className="style-card">
                        <h3>Detailed</h3>
                        <p>Comprehensive summary in 100-250 tokens. Ideal for research papers and technical documents.</p>
                    </div>
                    <div className="style-card">
                        <h3>Bullet Points</h3>
                        <p>Key points formatted as bullets in 60-180 tokens. Great for easy scanning and note-taking.</p>
                    </div>
                </div>
            </section>

            <section>
                <h2>Tech Stack</h2>
                <ul>
                    <li><strong>Backend:</strong> FastAPI (Python)</li>
                    <li><strong>Frontend:</strong> React with React Router</li>
                    <li><strong>AI Model:</strong> HuggingFace BART-large-cnn</li>
                    <li><strong>NLP:</strong> NLTK for sentence tokenization</li>
                </ul>
            </section>
        </div>
    )
}

export default About
