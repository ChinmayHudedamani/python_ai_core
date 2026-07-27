/* ==========================================================================
   CHINMAY PORTFOLIO - INTERACTIVE JAVASCRIPT LOGIC
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initTypingEffect();
  initThemeToggle();
  initNavigation();
  initSkillsFilter();
  initProjectsFilter();
  initProjectModals();
  initTerminal();
  initContactForm();
  initParticleCanvas();
});

/* --------------------------------------------------------------------------
   1. Dynamic Typing Effect
   -------------------------------------------------------------------------- */
function initTypingEffect() {
  const typingElement = document.getElementById('typing-target');
  if (!typingElement) return;

  const roles = [
    'Python & AI Systems Developer',
    'Full-Stack Web Architect',
    'Data Pipeline & Cloud Specialist',
    'LLM & Agentic AI Specialist'
  ];

  let roleIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let typingSpeed = 100;

  function type() {
    const currentRole = roles[roleIndex];

    if (isDeleting) {
      typingElement.textContent = currentRole.substring(0, charIndex - 1);
      charIndex--;
      typingSpeed = 50;
    } else {
      typingElement.textContent = currentRole.substring(0, charIndex + 1);
      charIndex++;
      typingSpeed = 90;
    }

    if (!isDeleting && charIndex === currentRole.length) {
      typingSpeed = 2200; // Pause at full word
      isDeleting = true;
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      roleIndex = (roleIndex + 1) % roles.length;
      typingSpeed = 400;
    }

    setTimeout(type, typingSpeed);
  }

  type();
}

/* --------------------------------------------------------------------------
   2. Theme Toggle (Dark / Light Mode)
   -------------------------------------------------------------------------- */
function initThemeToggle() {
  const themeBtn = document.getElementById('theme-toggle');
  if (!themeBtn) return;

  const savedTheme = localStorage.getItem('chinmay_portfolio_theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light-theme');
    themeBtn.innerHTML = '🌙';
  }

  themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('light-theme');
    const isLight = document.body.classList.contains('light-theme');
    themeBtn.innerHTML = isLight ? '🌙' : '☀️';
    localStorage.setItem('chinmay_portfolio_theme', isLight ? 'light' : 'dark');
  });
}

/* --------------------------------------------------------------------------
   3. Navbar Mobile Toggle & Scroll Spy
   -------------------------------------------------------------------------- */
function initNavigation() {
  const mobileBtn = document.getElementById('mobile-menu-btn');
  const navLinks = document.getElementById('nav-links');
  const links = document.querySelectorAll('.nav-link');

  if (mobileBtn && navLinks) {
    mobileBtn.addEventListener('click', () => {
      navLinks.classList.toggle('active');
    });

    links.forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('active');
      });
    });
  }

  // Active section scroll spy
  const sections = document.querySelectorAll('section[id]');
  window.addEventListener('scroll', () => {
    const scrollY = window.pageYOffset;

    sections.forEach(current => {
      const sectionHeight = current.offsetHeight;
      const sectionTop = current.offsetTop - 100;
      const sectionId = current.getAttribute('id');
      const targetLink = document.querySelector(`.nav-links a[href*=${sectionId}]`);

      if (targetLink) {
        if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
          links.forEach(l => l.classList.remove('active'));
          targetLink.classList.add('active');
        }
      }
    });
  });
}

/* --------------------------------------------------------------------------
   4. Skills Category Filtering
   -------------------------------------------------------------------------- */
function initSkillsFilter() {
  const filterBtns = document.querySelectorAll('.skills-filter-container .filter-btn');
  const skillCards = document.querySelectorAll('.skill-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const filterCategory = btn.getAttribute('data-filter');

      skillCards.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        if (filterCategory === 'all' || cardCat === filterCategory) {
          card.style.display = 'block';
          card.style.animation = 'fadeIn 0.4s ease forwards';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

/* --------------------------------------------------------------------------
   5. Projects Filtering
   -------------------------------------------------------------------------- */
function initProjectsFilter() {
  const filterBtns = document.querySelectorAll('.projects-filter-container .filter-btn');
  const projectCards = document.querySelectorAll('.project-card');

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const category = btn.getAttribute('data-filter');

      projectCards.forEach(card => {
        const cardCat = card.getAttribute('data-category');
        if (category === 'all' || cardCat === category) {
          card.style.display = 'flex';
          card.style.animation = 'fadeIn 0.4s ease forwards';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });
}

/* --------------------------------------------------------------------------
   6. Interactive Project Modals
   -------------------------------------------------------------------------- */

const projectDetailsData = {
  'antigravity-core': {
    title: 'AntiGravity Python AI Core',
    category: 'AI & Multi-Agent Architecture',
    desc: 'An enterprise-grade python framework for agentic workflows, conversational memory, state management, and multi-agent coordination with automated database synchronization.',
    architecture: 'Python 3.12, FastAPI, SQLite / PostgreSQL, Asyncio, Pytest, Docker.',
    highlights: [
      'Implemented robust ledger writers and persistent conversation stores with transaction safety.',
      'Designed structured state recovery mechanisms for long-running workflows.',
      'Integrated real-time PDF financial report generation and automated WhatsApp messaging adapters.'
    ],
    github: 'https://github.com',
    demo: '#'
  },
  'doctor-assistant': {
    title: 'Clinical Doctor Assistant & Ledger Engine',
    category: 'Healthcare & Financial Intelligence',
    desc: 'A specialized clinical management tool featuring patient lead tracking, appointment ledgers, automated financial analytics, and PDF invoice generation for dental and general practices.',
    architecture: 'Python, Pandas, ReportLab, SQL Schema, Scheduled Crons, WhatsApp Cloud API.',
    highlights: [
      'Automated automated daily financial report generation dispatched directly to clinic administrators.',
      'Constructed ledger validation rules preventing invalid appointments and duplicate transactions.',
      'Handled over 700k+ patient records with sub-second query performance.'
    ],
    github: 'https://github.com',
    demo: '#'
  },
  'car-detailing-suite': {
    title: 'CarDetailing Enterprise Web App',
    category: 'Full-Stack Web Application',
    desc: 'A high-performance auto-detailing booking and customer workflow portal with dynamic interactive service customizers, scheduling calendars, and live status tracking.',
    architecture: 'JavaScript, CSS3 Design System, HTML5, REST APIs, Dynamic Canvas Renderer.',
    highlights: [
      'Interactive customizer with real-time price estimation based on vehicle size and coating packages.',
      'Fully responsive UI with sleek glassmorphism aesthetic and smooth micro-animations.',
      'Seamless backend booking API integration.'
    ],
    github: 'https://github.com',
    demo: '#'
  },
  'bigquery-etl-pipeline': {
    title: 'Automated Data Warehouse & Analytics Engine',
    category: 'Data Engineering & Cloud ETL',
    desc: 'A scalable Google Cloud BigQuery and Dataform ELT pipeline transforming raw event streams into clean, modeled analytics schemas with automated data quality checks.',
    architecture: 'Google Cloud BigQuery, Dataform, dbt, SQLX, Python, Cloud Composer / Airflow.',
    highlights: [
      'Built automated data cleaning models with strict schema validation and anomaly detection.',
      'Optimized query costs by 40% through partitioning, clustering, and materialized views.',
      'Provided continuous telemetry and automated error alerting.'
    ],
    github: 'https://github.com',
    demo: '#'
  }
};

function initProjectModals() {
  const modalOverlay = document.getElementById('project-modal');
  const closeBtn = document.getElementById('modal-close-btn');
  const modalTitle = document.getElementById('modal-title');
  const modalCategory = document.getElementById('modal-category');
  const modalDesc = document.getElementById('modal-desc');
  const modalArch = document.getElementById('modal-arch');
  const modalHighlights = document.getElementById('modal-highlights');
  const modalGithub = document.getElementById('modal-github');
  const modalDemo = document.getElementById('modal-demo');

  if (!modalOverlay) return;

  document.querySelectorAll('.open-project-modal').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const projectId = btn.getAttribute('data-project');
      const data = projectDetailsData[projectId];

      if (data) {
        modalTitle.textContent = data.title;
        modalCategory.textContent = data.category;
        modalDesc.textContent = data.desc;
        modalArch.textContent = data.architecture;

        modalHighlights.innerHTML = data.highlights
          .map(h => `<li style="margin-bottom: 0.5rem; color: var(--text-sub);">• ${h}</li>`)
          .join('');

        modalGithub.href = data.github;
        modalDemo.href = data.demo;

        modalOverlay.classList.add('active');
      }
    });
  });

  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      modalOverlay.classList.remove('active');
    });
  }

  modalOverlay.addEventListener('click', (e) => {
    if (e.target === modalOverlay) {
      modalOverlay.classList.remove('active');
    }
  });
}

/* --------------------------------------------------------------------------
   7. Interactive CLI Terminal Component
   -------------------------------------------------------------------------- */
function initTerminal() {
  const terminalBody = document.getElementById('terminal-body');
  const terminalInput = document.getElementById('terminal-input');
  if (!terminalInput || !terminalBody) return;

  const commands = {
    'help': 'Available commands:<br>• <span class="terminal-cmd">skills</span> - List primary engineering skills<br>• <span class="terminal-cmd">projects</span> - View featured project portfolio<br>• <span class="terminal-cmd">experience</span> - View career highlights & history<br>• <span class="terminal-cmd">whoami</span> - Display profile overview<br>• <span class="terminal-cmd">socials</span> - Display GitHub, LinkedIn, Email<br>• <span class="terminal-cmd">sudo hire</span> - Unlock direct contact action<br>• <span class="terminal-cmd">clear</span> - Clear terminal screen',
    'whoami': 'Chinmay | Python & AI Systems Developer<br>Specialized in agentic AI frameworks, clinical ledger software, scalable data pipelines, and modern web applications.',
    'skills': '<span style="color: var(--cyan);">[AI / ML]:</span> PyTorch, Agentic AI, OpenAI/Gemini APIs, BigQuery ML<br><span style="color: var(--indigo);">[Backend]:</span> Python, FastAPI, Flask, Asyncio, SQL, PostgreSQL, SQLite<br><span style="color: var(--purple);">[Frontend]:</span> HTML5, CSS3 Glassmorphism, Vanilla JS, React, Tailwind<br><span style="color: var(--emerald);">[Cloud & Data]:</span> Google Cloud (GCP), BigQuery, Dataform, Docker, Git',
    'projects': '1. AntiGravity AI Core (Multi-Agent Python Engine)<br>2. Clinical Doctor Assistant & Ledger System<br>3. CarDetailing Enterprise Web App<br>4. Cloud Analytics & BigQuery ELT Pipeline',
    'experience': '• Lead Developer - AntiGravity AI Systems (2024 - Present)<br>• Full-Stack & Clinical Systems Architect (2023 - 2024)<br>• Python Data Pipelines Engineer (2022 - 2023)',
    'socials': '• GitHub: <a href="https://github.com" target="_blank" style="color: var(--cyan);">github.com/chinmay</a><br>• LinkedIn: <a href="https://linkedin.com" target="_blank" style="color: var(--cyan);">linkedin.com/in/chinmay</a><br>• Email: <a href="mailto:chinmay@example.com" style="color: var(--cyan);">chinmay@example.com</a>',
    'sudo hire': '<span style="color: var(--emerald); font-weight: bold;">[ACCESS GRANTED]</span> Great choice! Scroll down to the Contact section or click <a href="#contact" style="color: var(--cyan);">here to drop a message directly</a>.'
  };

  terminalInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      const inputVal = terminalInput.value.trim().toLowerCase();
      executeCommand(inputVal);
      terminalInput.value = '';
    }
  });

  // Chip click handlers
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const cmd = btn.getAttribute('data-cmd');
      executeCommand(cmd);
    });
  });

  function executeCommand(cmd) {
    if (!cmd) return;

    if (cmd === 'clear') {
      terminalBody.innerHTML = '';
      return;
    }

    const line = document.createElement('div');
    line.className = 'terminal-line';
    line.innerHTML = `<span class="terminal-prompt">chinmay@antigravity</span>:<span class="terminal-path">~</span>$ <span class="terminal-cmd">${escapeHtml(cmd)}</span>`;
    terminalBody.appendChild(line);

    const output = document.createElement('div');
    output.className = 'terminal-output';

    if (commands[cmd]) {
      output.innerHTML = commands[cmd];
    } else if (cmd.startsWith('echo ')) {
      output.textContent = cmd.replace('echo ', '');
    } else {
      output.innerHTML = `<span style="color: #ef4444;">Command not found: "${escapeHtml(cmd)}". Type <span class="terminal-cmd" style="color: var(--cyan);">help</span> for available commands.</span>`;
    }

    terminalBody.appendChild(output);
    terminalBody.scrollTop = terminalBody.scrollHeight;
  }

  function escapeHtml(str) {
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }
}

/* --------------------------------------------------------------------------
   8. Contact Form Handling
   -------------------------------------------------------------------------- */
function initContactForm() {
  const form = document.getElementById('contact-form');
  const toast = document.getElementById('toast-notification');
  const toastMsg = document.getElementById('toast-message');

  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const name = document.getElementById('form-name').value.trim();
    const email = document.getElementById('form-email').value.trim();

    if (!name || !email) {
      showToast('Please fill in all required fields.', false);
      return;
    }

    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = 'Sending... 🚀';
    submitBtn.disabled = true;

    setTimeout(() => {
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;
      form.reset();
      showToast(`Thank you, ${name}! Your message has been sent successfully.`, true);
    }, 1200);
  });

  function showToast(message, isSuccess) {
    if (!toast) return;
    toastMsg.textContent = message;
    toast.style.borderColor = isSuccess ? 'var(--emerald)' : '#ef4444';
    toast.classList.add('show');

    setTimeout(() => {
      toast.classList.remove('show');
    }, 4000);
  }
}

/* --------------------------------------------------------------------------
   9. Ambient Particle Backdrop Canvas
   -------------------------------------------------------------------------- */
function initParticleCanvas() {
  const canvas = document.getElementById('particle-canvas');
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = (canvas.width = window.innerWidth);
  let height = (canvas.height = window.innerHeight);

  window.addEventListener('resize', () => {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  });

  const particles = [];
  const particleCount = Math.min(Math.floor(width / 25), 45);

  for (let i = 0; i < particleCount; i++) {
    particles.push({
      x: Math.random() * width,
      y: Math.random() * height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      radius: Math.random() * 2 + 1,
      alpha: Math.random() * 0.5 + 0.2
    });
  }

  function animate() {
    ctx.clearRect(0, 0, width, height);

    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0 || p.x > width) p.vx *= -1;
      if (p.y < 0 || p.y > height) p.vy *= -1;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(99, 102, 241, ${p.alpha})`;
      ctx.fill();

      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p.x - p2.x;
        const dy = p.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < 130) {
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(6, 182, 212, ${0.15 * (1 - dist / 130)})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(animate);
  }

  animate();
}
