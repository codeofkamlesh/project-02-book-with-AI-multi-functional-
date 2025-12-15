import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { API_ENDPOINTS } from '../../utils/apiConfig';

// Mock implementation - in a real implementation, this would integrate with Better-Auth
const SignupForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    softwareBackground: 'beginner',
    hardwareBackground: 'none',
    languagesUsed: '',
    rosExperience: ''
  });

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // In a real implementation, this would call the Better-Auth API
    // and then call the backend to store profile in Neon Postgres
    try {
      // Mock API call to store profile in Neon Postgres
      const profileData = {
        user_id: 'mock-user-id', // This would come from the auth system
        software_background: {
          level: formData.softwareBackground,
          languages: formData.languagesUsed.split(',').map(lang => lang.trim()).filter(lang => lang)
        },
        hardware_background: {
          experience: formData.hardwareBackground,
          platforms: formData.rosExperience ? [formData.rosExperience] : []
        },
        preferences: {}
      };

      // Call backend API to store profile using configured endpoint
      const response = await fetch(API_ENDPOINTS.AUTH_PROFILE, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
      });

      if (response.ok) {
        // Redirect to home or dashboard after successful signup
        navigate('/');
      } else {
        console.error('Failed to store profile');
      }
    } catch (error) {
      console.error('Signup error:', error);
    }
  };

  return (
    <div className="signup-form-container">
      <h2>Create Your Account</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name">Full Name</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleChange}
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
            onChange={handleChange}
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
            onChange={handleChange}
            required
          />
        </div>

        <div className="form-group">
          <label htmlFor="softwareBackground">Software Background</label>
          <select
            id="softwareBackground"
            name="softwareBackground"
            value={formData.softwareBackground}
            onChange={handleChange}
          >
            <option value="none">None</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="languagesUsed">Programming Languages Used</label>
          <input
            type="text"
            id="languagesUsed"
            name="languagesUsed"
            placeholder="e.g., Python, C++, JavaScript"
            value={formData.languagesUsed}
            onChange={handleChange}
          />
        </div>

        <div className="form-group">
          <label htmlFor="hardwareBackground">Hardware Background</label>
          <select
            id="hardwareBackground"
            name="hardwareBackground"
            value={formData.hardwareBackground}
            onChange={handleChange}
          >
            <option value="none">None</option>
            <option value="basic robotics">Basic Robotics</option>
            <option value="jetson/embedded">Jetson/Embedded</option>
            <option value="ros experience">ROS Experience</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="rosExperience">ROS Experience Level</label>
          <select
            id="rosExperience"
            name="rosExperience"
            value={formData.rosExperience}
            onChange={handleChange}
          >
            <option value="">Select your ROS experience</option>
            <option value="no experience">No Experience</option>
            <option value="ros1">ROS 1</option>
            <option value="ros2">ROS 2</option>
            <option value="ros2 + navigation">ROS 2 + Navigation</option>
            <option value="ros2 + perception">ROS 2 + Perception</option>
          </select>
        </div>

        <button type="submit" className="button button--primary">
          Sign Up
        </button>
      </form>
    </div>
  );
};

export default SignupForm;