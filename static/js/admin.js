/* ==========================================================
   HGS SOLAR CRM — admin.js
   Sidebar toggle | Counter animation | Status AJAX |
   Follow-up modal | Timeline modal | Actions dropdown |
   Pagination | Profile dropdown
   ========================================================== */

(function () {
  'use strict';

  /* --------------------------------------------------------
     SIDEBAR TOGGLE
  -------------------------------------------------------- */
  const layout      = document.getElementById('crmLayout');
  const sidebar     = document.getElementById('crmSidebar');
  const toggleBtn   = document.getElementById('sidebarToggle');
  const mobileBtn   = document.getElementById('mobileMenuBtn');
  const overlay     = document.getElementById('sidebarOverlay');

  const COLLAPSED_KEY = 'hgs_sidebar_collapsed';

  function applySidebarState(collapsed) {
    if (collapsed) {
      layout.classList.add('sidebar-collapsed');
    } else {
      layout.classList.remove('sidebar-collapsed');
    }
  }

  // Restore saved state on desktop
  if (window.innerWidth >= 992) {
    const saved = localStorage.getItem(COLLAPSED_KEY);
    if (saved === 'true') applySidebarState(true);
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function () {
      const isCollapsed = layout.classList.contains('sidebar-collapsed');
      applySidebarState(!isCollapsed);
      if (window.innerWidth >= 992) {
        localStorage.setItem(COLLAPSED_KEY, !isCollapsed);
      }
    });
  }

  // Mobile open/close
  if (mobileBtn) {
    mobileBtn.addEventListener('click', function () {
      sidebar.classList.toggle('mobile-open');
      overlay.classList.toggle('active');
    });
  }
  if (overlay) {
    overlay.addEventListener('click', function () {
      sidebar.classList.remove('mobile-open');
      overlay.classList.remove('active');
    });
  }

  /* --------------------------------------------------------
     PROFILE DROPDOWN
  -------------------------------------------------------- */
  const profileWrap    = document.getElementById('profileDropdown');
  const profileTrigger = document.getElementById('profileTrigger');

  if (profileTrigger) {
    profileTrigger.addEventListener('click', function (e) {
      e.stopPropagation();
      profileWrap.classList.toggle('open');
    });
  }

  document.addEventListener('click', function (e) {
    if (profileWrap && !profileWrap.contains(e.target)) {
      profileWrap.classList.remove('open');
    }
  });

  /* --------------------------------------------------------
     ACTIONS DROPDOWN (per-row)
  -------------------------------------------------------- */
  document.addEventListener('click', function (e) {
    // Close all open action menus if clicking outside
    const allWraps = document.querySelectorAll('.actions-dropdown-wrap.open');
    allWraps.forEach(function (w) {
      if (!w.contains(e.target)) w.classList.remove('open');
    });
  });

  window.toggleActionsMenu = function (btn) {
    const wrap = btn.closest('.actions-dropdown-wrap');
    const isOpen = wrap.classList.contains('open');
    // Close all others first
    document.querySelectorAll('.actions-dropdown-wrap.open').forEach(function (w) {
      w.classList.remove('open');
    });
    if (!isOpen) wrap.classList.add('open');
  };

  /* --------------------------------------------------------
     ANIMATED COUNTERS
  -------------------------------------------------------- */
  function animateCounter(el) {
    const target = parseInt(el.getAttribute('data-target'), 10) || 0;
    const duration = 900;
    const step = 16;
    const steps = Math.floor(duration / step);
    let current = 0;
    const increment = target / steps;
    const timer = setInterval(function () {
      current += increment;
      if (current >= target) {
        clearInterval(timer);
        el.textContent = target.toLocaleString();
      } else {
        el.textContent = Math.floor(current).toLocaleString();
      }
    }, step);
  }

  // Run counters when visible (IntersectionObserver)
  const counters = document.querySelectorAll('.stat-number[data-target]');
  if ('IntersectionObserver' in window) {
    const obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCounter(entry.target);
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1 });
    counters.forEach(function (c) { obs.observe(c); });
  } else {
    counters.forEach(animateCounter);
  }

  /* --------------------------------------------------------
     NOTIFICATION BADGE — count today+overdue follow-ups
  -------------------------------------------------------- */
  const notifBadge    = document.getElementById('notifCount');
  const todayItems    = document.querySelectorAll('.followup-today .followup-item').length;
  const overdueItems  = document.querySelectorAll('.followup-overdue .followup-item').length;
  const totalNotif    = todayItems + overdueItems;
  if (notifBadge) {
    notifBadge.textContent = totalNotif;
    if (totalNotif === 0) notifBadge.style.display = 'none';
  }

  /* --------------------------------------------------------
     STATUS DROPDOWN — instant AJAX update
  -------------------------------------------------------- */
  window.updateStatus = function (leadId, newStatus, selectEl) {
    const encoded = encodeURIComponent(newStatus);
    fetch('/update-status/' + leadId + '/' + encoded)
      .then(function (res) {
        if (!res.ok) throw new Error('Failed');
        // Update select class for color
        const cls = newStatus.toLowerCase().replace(/ /g, '_');
        const allCls = ['status-new','status-assigned','status-contacted',
          'status-site_visit','status-quotation_sent','status-installation',
          'status-completed','status-cancelled'];
        selectEl.classList.remove.apply(selectEl.classList, allCls);
        selectEl.classList.add('status-' + cls);
        showToast('Status updated to ' + newStatus, 'success');
      })
      .catch(function () {
        showToast('Failed to update status. Please try again.', 'danger');
      });
  };

  /* --------------------------------------------------------
     FOLLOW UP MODAL
  -------------------------------------------------------- */
  window.openFollowModal = function (leadId, leadName, note, followDate) {
    document.getElementById('followLeadName').textContent = leadName;
    document.getElementById('followNote').value = note || '';
    document.getElementById('followDate').value = followDate || '';
    document.getElementById('followForm').action = '/add-note/' + leadId;
    const modal = new bootstrap.Modal(document.getElementById('followModal'));
    modal.show();
  };

  /* --------------------------------------------------------
     TIMELINE MODAL
  -------------------------------------------------------- */
  window.openTimeline = function (leadId, leadName) {
    document.getElementById('tlLeadName').textContent = leadName;
    const body = document.getElementById('timelineBody');
    body.innerHTML = '<div class="tl-loading"><div class="spinner-border text-success" role="status"></div><p class="mt-2 text-muted">Loading timeline...</p></div>';
    const modal = new bootstrap.Modal(document.getElementById('timelineModal'));
    modal.show();
    fetch('/lead-timeline/' + leadId)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (!data || !data.length) {
          body.innerHTML = '<div class="text-center py-4 text-muted"><i class="bi bi-clock fs-1 d-block mb-2"></i>No timeline entries yet.</div>';
          return;
        }
        var html = '<div class="tl-container">';
        data.forEach(function (e) {
          var icon = 'circle-fill';
          if (e.event.includes('Created'))    icon = 'plus-circle-fill';
          else if (e.event.includes('Assign')) icon = 'person-check-fill';
          else if (e.event.includes('Status')) icon = 'arrow-repeat';
          else if (e.event.includes('Note'))   icon = 'chat-dots-fill';
          else if (e.event.includes('Complet')) icon = 'check-circle-fill';
          html += '<div class="tl-item">';
          html += '<div class="tl-dot"></div>';
          html += '<div class="tl-card">';
          html += '<div class="tl-event"><i class="bi bi-' + icon + ' me-2"></i>' + escHtml(e.event) + '</div>';
          if (e.note) html += '<div class="tl-note">' + escHtml(e.note) + '</div>';
          html += '<div class="tl-meta"><i class="bi bi-person-fill me-1"></i>' + escHtml(e.created_by) + '<i class="bi bi-clock ms-2 me-1"></i>' + escHtml(e.created_at) + '</div>';
          html += '</div></div>';
        });
        html += '</div>';
        body.innerHTML = html;
      })
      .catch(function () {
        body.innerHTML = '<div class="text-center py-4 text-danger"><i class="bi bi-exclamation-triangle fs-2 d-block mb-2"></i>Failed to load timeline.</div>';
      });
  };

  /* --------------------------------------------------------
     TABLE PAGINATION
  -------------------------------------------------------- */
  const PAGE_SIZE = 25;

  function setupPagination() {
    const tbody    = document.getElementById('leadsTableBody');
    const pagEl    = document.getElementById('tablePagination');
    if (!tbody || !pagEl) return;

    const rows     = Array.from(tbody.querySelectorAll('tr.lead-row'));
    const total    = rows.length;
    if (total <= PAGE_SIZE) return; // No pagination needed

    let currentPage = 1;
    const totalPages = Math.ceil(total / PAGE_SIZE);

    function showPage(page) {
      currentPage = page;
      const start = (page - 1) * PAGE_SIZE;
      const end   = start + PAGE_SIZE;
      rows.forEach(function (row, idx) {
        row.style.display = (idx >= start && idx < end) ? '' : 'none';
      });
      renderPagination();
    }

    function renderPagination() {
      pagEl.innerHTML = '';

      // Info
      const info = document.createElement('span');
      info.style.cssText = 'font-size:11px;color:#888;margin-right:10px;font-weight:600;';
      const start = (currentPage - 1) * PAGE_SIZE + 1;
      const end   = Math.min(currentPage * PAGE_SIZE, total);
      info.textContent = start + '–' + end + ' of ' + total;
      pagEl.appendChild(info);

      // Prev
      const prev = document.createElement('button');
      prev.className = 'page-btn';
      prev.innerHTML = '<i class="bi bi-chevron-left"></i>';
      prev.disabled = currentPage === 1;
      prev.addEventListener('click', function () { if (currentPage > 1) showPage(currentPage - 1); });
      pagEl.appendChild(prev);

      // Page buttons (show up to 7)
      var start_p = Math.max(1, currentPage - 3);
      var end_p   = Math.min(totalPages, start_p + 6);
      if (end_p - start_p < 6) start_p = Math.max(1, end_p - 6);

      for (var p = start_p; p <= end_p; p++) {
        (function(pg) {
          const btn = document.createElement('button');
          btn.className = 'page-btn' + (pg === currentPage ? ' active' : '');
          btn.textContent = pg;
          btn.addEventListener('click', function () { showPage(pg); });
          pagEl.appendChild(btn);
        })(p);
      }

      // Next
      const next = document.createElement('button');
      next.className = 'page-btn';
      next.innerHTML = '<i class="bi bi-chevron-right"></i>';
      next.disabled = currentPage === totalPages;
      next.addEventListener('click', function () { if (currentPage < totalPages) showPage(currentPage + 1); });
      pagEl.appendChild(next);
    }

    showPage(1);
  }

  setupPagination();

  /* --------------------------------------------------------
     TOAST NOTIFICATION
  -------------------------------------------------------- */
  function showToast(message, type) {
    type = type || 'success';
    const toast = document.createElement('div');
    toast.style.cssText = [
      'position:fixed;bottom:24px;right:24px;z-index:9999',
      'padding:12px 20px;border-radius:12px;',
      'font-family:Poppins,sans-serif;font-size:13px;font-weight:600;',
      'display:flex;align-items:center;gap:8px;',
      'box-shadow:0 4px 20px rgba(0,0,0,.18);',
      'animation:fadeInUp .3s ease;',
      type === 'success'
        ? 'background:#005B38;color:#fff;'
        : 'background:#DC3545;color:#fff;'
    ].join('');
    const icon = type === 'success' ? 'check-circle-fill' : 'exclamation-triangle-fill';
    toast.innerHTML = '<i class="bi bi-' + icon + '"></i>' + escHtml(message);
    document.body.appendChild(toast);
    setTimeout(function () {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity .3s';
      setTimeout(function () { toast.remove(); }, 350);
    }, 2800);
  }

  /* --------------------------------------------------------
     HTML ESCAPE HELPER
  -------------------------------------------------------- */
  function escHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  /* --------------------------------------------------------
     AUTO-DISMISS FLASH ALERTS
  -------------------------------------------------------- */
  setTimeout(function () {
    document.querySelectorAll('.crm-alert').forEach(function (el) {
      el.classList.remove('show');
      setTimeout(function () { el.remove(); }, 300);
    });
  }, 5000);


  /* --------------------------------------------------------
     LEAD DETAIL / EDIT MODAL
  -------------------------------------------------------- */
  var _ldModal = null;
  var _ldCurrentId = null;

  window.openLeadDetail = function (leadId, leadName, tab) {
    _ldCurrentId = leadId;
    document.getElementById('ldLeadSubtitle').textContent = leadName;

    // Reset panels
    switchLeadTab(tab || 'view');

    if (!_ldModal) {
      _ldModal = new bootstrap.Modal(document.getElementById('leadDetailModal'));
    }
    _ldModal.show();

    // Fetch data
    fetch('/lead-detail/' + leadId)
      .then(function(r) { return r.json(); })
      .then(function(d) {
        populateLeadView(d);
        populateLeadEditForm(d);
        loadLeadTimeline(leadId);
      })
      .catch(function() {
        document.getElementById('ldViewGrid').innerHTML =
          '<div class="p-4 text-danger"><i class="bi bi-exclamation-triangle me-2"></i>Failed to load lead details.</div>';
      });
  };

  window.switchLeadTab = function(tab) {
    var viewPanel = document.getElementById('ldViewPanel');
    var editPanel = document.getElementById('ldEditPanel');
    var tabView   = document.getElementById('ldTabView');
    var tabEdit   = document.getElementById('ldTabEdit');
    if (tab === 'edit') {
      viewPanel.style.display = 'none';
      editPanel.style.display = '';
      tabView.classList.remove('active');
      tabEdit.classList.add('active');
    } else {
      editPanel.style.display = 'none';
      viewPanel.style.display = '';
      tabEdit.classList.remove('active');
      tabView.classList.add('active');
    }
  };

  function populateLeadView(d) {
    var statusColors = {
      'New':'#F5F5F5,#616161','Assigned':'#E3F2FD,#1565C0',
      'Contacted':'#E0F7FA,#00838F','Site Visit':'#F3E5F5,#7B1FA2',
      'Quotation Sent':'#FFF3E0,#E65100','Installation':'#E8EAF6,#283593',
      'Completed':'#E8F5E9,#1B5E20','Cancelled':'#FFEBEE,#B71C1C'
    };
    var sc = (statusColors[d.status] || '#F5F5F5,#616161').split(',');
    var statusBadge = '<span style="display:inline-block;padding:3px 12px;border-radius:20px;font-size:12px;font-weight:800;background:'+sc[0]+';color:'+sc[1]+'">' + escHtml(d.status) + '</span>';

    var fields = [
      {icon:'bi-hash',         label:'Lead ID',       value: '#' + d.id},
      {icon:'bi-person',       label:'Customer Name', value: d.name},
      {icon:'bi-telephone',    label:'Phone',         value: d.phone ? '<a href="tel:'+escHtml(d.phone)+'" style="color:#1565C0;text-decoration:none">'+escHtml(d.phone)+'</a>' : '', raw:true},
      {icon:'bi-building',     label:'City',          value: d.city},
      {icon:'bi-geo-alt',      label:'District',      value: d.district},
      {icon:'bi-lightning',    label:'Monthly Bill',  value: d.bill},
      {icon:'bi-flag',         label:'Status',        value: statusBadge, raw:true},
      {icon:'bi-building-check',label:'Vendor',       value: d.vendor_name || 'Unassigned'},
      {icon:'bi-calendar',     label:'Created',       value: d.created_at},
      {icon:'bi-calendar-event',label:'Follow-up Date',value: d.follow_date},
      {icon:'bi-person-check', label:'Updated By',    value: d.updated_by},
      {icon:'bi-chat-text',    label:'Note',          value: d.note, full: true},
    ];

    var html = '';
    fields.forEach(function(f) {
      var val = f.raw ? f.value : escHtml(f.value || '');
      var isEmpty = !f.value || (typeof f.value === 'string' && f.value.trim() === '');
      html += '<div class="ld-view-field' + (f.full ? ' ld-view-field-full" style="grid-column:1/-1' : '') + '">';
      html += '<div class="ld-view-label"><i class="bi ' + f.icon + '"></i>' + f.label + '</div>';
      html += '<div class="ld-view-value' + (isEmpty ? ' empty' : '') + '">' + (isEmpty ? 'Not set' : val) + '</div>';
      html += '</div>';
    });
    document.getElementById('ldViewGrid').innerHTML = html;
  }

  function populateLeadEditForm(d) {
    document.getElementById('ldEditLeadId').value    = d.id;
    document.getElementById('ldEditName').value      = d.name || '';
    document.getElementById('ldEditPhone').value     = d.phone || '';
    document.getElementById('ldEditCity').value      = d.city || '';
    document.getElementById('ldEditBill').value      = d.bill || '';
    document.getElementById('ldEditNote').value      = d.note || '';
    document.getElementById('ldEditFollowDate').value = d.follow_date || '';
    // District
    var distSel = document.getElementById('ldEditDistrict');
    for (var i = 0; i < distSel.options.length; i++) {
      if (distSel.options[i].value === d.district) { distSel.selectedIndex = i; break; }
    }
    // Status
    var statSel = document.getElementById('ldEditStatus');
    for (var j = 0; j < statSel.options.length; j++) {
      if (statSel.options[j].value === d.status) { statSel.selectedIndex = j; break; }
    }
    // Vendor
    var vendSel = document.getElementById('ldEditVendor');
    var vendId  = String(d.vendor_id);
    for (var k = 0; k < vendSel.options.length; k++) {
      if (vendSel.options[k].value === vendId) { vendSel.selectedIndex = k; break; }
    }
  }

  function loadLeadTimeline(leadId) {
    var tlBody = document.getElementById('ldTimelineBody');
    fetch('/lead-timeline/' + leadId)
      .then(function(r) { return r.json(); })
      .then(function(data) {
        if (!data || !data.length) {
          tlBody.innerHTML = '<p class="text-muted text-center py-3 small">No timeline entries yet.</p>';
          return;
        }
        var html = '<div class="tl-container">';
        data.forEach(function(e) {
          var icon = 'circle-fill';
          if (e.event.includes('Created'))    icon = 'plus-circle-fill';
          else if (e.event.includes('Assign')) icon = 'person-check-fill';
          else if (e.event.includes('Status')) icon = 'arrow-repeat';
          else if (e.event.includes('Note') || e.event.includes('Update')) icon = 'pencil-fill';
          else if (e.event.includes('Complet')) icon = 'check-circle-fill';
          html += '<div class="tl-item">';
          html += '<div class="tl-dot"></div>';
          html += '<div class="tl-card">';
          html += '<div class="tl-event"><i class="bi bi-' + icon + ' me-2"></i>' + escHtml(e.event) + '</div>';
          if (e.note) html += '<div class="tl-note">' + escHtml(e.note) + '</div>';
          html += '<div class="tl-meta"><i class="bi bi-person-fill me-1"></i>' + escHtml(e.created_by) + '<i class="bi bi-clock ms-2 me-1"></i>' + escHtml(e.created_at) + '</div>';
          html += '</div></div>';
        });
        html += '</div>';
        tlBody.innerHTML = html;
      })
      .catch(function() {
        tlBody.innerHTML = '<p class="text-danger text-center py-2 small">Failed to load timeline.</p>';
      });
  }

  window.submitLeadEdit = function(e) {
    e.preventDefault();
    var form    = document.getElementById('leadEditForm');
    var saveBtn = document.getElementById('ldSaveBtn');
    var leadId  = document.getElementById('ldEditLeadId').value;
    var data    = new FormData(form);
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status"></span>Saving...';
    fetch('/lead-edit/' + leadId, { method: 'POST', body: data })
      .then(function(r) { return r.json(); })
      .then(function(res) {
        if (res.success) {
          showToast(res.message || 'Lead updated!', 'success');
          // Refresh the view panel with new data
          fetch('/lead-detail/' + leadId)
            .then(function(r2) { return r2.json(); })
            .then(function(d2) {
              populateLeadView(d2);
              populateLeadEditForm(d2);
              loadLeadTimeline(leadId);
              // Update status select in table row
              var sel = document.querySelector('tr select[onchange*="' + leadId + '"]');
              if (sel) {
                sel.value = d2.status;
                var cls = d2.status.toLowerCase().replace(/ /g, '_');
                var allCls = ['status-new','status-assigned','status-contacted',
                  'status-site_visit','status-quotation_sent','status-installation',
                  'status-completed','status-cancelled'];
                sel.classList.remove.apply(sel.classList, allCls);
                sel.classList.add('status-' + cls);
              }
              switchLeadTab('view');
            });
        } else {
          showToast('Error: ' + (res.error || 'Unknown'), 'danger');
        }
      })
      .catch(function() { showToast('Network error. Please try again.', 'danger'); })
      .finally(function() {
        saveBtn.disabled = false;
        saveBtn.innerHTML = '<i class="bi bi-save me-1"></i>Save Changes';
      });
  };

})();
