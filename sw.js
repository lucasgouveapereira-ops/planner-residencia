const CACHE_NAME = 'planner-residencia-v7';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './assets/icon-192.png',
  './assets/icon-512.png',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap'
];

// Install — cache all assets
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(ASSETS).catch(err => {
        console.warn('Some assets failed to cache:', err);
        // Still install even if some assets fail (e.g. fonts)
        return cache.addAll(['./index.html', './manifest.json']);
      });
    })
  );
  self.skipWaiting();
});

// Activate — clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch — Network First para HTML, Cache First para assets estáticos
self.addEventListener('fetch', event => {
  const url = new URL(event.request.url);
  
  // Para navegação (HTML pages) e o próprio index.html: Network First
  // Isso garante que o código mais recente sempre seja carregado
  if (event.request.mode === 'navigate' || 
      url.pathname.endsWith('.html') || 
      url.pathname.endsWith('/')) {
    event.respondWith(
      fetch(event.request).then(response => {
        // Atualiza o cache com a versão mais recente da rede
        if (response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // Offline: usa a versão do cache como fallback
        return caches.match(event.request).then(cached => {
          return cached || caches.match('./index.html');
        });
      })
    );
    return;
  }
  
  // Para Firebase APIs: sempre usar a rede (nunca cachear)
  if (url.hostname.includes('firestore.googleapis.com') || 
      url.hostname.includes('identitytoolkit.googleapis.com') || 
      url.hostname.includes('securetoken.googleapis.com') ||
      url.hostname.includes('firebase')) {
    event.respondWith(fetch(event.request));
    return;
  }
  
  // Para assets estáticos (imagens, fontes, CSS, JS): Cache First
  event.respondWith(
    caches.match(event.request).then(cached => {
      if (cached) return cached;
      return fetch(event.request).then(response => {
        if (response.ok && event.request.method === 'GET') {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        }
        return response;
      }).catch(() => {
        // Offline fallback para documentos
        if (event.request.destination === 'document') {
          return caches.match('./index.html');
        }
      });
    })
  );
});
