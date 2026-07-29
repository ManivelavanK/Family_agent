BEGIN;

-- 1. Truncate existing tables and restart sequences
TRUNCATE TABLE 
    agent_memory,
    agent_reflections,
    consumption_history,
    document_vault,
    expiry_items,
    grocery_items,
    household_settings,
    kitchen_alerts,
    product_prices,
    purchase_history,
    user_memory
RESTART IDENTITY CASCADE;

-- 2. Populate grocery_items (Pantry Stock Status)
-- quantity is an INTEGER in the database schema
INSERT INTO grocery_items (name, category, quantity, unit, created_at, updated_at) VALUES
('Sona Masoori Rice', 'Staples', 8, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '4 days'),
('Ashirvaad Atta', 'Staples', 4, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '2 days'),
('Organic Sugar', 'Staples', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '5 days'),
('Tata Salt', 'Staples', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '10 days'),
('Amul Fresh Milk', 'Dairy', 1, 'L', NOW() - INTERVAL '30 days', NOW() - INTERVAL '1 day'),
('Amul Curd', 'Dairy', 1, 'L', NOW() - INTERVAL '30 days', NOW() - INTERVAL '1 day'),
('Milky Mist Paneer', 'Dairy', 0, 'g', NOW() - INTERVAL '30 days', NOW() - INTERVAL '3 days'),
('Free Range Eggs', 'Dairy', 6, 'pcs', NOW() - INTERVAL '30 days', NOW() - INTERVAL '2 days'),
('Fortune Sunflower Oil', 'Staples', 2, 'L', NOW() - INTERVAL '30 days', NOW() - INTERVAL '12 days'),
('Tomatoes', 'Vegetables', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '1 day'),
('Onions', 'Vegetables', 2, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '2 days'),
('Potatoes', 'Vegetables', 3, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '3 days'),
('Carrots', 'Vegetables', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '2 days'),
('French Beans', 'Vegetables', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '2 days'),
('Spinach', 'Vegetables', 0, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '3 days'),
('Fresh Chicken', 'Meat & Fish', 0, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '4 days'),
('Rohu Fish', 'Meat & Fish', 0, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '5 days'),
('Shimla Apples', 'Fruits', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '1 day'),
('Robusta Bananas', 'Fruits', 4, 'pcs', NOW() - INTERVAL '30 days', NOW() - INTERVAL '1 day'),
('Nagpur Oranges', 'Fruits', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '2 days'),
('Taj Mahal Tea Powder', 'Beverages', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '8 days'),
('Bru Instant Coffee', 'Beverages', 1, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '9 days'),
('Marie Gold Biscuits', 'Snacks', 2, 'packs', NOW() - INTERVAL '30 days', NOW() - INTERVAL '3 days'),
('Tropicana Orange Juice', 'Beverages', 0, 'L', NOW() - INTERVAL '30 days', NOW() - INTERVAL '6 days'),
('Lifebuoy Soap', 'Personal Care', 3, 'pcs', NOW() - INTERVAL '30 days', NOW() - INTERVAL '15 days'),
('Surf Excel Detergent', 'Cleaning', 2, 'kg', NOW() - INTERVAL '30 days', NOW() - INTERVAL '12 days'),
('Clinic Plus Shampoo', 'Personal Care', 1, 'bottle', NOW() - INTERVAL '30 days', NOW() - INTERVAL '20 days'),
('Colgate Toothpaste', 'Personal Care', 2, 'tubes', NOW() - INTERVAL '30 days', NOW() - INTERVAL '18 days');

-- 3. Populate purchase_history (approx 100 entries spread across 30 days)
-- quantity is an INTEGER in the database schema
INSERT INTO purchase_history (item_name, category, quantity, unit, price, purchase_date, created_at) VALUES
-- Week 1 Purchases
('Sona Masoori Rice', 'Staples', 10, 'kg', 600.0, CURRENT_DATE - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('Ashirvaad Atta', 'Staples', 10, 'kg', 450.0, CURRENT_DATE - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('Fortune Sunflower Oil', 'Staples', 5, 'L', 650.0, CURRENT_DATE - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('Tata Salt', 'Staples', 1, 'kg', 25.0, CURRENT_DATE - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('Taj Mahal Tea Powder', 'Beverages', 1, 'kg', 220.0, CURRENT_DATE - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('Amul Fresh Milk', 'Dairy', 7, 'L', 420.0, CURRENT_DATE - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('Free Range Eggs', 'Dairy', 12, 'pcs', 90.0, CURRENT_DATE - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('Tomatoes', 'Vegetables', 2, 'kg', 80.0, CURRENT_DATE - INTERVAL '26 days', NOW() - INTERVAL '26 days'),
('Onions', 'Vegetables', 3, 'kg', 105.0, CURRENT_DATE - INTERVAL '26 days', NOW() - INTERVAL '26 days'),
('Potatoes', 'Vegetables', 4, 'kg', 120.0, CURRENT_DATE - INTERVAL '26 days', NOW() - INTERVAL '26 days'),
('Fresh Chicken', 'Meat & Fish', 1, 'kg', 240.0, CURRENT_DATE - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
('Robusta Bananas', 'Fruits', 12, 'pcs', 60.0, CURRENT_DATE - INTERVAL '25 days', NOW() - INTERVAL '25 days'),

-- Week 2 Purchases
('Amul Fresh Milk', 'Dairy', 7, 'L', 420.0, CURRENT_DATE - INTERVAL '21 days', NOW() - INTERVAL '21 days'),
('Amul Curd', 'Dairy', 3, 'L', 210.0, CURRENT_DATE - INTERVAL '21 days', NOW() - INTERVAL '21 days'),
('Milky Mist Paneer', 'Dairy', 1, 'g', 150.0, CURRENT_DATE - INTERVAL '21 days', NOW() - INTERVAL '21 days'),
('Tomatoes', 'Vegetables', 3, 'kg', 100.0, CURRENT_DATE - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
('Onions', 'Vegetables', 3, 'kg', 105.0, CURRENT_DATE - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
('Spinach', 'Vegetables', 1, 'kg', 40.0, CURRENT_DATE - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
('French Beans', 'Vegetables', 1, 'kg', 80.0, CURRENT_DATE - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
('Rohu Fish', 'Meat & Fish', 2, 'kg', 375.0, CURRENT_DATE - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('Shimla Apples', 'Fruits', 2, 'kg', 320.0, CURRENT_DATE - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('Marie Gold Biscuits', 'Snacks', 4, 'packs', 80.0, CURRENT_DATE - INTERVAL '17 days', NOW() - INTERVAL '17 days'),
('Tropicana Orange Juice', 'Beverages', 2, 'L', 220.0, CURRENT_DATE - INTERVAL '17 days', NOW() - INTERVAL '17 days'),

-- Week 3 Purchases
('Sona Masoori Rice', 'Staples', 5, 'kg', 310.0, CURRENT_DATE - INTERVAL '14 days', NOW() - INTERVAL '14 days'),
('Ashirvaad Atta', 'Staples', 5, 'kg', 230.0, CURRENT_DATE - INTERVAL '14 days', NOW() - INTERVAL '14 days'),
('Amul Fresh Milk', 'Dairy', 7, 'L', 420.0, CURRENT_DATE - INTERVAL '14 days', NOW() - INTERVAL '14 days'),
('Free Range Eggs', 'Dairy', 12, 'pcs', 96.0, CURRENT_DATE - INTERVAL '14 days', NOW() - INTERVAL '14 days'),
('Tomatoes', 'Vegetables', 2, 'kg', 80.0, CURRENT_DATE - INTERVAL '12 days', NOW() - INTERVAL '12 days'),
('Onions', 'Vegetables', 3, 'kg', 87.5, CURRENT_DATE - INTERVAL '12 days', NOW() - INTERVAL '12 days'),
('Potatoes', 'Vegetables', 3, 'kg', 90.0, CURRENT_DATE - INTERVAL '12 days', NOW() - INTERVAL '12 days'),
('Carrots', 'Vegetables', 2, 'kg', 90.0, CURRENT_DATE - INTERVAL '12 days', NOW() - INTERVAL '12 days'),
('Fresh Chicken', 'Meat & Fish', 1, 'kg', 288.0, CURRENT_DATE - INTERVAL '11 days', NOW() - INTERVAL '11 days'),
('Robusta Bananas', 'Fruits', 12, 'pcs', 60.0, CURRENT_DATE - INTERVAL '11 days', NOW() - INTERVAL '11 days'),
('Nagpur Oranges', 'Fruits', 2, 'kg', 160.0, CURRENT_DATE - INTERVAL '10 days', NOW() - INTERVAL '10 days'),

-- Week 4 Purchases
('Amul Fresh Milk', 'Dairy', 7, 'L', 420.0, CURRENT_DATE - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('Amul Curd', 'Dairy', 2, 'L', 140.0, CURRENT_DATE - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('Milky Mist Paneer', 'Dairy', 1, 'g', 150.0, CURRENT_DATE - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('Tomatoes', 'Vegetables', 2, 'kg', 90.0, CURRENT_DATE - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('Onions', 'Vegetables', 3, 'kg', 120.0, CURRENT_DATE - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('Spinach', 'Vegetables', 1, 'kg', 45.0, CURRENT_DATE - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('French Beans', 'Vegetables', 1, 'kg', 72.0, CURRENT_DATE - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('Bru Instant Coffee', 'Beverages', 1, 'kg', 185.0, CURRENT_DATE - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
('Lifebuoy Soap', 'Personal Care', 4, 'pcs', 140.0, CURRENT_DATE - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
('Surf Excel Detergent', 'Cleaning', 2, 'kg', 280.0, CURRENT_DATE - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
('Colgate Toothpaste', 'Personal Care', 2, 'tubes', 150.0, CURRENT_DATE - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
('Marie Gold Biscuits', 'Snacks', 3, 'packs', 60.0, CURRENT_DATE - INTERVAL '2 days', NOW() - INTERVAL '2 days'),

-- Top-up Purchases (last 24-48 hours)
('Amul Fresh Milk', 'Dairy', 1, 'L', 60.0, CURRENT_DATE - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
('Tomatoes', 'Vegetables', 1, 'kg', 45.0, CURRENT_DATE - INTERVAL '1 day', NOW() - INTERVAL '1 day'),
('Shimla Apples', 'Fruits', 1, 'kg', 170.0, CURRENT_DATE - INTERVAL '1 day', NOW() - INTERVAL '1 day');

-- 4. Populate consumption_history (daily breakdown of 200+ logs)
INSERT INTO consumption_history (item_name, quantity_used, unit, consumption_date, created_at) VALUES
-- Daily Milk & Eggs (simulating breakfast habits)
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '30 days', NOW() - INTERVAL '30 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '29 days', NOW() - INTERVAL '29 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '28 days', NOW() - INTERVAL '28 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '27 days', NOW() - INTERVAL '27 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '26 days', NOW() - INTERVAL '26 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '24 days', NOW() - INTERVAL '24 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '23 days', NOW() - INTERVAL '23 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '22 days', NOW() - INTERVAL '22 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '21 days', NOW() - INTERVAL '21 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '17 days', NOW() - INTERVAL '17 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '16 days', NOW() - INTERVAL '16 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '15 days', NOW() - INTERVAL '15 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '14 days', NOW() - INTERVAL '14 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '13 days', NOW() - INTERVAL '13 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '12 days', NOW() - INTERVAL '12 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '11 days', NOW() - INTERVAL '11 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '10 days', NOW() - INTERVAL '10 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '9 days', NOW() - INTERVAL '9 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '7 days', NOW() - INTERVAL '7 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '6 days', NOW() - INTERVAL '6 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '4 days', NOW() - INTERVAL '4 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '2 days', NOW() - INTERVAL '2 days'),
('Amul Fresh Milk', 1.0, 'L', CURRENT_DATE - INTERVAL '1 day', NOW() - INTERVAL '1 day'),

-- Weekly Staples depletion
('Sona Masoori Rice', 2.0, 'kg', CURRENT_DATE - INTERVAL '24 days', NOW() - INTERVAL '24 days'),
('Sona Masoori Rice', 2.2, 'kg', CURRENT_DATE - INTERVAL '17 days', NOW() - INTERVAL '17 days'),
('Sona Masoori Rice', 2.1, 'kg', CURRENT_DATE - INTERVAL '10 days', NOW() - INTERVAL '10 days'),
('Sona Masoori Rice', 2.2, 'kg', CURRENT_DATE - INTERVAL '3 days', NOW() - INTERVAL '3 days'),
('Ashirvaad Atta', 3.0, 'kg', CURRENT_DATE - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
('Ashirvaad Atta', 3.2, 'kg', CURRENT_DATE - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('Ashirvaad Atta', 2.8, 'kg', CURRENT_DATE - INTERVAL '11 days', NOW() - INTERVAL '11 days'),
('Ashirvaad Atta', 2.0, 'kg', CURRENT_DATE - INTERVAL '4 days', NOW() - INTERVAL '4 days'),

-- Daily Vegetables Usage (curries/sambar)
('Tomatoes', 0.3, 'kg', CURRENT_DATE - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
('Tomatoes', 0.4, 'kg', CURRENT_DATE - INTERVAL '24 days', NOW() - INTERVAL '24 days'),
('Tomatoes', 0.3, 'kg', CURRENT_DATE - INTERVAL '23 days', NOW() - INTERVAL '23 days'),
('Tomatoes', 0.5, 'kg', CURRENT_DATE - INTERVAL '22 days', NOW() - INTERVAL '22 days'),
('Tomatoes', 0.3, 'kg', CURRENT_DATE - INTERVAL '21 days', NOW() - INTERVAL '21 days'),
('Tomatoes', 0.4, 'kg', CURRENT_DATE - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
('Tomatoes', 0.3, 'kg', CURRENT_DATE - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
('Tomatoes', 0.4, 'kg', CURRENT_DATE - INTERVAL '15 days', NOW() - INTERVAL '15 days'),
('Tomatoes', 0.3, 'kg', CURRENT_DATE - INTERVAL '14 days', NOW() - INTERVAL '14 days'),
('Tomatoes', 0.4, 'kg', CURRENT_DATE - INTERVAL '13 days', NOW() - INTERVAL '13 days'),
('Tomatoes', 0.3, 'kg', CURRENT_DATE - INTERVAL '12 days', NOW() - INTERVAL '12 days'),
('Tomatoes', 0.4, 'kg', CURRENT_DATE - INTERVAL '10 days', NOW() - INTERVAL '10 days'),
('Tomatoes', 0.3, 'kg', CURRENT_DATE - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
('Tomatoes', 0.4, 'kg', CURRENT_DATE - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('Tomatoes', 0.3, 'kg', CURRENT_DATE - INTERVAL '2 days', NOW() - INTERVAL '2 days'),

('Onions', 0.5, 'kg', CURRENT_DATE - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
('Onions', 0.4, 'kg', CURRENT_DATE - INTERVAL '24 days', NOW() - INTERVAL '24 days'),
('Onions', 0.5, 'kg', CURRENT_DATE - INTERVAL '23 days', NOW() - INTERVAL '23 days'),
('Onions', 0.4, 'kg', CURRENT_DATE - INTERVAL '21 days', NOW() - INTERVAL '21 days'),
('Onions', 0.5, 'kg', CURRENT_DATE - INTERVAL '19 days', NOW() - INTERVAL '19 days'),
('Onions', 0.5, 'kg', CURRENT_DATE - INTERVAL '15 days', NOW() - INTERVAL '15 days'),
('Onions', 0.4, 'kg', CURRENT_DATE - INTERVAL '12 days', NOW() - INTERVAL '12 days'),
('Onions', 0.5, 'kg', CURRENT_DATE - INTERVAL '10 days', NOW() - INTERVAL '10 days'),
('Onions', 0.4, 'kg', CURRENT_DATE - INTERVAL '8 days', NOW() - INTERVAL '8 days'),
('Onions', 0.5, 'kg', CURRENT_DATE - INTERVAL '5 days', NOW() - INTERVAL '5 days'),
('Onions', 0.4, 'kg', CURRENT_DATE - INTERVAL '2 days', NOW() - INTERVAL '2 days'),

-- Weekend specific logs (Biryani / Feasts)
('Fresh Chicken', 1.0, 'kg', CURRENT_DATE - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
('Rohu Fish', 1.5, 'kg', CURRENT_DATE - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('Fresh Chicken', 1.2, 'kg', CURRENT_DATE - INTERVAL '11 days', NOW() - INTERVAL '11 days'),
('Milky Mist Paneer', 0.5, 'g', CURRENT_DATE - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
('Milky Mist Paneer', 0.5, 'g', CURRENT_DATE - INTERVAL '6 days', NOW() - INTERVAL '6 days'),

-- Spinach, Beans
('Spinach', 1.0, 'kg', CURRENT_DATE - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('French Beans', 0.5, 'kg', CURRENT_DATE - INTERVAL '18 days', NOW() - INTERVAL '18 days'),
('Spinach', 1.0, 'kg', CURRENT_DATE - INTERVAL '4 days', NOW() - INTERVAL '4 days');

-- 5. Populate expiry_items (simulation of products nearing expiry)
INSERT INTO expiry_items (item_name, expiry_date, created_at) VALUES
('Amul Fresh Milk', CURRENT_DATE - INTERVAL '1 day', NOW() - INTERVAL '3 days'), 
('Amul Curd', CURRENT_DATE, NOW() - INTERVAL '2 days'),                          
('Milky Mist Paneer', CURRENT_DATE + INTERVAL '2 days', NOW() - INTERVAL '1 day'),
('Spinach', CURRENT_DATE + INTERVAL '3 days', NOW() - INTERVAL '1 day');          

-- 6. Populate product_prices (historical price logs)
-- Note: excluding updated_at which does not exist in the public schema of product_prices
INSERT INTO product_prices (item_name, store_name, price, created_at) VALUES
('Sona Masoori Rice', 'DMart', 58.0, CURRENT_DATE - INTERVAL '30 days'),
('Sona Masoori Rice', 'DMart', 60.0, CURRENT_DATE - INTERVAL '20 days'),
('Sona Masoori Rice', 'DMart', 62.0, CURRENT_DATE - INTERVAL '10 days'),
('Amul Fresh Milk', 'BigBasket', 55.0, CURRENT_DATE - INTERVAL '30 days'),
('Amul Fresh Milk', 'BigBasket', 58.0, CURRENT_DATE - INTERVAL '15 days'),
('Amul Fresh Milk', 'BigBasket', 60.0, CURRENT_DATE - INTERVAL '2 days'),
('Tomatoes', 'Local Vegetable Shop', 30.0, CURRENT_DATE - INTERVAL '30 days'),
('Tomatoes', 'Local Vegetable Shop', 40.0, CURRENT_DATE - INTERVAL '20 days'),
('Tomatoes', 'Local Vegetable Shop', 45.0, CURRENT_DATE - INTERVAL '5 days'),
('Fortune Sunflower Oil', 'Reliance Fresh', 120.0, CURRENT_DATE - INTERVAL '30 days'),
('Fortune Sunflower Oil', 'Reliance Fresh', 125.0, CURRENT_DATE - INTERVAL '15 days'),
('Fortune Sunflower Oil', 'Reliance Fresh', 130.0, CURRENT_DATE - INTERVAL '1 day');

-- 7. Populate kitchen_alerts (low stock, expired, budget warnings)
INSERT INTO kitchen_alerts (item_name, severity, title, description, recommended_action, status, created_at) VALUES
('Sona Masoori Rice', 'High', 'Rice may run out soon', 'Expected depletion in 4 days.', 'Add 5 kg to shopping list.', 'Pending', NOW() - INTERVAL '1 day'),
('Organic Milk', 'High', 'Milk stock depleted', 'Milk stock below critical alert threshold.', 'Buy 2 L immediately.', 'Pending', NOW()),
('Amul Fresh Milk', 'Medium', 'Milk has expired', 'One pack of Amul Milk purchased 3 days ago is past expiry.', 'Discard and replace.', 'Pending', NOW() - INTERVAL '1 day'),
('Tomatoes', 'Low', 'Waste warning: Tomatoes', 'Tomatoes are frequently purchased in excess and spoil.', 'Reduce next weekly purchase by 500 g.', 'Resolved', NOW() - INTERVAL '3 days'),
('Grocery Budget', 'Medium', 'Budget warning', 'Grocery spending is currently at 70% of weekly limit.', 'Consider postponing optional snacks.', 'Resolved', NOW() - INTERVAL '2 days');

-- 8. Populate household_settings
INSERT INTO household_settings (family_name, primary_contact_phone, budget_limit_weekly, preferred_store, auto_order_threshold, created_at) VALUES
('Arunachalam Family', 'whatsapp:+919840123456', 3000.0, 'DMart Supermarket', 2.0, NOW() - INTERVAL '30 days');

-- 9. Populate document_vault (receipt/invoice PDFs)
INSERT INTO document_vault (doc_type, title, file_path, metadata_json, uploaded_at) VALUES
('Receipt', 'DMart Monthly Staples Bill - July 2026', '/vault/receipts/dmart_jul_2026.pdf', '{"amount": 1850.0, "store": "DMart", "date": "2026-07-28"}', NOW() - INTERVAL '1 day'),
('Receipt', 'Local Vegetable Shop Bill - July 23', '/vault/receipts/veg_market_jul_23.pdf', '{"amount": 620.0, "store": "Vegetable Market", "date": "2026-07-23"}', NOW() - INTERVAL '6 days'),
('Receipt', 'Nilgiris Groceries Bill - July 15', '/vault/receipts/nilgiris_jul_15.pdf', '{"amount": 2450.0, "store": "Nilgiris Grocery Store", "date": "2026-07-15"}', NOW() - INTERVAL '14 days'),
('Bill', 'Electricity Bill - July 2026', '/vault/bills/tneb_electricity_jul_2026.pdf', '{"amount": 1420.0, "biller": "TNEB", "due_date": "2026-08-10"}', NOW() - INTERVAL '5 days'),
('Bill', 'Indane Cooking Gas Bill', '/vault/bills/indane_gas_jul.pdf', '{"amount": 1050.0, "biller": "Indane Gas", "date": "2026-07-20"}', NOW() - INTERVAL '9 days'),
('Warranty', 'Prestige Mixer Grinder Warranty Card', '/vault/warranties/mixer_grinder.pdf', '{"product": "Prestige Mixer Grinder", "duration": "2 years", "purchase_date": "2026-07-01"}', NOW() - INTERVAL '28 days');

-- 10. Populate user_memory (User memories logged inside user_memory table)
-- memory_value is nullable=NO
INSERT INTO user_memory (user_role, memory_type, item_name, memory_value, created_at) VALUES
('family', 'preference', 'Rice', 'Family prefers Sona Masoori Rice over Basmati for daily consumption.', NOW() - INTERVAL '28 days'),
('family', 'meal_log', 'Dosa', 'Prepared dosa with homemade coconut chutney for Sunday breakfast.', NOW() - INTERVAL '25 days'),
('family', 'shopping_note', 'Cooking Oil', 'Bought Fortune Sunflower Oil from Reliance Fresh on sale.', NOW() - INTERVAL '20 days'),
('family', 'household_event', 'Family Dinner', 'Grandparents cooked traditional sambar and potato fry for dinner.', NOW() - INTERVAL '15 days'),
('family', 'grocery_note', 'Milk', 'College student asked for organic full-fat milk for protein shakes.', NOW() - INTERVAL '5 days');

-- 11. Populate agent_memory (AI Agent memories logged inside agent_memory table)
-- value is nullable=NO (Note: table column is 'value', not 'memory_value')
INSERT INTO agent_memory (memory_type, item_name, value, created_at) VALUES
('pattern_insight', 'Milk', 'Weekly grocery usage of Amul Milk has stabilized at 7.2 L per week.', NOW() - INTERVAL '22 days'),
('spending_insight', 'Vegetables', 'Vegetable spending increased 18% this month due to organic purchases.', NOW() - INTERVAL '15 days'),
('pantry_check', 'Rice', 'Rice stock is critical. Expected depletion in 4 days.', NOW() - INTERVAL '4 days'),
('budget_audit', 'Weekly Budget', 'Weekly grocery budget limit met. Spending is currently 8% below the ₹3,000 threshold.', NOW() - INTERVAL '2 days'),
('shop_frequency', 'DMart', 'Frequent shopping trips are made to DMart Supermarket for dry staples.', NOW() - INTERVAL '10 days');

-- 12. Populate agent_reflections (one reflection log per day for the last 30 days)
INSERT INTO agent_reflections (item_name, insight, recommendation, created_at, updated_at) VALUES
('Vegetables', 'Vegetable purchases increased 12% in the first week.', 'Encourage meal planning to avoid over-ordering greens.', CURRENT_DATE - INTERVAL '29 days', NOW()),
('Milk', 'Milk consumption rises on school days.', 'Maintain milk replenishment rate at 1L daily.', CURRENT_DATE - INTERVAL '28 days', NOW()),
('Kitchen Assets', 'Weekly inventory check completed successfully.', 'No critical shortages detected in kitchen staples.', CURRENT_DATE - INTERVAL '27 days', NOW()),
('Budgeting', 'Spending is balanced within parameters.', 'Monthly budget utilization on target.', CURRENT_DATE - INTERVAL '26 days', NOW()),
('Meal Planning', 'Family dinners consumed more rice than forecasted.', 'Adjust weekly rice prediction model threshold by +5%.', CURRENT_DATE - INTERVAL '25 days', NOW()),
('Waste Monitor', 'Tomatoes show high spoilage risk in warm weather.', 'Reduce tomato purchase size from 2.5kg to 1.5kg.', CURRENT_DATE - INTERVAL '24 days', NOW()),
('Replenishment', 'Staples replenishment done at DMart.', 'Continue buying bulky staples from DMart for discount yields.', CURRENT_DATE - INTERVAL '23 days', NOW()),
('Dairy', 'Curd consumption increased by student.', 'Add curd stock buffer of 500ml for hot afternoons.', CURRENT_DATE - INTERVAL '22 days', NOW()),
('Personal Care', 'Personal care goods stock stable.', 'No shampoo or soap purchase needed for 10 days.', CURRENT_DATE - INTERVAL '21 days', NOW()),
('Pantry Check', 'Rice stocks decreased to 50%.', 'Monitor rice consumption curve closely.', CURRENT_DATE - INTERVAL '20 days', NOW()),
('Alert System', 'Nearing expiry alerts resolved for Paneer.', 'Paneer was successfully consumed in dinner kurma.', CURRENT_DATE - INTERVAL '19 days', NOW()),
('Fish & Meat', 'Rohu Fish bought from local market.', 'Ensure fish is prepared within 24 hours of acquisition.', CURRENT_DATE - INTERVAL '18 days', NOW()),
('Snacks', 'Biscuit stocks depleting rapidly.', 'Grandchildren eating snacks faster. Buy extra biscuits next trip.', CURRENT_DATE - INTERVAL '17 days', NOW()),
('Kitchen Assets', 'Pantry audits indicate high tea powder stock.', 'Postpone tea powder reordering for 3 weeks.', CURRENT_DATE - INTERVAL '16 days', NOW()),
('Budgeting', 'Budget utilization at 50% for this month.', 'Financial parameters normal.', CURRENT_DATE - INTERVAL '15 days', NOW()),
('Meal Planning', 'Vegetable Biryani planned for Sunday lunch.', 'Ensure chicken or paneer is available for side gravy.', CURRENT_DATE - INTERVAL '14 days', NOW()),
('Pantry Check', 'Wheat flour stocks depleted to low levels.', 'Recommend buying 5kg Atta on next trip.', CURRENT_DATE - INTERVAL '13 days', NOW()),
('Alert System', 'Low stock alert triggered for onions.', 'Add onions to next BigBasket smart list.', CURRENT_DATE - INTERVAL '12 days', NOW()),
('Replenishment', 'Onions and potatoes purchased successfully.', 'Inventory balance restored.', CURRENT_DATE - INTERVAL '11 days', NOW()),
('Fruit Rotation', 'Oranges purchased to replace apples.', 'Oranges provide seasonal vitamins for grandparents.', CURRENT_DATE - INTERVAL '10 days', NOW()),
('Waste Monitor', 'Tomato waste decreased by 5% after purchase limits.', 'Continue enforcing capped vegetable procurement caps.', CURRENT_DATE - INTERVAL '9 days', NOW()),
('Beverages', 'Instant coffee is nearing reorder threshold.', 'Add Bru Coffee to consider buying list.', CURRENT_DATE - INTERVAL '8 days', NOW()),
('Budgeting', 'Minor budget warning due to detergent purchase.', 'Budget limit remains safe within monthly parameters.', CURRENT_DATE - INTERVAL '7 days', NOW()),
('Dairy', 'Paneer stocks depleted to zero.', 'Add paneer to must buy list for weekend dinner.', CURRENT_DATE - INTERVAL '6 days', NOW()),
('Meal Planning', 'Paneer Butter Masala prepared successfully.', 'Pantry items aligned with scheduled meal slots.', CURRENT_DATE - INTERVAL '5 days', NOW()),
('Alert System', 'Critical alert: Rice stocks at 4 days remaining.', 'Recommend buying 5kg rice within 48 hours.', CURRENT_DATE - INTERVAL '4 days', NOW()),
('Replenishment', 'Detergents and personal care items top-up done.', 'Pantry stock health normal.', CURRENT_DATE - INTERVAL '3 days', NOW()),
('Budgeting', 'Spending reached 92% of budget limits.', 'Restrict snack purchases for the remaining week.', CURRENT_DATE - INTERVAL '2 days', NOW()),
('Waste Monitor', 'Milk carton expired due to negligence.', 'Alert family to inspect milk expiration tags daily.', CURRENT_DATE - INTERVAL '1 day', NOW()),
('Pantry Check', 'Weekly inventory audit completed.', 'Pantry health index is at 82%. Monitor milk levels.', CURRENT_DATE, NOW());

COMMIT;
