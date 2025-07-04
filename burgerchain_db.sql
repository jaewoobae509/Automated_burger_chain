CREATE DATABASE IF NOT EXISTS burger_chain;
USE burger_chain;
-- Users
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(50),
    user_type VARCHAR(50)
);

-- Trigger to set default user type to customer
DELIMITER //
CREATE TRIGGER set_default_user_type
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.user_type IS NULL OR NEW.user_type = '' THEN
        SET NEW.user_type = 'customer';
    END IF;
END;
//
DELIMITER ;

-- Ingredients
CREATE TABLE ingredients (
    ingredient_id INT AUTO_INCREMENT PRIMARY KEY,
    ingredient_name VARCHAR(50),
    unit VARCHAR(50)
);
-- Inventory
CREATE TABLE inventory (
    ingredient_id INT,
    count INT,
    supply_status ENUM('Empty', 'Low', 'In Transit', 'Abundant'),
    last_updated DATETIME,
    PRIMARY KEY (ingredient_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
);

-- Trigger to set last updated time to the time now
DELIMITER //
CREATE TRIGGER set_updated_time
BEFORE UPDATE ON inventory
FOR EACH ROW
BEGIN
    SET NEW.last_updated = NOW();
END;
//
DELIMITER ;

-- Recipes
CREATE TABLE recipes (
    recipe_id INT AUTO_INCREMENT PRIMARY KEY,
    recipe_name VARCHAR(50) UNIQUE NOT NULL,
    prep_time FLOAT,
    price DECIMAL(10,2)
);
-- RecipeIngredient
CREATE TABLE recipe_ingredients (
    recipe_id INT,
    ingredient_id INT,
    quantity_required INT,
    PRIMARY KEY (recipe_id, ingredient_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
    FOREIGN KEY (ingredient_id) REFERENCES ingredients(ingredient_id)
);
-- Machines
CREATE TABLE machines (
    machine_id INT AUTO_INCREMENT PRIMARY KEY,
    machine_name VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(50)
);
-- RecipeMachine
CREATE TABLE recipe_machines (
    recipe_id INT,
    machine_id INT,
    PRIMARY KEY (recipe_id, machine_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id),
    FOREIGN KEY (machine_id) REFERENCES machines(machine_id)
);
-- Orders
CREATE TABLE orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    recipe_id INT,  -- one recipe per order (one-to-many from recipe → orders)
    status VARCHAR(50) DEFAULT 'Pending' CHECK (status IN ('Pending', 'Confirmed', 'In Progress', 'Completed', 'Rejected')),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (recipe_id) REFERENCES recipes(recipe_id)
);

-- Stored procedure for checking whether a certain ingredient is available for recipe

DELIMITER //
CREATE PROCEDURE check_ingredients_for_recipe(IN recipeID INT)
BEGIN
    DECLARE insufficient_count INT;

    SELECT COUNT(*) INTO insufficient_count
    FROM recipe_ingredients ri
    JOIN inventory i ON ri.ingredient_id = i.ingredient_id
    WHERE ri.recipe_id = recipeID AND i.count < ri.quantity_required;

    IF insufficient_count > 0 THEN
        SELECT 'INSUFFICIENT' AS status;
    ELSE
        SELECT 'OK' AS status;
    END IF;
END;
//

DELIMITER ;


-- Stored procedure for cooking recipe that decreases ingredients used
DELIMITER //
CREATE PROCEDURE cook_recipe(IN recipeID INT)
BEGIN
    UPDATE Inventory i
    JOIN recipe_ingredients ri ON i.ingredient_id = ri.ingredient_id
    SET i.count = i.count - ri.quantity_required
    WHERE ri.recipe_id = recipeID;
END //
DELIMITER ;


-- STORED PROCEDURE: TRANSACTION - CONFIRM ORDER
DELIMITER //
CREATE PROCEDURE confirm_order_transaction(IN orderID INT)
BEGIN
    DECLARE recipeID INT;
    START TRANSACTION;
    SELECT recipe_id INTO recipeID FROM orders WHERE order_id = orderID;
    UPDATE orders SET status = 'Confirmed' WHERE order_id = orderID;
    CALL cook_recipe(recipeID);
    COMMIT;
END;
//
DELIMITER ;

-- VIEW: ACTIVE ORDERS
CREATE VIEW active_orders AS
SELECT 
    o.order_id,
    u.username AS customer_name,
    r.recipe_name,
    r.price,
    o.status,
    o.timestamp
FROM orders o
JOIN users u ON o.user_id = u.user_id
JOIN recipes r ON o.recipe_id = r.recipe_id
WHERE o.status IN ('Pending', 'Confirmed', 'In Progress', 'Completed', 'Rejected');