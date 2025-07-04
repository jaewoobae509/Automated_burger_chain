from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from dbConfig import get_db_connection, close_db_connection, get_db_cursor
import hashlib
import mysql.connector

app = Flask(__name__)
app.secret_key = "12345"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        mydb = get_db_connection()
        if mydb:
            cursor = get_db_cursor(mydb)
            try:
                cursor.execute("SELECT username FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    cursor.close()
                    close_db_connection(mydb)
                    return "User already exists"

                hashedPassword = hashlib.sha256(password.encode()).hexdigest()
                cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashedPassword))
                mydb.commit()

                cursor.execute("SELECT user_type FROM users WHERE username = %s", (username,))
                user_type = cursor.fetchone()[0]

                session['user'] = username
                session['user_type'] = user_type

                cursor.close()
                close_db_connection(mydb)
                return redirect(url_for('dashboard'))

            except mysql.connector.Error as err:
                if cursor: cursor.close()
                close_db_connection(mydb)
                return f"{err}"
        else:
            return "Database connection failed."
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        mydb = get_db_connection()
        if mydb:
            cursor = get_db_cursor(mydb)
            try:
                cursor.execute("SELECT username, password, user_type FROM users WHERE username = %s", (username,))
                userInfo = cursor.fetchone()
                if userInfo:
                    dbPassword = userInfo[1]
                    user_type = userInfo[2]
                    hashedPassword = hashlib.sha256(password.encode()).hexdigest()
                    if dbPassword == hashedPassword:
                        session['user'] = username
                        session['user_type'] = user_type

                        cursor.close()
                        close_db_connection(mydb)
                        return redirect(url_for('dashboard'))
                    else:
                        return "Invalid password"
                else:
                    cursor.close()
                    close_db_connection(mydb)
                    return "Invalid credentials"
            except mysql.connector.Error as err:
                if cursor: cursor.close()
                close_db_connection(mydb)
                return f"{err}"
        else:
            return "Database connection failed."
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    user_type = session.get('user_type')

    if not user or not user_type:
        return redirect(url_for('login'))

    if user_type == 'manager':
        return render_template('worker.html')
    elif user_type == 'customer':
        return render_template('burgerchain.html', username=user)
    else:
        return "Unauthorized", 403

@app.route('/burgerchain')
def burgerchain():
    if 'user' not in session:
        return redirect(url_for('index'))
    return render_template('burgerchain.html', username=session['user'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/order', methods=['GET', 'POST'])
def order():
    if 'user' not in session:
        return redirect(url_for('login'))

    mydb = get_db_connection()
    cursor = get_db_cursor(mydb)

    if request.method == 'POST':
        if 'order_items' in session and session['order_items']:
            user = session['user']
            cursor.execute("SELECT user_id FROM users WHERE username = %s", (user,))
            user_id = cursor.fetchone()[0]

            for recipe_id in session['order_items']:
                cursor.execute("INSERT INTO orders (user_id, recipe_id) VALUES (%s, %s)", (user_id, recipe_id))

            mydb.commit()
            session['order_items'] = []
            message = "Order placed successfully!"
        else:
            message = "No items in your order."
    else:
        message = None

    cursor.execute("SELECT recipe_id, recipe_name, price FROM recipes")
    menu_items = cursor.fetchall()

    order_items = session.get('order_items', [])
    item_details = []
    total_price = 0

    for recipe_id in order_items:
        cursor.execute("SELECT recipe_name, price FROM recipes WHERE recipe_id = %s", (recipe_id,))
        recipe = cursor.fetchone()
        if recipe:
            item_details.append(recipe)
            total_price += float(recipe[1])

    cursor.close()
    close_db_connection(mydb)

    return render_template('order.html', menu=menu_items, order_items=item_details, total=total_price, message=message)

@app.route('/orders', methods=['GET'])
def get_orders():
    mydb = get_db_connection()
    cursor = get_db_cursor(mydb)

    try:
        cursor.execute("SELECT * FROM active_orders ORDER BY timestamp DESC")
        rows = cursor.fetchall()
        keys = ['order_id', 'customer_name', 'recipe_name', 'price', 'status', 'timestamp']
        orders = [dict(zip(keys, row)) for row in rows]
        return jsonify(orders)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        close_db_connection(mydb)


@app.route('/add_to_order/<int:recipe_id>')
def add_to_order(recipe_id):
    if 'order_items' not in session:
        session['order_items'] = []

    items = session['order_items']
    items.append(recipe_id)
    session['order_items'] = items
    session.modified = True

    return redirect(url_for('order'))

@app.route('/orders/<int:order_id>/status', methods=['POST'])
def update_order_status(order_id):
    if session.get('user_type') != 'manager':
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.get_json()
    print(f"Received status update request: {data}")


    new_status = request.json.get('status')
    if new_status not in ['Confirmed', 'Rejected', 'In Progress', 'Completed']:
        return jsonify({"error": "Invalid status"}), 400

    mydb = get_db_connection()
    if mydb:
        cursor = get_db_cursor(mydb)
        try:
            cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s", (new_status, order_id))
            mydb.commit()
            cursor.close()
            close_db_connection(mydb)
            return jsonify({"message": "Order status updated"})
        except Exception as e:
            if cursor: cursor.close()
            close_db_connection(mydb)
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "DB connection failed"}), 500

@app.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):

    mydb = get_db_connection()
    if mydb:
        cursor = get_db_cursor(mydb)
        try:
            cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
            mydb.commit()
            cursor.close()
            close_db_connection(mydb)
            return jsonify({"message": "Order deleted"})
        except Exception as e:
            if cursor: cursor.close()
            close_db_connection(mydb)
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "Database connection failed"}), 500

@app.route('/confirm_order/<int:order_id>', methods=['POST'])
def confirm_order(order_id):
    if session.get('user_type') != 'manager':
        return jsonify({"error": "Unauthorized"}), 403

    conn = get_db_connection()
    cursor = get_db_cursor(conn)

    try:
        cursor.execute("SELECT recipe_id FROM orders WHERE order_id = %s", (order_id,))
        recipe = cursor.fetchone()
        if not recipe:
            return jsonify({"error": "Invalid order"}), 404
        recipe_id = recipe[0]

        # Check ingredients first
        cursor.callproc('check_ingredients_for_recipe', (recipe_id,))
        for result in cursor.stored_results():
            status = result.fetchone()[0]
        
        if status != "OK":
            return jsonify({"error": "Insufficient inventory"}), 400

        # Call transactional procedure
        cursor.callproc('confirm_order_transaction', (order_id,))
        conn.commit()

        return jsonify({"message": "Order confirmed and processed"})

    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        close_db_connection(conn)


if __name__ == '__main__':
    app.run(debug=True)


