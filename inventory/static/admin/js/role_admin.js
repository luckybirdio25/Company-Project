document.addEventListener('DOMContentLoaded', function() {
    // Handle group checkbox changes
    document.querySelectorAll('.permission-group').forEach(function(groupCheckbox) {
        groupCheckbox.addEventListener('change', function() {
            const groupName = this.className.split(' ')[1];
            const isChecked = this.checked;
            
            // Update all checkboxes in this group
            document.querySelectorAll('.' + groupName).forEach(function(checkbox) {
                checkbox.checked = isChecked;
            });
        });
    });

    // Handle individual permission checkbox changes
    document.querySelectorAll('.permission-checkbox').forEach(function(checkbox) {
        checkbox.addEventListener('change', function() {
            const groupName = this.className.split(' ')[1];
            const groupCheckbox = document.querySelector('.permission-group.' + groupName);
            
            if (groupCheckbox) {
                // Check if all permissions in the group are checked
                const allChecked = Array.from(document.querySelectorAll('.' + groupName))
                    .every(function(cb) { return cb.checked; });
                
                // Check if any permissions in the group are checked
                const anyChecked = Array.from(document.querySelectorAll('.' + groupName))
                    .some(function(cb) { return cb.checked; });
                
                // Update group checkbox state
                groupCheckbox.checked = allChecked;
                groupCheckbox.indeterminate = anyChecked && !allChecked;
            }
        });
    });
}); 