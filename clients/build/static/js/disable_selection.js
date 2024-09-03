window.addEventListener('load', function() {
    // Disable double-click on items to prevent them from shifting
    document.querySelectorAll('.selector-available select, .selector-chosen select').forEach(function(selectBox) {
        selectBox.ondblclick = function(event) {
            event.preventDefault(); // Prevent the default action (shifting the item)
            return false;
        };
    });

    // Disable the add/remove buttons to prevent shifting via buttons
    document.querySelectorAll('.selector-add, .selector-remove').forEach(function(button) {
        button.style.pointerEvents = 'none';  // Disable click events
        button.style.opacity = '0.5';  // Make the buttons look disabled
    });
});
