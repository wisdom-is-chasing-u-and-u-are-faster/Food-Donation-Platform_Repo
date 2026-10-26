-- =================================================================
-- Enterprise Food Donation Platform - DML Seed Data
-- =================================================================

-- 1. Seed Organizations
INSERT OR REPLACE INTO organizations (org_id, name, org_type, address, latitude, longitude, contact_email, phone, capacity_lbs, current_used_lbs, has_cold_storage, has_hot_holding)
VALUES 
('org_donor_001', 'Metro Whole Foods Market', 'DONOR', '101 Market St, San Francisco, CA', 37.7935, -122.3965, 'donations@metrowholefoods.com', '415-555-0101', 5000.0, 0.0, 1, 1),
('org_donor_002', 'Bistro Del Sol Catering', 'DONOR', '450 Mission St, San Francisco, CA', 37.7901, -122.3985, 'chef@bistrodelsol.com', '415-555-0102', 2000.0, 0.0, 1, 1),
('org_donor_003', 'Golden Gate Organic Bakery', 'DONOR', '820 Post St, San Francisco, CA', 37.7872, -122.4173, 'surplus@goldengatebakery.org', '415-555-0103', 1500.0, 0.0, 1, 0),
('org_recip_001', 'St. Anthony Foundation Dining Room', 'RECIPIENT', '150 Golden Gate Ave, San Francisco, CA', 37.7821, -122.4144, 'logistics@stanthonysf.org', '415-555-0201', 8000.0, 3200.0, 1, 1),
('org_recip_002', 'Glide Memorial Community Kitchen', 'RECIPIENT', '330 Ellis St, San Francisco, CA', 37.7852, -122.4116, 'intake@glide.org', '415-555-0202', 6000.0, 2100.0, 1, 1),
('org_recip_003', 'Mission Neighborhood Food Pantry', 'RECIPIENT', '2450 Mission St, San Francisco, CA', 37.7588, -122.4191, 'relief@missionpantry.org', '415-555-0203', 4000.0, 1850.0, 1, 0),
('org_3pl_001', 'DoorDash Drive Logistics Mesh', '3PL_PARTNER', '901 Market St, San Francisco, CA', 37.7831, -122.4065, 'dispatch@doordash.com', '800-555-3333', 99999.0, 0.0, 1, 1),
('org_3pl_002', 'Uber Direct Rapid Mesh', '3PL_PARTNER', '1455 Market St, San Francisco, CA', 37.7758, -122.4180, 'dispatch@uber.com', '800-555-4444', 99999.0, 0.0, 1, 1);

-- 2. Seed Donations
INSERT OR REPLACE INTO donations (donation_id, donor_id, food_category, description, weight_lbs, initial_temp_f, is_perishable, pickup_latitude, pickup_longitude, pickup_address, status, haccp_status, expiration_minutes, qr_handshake_secret, created_at)
VALUES 
('don_1001', 'org_donor_001', 'Prepared Meals', '50 Gourmet Rotisserie Chicken & Roasted Veggies Trays', 220.0, 142.5, 1, 37.7935, -122.3965, '101 Market St, San Francisco, CA', 'IN_TRANSIT', 'COMPLIANT', 120, 'sec_ecdsa_seed_don1001', datetime('now', '-25 minutes')),
('don_1002', 'org_donor_002', 'Fresh Produce', '12 Crates Organic Apples, Oranges, & Baby Spinach', 380.0, 38.0, 1, 37.7901, -122.3985, '450 Mission St, San Francisco, CA', 'MATCHED', 'COMPLIANT', 240, 'sec_ecdsa_seed_don1002', datetime('now', '-10 minutes')),
('don_1003', 'org_donor_003', 'Artisan Bakery', '80 Loaves Sourdough and Whole Grain Bread', 120.0, 68.0, 0, 37.7872, -122.4173, '820 Post St, San Francisco, CA', 'AVAILABLE', 'COMPLIANT', 360, 'sec_ecdsa_seed_don1003', datetime('now', '-2 minutes'));

-- 3. Seed Matches
INSERT OR REPLACE INTO matches (match_id, donation_id, recipient_id, distance_km, score, status, match_latency_ms, created_at)
VALUES 
('match_501', 'don_1001', 'org_recip_001', 1.85, 0.98, 'RESERVED', 18.4, datetime('now', '-24 minutes')),
('match_502', 'don_1002', 'org_recip_002', 1.25, 0.95, 'PROPOSED', 14.2, datetime('now', '-9 minutes'));

-- 4. Seed Dispatches
INSERT OR REPLACE INTO dispatches (dispatch_id, donation_id, fleet_type, provider, status, courier_name, courier_phone, ttl_seconds, tracking_url, created_at, updated_at)
VALUES 
('disp_801', 'don_1001', 'VOLUNTEER', 'SF Community Volunteers', 'IN_TRANSIT', 'Alex Morgan (Volunteer)', '415-555-7788', 210, 'https://logistics.foodmesh.io/track/disp_801', datetime('now', '-20 minutes'), datetime('now', '-5 minutes')),
('disp_802', 'don_1002', '3PL_DOORDASH', 'DoorDash Drive API', 'ACCEPTED', 'DoorDash Courier #4412', '415-555-9900', 300, 'https://doordash.com/drive/track/dd_99182', datetime('now', '-5 minutes'), datetime('now', '-1 minute'));

-- 5. Seed Custody Ledger (Genesis and Ingestion Blocks)
INSERT OR REPLACE INTO custody_ledger (block_id, donation_id, block_index, prev_hash, current_hash, action, actor_id, otp_token, signature, verified_at)
VALUES 
('blk_001', 'don_1001', 0, '0000000000000000000000000000000000000000000000000000000000000000', 'GENESIS_BLOCK_HASH_DONATION_INGESTION_RECORD_001', 'DONATION_INGESTED', 'org_donor_001', 'OTP-9182', 'SIG_ECDSA_DONOR_INIT_001', datetime('now', '-25 minutes')),
('blk_002', 'don_1001', 1, 'GENESIS_BLOCK_HASH_DONATION_INGESTION_RECORD_001', 'VERIFIED_CHAIN_BLOCK_HASH_PICKUP_CONFIRMED_002', 'COURIER_PICKUP_VERIFIED', 'vol_alex_morgan', 'OTP-4412', 'SIG_ECDSA_HANDSHAKE_002', datetime('now', '-18 minutes'));

-- 6. Seed Thermal Telemetry
INSERT OR REPLACE INTO thermal_telemetry (reading_id, donation_id, temp_f, ambient_temp_f, sensor_id, is_compliant, biological_window_remaining_minutes, warning, recorded_at)
VALUES 
('thm_001', 'don_1001', 142.5, 68.0, 'SENS_KITCHEN_HOT_01', 1, 120.0, NULL, datetime('now', '-25 minutes')),
('thm_002', 'don_1001', 139.8, 65.0, 'SENS_COURIER_POD_02', 1, 102.0, NULL, datetime('now', '-10 minutes'));

-- 7. Seed ESG Analytics Historical Rollups
INSERT OR REPLACE INTO esg_analytics (entry_id, donation_id, rescued_weight_lbs, co2_offset_kg, water_saved_gallons, meals_provided, month_year, recorded_at)
VALUES 
('esg_hist_01', 'don_1001', 52300.0, 99370.0, 130750.0, 43580, '2026-08', datetime('now', '-60 days')),
('esg_hist_02', 'don_1001', 58450.0, 111055.0, 146125.0, 48708, '2026-09', datetime('now', '-30 days')),
('esg_hist_03', 'don_1001', 54200.0, 102980.0, 135500.0, 45166, '2026-10', datetime('now', '-2 days'));
