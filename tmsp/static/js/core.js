document.addEventListener('DOMContentLoaded', function () {
  const searchInput = document.getElementById('studentSearch');
  const studentList = document.getElementById('studentList');
  const table = studentList ? studentList.closest('table') : null;

  // Live search filter
  if (searchInput && studentList) {
    searchInput.addEventListener('input', function () {
      const filter = searchInput.value.toLowerCase();
      const rows = studentList.getElementsByTagName('tr');

      Array.from(rows).forEach(row => {
        const nameCell = row.getElementsByTagName('td')[0];
        if (nameCell) {
          const nameText = nameCell.textContent || nameCell.innerText;
          if (nameText.toLowerCase().indexOf(filter) > -1) {
            row.style.display = '';
          } else {
            row.style.display = 'none';
          }
        }
      });
    });
  }

  // Table sorting
  if (table) {
    const headers = table.querySelectorAll('th');
    headers.forEach((header, index) => {
      header.style.cursor = 'pointer';
      header.addEventListener('click', () => {
        sortTableByColumn(table, index);
      });
    });
  }

  function sortTableByColumn(table, columnIndex) {
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.querySelectorAll('tr'));
    const isAscending = table.getAttribute('data-sort-dir') === 'asc';
    rows.sort((a, b) => {
      const aText = a.cells[columnIndex].textContent.trim();
      const bText = b.cells[columnIndex].textContent.trim();
      return isAscending ? aText.localeCompare(bText) : bText.localeCompare(aText);
    });
    rows.forEach(row => tbody.appendChild(row));
    table.setAttribute('data-sort-dir', isAscending ? 'desc' : 'asc');
  }

  // Pagination (simple)
  const rowsPerPage = 10;
  if (table && studentList) {
    const tbody = table.tBodies[0];
    const rows = Array.from(tbody.querySelectorAll('tr'));
    if (rows.length > rowsPerPage) {
      let currentPage = 1;
      const totalPages = Math.ceil(rows.length / rowsPerPage);

      function renderPage(page) {
        const start = (page - 1) * rowsPerPage;
        const end = start + rowsPerPage;
        rows.forEach((row, index) => {
          row.style.display = (index >= start && index < end) ? '' : 'none';
        });
        pageInfo.textContent = `Page ${page} of ${totalPages}`;
        prevBtn.disabled = page === 1;
        nextBtn.disabled = page === totalPages;
      }

      const paginationControls = document.createElement('div');
      paginationControls.className = 'pagination-controls d-flex justify-content-center align-items-center gap-3 mt-3';

      const prevBtn = document.createElement('button');
      prevBtn.textContent = 'Previous';
      prevBtn.className = 'btn btn-secondary btn-sm';
      prevBtn.disabled = true;
      prevBtn.addEventListener('click', () => {
        if (currentPage > 1) {
          currentPage--;
          renderPage(currentPage);
        }
      });

      const nextBtn = document.createElement('button');
      nextBtn.textContent = 'Next';
      nextBtn.className = 'btn btn-secondary btn-sm';
      nextBtn.addEventListener('click', () => {
        if (currentPage < totalPages) {
          currentPage++;
          renderPage(currentPage);
        }
      });

      const pageInfo = document.createElement('span');
      pageInfo.className = 'page-info';

      paginationControls.appendChild(prevBtn);
      paginationControls.appendChild(pageInfo);
      paginationControls.appendChild(nextBtn);

      table.parentNode.insertBefore(paginationControls, table.nextSibling);

      renderPage(currentPage);
    }
  }
});
