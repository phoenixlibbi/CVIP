// Pass the invoices data from Flask to JavaScript
const invoices = {{ invoices | tojson | safe }};

// Populate highlights
document.getElementById('total-invoices').innerText = invoices.length;
document.getElementById('unique-sellers').innerText = new Set(invoices.map(inv => inv.name)).size;
document.getElementById('unique-customers').innerText = new Set(invoices.map(inv => inv.customer_name)).size;
document.getElementById('unique-products').innerText = new Set(invoices.flatMap(inv => inv.products.map(p => p.product_name))).size;

// Function to generate table rows
function generateTableRows() {
    const tableBody = document.getElementById('invoice-table');
    tableBody.innerHTML = ''; // Clear existing rows

    invoices.forEach(invoice => {
        const row = document.createElement('tr');
        row.setAttribute('data-id', invoice.id);
        row.setAttribute('data-customer-receipt-no', invoice.customer_receipt_no);
        row.setAttribute('data-business-name', invoice.business_name);
        row.setAttribute('data-name', invoice.name);
        row.setAttribute('data-address', invoice.address);
        row.setAttribute('data-customer-name', invoice.customer_name);
        row.setAttribute('data-date', invoice.date);
        row.setAttribute('data-products', JSON.stringify(invoice.products));

        row.innerHTML = `
            <td>${invoice.customer_receipt_no}</td>
            <td>${invoice.business_name}</td>
            <td>${invoice.name}</td>
            <td>${invoice.address}</td>
            <td>${invoice.customer_name}</td>
            <td>${invoice.date}</td>
            <td>${invoice.products.map(p => `${p.product_name} x ${p.quantity}`).join(', ')}</td>
        `;

        // Add click event to the row
        row.addEventListener('click', () => openModal(row));
        tableBody.appendChild(row);
    });
}

// Generate table rows on page load
generateTableRows();

// Function to open the modal and populate it with receipt details
function openModal(row) {
    // Get the invoice data from the row's data attributes
    const invoice = {
        id: row.getAttribute('data-id'),
        customer_receipt_no: row.getAttribute('data-customer-receipt-no'),
        business_name: row.getAttribute('data-business-name'),
        name: row.getAttribute('data-name'),
        address: row.getAttribute('data-address'),
        customer_name: row.getAttribute('data-customer-name'),
        date: row.getAttribute('data-date'),
        products: JSON.parse(row.getAttribute('data-products'))
    };

    // Build the modal content
    const modalContent = `
        <p><strong>Serial Number:</strong> ${invoice.customer_receipt_no}</p>
        <p><strong>Business Name:</strong> ${invoice.business_name}</p>
        <p><strong>Seller Name:</strong> ${invoice.name}</p>
        <p><strong>Address:</strong> ${invoice.address}</p>
        <p><strong>Customer Name:</strong> ${invoice.customer_name}</p>
        <p><strong>Date:</strong> ${invoice.date}</p>
        <h3>Products</h3>
        <table class="product-table">
            <thead>
                <tr>
                    <th>Product Name</th>
                    <th>Quantity</th>
                    <th>Total Price</th>
                </tr>
            </thead>
            <tbody>
                ${invoice.products.map(product => `
                    <tr>
                        <td>${product.product_name}</td>
                        <td>${product.quantity}</td>
                        <td>${product.total_price}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>
    `;

    // Display the modal
    document.getElementById('modal-content').innerHTML = modalContent;
    document.getElementById('modal').style.display = 'block';
}

// Function to close the modal
function closeModal() {
    document.getElementById('modal').style.display = 'none';
}

// Close the modal if the user clicks outside of it
window.onclick = function (event) {
    const modal = document.getElementById('modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
};

// Search functionality
document.getElementById('search-box').addEventListener('input', function () {
    const searchValue = this.value.toLowerCase();
    const rows = document.querySelectorAll('#invoice-table tr');
    rows.forEach(row => {
        const rowText = row.innerText.toLowerCase();
        row.style.display = rowText.includes(searchValue) ? "" : "none";
    });
});

// Sorting functionality
function sortTable(columnIndex) {
    const tableBody = document.getElementById('invoice-table');
    const rows = Array.from(tableBody.children);
    rows.sort((a, b) => a.children[columnIndex].innerText.localeCompare(b.children[columnIndex].innerText));
    rows.forEach(row => tableBody.appendChild(row));
}

// Filter by date
document.getElementById('filter-date').addEventListener('click', function () {
    const startDate = new Date(document.getElementById('start-date').value);
    const endDate = new Date(document.getElementById('end-date').value);
    const rows = document.querySelectorAll('#invoice-table tr');
    rows.forEach(row => {
        const rowDate = new Date(row.children[5].innerText);
        row.style.display = rowDate >= startDate && rowDate <= endDate ? "" : "none";
    });
});

// Function to create the Top Sellers Chart
function createTopSellersChart() {
    // Group invoices by seller and count the number of invoices per seller
    const sellerCounts = {};
    invoices.forEach(invoice => {
        const seller = invoice.name;
        sellerCounts[seller] = (sellerCounts[seller] || 0) + 1;
    });

    // Sort sellers by invoice count and get the top 10
    const sortedSellers = Object.entries(sellerCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10);

    const labels = sortedSellers.map(seller => seller[0]);
    const data = sortedSellers.map(seller => seller[1]);

    new Chart(document.getElementById('top-sellers-chart'), {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Invoices',
                data: data,
                backgroundColor: '#61dafb'
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Function to create the Invoices Over Time Chart
function createInvoicesOverTimeChart() {
    // Group invoices by date and count the number of invoices per date
    const dateCounts = {};
    invoices.forEach(invoice => {
        const date = invoice.date;
        dateCounts[date] = (dateCounts[date] || 0) + 1;
    });

    // Sort dates in ascending order
    const sortedDates = Object.entries(dateCounts).sort((a, b) => new Date(a[0]) - new Date(b[0]));

    const labels = sortedDates.map(entry => entry[0]);
    const data = sortedDates.map(entry => entry[1]);

    new Chart(document.getElementById('invoices-over-time-chart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Number of Invoices',
                data: data,
                borderColor: '#4CAF50',
                fill: false
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

// Create charts on page load
createTopSellersChart();
createInvoicesOverTimeChart();