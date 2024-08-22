document.addEventListener('DOMContentLoaded', function() {
    const facultyDropdown = document.querySelector('select[name="faculty"]');
    const branchDropdown = document.querySelector('select[name="department"]');

    facultyDropdown.addEventListener('change', function() {
        const selectedFacultyId = this.value;
        branchDropdown.innerHTML = '<option value="">เลือกฝ่ายงาน / สาขา</option>';
        
        if (selectedFacultyId) {
            fetch(`/api/departments/?faculty_id=${selectedFacultyId}`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(department => {
                        const option = document.createElement('option');
                        option.value = department.id;
                        option.textContent = department.name;
                        branchDropdown.appendChild(option);
                    });
                })
                .catch(error => console.error('Error fetching departments:', error));
        }
    });
});

const dropdownButtonResearcher = document.getElementById(`dropdown-button-researcher-1`);
const dropdownMenuResearcher = document.getElementById(`dropdown-menu-researcher-1`);
const searchInputResearcher = document.getElementById(`search-input-researcher-1`);
const selectedResearcherInput = document.getElementById(`selected-researcher-1`);
const itemResearcher = dropdownMenuResearcher.querySelectorAll('li');
let isOpenResearcher = false;

dropdownButtonResearcher.addEventListener('click', () => {
    toggleDropdownResearcher();
});

searchInputResearcher.addEventListener('input', () => {
    const searchTerm = searchInputResearcher.value.toLowerCase();

    itemResearcher.forEach((item) => {
        const text = item.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
});

itemResearcher.forEach((item) => {
    item.addEventListener('click', () => {
        const selectedText = item.textContent.trim();
        dropdownButtonResearcher.querySelector('.mr-2').textContent = selectedText;
        selectedResearcherInput.value = selectedText;
        toggleDropdownResearcher();
    });
});

function toggleDropdownResearcher() {
    isOpenResearcher = !isOpenResearcher;
    dropdownMenuResearcher.classList.toggle('hidden', !isOpenResearcher);
}

const dropdownButtonSubdistrict = document.getElementById('dropdown-button-subdistrict');
const dropdownMenuSubdistrict = document.getElementById('dropdown-menu-subdistrict');
const searchInputSubdistrict = document.getElementById('search-input-subdistrict');
const selectedSubdistrictInput = document.getElementById('selected-subdistrict');
const itemsSubdistrict = dropdownMenuSubdistrict.querySelectorAll('li');

// Function to toggle the dropdown visibility
function toggleDropdownSubdistrict() {
    const isHidden = dropdownMenuSubdistrict.classList.contains('hidden');
    dropdownMenuSubdistrict.classList.toggle('hidden', !isHidden);
}

// Click event to toggle the dropdown
dropdownButtonSubdistrict.addEventListener('click', (event) => {
    event.stopPropagation(); // Prevent click from closing dropdown immediately
    toggleDropdownSubdistrict();
});

// Event to filter dropdown items based on search input
searchInputSubdistrict.addEventListener('input', (event) => {
    event.stopPropagation(); // Prevent input from closing dropdown
    const searchTerm = searchInputSubdistrict.value.toLowerCase();

    itemsSubdistrict.forEach((item) => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(searchTerm) ? 'block' : 'none';
    });
});

// Event to select an item and close the dropdown
itemsSubdistrict.forEach((item) => {
    item.addEventListener('click', (event) => {
        const selectedText = item.textContent.trim();
        dropdownButtonSubdistrict.querySelector('.mr-2').textContent = selectedText;
        selectedSubdistrictInput.value = selectedText;
        toggleDropdownSubdistrict(); // Close the dropdown
    });
});

// Clicking outside the dropdown closes it
document.addEventListener('click', () => {
    if (!dropdownMenuSubdistrict.classList.contains('hidden')) {
        dropdownMenuSubdistrict.classList.add('hidden');
    }
});

// Prevent dropdown menu clicks from closing the dropdown
dropdownMenuSubdistrict.addEventListener('click', (event) => {
    event.stopPropagation();
});



function confirmDeletefund(id) {
    if (confirm("Are you sure you want to delete this fund?")) {
        fetch(`/delete_fund/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.reload(); // Reload the page after successful deletion
            } else {
                // Optionally, handle error response
            }
        })
        .catch(error => console.error('Error:', error));
    }
}

function confirmDeleteagency(id, name) {
    if (confirm(`Are you sure you want to delete ${name}?`)) {
        fetch(`/delete_agency/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(response => {
            if (response.ok) {
                window.location.reload(); // Reload the page after successful deletion
            } else {
                // Optionally, handle error response
            }
        })
        .catch(error => console.error('Error:', error));
    }
}


