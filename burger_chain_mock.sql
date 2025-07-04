INSERT INTO users (username, password, email, user_type) VALUES
('john_doe', '9b8769a4a742959a2d0298c36fb70623f2dfacda8436237df08d8dfd5b37374c', 'john@example.com', NULL), 
('jane_doe', '1d4598d1949b47f7f211134b639ec32238ce73086a83c2f745713b3f12f817e5', 'jane@example.com', 'customer'),
('manager_max', '925ffdbd4036d405b65dccc2ceab9235093502365875b4ee7fafc594ffb39937', 'max@example.com', 'manager');


INSERT INTO ingredients (ingredient_name, unit) VALUES
('Beef Patty', 'pcs'),
('Lettuce', 'grams'),
('Tomato', 'grams'),
('Cheddar Cheese', 'slices'),
('Burger Bun', 'pcs');

INSERT INTO inventory (ingredient_id, count, supply_status, last_updated) VALUES
(1, 50, 'Abundant', NOW()),
(2, 200, 'Abundant', NOW()),
(3, 150, 'Abundant', NOW()),
(4, 80, 'In Transit', NOW()),
(5, 60, 'Low', NOW());

INSERT INTO recipes (recipe_name, prep_time, price) VALUES
('Classic Burger', 7.0, 11.99),
('Cheese Burger', 5.0, 12.99),
('Veggie Burger', 4.0, 10.99);

INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity_required) VALUES
(1, 1, 1),  
(1, 2, 30),
(1, 3, 20),
(1, 5, 1), 

(2, 1, 1),
(2, 2, 20),
(2, 3, 20),
(2, 4, 1),
(2, 5, 1),

(3, 2, 40),
(3, 3, 30),
(3, 5, 1);


INSERT INTO machines (machine_name, status) VALUES
('GrillMaster 3000', 'Available'),
('VeggiePress 1000', 'Busy'),
('BunToaster XT', 'Available');

