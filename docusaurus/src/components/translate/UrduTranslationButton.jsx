import React, { useState, useEffect } from 'react';
import { API_ENDPOINTS } from '../../utils/apiConfig';

const UrduTranslationButton = ({ children, docPath }) => {
  const [isTranslated, setIsTranslated] = useState(false);
  const [translatedContent, setTranslatedContent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const translateToUrdu = async () => {
    if (!docPath) return;

    setIsLoading(true);

    try {
      // In a real implementation, this would call the backend API
      const response = await fetch(API_ENDPOINTS.TRANSLATE_URDU, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          doc_path: docPath,
          text: document.querySelector('.markdown')?.innerText || '' // Get page content to translate
        })
      });

      if (response.ok) {
        const data = await response.json();
        setTranslatedContent(data.translated_text);
        setIsTranslated(true);
      } else {
        console.error('Failed to translate content');
      }
    } catch (error) {
      console.error('Translation error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleTranslation = () => {
    if (isTranslated) {
      setIsTranslated(false);
    } else {
      translateToUrdu();
    }
  };

  const buttonText = isLoading
    ? 'Translating...'
    : isTranslated
      ? 'Show in English'
      : 'Translate to Urdu';

  return (
    <div className="urdu-translation-container">
      <button
        className="button button--secondary"
        onClick={toggleTranslation}
        disabled={isLoading}
      >
        {buttonText}
      </button>

      {isTranslated && translatedContent && (
        <div className="urdu-content" lang="ur" dir="rtl">
          {translatedContent}
        </div>
      )}

      {!isTranslated && children}

      <style jsx>{`
        .urdu-translation-container {
          margin: 1rem 0;
        }

        .urdu-content {
          margin: 1rem 0;
          padding: 1rem;
          background-color: #f8f9fa;
          border: 1px solid #dee2e6;
          border-radius: 0.375rem;
          direction: rtl;
          text-align: right;
        }

        [lang="ur"] {
          font-family: 'Noto Sans Arabic', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
      `}</style>
    </div>
  );
};

export default UrduTranslationButton;