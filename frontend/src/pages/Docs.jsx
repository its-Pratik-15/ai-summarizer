function Docs() {
    return (
        <div className="docs-page">
            <h1>API Documentation</h1>

            <section>
                <h2>Base URL</h2>
                <pre className="code-block">http://localhost:8000/api</pre>
            </section>

            <section>
                <h2>Endpoints</h2>

                <div className="endpoint">
                    <h3>POST /summarize</h3>
                    <p>Generate a summary from text input.</p>

                    <h4>Request Body:</h4>
                    <pre className="code-block">{`{
  "text": "Your long text here...",
  "style": "standard"
}`}</pre>

                    <h4>Parameters:</h4>
                    <ul>
                        <li><code>text</code> (string, required): The text to summarize (50-1500 words, minimum 3 sentences)</li>
                        <li><code>style</code> (string, optional): Summarization style
                            <ul>
                                <li><code>"standard"</code> - Balanced summary (default)</li>
                                <li><code>"brief"</code> - Concise summary</li>
                                <li><code>"detailed"</code> - Comprehensive summary</li>
                                <li><code>"bullet_points"</code> - Bullet point format</li>
                            </ul>
                        </li>
                    </ul>

                    <h4>Response (200 OK):</h4>
                    <pre className="code-block">{`{
  "summary": "Generated summary text...",
  "style": "standard",
  "word_count": 45
}`}</pre>

                    <h4>Error Response (400 Bad Request):</h4>
                    <pre className="code-block">{`{
  "detail": "Text area: Text too short. Minimum 150 words required."
}`}</pre>

                    <h4>Error Response (502 Bad Gateway):</h4>
                    <pre className="code-block">{`{
  "detail": "Model error: ..."
}`}</pre>
                </div>

                <div className="endpoint">
                    <h3>POST /summarize-file</h3>
                    <p>Generate a summary from an uploaded file.</p>

                    <h4>Request (multipart/form-data):</h4>
                    <ul>
                        <li><code>file</code> (file, required): Text file (.txt, .md, .csv, .json)</li>
                        <li><code>style</code> (string, optional): Summarization style</li>
                    </ul>

                    <h4>Supported File Types:</h4>
                    <ul>
                        <li>.txt - Plain text</li>
                        <li>.csv - CSV files</li>
                        <li>.json - JSON files</li>
                    </ul>

                    <h4>File Size Limits:</h4>
                    <p>100-4000 words (minimum 3 complete sentences)</p>

                    <h4>Response:</h4>
                    <p>Same as /summarize endpoint</p>
                </div>

                <div className="endpoint">
                    <h3>GET /health</h3>
                    <p>Check API health status.</p>

                    <h4>Response (200 OK):</h4>
                    <pre className="code-block">{`{
  "status": "ok",
  "message": "Summarization API is running"
}`}</pre>
                </div>
            </section>

            <section>
                <h2>Example Usage</h2>

                <h3>JavaScript (Fetch API)</h3>
                <pre className="code-block">{`const response = await fetch('http://localhost:8000/api/summarize', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    text: 'Your long article text here...',
    style: 'brief'
  })
});

const data = await response.json();
console.log(data.summary);`}</pre>

                <h3>Python (requests)</h3>
                <pre className="code-block">{`import requests

response = requests.post(
    'http://localhost:8000/api/summarize',
    json={
        'text': 'Your long article text here...',
        'style': 'detailed'
    }
)

data = response.json()
print(data['summary'])`}</pre>

                <h3>cURL</h3>
                <pre className="code-block">{`curl -X POST http://localhost:8000/api/summarize \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Your long article text here...",
    "style": "bullet_points"
  }'`}</pre>
            </section>

            <section>
                <h2>Model Parameters by Style</h2>
                <table className="params-table">
                    <thead>
                        <tr>
                            <th>Style</th>
                            <th>Max Length</th>
                            <th>Min Length</th>
                            <th>Num Beams</th>
                            <th>Length Penalty</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Brief</td>
                            <td>60</td>
                            <td>20</td>
                            <td>4</td>
                            <td>1.2</td>
                        </tr>
                        <tr>
                            <td>Standard</td>
                            <td>140</td>
                            <td>50</td>
                            <td>4</td>
                            <td>1.0</td>
                        </tr>
                        <tr>
                            <td>Detailed</td>
                            <td>230</td>
                            <td>110</td>
                            <td>5</td>
                            <td>0.9</td>
                        </tr>
                        <tr>
                            <td>Bullet</td>
                            <td>140</td>
                            <td>40</td>
                            <td>4</td>
                            <td>1.0</td>
                        </tr>
                    </tbody>
                </table>
            </section>
        </div>
    )
}

export default Docs
