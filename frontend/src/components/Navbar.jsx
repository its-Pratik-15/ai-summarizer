import { Link, useLocation } from 'react-router-dom'

function Navbar() {
    const location = useLocation()

    // Helper function to check if link is active
    const isActive = (path) => location.pathname === path

    return (
        <nav className="navbar">
            <div className="nav-container">
                <Link to="/" className="nav-logo">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" style={{ marginRight: '10px' }}>
                        <rect width="32" height="32" rx="8" fill="url(#gradient)" />
                        <path d="M8 10h16M8 16h12M8 22h14" stroke="white" strokeWidth="2" strokeLinecap="round" />
                        <defs>
                            <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                                <stop offset="0%" stopColor="#667eea" />
                                <stop offset="100%" stopColor="#764ba2" />
                            </linearGradient>
                        </defs>
                    </svg>
                    SummarizeAI
                </Link>

                <ul className="nav-menu">
                    <li className="nav-item">
                        <Link
                            to="/"
                            className={`nav-link ${isActive('/') ? 'active' : ''}`}
                        >
                            Home
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link
                            to="/about"
                            className={`nav-link ${isActive('/about') ? 'active' : ''}`}
                        >
                            About
                        </Link>
                    </li>
                    <li className="nav-item">
                        <Link
                            to="/docs"
                            className={`nav-link ${isActive('/docs') ? 'active' : ''}`}
                        >
                            Docs
                        </Link>
                    </li>
                </ul>
            </div>
        </nav>
    )
}

export default Navbar
