import React from 'react';
import { useLocation } from '@docusaurus/router';
import OriginalLayout from '@theme-original/DocItem/Layout';
import PersonalizeButton from '@site/src/components/personalize/PersonalizeButton';

// Custom DocItem layout to inject PersonalizeButton at the top of chapter pages
export default function DocItemLayout(props) {
  const location = useLocation();

  // Only show buttons on docs pages, not on homepage or other pages
  const isDocsPage = location.pathname.startsWith('/docs/');

  return (
    <OriginalLayout {...props}>
      {isDocsPage && (
        <div className="controls-section">
          <div className="controls-bar">
            <PersonalizeButton docPath={location.pathname} />
          </div>
        </div>
      )}
      {props.children}
    </OriginalLayout>
  );
}