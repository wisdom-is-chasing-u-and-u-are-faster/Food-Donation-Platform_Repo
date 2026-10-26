-- =================================================================
-- Enterprise Food Donation Platform - DDL Schema
-- Compatible with PostgreSQL (PostGIS) and SQLite
-- =================================================================

-- 1. Organizations (Donors, Recipient Shelters, Pantries)
CREATE TABLE IF NOT EXISTS organizations (
    org_id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    org_type VARCHAR(32) NOT NULL CHECK (org_type IN ('DONOR', 'RECIPIENT', '3PL_PARTNER')),
    address VARCHAR(255) NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    phone VARCHAR(32),
    capacity_lbs REAL DEFAULT 1000.0,
    current_used_lbs REAL DEFAULT 0.0,
    has_cold_storage BOOLEAN DEFAULT 1,
    has_hot_holding BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Surplus Food Donations
CREATE TABLE IF NOT EXISTS donations (
    donation_id VARCHAR(64) PRIMARY KEY,
    donor_id VARCHAR(64) NOT NULL,
    food_category VARCHAR(64) NOT NULL,
    description TEXT NOT NULL,
    weight_lbs REAL NOT NULL CHECK (weight_lbs > 0),
    initial_temp_f REAL NOT NULL,
    is_perishable BOOLEAN DEFAULT 1,
    pickup_latitude REAL NOT NULL,
    pickup_longitude REAL NOT NULL,
    pickup_address VARCHAR(255) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'AVAILABLE' CHECK (status IN ('AVAILABLE', 'MATCHED', 'DISPATCHED', 'IN_TRANSIT', 'COMPLETED', 'REJECTED')),
    haccp_status VARCHAR(32) NOT NULL DEFAULT 'COMPLIANT' CHECK (haccp_status IN ('COMPLIANT', 'WARNING', 'VIOLATION')),
    expiration_minutes INTEGER DEFAULT 180,
    qr_handshake_secret VARCHAR(128),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donor_id) REFERENCES organizations(org_id)
);

-- 3. Geospatial Proximity Matches & Reservations
CREATE TABLE IF NOT EXISTS matches (
    match_id VARCHAR(64) PRIMARY KEY,
    donation_id VARCHAR(64) NOT NULL,
    recipient_id VARCHAR(64) NOT NULL,
    distance_km REAL NOT NULL,
    score REAL DEFAULT 1.0,
    status VARCHAR(32) NOT NULL DEFAULT 'PROPOSED' CHECK (status IN ('PROPOSED', 'RESERVED', 'ACCEPTED', 'EXPIRED')),
    match_latency_ms REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donation_id) REFERENCES donations(donation_id),
    FOREIGN KEY (recipient_id) REFERENCES organizations(org_id)
);

-- 4. Dual-Fleet Dispatch State Machine (Volunteer vs 3PL Failover)
CREATE TABLE IF NOT EXISTS dispatches (
    dispatch_id VARCHAR(64) PRIMARY KEY,
    donation_id VARCHAR(64) NOT NULL,
    fleet_type VARCHAR(32) NOT NULL DEFAULT 'VOLUNTEER' CHECK (fleet_type IN ('VOLUNTEER', '3PL_DOORDASH', '3PL_UBER')),
    provider VARCHAR(64) NOT NULL DEFAULT 'CommunityVolunteerFleet',
    status VARCHAR(32) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'ACCEPTED', 'EN_ROUTE_PICKUP', 'PICKED_UP', 'IN_TRANSIT', 'DELIVERED', 'FAILED', 'EXPIRED')),
    courier_name VARCHAR(128) DEFAULT 'Unassigned Volunteer',
    courier_phone VARCHAR(32) DEFAULT '555-0199',
    ttl_seconds INTEGER DEFAULT 300,
    tracking_url VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donation_id) REFERENCES donations(donation_id)
);

-- 5. Immutable SHA-256 Custody Ledger
CREATE TABLE IF NOT EXISTS custody_ledger (
    block_id VARCHAR(64) PRIMARY KEY,
    donation_id VARCHAR(64) NOT NULL,
    block_index INTEGER NOT NULL,
    prev_hash VARCHAR(128) NOT NULL,
    current_hash VARCHAR(128) NOT NULL,
    action VARCHAR(64) NOT NULL,
    actor_id VARCHAR(64) NOT NULL,
    otp_token VARCHAR(32),
    signature VARCHAR(255),
    verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donation_id) REFERENCES donations(donation_id)
);

-- 6. HACCP Thermal Telemetry & Biological Safety Transit Windows
CREATE TABLE IF NOT EXISTS thermal_telemetry (
    reading_id VARCHAR(64) PRIMARY KEY,
    donation_id VARCHAR(64) NOT NULL,
    temp_f REAL NOT NULL,
    ambient_temp_f REAL NOT NULL,
    sensor_id VARCHAR(64) NOT NULL,
    is_compliant BOOLEAN NOT NULL,
    biological_window_remaining_minutes REAL NOT NULL,
    warning VARCHAR(255),
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (donation_id) REFERENCES donations(donation_id)
);

-- 7. ESG Carbon-Offset & Waste Elimination Analytics
CREATE TABLE IF NOT EXISTS esg_analytics (
    entry_id VARCHAR(64) PRIMARY KEY,
    donation_id VARCHAR(64),
    rescued_weight_lbs REAL NOT NULL,
    co2_offset_kg REAL NOT NULL,
    water_saved_gallons REAL NOT NULL,
    meals_provided INTEGER NOT NULL,
    month_year VARCHAR(16) NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for high-performance spatial & time-series queries
CREATE INDEX IF NOT EXISTS idx_donations_status ON donations(status);
CREATE INDEX IF NOT EXISTS idx_donations_created ON donations(created_at);
CREATE INDEX IF NOT EXISTS idx_orgs_location ON organizations(latitude, longitude);
CREATE INDEX IF NOT EXISTS idx_matches_donation ON matches(donation_id);
CREATE INDEX IF NOT EXISTS idx_dispatches_donation ON dispatches(donation_id);
CREATE INDEX IF NOT EXISTS idx_custody_donation ON custody_ledger(donation_id);
CREATE INDEX IF NOT EXISTS idx_thermal_donation ON thermal_telemetry(donation_id);
