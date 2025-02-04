document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.category-toggle').forEach(function(header) {
        header.addEventListener('click', function() {
            var queriesDiv = this.nextElementSibling;
            queriesDiv.style.display = queriesDiv.style.display === 'none' ? 'block' : 'none';
            var indicator = this.querySelector('.toggle-indicator');
            indicator.innerHTML = queriesDiv.style.display === 'none' ? '<i class="fas fa-chevron-down"></i>' : '<i class="fas fa-chevron-up"></i>';
        });
    });
});
