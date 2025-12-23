import { Link, useNavigate } from "react-router-dom";
import "./Navbar.css";
import logo from "../assets/logo.png";

const Navbar = () => {
  const token = localStorage.getItem("token");
  const navigate = useNavigate();

  const logout = () => {
    localStorage.removeItem("token");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          <img src={logo} alt="Schedulify" className="logo-img" />
          <span className="logo-text">Schedulify</span>
        </Link>

        <ul className="nav-menu">
          <li>
            <Link to="/" className="nav-link">
              Home
            </Link>
          </li>

          {token && (
            <li>
              <Link to="/dashboard" className="nav-link">
                Dashboard
              </Link>
            </li>
          )}

          {!token ? (
            <>
              <li>
                <Link to="/login" className="nav-link btn-primary">
                  Login
                </Link>
              </li>
              <li>
                <Link to="/register" className="nav-link">
                  Register
                </Link>
              </li>
            </>
          ) : (
            <li>
              <button onClick={logout} className="nav-link btn-primary">
                Logout
              </button>
            </li>
          )}
        </ul>
      </div>
    </nav>
  );
};

export default Navbar;
