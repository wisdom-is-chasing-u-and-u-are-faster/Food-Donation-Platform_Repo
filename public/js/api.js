/**
 * Enterprise Food Donation Platform - REST API Client SDK
 * Provides typed, asynchronous API fetch methods connecting UI screens to backend services.
 */

const API_BASE = '/api/v1';

const apiClient = {
    // Health Check
    async checkHealth() {
        const res = await fetch('/health');
        if (!res.ok) throw new Error('Health check failed');
        return res.json();
    },

    // Telemetry Endpoints
    async getAdminTelemetry() {
        const res = await fetch(`${API_BASE}/telemetry/admin`);
        if (!res.ok) throw new Error('Failed to load administrator telemetry');
        return res.json();
    },

    async getDonorTelemetry(donorId = null) {
        const url = donorId ? `${API_BASE}/telemetry/donor?donor_id=${encodeURIComponent(donorId)}` : `${API_BASE}/telemetry/donor`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to load donor telemetry');
        return res.json();
    },

    async getRecipientTelemetry(recipientId = null) {
        const url = recipientId ? `${API_BASE}/telemetry/recipient?recipient_id=${encodeURIComponent(recipientId)}` : `${API_BASE}/telemetry/recipient`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('Failed to load recipient telemetry');
        return res.json();
    },

    // Donations Management
    async createDonation(payload) {
        const res = await fetch(`${API_BASE}/donations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Failed to submit surplus donation');
        }
        return res.json();
    },

    async listDonations(status = null, category = null) {
        const params = new URLSearchParams();
        if (status) params.append('status', status);
        if (category) params.append('category', category);
        const res = await fetch(`${API_BASE}/donations?${params.toString()}`);
        if (!res.ok) throw new Error('Failed to fetch donations list');
        return res.json();
    },

    async getDonation(donationId) {
        const res = await fetch(`${API_BASE}/donations/${encodeURIComponent(donationId)}`);
        if (!res.ok) throw new Error('Failed to fetch donation details');
        return res.json();
    },

    // Geospatial Matching & Capacity
    async findRecipients(donationId, maxDistanceKm = 15.0) {
        const res = await fetch(`${API_BASE}/matching/find-recipients`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ donation_id: donationId, max_distance_km: maxDistanceKm })
        });
        if (!res.ok) throw new Error('Failed to match recipients');
        return res.json();
    },

    async reserveDonation(donationId, recipientId) {
        const res = await fetch(`${API_BASE}/matching/reserve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ donation_id: donationId, recipient_id: recipientId })
        });
        if (!res.ok) throw new Error('Failed to reserve donation');
        return res.json();
    },

    // Dual-Fleet Dispatch & 3PL Failover
    async updateDispatch(donationId, dispatchMode = 'VOLUNTEER', force3pl = false) {
        const res = await fetch(`${API_BASE}/dispatch/state`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ donation_id: donationId, dispatch_mode: dispatchMode, force_3pl: force3pl })
        });
        if (!res.ok) throw new Error('Failed to update dispatch state');
        return res.json();
    },

    // Cryptographic Handshake & Custody
    async verifyHandshake(donationId, step, otpToken, signature, verifierPublicKey) {
        const res = await fetch(`${API_BASE}/custody/handshake`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                donation_id: donationId,
                step: step,
                otp_token: otpToken,
                signature: signature,
                verifier_public_key: verifierPublicKey
            })
        });
        if (!res.ok) throw new Error('Handshake verification failed');
        return res.json();
    },

    async getCustodyLedger(donationId) {
        const res = await fetch(`${API_BASE}/custody/ledger/${encodeURIComponent(donationId)}`);
        if (!res.ok) throw new Error('Failed to fetch custody ledger');
        return res.json();
    },

    // HACCP Thermal Telemetry
    async logThermalReading(donationId, tempF, ambientTempF, sensorId) {
        const res = await fetch(`${API_BASE}/telemetry/thermal-log`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                donation_id: donationId,
                temp_f: tempF,
                ambient_temp_f: ambientTempF,
                sensor_id: sensorId
            })
        });
        if (!res.ok) throw new Error('Failed to log thermal reading');
        return res.json();
    },

    // ESG Analytics
    async getESGAnalytics() {
        const res = await fetch(`${API_BASE}/analytics/esg`);
        if (!res.ok) throw new Error('Failed to fetch ESG analytics');
        return res.json();
    }
};

window.apiClient = apiClient;
