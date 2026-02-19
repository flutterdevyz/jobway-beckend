document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const loginView = document.getElementById('login-view');
    const appContainer = document.getElementById('app-container');
    const loginForm = document.getElementById('login-form');
    const loginError = document.getElementById('login-error');
    const contentArea = document.getElementById('content-area');
    const viewTitle = document.getElementById('view-title');
    const navItems = document.querySelectorAll('.nav-item');
    const logoutBtn = document.getElementById('logout-btn');
    const modal = document.getElementById('modal-container');
    const modalTitle = document.getElementById('modal-title');
    const modalForm = document.getElementById('modal-form');
    const formFields = document.getElementById('form-fields');
    const closeModal = document.querySelector('.close-modal');

    // State management
    const state = {
        currentView: 'dashboard',
        token: localStorage.getItem('access_token'),
        modalType: null, // Added for modal context
        editItem: null   // Added for modal context
    };

    // Initialize Page
    function init() {
        if (typeof feather !== 'undefined') {
            feather.replace();
        } else {
            console.warn('Feather icons script not loaded.');
        }
        setupEventListeners();
        if (!state.token) {
            showLogin();
        } else {
            showApp();
        }
    }

    function showLogin() {
        loginView.classList.remove('hidden');
        appContainer.classList.add('hidden');
    }

    function showApp() {
        loginView.classList.add('hidden');
        appContainer.classList.remove('hidden');
        switchView('dashboard');
    }

    function setupEventListeners() {
        closeModal.onclick = () => modal.classList.add('hidden');
        window.onclick = (e) => { if (e.target == modal) modal.classList.add('hidden'); };
        modalForm.onsubmit = (e) => handleModalSubmit(e);
    }

    // Login Logic
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        loginError.classList.add('hidden');

        const phone_number = document.getElementById('login-phone').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ phone_number, password })
            });

            if (!response.ok) {
                const err = await response.json();
                throw new Error(err.detail || 'Login failed');
            }

            const data = await response.json();

            // Check if user is admin (optional safety, backend already restricts admin endpoints)
            // Save token
            state.token = data.access_token;
            localStorage.setItem('access_token', state.token);
            showApp();
        } catch (err) {
            loginError.innerText = err.message;
            loginError.classList.remove('hidden');
        }
    });

    // Logout Logic
    logoutBtn.addEventListener('click', () => {
        state.token = null;
        localStorage.removeItem('access_token');
        showLogin();
    });

    // Navigation and Routing
    navItems.forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const view = item.getAttribute('data-view');
            switchView(view);
        });
    });

    async function switchView(view) {
        state.currentView = view;
        navItems.forEach(i => i.classList.remove('active'));
        const activeItem = document.querySelector(`.nav-item[data-view="${view}"]`);
        if (activeItem) activeItem.classList.add('active');
        viewTitle.innerText = view.charAt(0).toUpperCase() + view.slice(1);
        renderView(view);
    }

    async function renderView(view) {
        contentArea.innerHTML = '<div class="loader">Loading...</div>';
        try {
            if (view === 'dashboard') {
                const stats = await fetchData('/api/admin/stats');
                renderDashboard(stats);
            } else if (view === 'users') {
                const users = await fetchData('/api/admin/users');
                renderTable('users', users, ['ID', 'Full Name', 'Phone', 'Role', 'Premium', 'Password', 'Status']);
            } else if (view === 'jobs') {
                const jobs = await fetchData('/api/admin/jobs');
                renderTable('jobs', jobs, ['Title', 'Company', 'Salary', 'Date']);
            } else if (view === 'categories') {
                const cats = await fetchData('/api/admin/categories');
                renderTable('categories', cats, ['ID', 'Name', 'Image']);
            } else if (view === 'applications') {
                const apps = await fetchData('/api/admin/applications');
                renderTable('applications', apps, ['ID', 'Job', 'Applicant', 'Phone', 'Date']);
            } else if (view === 'notifications') {
                const notifications = await fetchData('/api/admin/notifications');
                renderTable('notifications', notifications, ['ID', 'User ID', 'Title', 'Message', 'Date']);
            } else if (view === 'contact_requests') {
                const contacts = await fetchData('/api/admin/contact-requests');
                renderTable('contact_requests', contacts, ['ID', 'Name', 'Phone', 'Date']);
            }
        } catch (err) {
            contentArea.innerHTML = `<div class="error">Error loading data: ${err.message}</div>`;
        }
    }

    function renderDashboard(stats) {
        contentArea.innerHTML = `
            <div class="stats-grid">
                ${createStatCard('users', stats.total_users, 'Total Users', 'users')}
                ${createStatCard('briefcase', stats.total_jobs, 'Jobs Posted', 'briefcase')}
                ${createStatCard('layers', stats.total_categories, 'Categories', 'layers')}
                ${createStatCard('file-text', stats.total_applications, 'Applications', 'file-text')}
                ${createStatCard('mail', stats.total_contact_requests, 'Contacts', 'mail')}
                ${createStatCard('bell', stats.total_notifications, 'Notifications', 'bell')}
                ${createStatCard('zap', stats.premium_users, 'Premium Users', 'zap')}
            </div>
            <div class="data-card">
                <div class="data-header"><h3>Recent Activities</h3></div>
                <div style="padding: 24px; color: var(--text-secondary);">Admin panel is synced.</div>
            </div>
        `;
        feather.replace();
    }

    function createStatCard(icon, value, label, colorClass) {
        return `
            <div class="stat-card">
                <div class="stat-icon ${colorClass}"><i data-feather="${icon}"></i></div>
                <div class="stat-value">${value}</div>
                <div class="stat-label">${label}</div>
            </div>`;
    }

    function renderTable(type, data, headers) {
        contentArea.innerHTML = `
            <div class="data-card">
                <div class="data-header">
                    <h3>Manage ${type.charAt(0).toUpperCase() + type.slice(1)}</h3>
                    ${['jobs', 'categories', 'notifications'].includes(type) ? `<button class="primary-btn" onclick="${type === 'notifications' ? 'showNotificationModal()' : `showModal('${type}')`}">Add ${type === 'notifications' ? 'Notification' : type.slice(0, -1)}</button>` : ''}
                </div>
                <div class="table-container">
                    <table>
                        <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}<th>Actions</th></tr></thead>
                        <tbody>${data.map(item => createTableRow(type, item)).join('')}</tbody>
                    </table>
                </div>
            </div>`;
        feather.replace();
    }

    async function fetchData(url) {
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });
        return handleResponse(response);
    }

    // Helper to handle both methods
    async function handleResponse(response) {
        if (response.status === 401) {
            localStorage.removeItem('access_token');
            state.token = null;
            showLogin();
            throw new Error('Unauthorized');
        }
        if (!response.ok) {
            let detail = `API Error (${response.status})`;
            try {
                const err = await response.json();
                detail = err.detail || detail;
            } catch (e) { }
            throw new Error(detail);
        }
        return await response.json();
    }

    function createTableRow(type, item) {
        let cells = [];
        if (type === 'users') {
            const premium = item.is_premium ? `<span class="badge premium">Premium</span>` : `<span class="badge free">Free</span>`;
            const pwd = `<span class="pwd-truncate" title="${item.hashed_password}">${item.hashed_password.substring(0, 8)}...</span>`;
            cells = [item.id, item.full_name, item.phone_number, item.role, premium, pwd, item.is_active ? 'Active' : 'Inactive'];
        } else if (type === 'jobs') cells = [item.title, item.company_name, `${item.min_salary || 0}-${item.max_salary || 0}`, new Date(item.created_at).toLocaleDateString()];
        else if (type === 'categories') cells = [item.id, item.name, item.image_url ? `<img src="${item.image_url}" style="width: 30px; height: 30px; border-radius: 4px;">` : 'None'];
        else if (type === 'applications') {
            cells = [item.id, item.job?.title || 'Unknown Job', item.full_name, item.phone_number, new Date(item.applied_at).toLocaleDateString()];
        } else if (type === 'contact_requests') {
            cells = [item.id, item.name, item.phone_number, new Date(item.created_at).toLocaleDateString()];
        } else if (type === 'notifications') {
            const msg = item.message || '';
            const truncated = msg.length > 30 ? msg.substring(0, 30) + '...' : msg;
            cells = [item.id, item.user_id, item.title, truncated, new Date(item.created_at).toLocaleDateString()];
        }

        return `
            <tr>
                ${cells.map(c => `<td>${c}</td>`).join('')}
                <td>
                    <div class="action-btns">
                        ${type === 'users' ? `
                        <button class="btn-icon view" onclick='showUserDetails(${JSON.stringify(item).replace(/'/g, "&apos;")})'>
                            <i data-feather="eye"></i>
                        </button>
                        <button class="btn-icon notify" title="Send Notification" onclick="showNotificationModal(${item.id})">
                            <i data-feather="bell"></i>
                        </button>` : ''}
                        ${type === 'applications' ? `
                        <button class="btn-icon view" title="View Cover Letter" onclick='showApplicationDetails(${JSON.stringify(item).replace(/'/g, "&apos;")})'>
                            <i data-feather="file-text"></i>
                        </button>
                        <button class="btn-icon notify" title="Send Notification" onclick="showNotificationModal(${item.applicant_id})">
                            <i data-feather="bell"></i>
                        </button>` : ''}
                        ${type === 'contact_requests' ? `
                        <button class="btn-icon view" title="View Letter" onclick='showContactDetails(${JSON.stringify(item).replace(/'/g, "&apos;")})'>
                            <i data-feather="mail"></i>
                        </button>` : ''}
                        ${type === 'notifications' ? `
                        <button class="btn-icon view" title="View Message" onclick='showNotificationDetails(${JSON.stringify(item).replace(/'/g, "&apos;")})'>
                            <i data-feather="eye"></i>
                        </button>` : ''}
                        ${['jobs', 'categories'].includes(type) ? `
                        <button class="btn-icon edit" onclick='showModal("${type}", ${JSON.stringify(item).replace(/'/g, "&apos;")})'>
                            <i data-feather="edit-2"></i>
                        </button>` : ''}
                        <button class="btn-icon delete" onclick="deleteItem('${type}', ${item.id})"><i data-feather="trash-2"></i></button>
                    </div>
                </td>
            </tr>`;
    }

    window.showUserDetails = (user) => {
        modalTitle.innerText = "User Details";
        formFields.innerHTML = `
            <div class="user-details-grid">
                <div class="detail-item"><strong>Full Name:</strong> ${user.full_name}</div>
                <div class="detail-item"><strong>Phone:</strong> ${user.phone_number}</div>
                <div class="detail-item"><strong>Email:</strong> ${user.email || 'N/A'}</div>
                <div class="detail-item"><strong>Role:</strong> ${user.role}</div>
                <div class="detail-item"><strong>Premium:</strong> ${user.is_premium ? 'Yes' : 'No'}</div>
                <div class="detail-item"><strong>Premium Expires:</strong> ${user.premium_expires_at ? new Date(user.premium_expires_at).toLocaleString() : 'N/A'}</div>
                <div class="detail-item"><strong>Status:</strong> ${user.is_active ? 'Active' : 'Inactive'}</div>
                <div class="detail-item"><strong>Company:</strong> ${user.company_name || 'N/A'}</div>
                <div class="detail-item"><strong>City:</strong> ${user.city || 'N/A'}</div>
                <div class="detail-item"><strong>Location:</strong> ${user.location || 'N/A'}</div>
                <div class="detail-item wide"><strong>Description:</strong> ${user.company_description || 'N/A'}</div>
                <div class="detail-item wide"><strong>Hashed Password:</strong> <code class="pwd-code">${user.hashed_password}</code></div>
                <div class="detail-item wide" style="text-align: right; background: transparent; border: none;">
                    <button class="primary-btn danger" onclick="resetUserPassword(${user.id})">Reset Password</button>
                </div>
            </div>
        `;
        // Hide the save button for view-only modal
        const formActions = modalForm.querySelector('.form-actions');
        if (formActions) formActions.classList.add('hidden');
        modal.classList.remove('hidden');
        feather.replace();
    };

    window.showApplicationDetails = (app) => {
        modalTitle.innerText = "Application Details";
        formFields.innerHTML = `
            <div class="user-details-grid">
                <div class="detail-item"><strong>Job Title:</strong> ${app.job?.title || 'N/A'}</div>
                <div class="detail-item"><strong>Applicant:</strong> ${app.full_name}</div>
                <div class="detail-item"><strong>Phone:</strong> ${app.phone_number}</div>
                <div class="detail-item"><strong>Applied At:</strong> ${new Date(app.applied_at).toLocaleString()}</div>
                <div class="detail-item wide"><strong>Cover Letter:</strong> 
                    <div style="padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-top:8px; white-space: pre-wrap;">
                        ${app.cover_letter || 'No cover letter provided.'}
                    </div>
                </div>
            </div>
        `;
        const formActions = modalForm.querySelector('.form-actions');
        if (formActions) formActions.classList.add('hidden');
        modal.classList.remove('hidden');
        feather.replace();
    };

    window.showContactDetails = (contact) => {
        modalTitle.innerText = "Contact Request Details";
        formFields.innerHTML = `
            <div class="user-details-grid">
                <div class="detail-item"><strong>ID:</strong> ${contact.id}</div>
                <div class="detail-item"><strong>Name:</strong> ${contact.name}</div>
                <div class="detail-item"><strong>Phone:</strong> ${contact.phone_number}</div>
                <div class="detail-item"><strong>Date:</strong> ${new Date(contact.created_at).toLocaleString()}</div>
                <div class="detail-item wide"><strong>Letter:</strong> 
                    <div style="padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-top:8px; white-space: pre-wrap;">
                        ${contact.letter || 'No letter provided.'}
                    </div>
                </div>
            </div>
        `;
        const formActions = modalForm.querySelector('.form-actions');
        if (formActions) formActions.classList.add('hidden');
        modal.classList.remove('hidden');
        feather.replace();
    };

    window.showNotificationModal = async (userId = null) => {
        modalTitle.innerText = "Send Notification";

        if (userId) {
            formFields.innerHTML = `
                <input type="hidden" id="notif-user-id" value="${userId}">
                <div class="form-group">
                    <label>Recipient ID</label>
                    <input type="text" value="${userId}" disabled style="background: rgba(255,255,255,0.05);">
                </div>
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" id="notif-title" placeholder="Message title" required>
                </div>
                <div class="form-group">
                    <label>Message</label>
                    <textarea id="notif-message" rows="4" placeholder="Enter notification message..." required></textarea>
                </div>
            `;
        } else {
            formFields.innerHTML = `<div class="loading-spinner">Loading users...</div>`;
            try {
                const users = await fetchData('/api/admin/users');
                const userOptions = users.map(u => `<option value="${u.id}">ID: ${u.id} | ${u.full_name}</option>`).join('');

                formFields.innerHTML = `
                    <div class="form-group">
                        <label>Select Recipient</label>
                        <select id="notif-user-id" required style="width:100%; padding:10px; background:var(--bg-secondary); border:1px solid var(--border-color); border-radius:8px; color:var(--text-primary);">
                            <option value="">-- Choose User --</option>
                            ${userOptions}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Title</label>
                        <input type="text" id="notif-title" placeholder="Message title" required>
                    </div>
                    <div class="form-group">
                        <label>Message</label>
                        <textarea id="notif-message" rows="4" placeholder="Enter notification message..." required></textarea>
                    </div>
                `;
            } catch (err) {
                formFields.innerHTML = `<div class="error">Failed to load users: ${err.message}</div>`;
            }
        }

        const formActions = modalForm.querySelector('.form-actions');
        if (formActions) formActions.classList.remove('hidden');
        modal.classList.remove('hidden');
        feather.replace();
    };

    modalForm.onsubmit = async (e) => {
        e.preventDefault();
        const data = {
            user_id: parseInt(document.getElementById('notif-user-id').value),
            title: document.getElementById('notif-title').value,
            message: document.getElementById('notif-message').value
        };

        try {
            const res = await fetch('/api/admin/notifications', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${state.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                alert('Notification sent!');
                modal.classList.add('hidden');
                modalForm.onsubmit = handleModalSubmit;
            } else {
                const err = await res.json();
                alert('Failed: ' + (err.detail || 'check console'));
            }
        } catch (err) {
            alert('Error: ' + err.message);
        }
    };

    window.showNotificationDetails = (notif) => {
        modalTitle.innerText = "Notification Details";
        formFields.innerHTML = `
            <div class="user-details-grid">
                <div class="detail-item"><strong>ID:</strong> ${notif.id}</div>
                <div class="detail-item"><strong>User ID:</strong> ${notif.user_id}</div>
                <div class="detail-item"><strong>Title:</strong> ${notif.title}</div>
                <div class="detail-item"><strong>Date:</strong> ${new Date(notif.created_at).toLocaleString()}</div>
                <div class="detail-item wide"><strong>Message:</strong> 
                    <div style="padding: 12px; background: rgba(255,255,255,0.03); border-radius: 8px; margin-top:8px; white-space: pre-wrap;">
                        ${notif.message}
                    </div>
                </div>
            </div>
        `;
        const formActions = modalForm.querySelector('.form-actions');
        if (formActions) formActions.classList.add('hidden');
        modal.classList.remove('hidden');
        feather.replace();
    };

    window.resetUserPassword = async (userId) => {
        const newPassword = prompt("Foydalanuvchi uchun yangi parol kiriting:");
        if (!newPassword || newPassword.length < 4) {
            alert("Parol juda qisqa yoki bekor qilindi.");
            return;
        }

        try {
            const res = await fetch(`/api/admin/users/${userId}/reset-password`, {
                method: 'PUT',
                headers: {
                    'Authorization': `Bearer ${state.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ new_password: newPassword })
            });

            if (res.ok) {
                alert("Parol muvaffaqiyatli yangilandi!");
                modal.classList.add('hidden');
                switchView('users');
            } else {
                const err = await res.json();
                alert('Xatolik: ' + (err.detail || 'parolni o\'zgartirib bo\'lmadi'));
            }
        } catch (err) {
            alert('Error: ' + err.message);
        }
    };

    // Modal Handling
    const _originalShowModal = window.showModal; // Capture the original showModal
    window.showModal = (type, item = null) => {
        // Ensure the save button is visible when opening a modal for editing/adding
        const formActions = modalForm.querySelector('.form-actions');
        if (formActions) formActions.classList.remove('hidden');

        state.modalType = type;
        state.editItem = item;
        modalTitle.innerText = item ? `Edit ${type.slice(0, -1)}` : `Add New ${type.slice(0, -1)}`;

        // Generate Form Content
        formFields.innerHTML = generateFormFields(type, item);
        modal.classList.remove('hidden');
        feather.replace();
    };

    function generateFormFields(type, item) {
        if (type === 'categories') {
            return `
                <div class="form-group">
                    <label>Category Name</label>
                    <input type="text" name="name" value="${item ? item.name : ''}" required>
                </div>
                <div class="form-group">
                    <label>Icon Image</label>
                    <div class="file-input-group">
                        <input type="hidden" name="image_url" id="category-image-url" value="${item ? (item.image_url || '') : ''}">
                        <div class="file-preview" id="category-preview">
                            ${item && item.image_url ? `<img src="${item.image_url}">` : '<i data-feather="image"></i>'}
                        </div>
                        <input type="file" id="category-file" style="display:none" onchange="handleFileUpload(event, 'category')">
                        <button type="button" class="btn-icon" onclick="document.getElementById('category-file').click()">
                            <i data-feather="upload"></i>
                        </button>
                    </div>
                </div>
            `;
        } else if (type === 'jobs') {
            return `
                <div class="form-group">
                    <label>Title</label>
                    <input type="text" name="title" value="${item ? item.title : ''}" required>
                </div>
                <div class="form-group">
                    <label>Company Name</label>
                    <input type="text" name="company_name" value="${item ? item.company_name : ''}">
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <textarea name="description" rows="4">${item ? item.description : ''}</textarea>
                </div>
                <div class="form-group">
                    <label>Job Image URL</label>
                    <div class="file-input-group">
                        <input type="hidden" name="job_image_url" id="job-image-url" value="${item ? (item.job_image_url || '') : ''}">
                        <div class="file-preview" id="job-preview">
                            ${item && item.job_image_url ? `<img src="${item.job_image_url}">` : '<i data-feather="image"></i>'}
                        </div>
                        <input type="file" id="job-file" style="display:none" onchange="handleFileUpload(event, 'job')">
                        <button type="button" class="btn-icon" onclick="document.getElementById('job-file').click()">
                            <i data-feather="upload"></i>
                        </button>
                    </div>
                </div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
                    <div class="form-group">
                        <label>Min Salary</label>
                        <input type="number" name="min_salary" value="${item ? item.min_salary : ''}">
                    </div>
                    <div class="form-group">
                        <label>Max Salary</label>
                        <input type="number" name="max_salary" value="${item ? item.max_salary : ''}">
                    </div>
                </div>
            `;
        }
        return '';
    }

    window.handleFileUpload = async (e, type) => {
        const file = e.target.files[0];
        if (!file) return;

        const formData = new FormData();
        formData.append('file', file);

        try {
            const res = await fetch('/api/upload', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${state.token}` },
                body: formData
            });
            const data = await res.json();

            if (res.ok) {
                // Update hidden input and preview
                const urlInput = document.getElementById(`${type}-image-url`);
                const preview = document.getElementById(`${type}-preview`);
                // Use the filename for saving to DB (backend prepends base_url on return)
                urlInput.value = data.filename;
                preview.innerHTML = `<img src="/uploads/${data.filename}">`;
            } else {
                alert('Upload failed: ' + data.detail);
            }
        } catch (err) {
            alert('Upload error: ' + err.message);
        }
    };

    async function handleModalSubmit(e) {
        e.preventDefault();
        const formData = new FormData(modalForm);
        const data = Object.fromEntries(formData.entries());

        // Convert some strings to numbers
        if (data.min_salary) data.min_salary = parseInt(data.min_salary);
        if (data.max_salary) data.max_salary = parseInt(data.max_salary);

        const method = state.editItem ? 'PUT' : 'POST';
        const url = state.editItem
            ? `/api/admin/${state.modalType}/${state.editItem.id}`
            : `/api/admin/${state.modalType}`;

        try {
            const res = await fetch(url, {
                method,
                headers: {
                    'Authorization': `Bearer ${state.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (res.ok) {
                modal.classList.add('hidden');
                renderView(state.currentView);
            } else {
                const err = await res.json();
                alert('Action failed: ' + (err.detail || 'check console'));
            }
        } catch (err) {
            alert('Error: ' + err.message);
        }
    }

    async function fetchData(url) {
        const response = await fetch(url, {
            headers: { 'Authorization': `Bearer ${state.token}` }
        });

        if (response.status === 401) {
            localStorage.removeItem('access_token');
            state.token = null;
            showLogin();
            throw new Error('Unauthorized');
        }

        if (!response.ok) throw new Error('API Error');
        return await response.json();
    }

    window.deleteItem = async (type, id) => {
        if (!confirm('Are you sure?')) return;
        try {
            const res = await fetch(`/api/admin/${type}/${id}`, {
                method: 'DELETE',
                headers: { 'Authorization': `Bearer ${state.token}` }
            });
            if (res.ok) {
                renderView(state.currentView);
            } else {
                alert('Delete failed');
            }
        } catch (err) {
            alert('Error: ' + err.message);
        }
    };

    init();});
