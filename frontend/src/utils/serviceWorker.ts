// Enhanced Service Worker registration for PWA features and Task 11.2
const isLocalhost = Boolean(
  window.location.hostname === 'localhost' ||
  window.location.hostname === '[::1]' ||
  window.location.hostname.match(
    /^127(?:\.(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)){3}$/
  )
);

type Config = {
  onSuccess?: (registration: ServiceWorkerRegistration) => void;
  onUpdate?: (registration: ServiceWorkerRegistration) => void;
  onOfflineReady?: () => void;
  onNeedRefresh?: () => void;
};

// PWA installation prompt
let deferredPrompt: any;

export function register(config?: Config) {
  // Skip service worker registration in development if disabled
  if (process.env.REACT_APP_DISABLE_SERVICE_WORKER === 'true') {
    console.log('Service worker disabled via environment variable');
    return;
  }
  
  if ('serviceWorker' in navigator) {
    const publicUrl = new URL(process.env.PUBLIC_URL!, window.location.href);
    if (publicUrl.origin !== window.location.origin) {
      return;
    }

    window.addEventListener('load', () => {
      const swUrl = `${process.env.PUBLIC_URL}/sw.js`;

      if (isLocalhost) {
        checkValidServiceWorker(swUrl, config);
        navigator.serviceWorker.ready.then(() => {
          console.log('This web app is being served cache-first by a service worker.');
          if (config?.onOfflineReady) {
            config.onOfflineReady();
          }
        });
      } else {
        registerValidSW(swUrl, config);
      }
    });

    // Setup PWA install prompt
    setupPWAInstallPrompt();
    
    // Setup update notifications
    setupUpdateNotifications(config);
  }
}

function registerValidSW(swUrl: string, config?: Config) {
  navigator.serviceWorker
    .register(swUrl)
    .then((registration) => {
      registration.onupdatefound = () => {
        const installingWorker = registration.installing;
        if (installingWorker == null) {
          return;
        }
        installingWorker.onstatechange = () => {
          if (installingWorker.state === 'installed') {
            if (navigator.serviceWorker.controller) {
              console.log('New content is available and will be used when all tabs are closed.');
              if (config && config.onUpdate) {
                config.onUpdate(registration);
              }
            } else {
              console.log('Content is cached for offline use.');
              if (config && config.onSuccess) {
                config.onSuccess(registration);
              }
            }
          }
        };
      };
    })
    .catch((error) => {
      console.error('Error during service worker registration:', error);
      // Don't throw the error, just log it to prevent app crashes
    });
}

function checkValidServiceWorker(swUrl: string, config?: Config) {
  fetch(swUrl, {
    headers: { 'Service-Worker': 'script' },
  })
    .then((response) => {
      const contentType = response.headers.get('content-type');
      if (
        response.status === 404 ||
        (contentType != null && contentType.indexOf('javascript') === -1)
      ) {
        navigator.serviceWorker.ready.then((registration) => {
          registration.unregister().then(() => {
            window.location.reload();
          });
        });
      } else {
        registerValidSW(swUrl, config);
      }
    })
    .catch(() => {
      console.log('No internet connection found. App is running in offline mode.');
    });
}

export function unregister() {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready
      .then((registration) => {
        registration.unregister();
      })
      .catch((error) => {
        console.error(error.message);
      });
  }
}

// Background sync for offline functionality
export function registerBackgroundSync() {
  if ('serviceWorker' in navigator && 'sync' in (window as any).ServiceWorkerRegistration.prototype) {
    navigator.serviceWorker.ready.then((registration) => {
      return (registration as any).sync.register('assessment-submission');
    }).catch((error) => {
      console.log('Background sync registration failed:', error);
    });
  }
}

// Store assessment data for offline sync
export function storeAssessmentForSync(assessmentData: any) {
  if ('indexedDB' in window) {
    const request = indexedDB.open('AutoMarkDB', 1);
    
    request.onupgradeneeded = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      if (!db.objectStoreNames.contains('assessments')) {
        db.createObjectStore('assessments');
      }
    };
    
    request.onsuccess = (event) => {
      const db = (event.target as IDBOpenDBRequest).result;
      const transaction = db.transaction(['assessments'], 'readwrite');
      const store = transaction.objectStore('assessments');
      store.put(assessmentData, 'pending');
    };
  }
}

// PWA installation prompt setup
function setupPWAInstallPrompt() {
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    
    // Show install button or banner
    const installButton = document.getElementById('pwa-install-button');
    if (installButton) {
      installButton.style.display = 'block';
      installButton.addEventListener('click', showInstallPrompt);
    }
  });

  window.addEventListener('appinstalled', () => {
    console.log('PWA was installed');
    deferredPrompt = null;
    
    // Hide install button
    const installButton = document.getElementById('pwa-install-button');
    if (installButton) {
      installButton.style.display = 'none';
    }
  });
}

// Show PWA install prompt
export function showInstallPrompt() {
  if (deferredPrompt) {
    deferredPrompt.prompt();
    
    deferredPrompt.userChoice.then((choiceResult: any) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      deferredPrompt = null;
    });
  }
}

// Setup update notifications
function setupUpdateNotifications(config?: Config) {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (config?.onNeedRefresh) {
        config.onNeedRefresh();
      } else {
        // Default behavior: show update notification
        showUpdateNotification();
      }
    });
  }
}

// Show update notification
function showUpdateNotification() {
  const notification = document.createElement('div');
  notification.id = 'update-notification';
  notification.innerHTML = `
    <div style="
      position: fixed;
      top: 20px;
      right: 20px;
      background: #2563eb;
      color: white;
      padding: 1rem;
      border-radius: 0.5rem;
      box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      z-index: 9999;
      max-width: 300px;
    ">
      <p style="margin: 0 0 0.5rem 0; font-weight: 600;">Update Available</p>
      <p style="margin: 0 0 1rem 0; font-size: 0.875rem;">A new version is available. Refresh to update.</p>
      <button id="refresh-button" style="
        background: white;
        color: #2563eb;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        cursor: pointer;
        font-weight: 600;
        margin-right: 0.5rem;
      ">Refresh</button>
      <button id="dismiss-button" style="
        background: transparent;
        color: white;
        border: 1px solid white;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        cursor: pointer;
      ">Later</button>
    </div>
  `;
  
  document.body.appendChild(notification);
  
  // Add event listeners
  document.getElementById('refresh-button')?.addEventListener('click', () => {
    window.location.reload();
  });
  
  document.getElementById('dismiss-button')?.addEventListener('click', () => {
    notification.remove();
  });
  
  // Auto-dismiss after 10 seconds
  setTimeout(() => {
    if (document.getElementById('update-notification')) {
      notification.remove();
    }
  }, 10000);
}

// Check if app is running as PWA
export function isPWA(): boolean {
  return window.matchMedia('(display-mode: standalone)').matches ||
         (window.navigator as any).standalone === true;
}

// Get PWA capabilities
export function getPWACapabilities() {
  return {
    serviceWorker: 'serviceWorker' in navigator,
    pushNotifications: 'PushManager' in window,
    backgroundSync: 'serviceWorker' in navigator && 'sync' in (window as any).ServiceWorkerRegistration.prototype,
    webShare: 'share' in navigator,
    installPrompt: deferredPrompt !== null,
    isInstalled: isPWA()
  };
}