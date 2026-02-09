import { Link, useLocation } from 'react-router-dom'

function Navbar() {
    const location = useLocation()

    // Helper function to check if link is active
    const isActive = (path) => location.pathname === path

    return (
        <nav className="navbar">
            <div className="nav-container">
                <Link to="/" className="nav-logo">
                    AI Summarizer
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
