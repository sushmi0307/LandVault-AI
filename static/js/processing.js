/**
 * LANDVAULT AI — DOCUMENT PROCESSING & AI PIPELINE
 * Handles drag-and-drop upload, sample picker, pipeline animation,
 * split-screen OCR inspection, and officer verification.
 */

let currentProcessedData = null;
let currentZoom = 1;

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const uploadCard = document.getElementById('uploadedFileCard');
  const startProcessBtn = document.getElementById('startProcessingBtn');
  const pipelineSection = document.getElementById('pipelineSection');
  const splitScreenSection = document.getElementById('splitScreenSection');
  
  let selectedFile = null;
  let selectedSamplePath = null;

  // Drag and drop event handlers
  if (dropzone && fileInput) {
    ['dragenter', 'dragover'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.add('dragover');
      });
    });

    ['dragleave', 'drop'].forEach(eventName => {
      dropzone.addEventListener(eventName, (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropzone.classList.remove('dragover');
      });
    });

    dropzone.addEventListener('drop', (e) => {
      if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
        handleFileSelect(e.dataTransfer.files[0]);
      }
    });

    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files.length > 0) {
        handleFileSelect(fileInput.files[0]);
      }
    });
  }

  // Quick Sample Selector Cards
  document.querySelectorAll('.sample-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.sample-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      
      const sampleFilename = card.dataset.filename;
      const sampleName = card.dataset.name;
      selectedSamplePath = sampleFilename;
      selectedFile = null;

      displaySelectedFileInfo(sampleName, 'Image (Sample PNG)', '1.2 MB');
    });
  });

  function handleFileSelect(file) {
    selectedFile = file;
    selectedSamplePath = null;
    document.querySelectorAll('.sample-card').forEach(c => c.classList.remove('active'));
    
    const sizeMb = (file.size / (1024 * 1024)).toFixed(2) + ' MB';
    displaySelectedFileInfo(file.name, file.type || 'Document File', sizeMb);
  }

  function displaySelectedFileInfo(name, type, size) {
    if (uploadCard) {
      uploadCard.style.display = 'block';
      document.getElementById('docFileName').textContent = name;
      document.getElementById('docFileType').textContent = type;
      document.getElementById('docFileSize').textContent = size;
      document.getElementById('docUploadTime').textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
  }

  // Start AI Processing Button
  if (startProcessBtn) {
    startProcessBtn.addEventListener('click', () => {
      if (!selectedFile && !selectedSamplePath) {
        showToast('Please upload a file or choose a sample document first.', 'warning');
        return;
      }
      runPipeline();
    });
  }

  async function runPipeline() {
    // Show pipeline section & scroll smoothly
    if (pipelineSection) {
      pipelineSection.style.display = 'block';
      pipelineSection.scrollIntoView({ behavior: 'smooth' });
    }
    if (splitScreenSection) {
      splitScreenSection.style.display = 'none';
    }

    startProcessBtn.disabled = true;
    startProcessBtn.innerHTML = `Processing...`;

    // Step 1: Uploading / Initializing
    await activateStep(1, 'Uploading document to secure sandbox...');
    await delay(500);
    markStepDone(1, 'Uploaded successfully');

    // Step 2: Classification
    await activateStep(2, 'Classifying document type...');
    await delay(500);
    markStepDone(2, 'Patta / Land Record identified');

    // Step 3: Preprocessing
    await activateStep(3, 'Deskewing, contrast adjustment & adaptive thresholding...');
    await delay(600);
    markStepDone(3, 'Computer vision preprocessed');

    // Step 4: OCR Extraction
    await activateStep(4, 'Reading text lines & cadastre tokens...');
    
    // Call backend API
    try {
      const formData = new FormData();
      if (selectedFile) {
        formData.append('document', selectedFile);
      } else if (selectedSamplePath) {
        formData.append('sample_name', selectedSamplePath);
      }

      const response = await fetch('/api/process-document', {
        method: 'POST',
        body: formData
      });

      const res = await response.json();
      if (!res.success) {
        throw new Error(res.error || 'Failed to process document');
      }

      currentProcessedData = res.data;

      markStepDone(4, 'Text and cadastre blocks extracted');

      // Step 5: Field Identification
      await activateStep(5, 'Extracting owner, survey, patta & boundaries...');
      await delay(500);
      markStepDone(5, 'Key fields identified');

      // Step 6: Validation
      await activateStep(6, 'Validating field rules & district registry checks...');
      await delay(500);
      markStepDone(6, 'Intelligent validation checks completed');

      // Step 7: Confidence Calculation
      await activateStep(7, 'Calculating statistical confidence matrix...');
      await delay(400);
      markStepDone(7, `Overall confidence: ${res.data.overall_confidence}%`);

      // Step 8: Duplicate Check
      await activateStep(8, 'Searching cadastral database for matches...');
      await delay(500);
      if (res.data.duplicate_info) {
        markStepDone(8, `Possible duplicate detected (${res.data.duplicate_info.similarity}% match)`);
      } else {
        markStepDone(8, 'No duplicate parcel found');
      }

      // Step 9: Final Review
      await activateStep(9, 'Preparing officer review workspace...');
      await delay(400);
      markStepDone(9, 'Ready for officer verification');

      // Display Split-Screen Result
      renderSplitScreenResult(res.data);

    } catch (err) {
      console.error(err);
      showToast('Error during AI processing: ' + err.message, 'danger');
    } finally {
      startProcessBtn.disabled = false;
      startProcessBtn.innerHTML = `Start AI Processing`;
    }
  }

  function activateStep(stepNum, statusText) {
    const el = document.getElementById(`step-${stepNum}`);
    if (el) {
      el.className = 'timeline-step active';
      el.querySelector('.step-status').textContent = statusText;
    }
    return Promise.resolve();
  }

  function markStepDone(stepNum, statusText) {
    const el = document.getElementById(`step-${stepNum}`);
    if (el) {
      el.className = 'timeline-step completed';
      el.querySelector('.step-circle').innerHTML = '✓';
      el.querySelector('.step-status').textContent = statusText;
    }
  }

  function delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Render Split-Screen Result
  function renderSplitScreenResult(data) {
    if (!splitScreenSection) return;
    splitScreenSection.style.display = 'block';
    splitScreenSection.scrollIntoView({ behavior: 'smooth' });

    // Set Document Image Preview
    const previewImg = document.getElementById('splitDocImage');
    if (previewImg && data.preview_url) {
      previewImg.src = data.preview_url;
    }

    // Set Record ID
    document.getElementById('reviewRecordNumber').textContent = data.record_number;

    // Overall Confidence Score & Gauge
    const gaugeScore = document.getElementById('gaugeScore');
    const gaugeCircle = document.getElementById('gaugeCircle');
    if (gaugeScore) gaugeScore.textContent = `${data.overall_confidence}%`;
    if (gaugeCircle) gaugeCircle.style.setProperty('--score', data.overall_confidence);

    // Populate Editable Fields
    const fields = data.fields;
    const confs = data.field_confidences || {};
    
    setFieldValue('f_owner_name', fields.owner_name, confs.owner_name);
    setFieldValue('f_survey_number', fields.survey_number, confs.survey_number);
    setFieldValue('f_subdivision_number', fields.subdivision_number, confs.subdivision_number);
    setFieldValue('f_patta_number', fields.patta_number, confs.patta_number);
    setFieldValue('f_district', fields.district, confs.district);
    setFieldValue('f_taluk', fields.taluk, confs.taluk);
    setFieldValue('f_village', fields.village, confs.village);
    setFieldValue('f_land_area', fields.land_area, confs.land_area);
    setFieldValue('f_document_type', fields.document_type, confs.document_type);
    setFieldValue('f_document_date', fields.document_date, confs.document_date);

    // Validation Checks
    renderValidationChecks(data.validation_checks, confs);

    // Anomalies Card
    const anomalyCard = document.getElementById('anomalyCard');
    const anomalyList = document.getElementById('anomalyList');
    if (anomalyCard && anomalyList) {
      if (data.anomalies && data.anomalies.length > 0) {
        anomalyCard.style.display = 'block';
        anomalyList.innerHTML = data.anomalies.map(a => `<li>⚠ ${a}</li>`).join('');
      } else {
        anomalyCard.style.display = 'none';
      }
    }

    // Duplicates Card
    const duplicateCard = document.getElementById('duplicateCard');
    if (duplicateCard) {
      if (data.duplicate_info) {
        duplicateCard.style.display = 'block';
        document.getElementById('dupRecordId').textContent = data.duplicate_info.record_number;
        document.getElementById('dupSimilarity').textContent = `${data.duplicate_info.similarity}%`;
        document.getElementById('dupMatchingFields').textContent = data.duplicate_info.matching_fields.join(', ');
        
        // Link button to existing record
        const viewExistingBtn = document.getElementById('btnViewExistingDup');
        if (viewExistingBtn) {
          viewExistingBtn.onclick = () => {
            window.open(`/record/${data.duplicate_info.record_number}`, '_blank');
          };
        }
      } else {
        duplicateCard.style.display = 'none';
      }
    }

    // AI Recommendation Banner
    const recBanner = document.getElementById('aiRecText');
    if (recBanner) {
      recBanner.textContent = data.ai_recommendation;
    }
  }

  function setFieldValue(id, val, conf) {
    const input = document.getElementById(id);
    if (input) input.value = val || '';
    const badge = document.getElementById(`${id}_conf`);
    if (badge && conf !== undefined) {
      badge.textContent = `${conf}%`;
      badge.className = 'field-conf-badge ' + (conf >= 85 ? 'conf-high' : (conf >= 75 ? 'conf-med' : 'conf-low'));
    }
  }

  function renderValidationChecks(checks, confs) {
    const container = document.getElementById('validationChecksList');
    if (!container) return;

    const list = [
      { label: 'Required fields present', valid: checks.required_fields },
      { label: 'Survey number format valid', valid: checks.survey_format },
      { label: 'Land area format valid', valid: checks.area_format },
      { label: 'District detected in registry', valid: checks.district_valid },
      { label: 'Village confidence acceptable', valid: checks.village_confidence },
      { label: 'Patta number format valid', valid: checks.patta_format }
    ];

    if (checks.quality_valid !== undefined) {
      list.unshift({ label: 'Document image clarity & quality', valid: checks.quality_valid });
    }

    container.innerHTML = list.map(item => `
      <div style="display:flex; align-items:center; justify-content:space-between; padding: 6px 0; font-size:13px; border-bottom:1px dashed var(--color-border);">
        <span style="color:var(--color-primary);">${item.valid ? '✓' : '⚠'} ${item.label}</span>
        <span style="font-weight:700; color:${item.valid ? 'var(--color-emerald)' : 'var(--color-amber)'}">
          ${item.valid ? 'PASSED' : 'REVIEW'}
        </span>
      </div>
    `).join('');
  }

  // Zoom Controls for Left Document Viewer
  const zoomInBtn = document.getElementById('btnZoomIn');
  const zoomOutBtn = document.getElementById('btnZoomOut');
  const zoomResetBtn = document.getElementById('btnZoomReset');
  const previewImg = document.getElementById('splitDocImage');

  if (zoomInBtn && previewImg) {
    zoomInBtn.addEventListener('click', () => {
      currentZoom = Math.min(currentZoom + 0.25, 2.5);
      previewImg.style.transform = `scale(${currentZoom})`;
    });
  }
  if (zoomOutBtn && previewImg) {
    zoomOutBtn.addEventListener('click', () => {
      currentZoom = Math.max(currentZoom - 0.25, 0.5);
      previewImg.style.transform = `scale(${currentZoom})`;
    });
  }
  if (zoomResetBtn && previewImg) {
    zoomResetBtn.addEventListener('click', () => {
      currentZoom = 1;
      previewImg.style.transform = `scale(1)`;
    });
  }

  // OFFICER ACTION BUTTONS
  const btnApprove = document.getElementById('btnApproveRecord');
  const btnReject = document.getElementById('btnRejectRecord');
  const btnSendReview = document.getElementById('btnSendForReview');
  const chkReviewed = document.getElementById('officerReviewedCheck');
  const txtRemarks = document.getElementById('officerRemarksInput');

  if (btnApprove) {
    btnApprove.addEventListener('click', () => submitOfficerDecision('VERIFIED'));
  }
  if (btnReject) {
    btnReject.addEventListener('click', () => submitOfficerDecision('REJECTED'));
  }
  if (btnSendReview) {
    btnSendReview.addEventListener('click', () => submitOfficerDecision('NEEDS_REVIEW'));
  }

  async function submitOfficerDecision(newStatus) {
    if (!currentProcessedData) {
      showToast('No record loaded to verify.', 'danger');
      return;
    }

    if (!chkReviewed.checked && newStatus === 'VERIFIED') {
      showToast('Please check "I have reviewed the extracted information" before approving.', 'warning');
      chkReviewed.focus();
      return;
    }

    // Collect edited field values
    const updatedFields = {
      owner_name: document.getElementById('f_owner_name').value,
      survey_number: document.getElementById('f_survey_number').value,
      subdivision_number: document.getElementById('f_subdivision_number') ? document.getElementById('f_subdivision_number').value : '',
      patta_number: document.getElementById('f_patta_number').value,
      district: document.getElementById('f_district').value,
      taluk: document.getElementById('f_taluk').value,
      village: document.getElementById('f_village').value,
      land_area: document.getElementById('f_land_area').value,
      document_type: document.getElementById('f_document_type').value,
      document_date: document.getElementById('f_document_date').value
    };

    const payload = {
      record_number: currentProcessedData.record_number,
      fields: updatedFields,
      status: newStatus,
      confidence_score: currentProcessedData.overall_confidence,
      officer_remarks: txtRemarks ? txtRemarks.value : '',
      anomaly_flags: currentProcessedData.anomalies,
      duplicate_of_id: currentProcessedData.duplicate_info ? currentProcessedData.duplicate_info.record_number : null,
      duplicate_similarity: currentProcessedData.duplicate_info ? currentProcessedData.duplicate_info.similarity : null
    };

    try {
      const response = await fetch('/api/save-verification', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const res = await response.json();
      if (res.success) {
        showToast(`Record ${res.record_number} saved as ${newStatus}!`, 'success');
        setTimeout(() => {
          window.location.href = `/record/${res.record_number}`;
        }, 1200);
      } else {
        showToast('Error: ' + res.error, 'danger');
      }
    } catch (err) {
      showToast('Failed to save officer decision: ' + err.message, 'danger');
    }
  }
});
