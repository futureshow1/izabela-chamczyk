/* Simple password gate for private preview */
(function() {
  var HASH = '2925f53ed61a17d7cdf5166efbe94870aa51cd00f12b8ef58df43e9423feee4b';
  var KEY = 'chamczyk_auth';

  function sha256(str) {
    var buf = new TextEncoder().encode(str);
    return crypto.subtle.digest('SHA-256', buf).then(function(h) {
      return Array.from(new Uint8Array(h)).map(function(b) {
        return b.toString(16).padStart(2, '0');
      }).join('');
    });
  }

  function showGate() {
    document.documentElement.style.overflow = 'hidden';
    var overlay = document.createElement('div');
    overlay.id = 'auth-gate';
    overlay.innerHTML =
      '<div style="position:fixed;inset:0;background:#111;z-index:99999;display:flex;align-items:center;justify-content:center;font-family:Helvetica,Arial,sans-serif">' +
        '<div style="text-align:center;color:#ccc;max-width:340px;padding:20px">' +
          '<h1 style="font-size:20px;font-weight:300;letter-spacing:3px;margin-bottom:30px;color:#fff">IZABELA CHAMCZYK</h1>' +
          '<p style="font-size:13px;margin-bottom:20px;color:#888">Ta strona jest chroniona haslem.<br>This site is password protected.</p>' +
          '<input id="auth-pw" type="password" placeholder="Haslo / Password" ' +
            'style="width:100%;padding:12px 16px;font-size:15px;background:#222;border:1px solid #444;color:#fff;text-align:center;outline:none;box-sizing:border-box;margin-bottom:12px" />' +
          '<button id="auth-btn" ' +
            'style="width:100%;padding:10px;font-size:14px;background:#333;color:#fff;border:1px solid #555;cursor:pointer;letter-spacing:1px">WEJDZ / ENTER</button>' +
          '<p id="auth-err" style="color:#c44;font-size:12px;margin-top:12px;display:none">Nieprawidlowe haslo / Wrong password</p>' +
        '</div>' +
      '</div>';
    document.body.appendChild(overlay);

    var inp = document.getElementById('auth-pw');
    var btn = document.getElementById('auth-btn');
    var err = document.getElementById('auth-err');

    function tryAuth() {
      sha256(inp.value).then(function(h) {
        if (h === HASH) {
          sessionStorage.setItem(KEY, '1');
          overlay.remove();
          document.documentElement.style.overflow = '';
        } else {
          err.style.display = 'block';
          inp.value = '';
          inp.focus();
        }
      });
    }

    btn.addEventListener('click', tryAuth);
    inp.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') tryAuth();
    });
    inp.focus();
  }

  if (sessionStorage.getItem(KEY) === '1') return;
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', showGate);
  } else {
    showGate();
  }
})();
