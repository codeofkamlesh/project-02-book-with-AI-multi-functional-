import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';

// AuthWidget component that shows Login/Sign Up buttons when not authenticated, and user dropdown when authenticated
const AuthWidget = () => {
  const { user, login, signup, logout, loading, isAuthenticated } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [isLoginView, setIsLoginView] = useState(true); // True for login, false for signup
  const [currentStep, setCurrentStep] = useState(1); // For multi-step signup: 1 = account details, 2 = background questionnaire
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    softwareBackground: 'beginner',
    hardwareBackground: 'none',
    languagesUsed: '',
    rosExperience: '',
    nvidiaIsaacSimExperience: '', // Added for specification requirement
    hardwarePlatforms: '' // Added for specification requirement (Jetson, Raspberry Pi, etc.)
  });
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    const result = await login(formData.email, formData.password);
    if (!result.success) {
      setError(result.error);
    } else {
      setShowAuthModal(false);
      // Reset form and modal state
      setCurrentStep(1);
      setFormData({
        email: '',
        password: '',
        name: '',
        softwareBackground: 'beginner',
        hardwareBackground: 'none',
        languagesUsed: '',
        rosExperience: '',
        nvidiaIsaacSimExperience: '',
        hardwarePlatforms: ''
      });
    }
  };

  const handleSignupStep1 = (e) => {
    e.preventDefault();
    setCurrentStep(2); // Move to background questionnaire
  };

  const handleSignupStep2 = async (e) => {
    e.preventDefault();
    setError('');
    const result = await signup({
      ...formData,
      softwareBackground: formData.softwareBackground,
      hardwareBackground: formData.hardwareBackground,
      languagesUsed: formData.languagesUsed,
      rosExperience: formData.rosExperience,
      nvidiaIsaacSimExperience: formData.nvidiaIsaacSimExperience,
      hardwarePlatforms: formData.hardwarePlatforms
    });
    if (!result.success) {
      setError(result.error);
    } else {
      setShowAuthModal(false);
      // Reset form and modal state
      setCurrentStep(1);
      setFormData({
        email: '',
        password: '',
        name: '',
        softwareBackground: 'beginner',
        hardwareBackground: 'none',
        languagesUsed: '',
        rosExperience: '',
        nvidiaIsaacSimExperience: '',
        hardwarePlatforms: ''
      });
    }
  };

  const toggleView = () => {
    setIsLoginView(!isLoginView);
    setCurrentStep(1); // Reset to first step when toggling
    setError('');
  };

  const closeModal = () => {
    setShowAuthModal(false);
    setCurrentStep(1); // Reset to first step when closing modal
    setFormData({
      email: '',
      password: '',
      name: '',
      softwareBackground: 'beginner',
      hardwareBackground: 'none',
      languagesUsed: '',
      rosExperience: '',
      nvidiaIsaacSimExperience: '',
      hardwarePlatforms: ''
    });
    setError('');
  };

  if (loading) {
    return <div className="auth-loading">Loading...</div>;
  }

  if (isAuthenticated && user) {
    return (
      <div className="auth-widget">
        <div className="dropdown dropdown--right dropdown--nocaret">
          <button className="navbar__link dropdown__trigger">
            {user.name || user.email}
          </button>
          <ul className="dropdown__menu">
            <li>
              <button
                className="dropdown__item"
                onClick={logout}
              >
                Sign Out
              </button>
            </li>
          </ul>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-widget">
      <div className="auth-buttons">
        <button
          className="button button--secondary button--sm auth-login-btn"
          onClick={() => {
            setIsLoginView(true);
            setCurrentStep(1);
            setShowAuthModal(true);
          }}
        >
          Login
        </button>
        <button
          className="button button--primary button--sm auth-signup-btn"
          onClick={() => {
            setIsLoginView(false);
            setCurrentStep(1);
            setShowAuthModal(true);
          }}
        >
          Sign Up
        </button>
      </div>

      {showAuthModal && (
        <div className="auth-modal">
          <div className="auth-modal-overlay" onClick={closeModal}></div>
          <div className="auth-modal-content">
            <div className="auth-modal-header">
              <h3>
                {isLoginView
                  ? 'Login'
                  : currentStep === 1
                    ? 'Create Account'
                    : 'Background Information'}
              </h3>
              <button
                className="auth-modal-close"
                onClick={closeModal}
              >
                ×
              </button>
            </div>

            {error && <div className="auth-error">{error}</div>}

            {isLoginView ? (
              // Login Form
              <form onSubmit={handleLogin}>
                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <button type="submit" className="button button--primary">
                  Login
                </button>
              </form>
            ) : currentStep === 1 ? (
              // Step 1: Account Details
              <form onSubmit={handleSignupStep1}>
                <div className="form-group">
                  <label htmlFor="name">Full Name</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="email">Email</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="password">Password</label>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="auth-step-navigation">
                  <button type="submit" className="button button--primary">
                    Next: Background Info
                  </button>
                </div>
              </form>
            ) : (
              // Step 2: Background Questionnaire
              <form onSubmit={handleSignupStep2}>
                <div className="form-group">
                  <label htmlFor="softwareBackground">Experience with Python</label>
                  <select
                    id="softwareBackground"
                    name="softwareBackground"
                    value={formData.softwareBackground}
                    onChange={handleInputChange}
                  >
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="rosExperience">Experience with ROS 2</label>
                  <select
                    id="rosExperience"
                    name="rosExperience"
                    value={formData.rosExperience}
                    onChange={handleInputChange}
                  >
                    <option value="no experience">No Experience</option>
                    <option value="ros1">ROS 1</option>
                    <option value="ros2">ROS 2</option>
                    <option value="ros2 + navigation">ROS 2 + Navigation</option>
                    <option value="ros2 + perception">ROS 2 + Perception</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="nvidiaIsaacSimExperience">Experience with NVIDIA Isaac Sim</label>
                  <select
                    id="nvidiaIsaacSimExperience"
                    name="nvidiaIsaacSimExperience"
                    value={formData.nvidiaIsaacSimExperience}
                    onChange={handleInputChange}
                  >
                    <option value="none">None</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </select>
                </div>

                <div className="form-group">
                  <label htmlFor="hardwarePlatforms">Hardware Platforms Experience (Jetson, Raspberry Pi, etc.)</label>
                  <input
                    type="text"
                    id="hardwarePlatforms"
                    name="hardwarePlatforms"
                    placeholder="e.g., Jetson, Raspberry Pi, Arduino, etc."
                    value={formData.hardwarePlatforms}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="form-group">
                  <label htmlFor="languagesUsed">Other Programming Languages Used</label>
                  <input
                    type="text"
                    id="languagesUsed"
                    name="languagesUsed"
                    placeholder="e.g., C++, JavaScript, etc."
                    value={formData.languagesUsed}
                    onChange={handleInputChange}
                  />
                </div>

                <div className="auth-step-navigation">
                  <button
                    type="button"
                    className="button button--secondary"
                    onClick={() => setCurrentStep(1)}
                  >
                    Back
                  </button>
                  <button type="submit" className="button button--primary">
                    Complete Registration
                  </button>
                </div>
              </form>
            )}

            {!isLoginView && currentStep === 1 && (
              <div className="auth-toggle">
                <button onClick={toggleView}>
                  Already have an account? Login
                </button>
              </div>
            )}

            {isLoginView && (
              <div className="auth-toggle">
                <button onClick={toggleView}>
                  Don't have an account? Sign up
                </button>
              </div>
            )}
          </div>

          <style jsx>{`
            .auth-widget {
              display: flex;
              align-items: center;
              gap: 0.5rem;
            }

            .auth-buttons {
              display: flex;
              gap: 0.5rem;
            }

            .auth-login-btn {
              margin-right: 0.25rem;
            }

            .auth-signup-btn {
              margin-left: 0.25rem;
            }

            .auth-modal {
              position: fixed;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              display: flex;
              align-items: center;
              justify-content: center;
              z-index: 1000;
            }

            .auth-modal-overlay {
              position: absolute;
              top: 0;
              left: 0;
              right: 0;
              bottom: 0;
              background-color: rgba(0, 0, 0, 0.5);
            }

            .auth-modal-content {
              position: relative;
              background: white;
              padding: 1.5rem;
              border-radius: 8px;
              box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
              width: 90%;
              max-width: 450px;
              z-index: 1001;
            }

            .auth-modal-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 1rem;
            }

            .auth-modal-close {
              background: none;
              border: none;
              font-size: 1.5rem;
              cursor: pointer;
            }

            .form-group {
              margin-bottom: 1rem;
            }

            .form-group label {
              display: block;
              margin-bottom: 0.25rem;
              font-weight: bold;
            }

            .form-group input,
            .form-group select {
              width: 100%;
              padding: 0.5rem;
              border: 1px solid #ccc;
              border-radius: 4px;
              box-sizing: border-box;
            }

            .auth-error {
              color: #e31e1e;
              margin-bottom: 1rem;
              padding: 0.5rem;
              background-color: #ffecec;
              border-radius: 4px;
            }

            .auth-toggle {
              margin-top: 1rem;
              text-align: center;
            }

            .auth-toggle button {
              background: none;
              border: none;
              color: #25c2a0;
              cursor: pointer;
              text-decoration: underline;
              font-size: 0.875rem;
            }

            .auth-step-navigation {
              display: flex;
              justify-content: space-between;
              margin-top: 1rem;
            }
          `}</style>
        </div>
      )}
    </div>
  );
};

export default AuthWidget;