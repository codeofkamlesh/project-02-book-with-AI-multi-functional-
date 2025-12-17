import React, { createContext, useContext, useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../utils/apiConfig';
import { getCurrentUser } from '../utils/authClient';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Check if user is logged in on component mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await fetch(API_ENDPOINTS.AUTH_ME, {
          method: 'GET',
          credentials: 'include', // Include cookies for session
        });

        if (response.ok) {
          const data = await response.json();
          if (data.user && data.user.id !== 'anonymous' && data.user.id !== 'unknown') {
            // User is authenticated
            setUser({
              ...data.user,
              profile: data.profile || {}
            });
          }
          // If user is not authenticated, user remains null
        }
      } catch (error) {
        console.error('Auth check failed:', error);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (email, password) => {
    try {
      // In a real implementation, this would call the Better-Auth login endpoint
      // For now, we'll simulate the login process with our backend
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
        credentials: 'include', // Include cookies for session
      });

      if (response.ok) {
        // Fetch user data after successful login
        const userData = await getCurrentUser();
        if (userData && userData.user && userData.user.id !== 'anonymous' && userData.user.id !== 'unknown') {
          // Fetch extended profile from our backend API
          const profileResponse = await fetch(API_ENDPOINTS.AUTH_ME, {
            method: 'GET',
            credentials: 'include', // Include cookies for session
          });

          if (profileResponse.ok) {
            const profileData = await profileResponse.json();
            setUser({
              ...userData.user,
              profile: profileData.profile || {}
            });
          } else {
            setUser(userData.user);
          }
        } else {
          // If /api/v1/auth/me doesn't return a valid user, create a mock user
          setUser({
            id: 'mock-user-id',
            email,
            name: email.split('@')[0], // Use part of email as name
            profile: {}
          });
        }
        return { success: true };
      } else {
        return { success: false, error: 'Invalid credentials' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: error.message || 'Login failed' };
    }
  };

  const signup = async (userData) => {
    try {
      // In a real implementation, this would call the Better-Auth register endpoint
      // For now, we'll simulate the registration process with our backend
      const authResponse = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userData.email,
          password: userData.password,
          name: userData.name,
        }),
        credentials: 'include', // Include cookies for session
      });

      if (authResponse.ok) {
        // After successful registration, save extended profile to our backend
        const profileResponse = await fetch(API_ENDPOINTS.AUTH_PROFILE, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            user_id: 'mock-user-id', // In a real implementation, this would come from the auth system
            software_background: {
              level: userData.softwareBackground,
              languages: userData.languagesUsed.split(',').map(lang => lang.trim()).filter(lang => lang),
              python_experience: userData.softwareBackground, // Added for specification
              ros2_experience: userData.rosExperience, // Added for specification
              nvidia_isaac_sim_experience: userData.nvidiaIsaacSimExperience // Added for specification
            },
            hardware_background: {
              experience: userData.hardwareBackground,
              platforms: userData.hardwarePlatforms ? userData.hardwarePlatforms.split(',').map(p => p.trim()).filter(p => p) : [], // Added for specification (Jetson, Raspberry Pi, etc.)
              jetson_experience: userData.hardwarePlatforms.toLowerCase().includes('jetson') ? true : false, // Added for specification
              raspberry_pi_experience: userData.hardwarePlatforms.toLowerCase().includes('raspberry') ? true : false // Added for specification
            },
            preferences: {}
          }),
          credentials: 'include', // Include cookies for session
        });

        if (profileResponse.ok) {
          // Fetch user data after successful signup and profile creation
          const finalUserData = await getCurrentUser();
          if (finalUserData && finalUserData.user && finalUserData.user.id !== 'anonymous' && finalUserData.user.id !== 'unknown') {
            const profileData = await profileResponse.json();
            setUser({
              ...finalUserData.user,
              profile: profileData || {}
            });
          } else {
            // If /api/v1/auth/me doesn't return a valid user, create a mock user
            setUser({
              id: 'mock-user-id',
              email: userData.email,
              name: userData.name,
              profile: await profileResponse.json()
            });
          }
          return { success: true };
        } else {
          // If profile save failed, try to logout the user
          await fetch('/api/auth/logout', {
            method: 'POST',
            credentials: 'include',
          });
          return { success: false, error: 'Failed to create profile' };
        }
      } else {
        const errorData = await authResponse.json();
        return { success: false, error: errorData.error || 'Registration failed' };
      }
    } catch (error) {
      console.error('Signup error:', error);
      return { success: false, error: error.message || 'Signup failed' };
    }
  };

  const logout = async () => {
    try {
      // In a real implementation, this would call the Better-Auth logout endpoint
      await fetch('/api/auth/logout', {
        method: 'POST',
        credentials: 'include', // Include cookies for session
      });
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};