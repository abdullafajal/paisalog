function handleEntryTypeChange(selectElement) {
    const categorySelect = document.getElementById('id_category');
    if (selectElement.value) {
        categorySelect.disabled = false;
    } else {
        categorySelect.disabled = true;
        categorySelect.value = '';
    }
}

// Initialize form state on page load
document.addEventListener('DOMContentLoaded', function() {
    const entryTypeSelect = document.querySelector('select[name="entry_type"]');
    if (entryTypeSelect) {
        handleEntryTypeChange(entryTypeSelect);
    }
}); 