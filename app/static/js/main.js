function go(id) {
  document.querySelectorAll('.page').forEach(p => p.classList.remove('on'));
  document.querySelectorAll('.menu a').forEach(a => a.classList.remove('on'));
  const page = document.getElementById(id);
  if (page) page.classList.add('on');
  const m = document.getElementById('m-' + id);
  if (m) m.classList.add('on');
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Student Portal Modal Functions
function openStudentModal() {
  const modal = document.getElementById('studentModal');
  if (modal) modal.classList.add('active');
}

function closeStudentModal() {
  const modal = document.getElementById('studentModal');
  if (modal) modal.classList.remove('active');
}

document.addEventListener('DOMContentLoaded', () => {
  // Catch the Student Area button click
  const studentBtn = document.querySelector('.nav-cta');
  if (studentBtn) {
    // Intercept onclick and open the modal instead
    studentBtn.removeAttribute('onclick');
    studentBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openStudentModal();
    });
  }

  // Handle Contact Form Submission
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const alertDiv = document.getElementById('form-alert');
      alertDiv.style.display = 'none';
      alertDiv.className = '';
      alertDiv.style.background = '';
      alertDiv.style.color = '';
      alertDiv.innerHTML = 'Enviando consulta...';
      alertDiv.style.display = 'block';

      const nombre = document.getElementById('nombre').value;
      const email = document.getElementById('email').value;
      const servicio = document.getElementById('servicio').value;
      const whatsapp = document.getElementById('whatsapp').value;
      const mensaje = document.getElementById('mensaje').value;

      try {
        const response = await fetch('/api/contacto', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ nombre, email, servicio, whatsapp, mensaje })
        });
        
        const result = await response.json();

        if (result.success) {
          alertDiv.style.background = '#e6f6f6';
          alertDiv.style.color = '#0b7a8a';
          alertDiv.style.border = '1px solid #0b7a8a';
          
          // Generate a WhatsApp prefilled text for direct contact
          const wsText = `Hola ASLYON_va SOLUCIONES, mi nombre es ${nombre}. Acabo de enviar una solicitud para el servicio de "${servicio}" sobre: ${mensaje}`;
          const encodedText = encodeURIComponent(wsText);
          const wsUrl = `https://wa.me/34641123456?text=${encodedText}`;

          alertDiv.innerHTML = `
            <div><strong>¡Enviado con éxito!</strong> ${result.message}</div>
            <div style="margin-top: 10px;">
              <a href="${wsUrl}" target="_blank" style="display: inline-block; background: #25d366; color: white; padding: 8px 15px; border-radius: 8px; text-decoration: none; font-weight: 700; margin-top: 5px;">
                💬 Chatear por WhatsApp Directo
              </a>
            </div>
          `;
          contactForm.reset();
        } else {
          alertDiv.style.background = '#fee2e2';
          alertDiv.style.color = '#991b1b';
          alertDiv.style.border = '1px solid #ef4444';
          alertDiv.innerHTML = `<strong>Error:</strong> ${result.message}`;
        }
      } catch (error) {
        alertDiv.style.background = '#fee2e2';
        alertDiv.style.color = '#991b1b';
        alertDiv.style.border = '1px solid #ef4444';
        alertDiv.innerHTML = '<strong>Error:</strong> No se pudo conectar con el servidor. Inténtalo más tarde.';
        console.error(error);
      }
    });
  }
});

// ── Student Portal Login ──────────────────────────────────────────────────────
async function handleStudentLogin(e) {
  e.preventDefault();
  const errDiv = document.getElementById('student-login-error');
  const btn    = document.getElementById('student-login-btn');
  errDiv.style.display = 'none';
  btn.disabled = true;
  btn.textContent = 'Verificando...';

  const email    = document.getElementById('student-email').value.trim();
  const password = document.getElementById('student-password').value.trim();

  try {
    const res  = await fetch('/api/estudiante/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();

    if (data.success) {
      btn.textContent = '✅ Acceso correcto...';
      window.location.href = data.redirect;
    } else {
      errDiv.textContent   = data.message;
      errDiv.style.display = 'block';
      btn.disabled    = false;
      btn.textContent = 'Iniciar Sesión';
    }
  } catch (err) {
    errDiv.textContent   = 'Error de conexión. Inténtalo de nuevo.';
    errDiv.style.display = 'block';
    btn.disabled    = false;
    btn.textContent = 'Iniciar Sesión';
  }
}

// ── Toggle Student Modal View (Login / Register) ──────────────────────────────
function toggleStudentModalView(view) {
  const loginView = document.getElementById('login-view');
  const registerView = document.getElementById('register-view');
  
  if (view === 'register') {
    loginView.style.display = 'none';
    registerView.style.display = 'block';
  } else {
    loginView.style.display = 'block';
    registerView.style.display = 'none';
  }
}

// ── Handle Student Registration ───────────────────────────────────────────────
async function handleStudentRegister(e) {
  e.preventDefault();
  const alertDiv = document.getElementById('student-register-alert');
  const btn = document.getElementById('student-register-btn');
  
  alertDiv.style.display = 'none';
  alertDiv.className = '';
  btn.disabled = true;
  btn.textContent = 'Procesando solicitud...';

  const name = document.getElementById('reg-name').value.trim();
  const email = document.getElementById('reg-email').value.trim();
  const password = document.getElementById('reg-password').value.trim();
  const whatsapp = document.getElementById('reg-whatsapp').value.trim();
  const service = document.getElementById('reg-service').value;

  try {
    const res = await fetch('/api/inscripcion/nueva', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password, whatsapp, service })
    });
    const data = await res.json();

    if (data.success) {
      alertDiv.style.background = '#e6f6f6';
      alertDiv.style.color = '#0b7a8a';
      alertDiv.style.border = '1px solid #0b7a8a';
      alertDiv.textContent = data.message;
      alertDiv.style.display = 'block';
      document.getElementById('studentRegisterForm').reset();
      
      // Auto switch back to login after 3 seconds
      setTimeout(() => {
        toggleStudentModalView('login');
        alertDiv.style.display = 'none';
        btn.disabled = false;
        btn.textContent = 'Solicitar Matrícula';
      }, 4000);
    } else {
      alertDiv.style.background = '#fee2e2';
      alertDiv.style.color = '#991b1b';
      alertDiv.style.border = '1px solid #ef4444';
      alertDiv.textContent = data.message;
      alertDiv.style.display = 'block';
      btn.disabled = false;
      btn.textContent = 'Solicitar Matrícula';
    }
  } catch (err) {
    alertDiv.style.background = '#fee2e2';
    alertDiv.style.color = '#991b1b';
    alertDiv.style.border = '1px solid #ef4444';
    alertDiv.textContent = 'Error de conexión. Inténtalo de nuevo.';
    alertDiv.style.display = 'block';
    btn.disabled = false;
    btn.textContent = 'Solicitar Matrícula';
  }
}

