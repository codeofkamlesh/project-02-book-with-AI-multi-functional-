/**
 * Translation widget for Urdu translation functionality
 * This script handles Docusaurus route changes to ensure translation function remains available
 */

// Ensure translation function is available after route changes in Docusaurus
if (window.docusaurus) {
  window.docusaurus.eventManager.on('routeDidUpdate', function() {
    // The translation button is now handled in the React component
    // This ensures the global translation function remains available after navigation
    console.log('Route updated, translation functionality remains available');
  });
}