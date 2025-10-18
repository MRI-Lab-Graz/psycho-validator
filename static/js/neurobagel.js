// NeuroBagel helper for participants suggestions
async function fetchNeurobagelParticipants() {
  try {
    const resp = await fetch('/api/neurobagel/participants');
    if (!resp.ok) throw new Error('Network response not ok');
    const json = await resp.json();
    return json.data;
  } catch (err) {
    console.error('NeuroBagel fetch failed', err);
    return null;
  }
}

// Populate a suggestions dropdown for participants (attaches to window)
window.populateParticipantsSuggestions = async function populateParticipantsSuggestions(selectEl) {
  const data = await fetchNeurobagelParticipants();
  if (!data) {
    // keep existing options if fetch failed
    return;
  }
  // NeuroBagel participants format may vary; safely extract properties
  const fields = Object.keys((data && data.properties) || {});
  selectEl.innerHTML = '';
  if (fields.length === 0) {
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = 'No fields found';
    selectEl.appendChild(opt);
    return;
  }
  fields.forEach(f => {
    const opt = document.createElement('option');
    opt.value = f;
    opt.textContent = f;
    selectEl.appendChild(opt);
  });
  // cache the raw NeuroBagel data on window for reuse
  window.__neurobagel_participants = data;
};

// Apply a NeuroBagel suggestion into matching fields in the participants form
window.applyNeurobagelSuggestion = async function applyNeurobagelSuggestion(fieldKey) {
  if (!fieldKey) {
    return;
  }
  let data = window.__neurobagel_participants;
  if (!data) {
    data = await fetchNeurobagelParticipants();
    if (!data) {
      console.warn('No NeuroBagel data available to apply suggestion');
      return;
    }
    window.__neurobagel_participants = data;
  }

  const fieldDef = (data.properties || {})[fieldKey];
  if (!fieldDef) {
    console.warn('Selected field not found in NeuroBagel data:', fieldKey);
    return;
  }

  // Determine a reasonable suggestion string: prefer description, then examples, then type
  let suggestion = '';
  if (fieldDef.description) suggestion = fieldDef.description;
  else if (Array.isArray(fieldDef.examples) && fieldDef.examples.length > 0) suggestion = JSON.stringify(fieldDef.examples[0]);
  else if (fieldDef.type) suggestion = String(fieldDef.type);
  else suggestion = JSON.stringify(fieldDef);

  // Find all textareas in the participants form that have a data-json-path starting with the fieldKey
  const selector = `[data-json-path^="${fieldKey}"]`;
  const matches = Array.from(document.querySelectorAll(selector));
  if (matches.length === 0) {
    // If no direct matches, try matching any path that contains the fieldKey
    const fallback = Array.from(document.querySelectorAll('[data-json-path]')).filter(el => el.dataset.jsonPath.includes(fieldKey));
    if (fallback.length === 0) {
      console.warn('No form fields found for NeuroBagel key:', fieldKey);
      return;
    }
    fallback.forEach(el => { el.value = suggestion; });
    // Notify user
    if (typeof showAlert === 'function') showAlert(`Inserted NeuroBagel suggestion for ${fieldKey}`, 'success');
    return;
  }

  matches.forEach(el => {
    el.value = suggestion;
  });

  if (typeof showAlert === 'function') showAlert(`Inserted NeuroBagel suggestion for ${fieldKey}`, 'success');
};
