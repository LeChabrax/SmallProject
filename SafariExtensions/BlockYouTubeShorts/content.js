// Redirect /shorts/ URLs via client-side navigation (catches SPA navigations
// that don't trigger a full page load and thus bypass declarativeNetRequest).
function checkAndRedirect() {
  const path = window.location.pathname;
  if (path.startsWith("/shorts/")) {
    const videoId = path.split("/shorts/")[1].split(/[?#]/)[0];
    if (videoId) {
      window.location.replace("https://www.youtube.com/watch?v=" + videoId);
    }
  }
}

// Run on initial load
checkAndRedirect();

// YouTube is an SPA -- watch for URL changes via History API
const originalPushState = history.pushState;
history.pushState = function () {
  originalPushState.apply(this, arguments);
  checkAndRedirect();
};

const originalReplaceState = history.replaceState;
history.replaceState = function () {
  originalReplaceState.apply(this, arguments);
  checkAndRedirect();
};

window.addEventListener("popstate", checkAndRedirect);

// Also observe the DOM for dynamically injected Shorts shelves that CSS
// selectors with :has() might not catch in all Safari versions.
const observer = new MutationObserver(() => {
  // Remove Shorts shelf elements
  document
    .querySelectorAll(
      'ytd-rich-shelf-renderer[is-shorts], ytd-reel-shelf-renderer'
    )
    .forEach((el) => el.remove());
});

observer.observe(document.documentElement, {
  childList: true,
  subtree: true,
});
