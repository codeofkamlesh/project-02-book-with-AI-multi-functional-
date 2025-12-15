import React, { useState } from 'react';
import { API_ENDPOINTS } from '../../utils/apiConfig';

const PersonalizeButton = ({ docPath }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedMode, setSelectedMode] = useState('default');

  const handlePersonalize = async () => {
    if (!docPath) return;

    try {
      // In a real implementation, this would call the backend API
      const response = await fetch(API_ENDPOINTS.PERSONALIZE_RENDER, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          doc_path: docPath,
          profile: {}, // Would get user profile from auth context
          mode: selectedMode
        })
      });

      if (response.ok) {
        const data = await response.json();
        // In a real implementation, this would update the page content
        // with the personalized version
        console.log('Personalized content received:', data);
        alert(`Content personalized in ${selectedMode} mode`);
      } else {
        console.error('Failed to personalize content');
      }
    } catch (error) {
      console.error('Personalization error:', error);
    }
  };

  return (
    <div className="personalize-button-container">
      <button
        className="button button--secondary"
        onClick={() => setIsOpen(!isOpen)}
      >
        Personalize for Me
      </button>

      {isOpen && (
        <div className="personalize-modal">
          <div className="personalize-options">
            <h4>Select Personalization Mode</h4>

            <div className="option-group">
              <label>
                <input
                  type="radio"
                  name="mode"
                  value="simpler"
                  checked={selectedMode === 'simpler'}
                  onChange={(e) => setSelectedMode(e.target.value)}
                />
                <span>Simpler (for beginners)</span>
              </label>

              <label>
                <input
                  type="radio"
                  name="mode"
                  value="advanced"
                  checked={selectedMode === 'advanced'}
                  onChange={(e) => setSelectedMode(e.target.value)}
                />
                <span>Advanced (more technical)</span>
              </label>

              <label>
                <input
                  type="radio"
                  name="mode"
                  value="visual"
                  checked={selectedMode === 'visual'}
                  onChange={(e) => setSelectedMode(e.target.value)}
                />
                <span>Visual (more diagrams/examples)</span>
              </label>

              <label>
                <input
                  type="radio"
                  name="mode"
                  value="code-heavy"
                  checked={selectedMode === 'code-heavy'}
                  onChange={(e) => setSelectedMode(e.target.value)}
                />
                <span>Code Heavy (more examples)</span>
              </label>
            </div>

            <div className="modal-actions">
              <button
                className="button button--primary"
                onClick={handlePersonalize}
              >
                Apply Personalization
              </button>
              <button
                className="button button--secondary"
                onClick={() => setIsOpen(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .personalize-button-container {
          position: relative;
          display: inline-block;
          margin-bottom: 1rem;
        }

        .personalize-modal {
          position: absolute;
          top: 100%;
          left: 0;
          background: white;
          border: 1px solid #ccc;
          border-radius: 4px;
          box-shadow: 0 2px 10px rgba(0,0,0,0.1);
          z-index: 1000;
          padding: 1rem;
          min-width: 300px;
        }

        .personalize-options h4 {
          margin-top: 0;
          margin-bottom: 1rem;
        }

        .option-group label {
          display: block;
          margin-bottom: 0.5rem;
          cursor: pointer;
        }

        .option-group input[type="radio"] {
          margin-right: 0.5rem;
        }

        .modal-actions {
          margin-top: 1rem;
          display: flex;
          gap: 0.5rem;
        }
      `}</style>
    </div>
  );
};

export default PersonalizeButton;