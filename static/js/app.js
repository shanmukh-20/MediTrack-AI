/**
 * MediTrack AI — Main JavaScript
 * Vanilla JS + Bootstrap 5 — no jQuery
 * ============================================================
 */

'use strict';

/* ============================================================
   1. MEDICINE SEARCH & FILTER (Medicines List page)
   ============================================================ */
(function initMedicineSearch() {
  const searchInput = document.getElementById('searchInput');
  const formFilter  = document.getElementById('formFilter');
  const statusFilter= document.getElementById('statusFilter');
  const tableBody   = document.getElementById('medicineTableBody');

  if (!tableBody) return;

  function filterRows() {
    const q      = (searchInput  ? searchInput.value.toLowerCase()  : '');
    const form   = (formFilter   ? formFilter.value.toLowerCase()   : '');
    const status = (statusFilter ? statusFilter.value.toLowerCase() : '');

    const rows = tableBody.querySelectorAll('tr[data-name]');
    let visible = 0;

    rows.forEach(row => {
      const name    = (row.dataset.name    || '').toLowerCase();
      const generic = (row.dataset.generic || '').toLowerCase();
      const rowForm = (row.dataset.form    || '').toLowerCase();
      const rowStat = (row.dataset.status  || '').toLowerCase();

      const matchQ      = !q      || name.includes(q) || generic.includes(q);
      const matchForm   = !form   || rowForm === form;
      const matchStatus = !status || rowStat === status;

      const show = matchQ && matchForm && matchStatus;
      row.style.display = show ? '' : 'none';
      if (show) visible++;
    });

    // show/hide empty-state row if present
    const emptyRow = tableBody.querySelector('.empty-row');
    if (emptyRow) emptyRow.style.display = visible === 0 ? '' : 'none';
  }

  if (searchInput)   searchInput.addEventListener('input', filterRows);
  if (formFilter)    formFilter.addEventListener('change', filterRows);
  if (statusFilter)  statusFilter.addEventListener('change', filterRows);
})();


/* ============================================================
   2. REMINDERS — MARK DOSE TAKEN / MISSED
   ============================================================ */
(function initMarkDose() {
  if (!document.querySelector('.mark-taken-btn, .mark-missed-btn')) return;

  document.addEventListener('click', async function(e) {
    const btn = e.target.closest('.mark-taken-btn, .mark-missed-btn');
    if (!btn) return;

    const status       = btn.classList.contains('mark-taken-btn') ? 'taken' : 'missed';
    const medicineId   = btn.dataset.medicineId;
    const scheduledTime= btn.dataset.scheduledTime;
    const logDate      = btn.dataset.logDate;
    const row          = btn.closest('.dose-row') || btn.closest('tr');

    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';

    try {
      const res = await fetch('/reminders/mark', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ medicine_id: medicineId, scheduled_time: scheduledTime, log_date: logDate, status })
      });

      const data = await res.json();

      if (res.ok && data.success) {
        // Update badge
        const badge = row ? row.querySelector('.dose-status-badge') : null;
        if (badge) {
          badge.className = 'badge ' + (status === 'taken' ? 'badge-success' : 'badge-danger');
          badge.textContent = status === 'taken' ? 'Taken' : 'Missed';
        }

        // Disable sibling action buttons
        if (row) {
          row.querySelectorAll('.mark-taken-btn, .mark-missed-btn').forEach(b => {
            b.disabled = true;
            b.style.opacity = '0.5';
          });
        }

        showToast(status === 'taken' ? 'Dose marked as taken ✓' : 'Dose marked as missed', status === 'taken' ? 'success' : 'error');
      } else {
        showToast(data.message || 'Could not update dose status', 'error');
        btn.disabled = false;
        btn.innerHTML = status === 'taken' ? '✓ Taken' : '✗ Missed';
      }
    } catch (err) {
      console.error('Mark dose error:', err);
      showToast('Network error — please try again', 'error');
      btn.disabled = false;
      btn.innerHTML = status === 'taken' ? '✓ Taken' : '✗ Missed';
    }
  });
})();


/* ============================================================
   3. ANALYTICS CHARTS
   ============================================================ */
(function initAnalyticsCharts() {
  if (!document.getElementById('dosesLineChart') &&
      !document.getElementById('formDoughnut')) return;

  // Chart.js global defaults
  if (window.Chart) {
    Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    Chart.defaults.font.size   = 13;
    Chart.defaults.color       = '#64748B';
    Chart.defaults.plugins.legend.labels.boxWidth = 12;
    Chart.defaults.plugins.legend.labels.padding  = 16;
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(30,41,59,.92)';
    Chart.defaults.plugins.tooltip.titleColor      = '#F1F5F9';
    Chart.defaults.plugins.tooltip.bodyColor       = '#CBD5E1';
    Chart.defaults.plugins.tooltip.padding         = 10;
    Chart.defaults.plugins.tooltip.cornerRadius    = 6;
  }

  async function loadCharts() {
    let data;
    try {
      const res = await fetch('/analytics/data');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      data = await res.json();
    } catch (err) {
      console.error('Analytics data fetch failed:', err);
      return;
    }

    // 3a. Doses Line Chart (taken + missed per day)
    const lineEl = document.getElementById('dosesLineChart');
    if (lineEl && data.doses_per_day) {
      const labels = data.doses_per_day.map(d => d.date);
      new Chart(lineEl, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: 'Taken',
              data: data.doses_per_day.map(d => d.taken),
              borderColor: '#2563EB',
              backgroundColor: 'rgba(37,99,235,.1)',
              fill: true,
              tension: 0.35,
              pointRadius: 3,
              pointHoverRadius: 5
            },
            {
              label: 'Missed',
              data: data.doses_per_day.map(d => d.missed),
              borderColor: '#EF4444',
              backgroundColor: 'rgba(239,68,68,.08)',
              fill: true,
              tension: 0.35,
              pointRadius: 3,
              pointHoverRadius: 5
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: { legend: { position: 'top' } },
          scales: {
            x: { grid: { color: '#F1F5F9' }, ticks: { maxRotation: 45 } },
            y: { grid: { color: '#F1F5F9' }, beginAtZero: true, ticks: { stepSize: 1 } }
          }
        }
      });
    }

    // 3b. Form Doughnut Chart
    const doughEl = document.getElementById('formDoughnut');
    if (doughEl && data.medicine_by_form) {
      const palette = ['#2563EB','#10B981','#F59E0B','#EF4444','#8B5CF6','#06B6D4','#D97706'];
      new Chart(doughEl, {
        type: 'doughnut',
        data: {
          labels: data.medicine_by_form.map(f => f.form),
          datasets: [{
            data: data.medicine_by_form.map(f => f.count),
            backgroundColor: palette.slice(0, data.medicine_by_form.length),
            borderWidth: 2,
            borderColor: '#fff',
            hoverOffset: 6
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: '62%',
          plugins: {
            legend: { position: 'right' },
            tooltip: { callbacks: { label: ctx => ` ${ctx.label}: ${ctx.parsed}` } }
          },
          scales: { x: { display: false }, y: { display: false } }
        }
      });
    }

    // 3c. Adherence Bar (horizontal, per medicine)
    const adherEl = document.getElementById('adherenceBar');
    if (adherEl && data.adherence_rate) {
      new Chart(adherEl, {
        type: 'bar',
        data: {
          labels: data.adherence_rate.map(m => m.name),
          datasets: [{
            label: 'Adherence %',
            data: data.adherence_rate.map(m => m.rate),
            backgroundColor: data.adherence_rate.map(m =>
              m.rate >= 80 ? 'rgba(16,185,129,.75)' :
              m.rate >= 50 ? 'rgba(245,158,11,.75)' :
                             'rgba(239,68,68,.75)'),
            borderRadius: 4
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            x: { grid: { color: '#F1F5F9' }, min: 0, max: 100,
                 ticks: { callback: v => v + '%' } },
            y: { grid: { display: false } }
          }
        }
      });
    }

    // 3d. Taken vs Missed Grouped Bar
    const tmEl = document.getElementById('takenMissedBar');
    if (tmEl && data.taken_vs_missed) {
      new Chart(tmEl, {
        type: 'bar',
        data: {
          labels: data.taken_vs_missed.map(d => d.date),
          datasets: [
            {
              label: 'Taken',
              data: data.taken_vs_missed.map(d => d.taken),
              backgroundColor: 'rgba(37,99,235,.72)',
              borderRadius: 3
            },
            {
              label: 'Missed',
              data: data.taken_vs_missed.map(d => d.missed),
              backgroundColor: 'rgba(239,68,68,.72)',
              borderRadius: 3
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          interaction: { mode: 'index', intersect: false },
          plugins: { legend: { position: 'top' } },
          scales: {
            x: { grid: { display: false }, stacked: false },
            y: { grid: { color: '#F1F5F9' }, beginAtZero: true, ticks: { stepSize: 1 } }
          }
        }
      });
    }
  }

  loadCharts();
})();


/* ============================================================
   4. SAFETY CHECKER
   ============================================================ */
(function initSafetyChecker() {
  const form       = document.getElementById('safetyForm');
  const resultDiv  = document.getElementById('safetyResult');
  if (!form) return;

  // Autocomplete helper
  let medicineCatalog = null;

  async function getMedicines() {
    if (medicineCatalog) return medicineCatalog;
    try {
      const res = await fetch('/api/medicines');
      medicineCatalog = await res.json();
    } catch { medicineCatalog = []; }
    return medicineCatalog;
  }

  function buildAutocomplete(input) {
    const wrapper = input.parentElement;
    wrapper.style.position = 'relative';

    let list = null;
    let activeIdx = -1;

    function closeList() {
      if (list) { list.remove(); list = null; activeIdx = -1; }
    }

    input.addEventListener('input', async function() {
      closeList();
      const q = this.value.trim().toLowerCase();
      if (q.length < 1) return;

      const meds = await getMedicines();
      const matches = meds.filter(m =>
        m.name.toLowerCase().includes(q) ||
        (m.generic_name || '').toLowerCase().includes(q)
      ).slice(0, 8);

      if (!matches.length) return;

      list = document.createElement('div');
      list.className = 'autocomplete-list';

      matches.forEach((m, i) => {
        const item = document.createElement('div');
        item.className = 'autocomplete-item';
        item.textContent = m.name + (m.generic_name ? ` (${m.generic_name})` : '');
        item.addEventListener('mousedown', e => {
          e.preventDefault();
          input.value = m.name;
          closeList();
        });
        list.appendChild(item);
      });

      wrapper.appendChild(list);
    });

    input.addEventListener('keydown', function(e) {
      if (!list) return;
      const items = list.querySelectorAll('.autocomplete-item');
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        activeIdx = Math.min(activeIdx + 1, items.length - 1);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        activeIdx = Math.max(activeIdx - 1, -1);
      } else if (e.key === 'Enter' && activeIdx >= 0) {
        e.preventDefault();
        input.value = items[activeIdx].textContent.split(' (')[0];
        closeList();
        return;
      } else if (e.key === 'Escape') {
        closeList(); return;
      }
      items.forEach((it, i) => it.classList.toggle('active', i === activeIdx));
    });

    document.addEventListener('click', e => {
      if (!wrapper.contains(e.target)) closeList();
    });
  }

  // Attach autocomplete to both drug inputs
  document.querySelectorAll('.drug-input').forEach(buildAutocomplete);

  // Form submission
  form.addEventListener('submit', async function(e) {
    e.preventDefault();

    const drug1 = (form.querySelector('#drug1') || form.querySelector('[name="drug1"]'));
    const drug2 = (form.querySelector('#drug2') || form.querySelector('[name="drug2"]'));

    if (!drug1 || !drug2 || !drug1.value.trim() || !drug2.value.trim()) {
      showToast('Please enter both drug names', 'warning');
      return;
    }

    const submitBtn = form.querySelector('[type="submit"]');
    const origText  = submitBtn ? submitBtn.innerHTML : '';
    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Checking…';
    }

    if (resultDiv) resultDiv.innerHTML = '';

    try {
      const res  = await fetch('/safety/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ drug1: drug1.value.trim(), drug2: drug2.value.trim() })
      });
      const data = await res.json();

      if (data.interaction) {
        const severityClass =
          data.severity === 'high'   ? 'danger'  :
          data.severity === 'medium' ? 'warning' : 'warning';

        resultDiv.innerHTML = `
          <div class="safety-result ${severityClass}">
            <p class="result-title">
              ⚠ Interaction Detected
              <span class="severity-badge severity-${data.severity || 'medium'}">
                ${(data.severity || 'moderate').toUpperCase()}
              </span>
            </p>
            <p class="result-msg">${escapeHtml(data.message)}</p>
          </div>`;
      } else {
        resultDiv.innerHTML = `
          <div class="safety-result safe">
            <p class="result-title">✓ No Known Interaction</p>
            <p class="result-msg">${escapeHtml(data.message || 'No significant interaction found between these medications. Always consult your healthcare provider.')}</p>
          </div>`;
      }
    } catch (err) {
      console.error('Safety check error:', err);
      resultDiv.innerHTML = `
        <div class="safety-result danger">
          <p class="result-title">Error</p>
          <p class="result-msg">Could not complete the check. Please try again.</p>
        </div>`;
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.innerHTML = origText;
      }
    }
  });
})();


/* ============================================================
   5. TOAST NOTIFICATIONS
   ============================================================ */
function showToast(message, type) {
  type = type || 'info';

  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    document.body.appendChild(container);
  }

  const colorMap = {
    success: { icon: '✓', cls: 'toast-success', hdr: 'Success' },
    error:   { icon: '✕', cls: 'toast-error',   hdr: 'Error'   },
    warning: { icon: '⚠', cls: 'toast-warning', hdr: 'Warning' },
    info:    { icon: 'ℹ', cls: 'toast-info',    hdr: 'Info'    }
  };
  const cfg = colorMap[type] || colorMap.info;

  const toastEl = document.createElement('div');
  toastEl.className = `toast align-items-center ${cfg.cls} show`;
  toastEl.role = 'alert';
  toastEl.setAttribute('aria-live', 'assertive');
  toastEl.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        <span class="me-2">${cfg.icon}</span>${escapeHtml(message)}
      </div>
      <button type="button" class="btn-close me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>`;

  container.appendChild(toastEl);

  // Bootstrap Toast API
  if (window.bootstrap && bootstrap.Toast) {
    const bsToast = new bootstrap.Toast(toastEl, { delay: 3000, autohide: true });
    bsToast.show();
    toastEl.addEventListener('hidden.bs.toast', () => toastEl.remove());
  } else {
    // Fallback auto-dismiss
    setTimeout(() => {
      toastEl.classList.remove('show');
      setTimeout(() => toastEl.remove(), 300);
    }, 3000);
  }

  // Manual close button
  toastEl.querySelector('.btn-close').addEventListener('click', () => toastEl.remove());
}


/* ============================================================
   6. DELETE CONFIRMATION MODAL
   ============================================================ */
(function initDeleteConfirmation() {
  const modal = document.getElementById('deleteModal');
  if (!modal) return;

  let pendingForm = null;

  document.addEventListener('click', function(e) {
    const btn = e.target.closest('[data-delete-id]');
    if (!btn) return;

    e.preventDefault();

    const medId   = btn.dataset.deleteId;
    const medName = btn.dataset.deleteName || 'this medicine';

    // Set medicine name in modal
    const nameEl = modal.querySelector('#deleteModalMedName');
    if (nameEl) nameEl.textContent = medName;

    // Store the form/action
    const targetForm = document.getElementById(`deleteForm-${medId}`);
    pendingForm = targetForm || null;

    // If using a hidden <form>, point confirmBtn to it
    const confirmBtn = modal.querySelector('#confirmDeleteBtn');
    if (confirmBtn && pendingForm) {
      confirmBtn.onclick = () => {
        confirmBtn.disabled = true;
        confirmBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Deleting…';
        pendingForm.submit();
      };
    } else if (confirmBtn && medId) {
      // Fallback: construct a form and submit
      confirmBtn.onclick = () => {
        confirmBtn.disabled = true;
        const f = document.createElement('form');
        f.method = 'POST';
        f.action = `/medicines/${medId}/delete`;
        document.body.appendChild(f);
        f.submit();
      };
    }

    const bsModal = bootstrap.Modal.getOrCreateInstance(modal);
    bsModal.show();
  });
})();


/* ============================================================
   7. DASHBOARD REFRESH (every 60 seconds)
   ============================================================ */
(function initDashboardRefresh() {
  const statCards = document.querySelectorAll('[data-stat-key]');
  if (!statCards.length) return;

  async function refreshStats() {
    try {
      const res  = await fetch('/api/dashboard-stats');
      if (!res.ok) return;
      const data = await res.json();

      statCards.forEach(card => {
        const key = card.dataset.statKey;
        if (data[key] !== undefined) {
          const numEl = card.querySelector('.stat-number');
          if (numEl) {
            numEl.textContent = data[key];
            // Brief flash to indicate update
            numEl.style.transition = 'opacity 0.2s';
            numEl.style.opacity = '0.5';
            setTimeout(() => { numEl.style.opacity = '1'; }, 200);
          }
        }
      });
    } catch (err) {
      console.warn('Dashboard refresh failed:', err);
    }
  }

  setInterval(refreshStats, 60_000);
})();


/* ============================================================
   8. FORM VALIDATION (Add / Edit Medicine)
   ============================================================ */
(function initFormValidation() {
  const medicineForm = document.getElementById('medicineForm');
  if (!medicineForm) return;

  function showError(input, msg) {
    input.classList.add('is-invalid');
    let fb = input.nextElementSibling;
    if (!fb || !fb.classList.contains('invalid-feedback')) {
      fb = document.createElement('div');
      fb.className = 'invalid-feedback';
      input.parentNode.insertBefore(fb, input.nextSibling);
    }
    fb.textContent = msg;
  }

  function clearError(input) {
    input.classList.remove('is-invalid');
    const fb = input.nextElementSibling;
    if (fb && fb.classList.contains('invalid-feedback')) fb.textContent = '';
  }

  function validateForm() {
    let valid = true;
    const today = new Date(); today.setHours(0,0,0,0);

    // Name — required
    const nameInput = medicineForm.querySelector('#name, [name="name"]');
    if (nameInput) {
      clearError(nameInput);
      if (!nameInput.value.trim()) {
        showError(nameInput, 'Medicine name is required.');
        valid = false;
      }
    }

    // Expiry date — must be in the future (or empty)
    const expiryInput = medicineForm.querySelector('#expiry_date, [name="expiry_date"]');
    if (expiryInput && expiryInput.value) {
      clearError(expiryInput);
      const expDate = new Date(expiryInput.value);
      expDate.setHours(0,0,0,0);
      if (isNaN(expDate.getTime())) {
        showError(expiryInput, 'Please enter a valid date.');
        valid = false;
      } else if (expDate <= today) {
        showError(expiryInput, 'Expiry date must be in the future.');
        valid = false;
      }
    }

    // Quantity — must be >= 0
    const qtyInput = medicineForm.querySelector('#quantity, [name="quantity"]');
    if (qtyInput && qtyInput.value !== '') {
      clearError(qtyInput);
      const qty = parseFloat(qtyInput.value);
      if (isNaN(qty) || qty < 0) {
        showError(qtyInput, 'Quantity must be 0 or greater.');
        valid = false;
      }
    }

    return valid;
  }

  // Clear error on input
  medicineForm.addEventListener('input', function(e) {
    if (e.target.classList.contains('is-invalid')) clearError(e.target);
  });

  medicineForm.addEventListener('submit', function(e) {
    if (!validateForm()) {
      e.preventDefault();
      e.stopPropagation();
      // Scroll to first error
      const firstErr = medicineForm.querySelector('.is-invalid');
      if (firstErr) firstErr.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  });
})();


/* ============================================================
   UTILITY — HTML Escape
   ============================================================ */
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}


/* ============================================================
   UTILITY — Active nav link highlighting
   ============================================================ */
(function highlightActiveNav() {
  const path = window.location.pathname;
  document.querySelectorAll('.navbar-nav .nav-link').forEach(link => {
    const href = link.getAttribute('href');
    if (!href) return;
    // Exact match for /, prefix match for others
    const isActive = href === '/' ? path === '/' : path.startsWith(href);
    if (isActive) link.classList.add('active');
  });
})();


/* ============================================================
   UTILITY — Flash message auto-dismiss
   ============================================================ */
(function autoHideAlerts() {
  document.querySelectorAll('.alert-auto-dismiss').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });
})();
