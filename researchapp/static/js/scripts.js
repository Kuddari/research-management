
function updateFileLabel(inputElement, labelId) {
    var labelElement = document.getElementById(labelId);
    var fileName = inputElement.files[0].name;  // Get the name of the file
    labelElement.textContent = fileName;  // Update the label text
}


document.addEventListener('DOMContentLoaded', () => {
    const menuContainer = document.getElementById('menuContainer');
    const toggleButton = document.getElementById('toggleButton');

    // Toggle menu visibility when the toggle button is clicked
    toggleButton.addEventListener('click', (event) => {
        menuContainer.classList.toggle('hidden');
        event.stopPropagation(); // Prevent click from propagating to the document
    });

    // Close the menu when clicking anywhere else
    document.addEventListener('click', (event) => {
        if (!menuContainer.contains(event.target) && !toggleButton.contains(event.target)) {
            menuContainer.classList.add('hidden');
        }
    });
});

