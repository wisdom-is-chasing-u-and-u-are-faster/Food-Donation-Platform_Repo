/**
 * Enterprise Food Donation Platform - Live Telemetry & Dashboard Controller
 * Implements automated 15-30s polling engine, countdown timer, and dynamic DOM updating.
 */

let refreshTimer = null;
let countdownSeconds = 20;
const REFRESH_INTERVAL = 20;

document.addEventListener('DOMContentLoaded', () => {
    initDashboard();
    startAutoRefresh();
});

function initDashboard() {
    loadActiveViewData();
    setupEventListeners();
}

function startAutoRefresh() {
    countdownSeconds = REFRESH_INTERVAL;
    updateCountdownUI();

    if (refreshTimer) clearInterval(refreshTimer);

    refreshTimer = setInterval(() => {
        countdownSeconds -= 1;
        if (countdownSeconds <= 0) {
            countdownSeconds = REFRESH_INTERVAL;
            loadActiveViewData();
        }
        updateCountdownUI();
    }, 1000);
}

function updateCountdownUI() {
    const el = document.getElementById('refreshTimerDisplay');
    if (el) {
        el.textContent = `Auto-refresh: ${countdownSeconds}s`;
    }
}

async function loadActiveViewData() {
    try {
        const pageType = document.body.dataset.page;
        if (pageType === 'admin') {
            await loadAdminView();
        } else if (pageType === 'donor') {
            await loadDonorView();
        } else if (pageType === 'recipient') {
            await loadRecipientView();
        } else if (pageType === 'overview') {
            await loadOverview();
        }
    } catch (err) {
        console.error('Error loading telemetry view:', err);
    }
}

async function loadOverview() {
    const adminData = await apiClient.getAdminTelemetry();
    const esgData = await apiClient.getESGAnalytics();
    
    setText('activeDonationsCount', adminData.active_donations);
    setText('matchLatencyP99', `${adminData.match_latency_p99_seconds}s`);
    setText('fulfillmentRate', `${adminData.claim_fulfillment_rate_percent}%`);
    setText('complianceRate', `${adminData.safe_transit_compliance_percent}%`);
    setText('totalRescuedLbs', `${Number(adminData.total_pounds_rescued).toLocaleString()} lbs`);
    setText('co2SavedKg', `${Number(adminData.co2_offset_kg).toLocaleString()} kg`);

    renderDispatchesTable(adminData.recent_dispatches || []);
}

async function loadAdminView() {
    const data = await apiClient.getAdminTelemetry();
    setText('activeDonationsCount', data.active_donations);
    setText('matchLatencyP99', `${data.match_latency_p99_seconds}s`);
    setText('fulfillmentRate', `${data.claim_fulfillment_rate_percent}%`);
    setText('complianceRate', `${data.safe_transit_compliance_percent}%`);
    setText('activeFailovers', data.active_3pl_failovers);
    setText('haccpViolations', data.haccp_violations_count);
    
    renderDispatchesTable(data.recent_dispatches || []);
}

async function loadDonorView() {
    const donorId = document.getElementById('donorSelector')?.value || 'org_donor_001';
    const data = await apiClient.getDonorTelemetry(donorId);
    
    setText('donorNameHeader', data.donor_name);
    setText('donorTotalCount', data.total_donations_count);
    setText('donorWeightLbs', `${Number(data.pounds_donated_month).toLocaleString()} lbs`);
    setText('donorMealsCount', Number(data.meals_provided).toLocaleString());
    setText('donorCarbonSaved', `${Number(data.esg_carbon_saved_kg).toLocaleString()} kg`);

    renderDonorListings(data.active_listings || []);
}

async function loadRecipientView() {
    const recipId = document.getElementById('recipientSelector')?.value || 'org_recip_001';
    const data = await apiClient.getRecipientTelemetry(recipId);

    setText('recipientOrgName', data.organization_name);
    setText('capacityPercent', `${data.storage_capacity_used_percent}%`);
    setText('mealsDistributed', Number(data.meals_distributed).toLocaleString());
    setText('safeWindowTimer', `${Math.floor(data.safe_window_timer_seconds / 60)} mins`);

    renderIncomingDeliveries(data.incoming_deliveries || []);
}

function renderDispatchesTable(dispatches) {
    const tbody = document.getElementById('dispatchesTableBody');
    if (!tbody) return;

    if (dispatches.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center" style="text-align: center; color: var(--text-muted);">No active dispatches found.</td></tr>';
        return;
    }

    tbody.innerHTML = dispatches.map(d => `
        <tr>
            <td><strong>${d.dispatch_id}</strong></td>
            <td>${d.food_category} (${d.weight_lbs} lbs)</td>
            <td><span class="badge ${d.fleet_type.startsWith('3PL') ? 'badge-warning' : 'badge-primary'}">${d.provider}</span></td>
            <td><span class="badge badge-success">${d.status}</span></td>
            <td>${d.ttl_seconds}s</td>
            <td>
                <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" onclick="triggerFailover('${d.donation_id}')">
                    3PL Failover
                </button>
            </td>
        </tr>
    `).join('');
}

function renderDonorListings(listings) {
    const tbody = document.getElementById('donorListingsBody');
    if (!tbody) return;

    if (listings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: var(--text-muted);">No surplus listings yet. Create your first donation above.</td></tr>';
        return;
    }

    tbody.innerHTML = listings.map(l => `
        <tr>
            <td><strong>${l.donation_id}</strong></td>
            <td>${l.food_category}</td>
            <td>${l.weight_lbs} lbs</td>
            <td>${l.initial_temp_f}°F (<span class="badge badge-success">${l.haccp_status}</span>)</td>
            <td><span class="badge badge-info">${l.status}</span></td>
        </tr>
    `).join('');
}

function renderIncomingDeliveries(incoming) {
    const container = document.getElementById('incomingDeliveriesList');
    if (!container) return;

    if (incoming.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); padding: 1rem 0;">No incoming food deliveries at this time.</p>';
        return;
    }

    container.innerHTML = incoming.map(inc => `
        <div style="border: 1px solid var(--border); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 0.75rem; background: var(--bg-page);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
                <strong>${inc.food_category} (${inc.weight_lbs} lbs)</strong>
                <span class="badge badge-warning">${inc.delivery_status || 'In Transit'}</span>
            </div>
            <p style="font-size: 0.8125rem; color: var(--text-muted); margin-bottom: 0.5rem;">
                Courier: ${inc.courier_name || 'Volunteer Fleet'} (${inc.provider || 'Local Mesh'}) | Core Temp: ${inc.initial_temp_f}°F
            </p>
            <button class="btn btn-primary" style="padding: 0.35rem 0.75rem; font-size: 0.75rem;" onclick="openVerificationModal('${inc.donation_id}')">
                Verify Inbound Handshake (OTP/QR)
            </button>
        </div>
    `).join('');
}

function setupEventListeners() {
    const donationForm = document.getElementById('surplusIngestForm');
    if (donationForm) {
        donationForm.addEventListener('submit', handleDonationSubmit);
    }

    const donorSelect = document.getElementById('donorSelector');
    if (donorSelect) {
        donorSelect.addEventListener('change', loadDonorView);
    }

    const recipSelect = document.getElementById('recipientSelector');
    if (recipSelect) {
        recipSelect.addEventListener('change', loadRecipientView);
    }

    const manualRefreshBtn = document.getElementById('manualRefreshBtn');
    if (manualRefreshBtn) {
        manualRefreshBtn.addEventListener('click', () => {
            loadActiveViewData();
            startAutoRefresh();
        });
    }
}

async function handleDonationSubmit(e) {
    e.preventDefault();
    const alertBox = document.getElementById('formAlertBox');
    try {
        const payload = {
            donor_id: document.getElementById('donorIdInput').value || 'org_donor_001',
            food_category: document.getElementById('foodCategoryInput').value,
            description: document.getElementById('descriptionInput').value,
            weight_lbs: parseFloat(document.getElementById('weightInput').value),
            initial_temp_f: parseFloat(document.getElementById('tempInput').value),
            is_perishable: document.getElementById('perishableInput').checked,
            pickup_latitude: 37.7935,
            pickup_longitude: -122.3965,
            pickup_address: document.getElementById('addressInput').value || '101 Market St, San Francisco, CA',
            expiration_minutes: 180
        };

        const result = await apiClient.createDonation(payload);
        if (alertBox) {
            alertBox.className = 'alert alert-success';
            alertBox.style.display = 'block';
            alertBox.innerHTML = `✅ Surplus donation registered successfully! ID: <strong>${result.donation_id}</strong> (HACCP: ${result.haccp_status})`;
        }
        e.target.reset();
        await loadActiveViewData();
    } catch (err) {
        if (alertBox) {
            alertBox.className = 'alert alert-danger';
            alertBox.style.display = 'block';
            alertBox.textContent = `❌ ${err.message}`;
        }
    }
}

async function triggerFailover(donationId) {
    try {
        await apiClient.updateDispatch(donationId, '3PL_DOORDASH', true);
        alert(`Dispatched 3PL failover to DoorDash Drive for donation ${donationId}.`);
        await loadActiveViewData();
    } catch (err) {
        alert(`Failover failed: ${err.message}`);
    }
}

async function openVerificationModal(donationId) {
    const otp = prompt(`Enter 4-digit recipient verification OTP for donation ${donationId}:`, '9182');
    if (!otp) return;
    try {
        const res = await apiClient.verifyHandshake(donationId, 'RECIPIENT_DELIVERY_CONFIRMED', otp, 'SIG_ECDSA_RECIP_001', 'PUBKEY_RECIP_ST_ANTHONY');
        alert(`✅ Handshake verified! Cryptographic Block Hash: ${res.ledger_hash.substring(0, 16)}...`);
        await loadActiveViewData();
    } catch (err) {
        alert(`Verification failed: ${err.message}`);
    }
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}
