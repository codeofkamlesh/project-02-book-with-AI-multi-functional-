import React from 'react';
import ChatWidget from '../components/rag/ChatWidget';
import UrduTranslator from '../components/UrduTranslator';
import { AuthProvider } from '../contexts/AuthContext';

// Root component that wraps the entire Docusaurus application
// This ensures the Auth context is available on every page
export default function Root({ children }) {
  return (
    <AuthProvider>
      <UrduTranslator>
        {children}
        <ChatWidget />
      </UrduTranslator>
    </AuthProvider>
  );
}