/**
 * LANDVAULT AI — LAND RECORDS SEARCH & FILTER CONTROLLER
 */

document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('recordSearchInput');
  const districtFilter = document.getElementById('districtFilter');
  const statusFilter = document.getElementById('statusFilter');
  const clearFiltersBtn = document.getElementById('clearFiltersBtn');
  const tableRows = document.querySelectorAll('.record-table-row');
  const emptyState = document.getElementById('recordsEmptyState');
  const resultsCount = document.getElementById('resultsCount');

  function filterRecords() {
    const query = searchInput ? searchInput.value.toLowerCase().trim() : '';
    const district = districtFilter ? districtFilter.value.toLowerCase() : '';
    const status = statusFilter ? statusFilter.value.toUpperCase() : '';

    let visibleCount = 0;

    tableRows.forEach(row => {
      const text = row.textContent.toLowerCase();
      const rowDistrict = (row.dataset.district || '').toLowerCase();
      const rowStatus = (row.dataset.status || '').toUpperCase();

      const matchQuery = !query || text.includes(query);
      const matchDistrict = !district || rowDistrict === district;
      const matchStatus = !status || rowStatus === status;

      if (matchQuery && matchDistrict && matchStatus) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    if (resultsCount) {
      resultsCount.textContent = visibleCount;
    }

    if (emptyState) {
      emptyState.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  if (searchInput) searchInput.addEventListener('input', filterRecords);
  if (districtFilter) districtFilter.addEventListener('change', filterRecords);
  if (statusFilter) statusFilter.addEventListener('change', filterRecords);

  if (clearFiltersBtn) {
    clearFiltersBtn.addEventListener('click', () => {
      if (searchInput) searchInput.value = '';
      if (districtFilter) districtFilter.value = '';
      if (statusFilter) statusFilter.value = '';
      filterRecords();
    });
  }

  // Quick Patta Number Search Form (Citizen / Fast Lookup)
  const pattaSearchForm = document.getElementById('pattaSearchForm');
  if (pattaSearchForm) {
    pattaSearchForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const pattaInput = document.getElementById('pattaNumberInput');
      const val = pattaInput ? pattaInput.value.trim() : '';
      if (!val) {
        showToast('Please enter a Patta Number', 'warning');
        return;
      }
      
      const resContainer = document.getElementById('pattaSearchResultContainer');
      if (resContainer) {
        resContainer.innerHTML = `<div style="text-align:center; padding:20px; color:var(--color-teal);">Searching Land Records Vault...</div>`;
      }

      try {
        const response = await fetch(`/api/search-patta?patta=${encodeURIComponent(val)}`);
        const res = await response.json();
        
        if (res.found && resContainer) {
          const rec = res.record;
          resContainer.innerHTML = `
            <div class="card" style="border: 2px solid var(--color-teal); margin-top:16px;">
              <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <h3 style="color:var(--color-primary);">${rec.record_number}</h3>
                <span class="status-pill ${rec.status.toLowerCase()}">${rec.status}</span>
              </div>
              <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:12px; font-size:13.5px;">
                <div><strong style="color:var(--color-text-muted);">Owner:</strong> ${rec.owner_name}</div>
                <div><strong style="color:var(--color-text-muted);">Survey No:</strong> ${rec.survey_number}</div>
                <div><strong style="color:var(--color-text-muted);">Patta No:</strong> ${rec.patta_number}</div>
                <div><strong style="color:var(--color-text-muted);">District:</strong> ${rec.district}</div>
                <div><strong style="color:var(--color-text-muted);">Village:</strong> ${rec.village}</div>
                <div><strong style="color:var(--color-text-muted);">Land Area:</strong> ${rec.land_area}</div>
              </div>
              <div style="margin-top:16px; display:flex; gap:10px;">
                <a href="/record/${rec.record_number}" class="btn btn-teal btn-sm">View Full Record</a>
                <a href="/verify/${rec.record_number}" target="_blank" class="btn btn-secondary btn-sm">Open QR Certificate</a>
              </div>
            </div>
          `;
        } else if (resContainer) {
          resContainer.innerHTML = `
            <div style="text-align:center; padding:30px; background-color:#FFFFFF; border-radius:12px; border:1px dashed var(--color-border); margin-top:16px;">
              <p style="color:var(--color-danger); font-weight:600;">No land record found for Patta #${val}</p>
              <p style="font-size:12.5px; color:var(--color-text-muted); margin-top:4px;">Please verify your Patta Number or try searching by Survey Number.</p>
            </div>
          `;
        }
      } catch (err) {
        if (resContainer) {
          resContainer.innerHTML = `<p style="color:var(--color-danger);">Search error: ${err.message}</p>`;
        }
      }
    });
  }
});
