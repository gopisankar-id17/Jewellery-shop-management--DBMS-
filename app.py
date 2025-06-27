from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database initialization
DATABASE = 'test.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return redirect(url_for('customer'))

@app.route('/customer')
def customer():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM book').fetchall()
    conn.close()
    return render_template('Customer.html', books=books)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    book_id = request.form['book_id']
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM book WHERE id = ?', (book_id,)).fetchone()
    conn.close()

    if book:
        cart = session.get('cart', [])
        cart.append(dict(book))
        session['cart'] = cart
        flash(f"Added '{book['title']}' to cart.", 'success')
    return redirect(url_for('customer'))

# Route to render the cart page
@app.route('/cart')
def cart():
    return render_template('cart.html')

# Route to render the wishlist page
@app.route('/wishlist')
def wishlist():
    return render_template('wishlist.html')

# API endpoint to add a book to cart (optional server-side implementation)
@app.route('/api/add_to_cart', methods=['POST'])
def api_add_to_cart():
    if 'cart' not in session:
        session['cart'] = []
    
    book_id = request.json.get('id')
    
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM book WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    
    if book:
        book_dict = dict(book)
        cart_item = {
            'id': book_dict['id'],
            'title': book_dict['title'],
            'author': book_dict['author'],
            'price': book_dict['price'],
            'quantity': 1
        }
        session['cart'].append(cart_item)
        session.modified = True
        return jsonify({'success': True, 'message': 'Book added to cart', 'cart_count': len(session['cart'])})
    
    return jsonify({'success': False, 'message': 'Book not found'})

# API endpoint to get cart items (optional server-side implementation)
@app.route('/api/get_cart')
def get_cart():
    if 'cart' not in session:
        session['cart'] = []
    
    return jsonify({'cart': session['cart']})

# API endpoint to update cart item quantity (optional server-side implementation)
@app.route('/api/update_cart_item', methods=['POST'])
def update_cart_item():
    if 'cart' not in session:
        session['cart'] = []
    
    book_id = request.json.get('id')
    quantity = request.json.get('quantity')
    
    for item in session['cart']:
        if item['id'] == book_id:
            item['quantity'] = quantity
            session.modified = True
            break
    
    return jsonify({'success': True, 'message': 'Cart updated'})

# API endpoint to remove cart item (optional server-side implementation)
@app.route('/api/remove_cart_item', methods=['POST'])
def remove_cart_item():
    if 'cart' not in session:
        session['cart'] = []
    
    book_id = request.json.get('id')
    
    session['cart'] = [item for item in session['cart'] if item['id'] != book_id]
    session.modified = True
    
    return jsonify({'success': True, 'message': 'Item removed from cart', 'cart_count': len(session['cart'])})

# API endpoint to clear cart (optional server-side implementation)
@app.route('/api/clear_cart', methods=['POST'])
def clear_cart():
    session['cart'] = []
    session.modified = True
    
    return jsonify({'success': True, 'message': 'Cart cleared'})

# Helper function to get a book by ID
def get_book_by_id(book_id):
    conn = get_db_connection()
    book = conn.execute('SELECT * FROM book WHERE id = ?', (book_id,)).fetchone()
    conn.close()
    return dict(book) if book else None

@app.route('/manager')
def manager():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM book').fetchall()
    # Convert Row objects to dictionaries
    books = [dict(book) for book in books]
    conn.close()
    return render_template('Manager.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    description = request.form['description']

    conn = get_db_connection()
    conn.execute('INSERT INTO book (title, author, genre, price, stock, description) VALUES (?, ?, ?, ?, ?, ?)',
                 (title, author, genre, price, stock, description))
    conn.commit()
    conn.close()

    flash(f"Book '{title}' added successfully!", 'success')
    return redirect(url_for('manager'))

@app.route('/remove_book/<int:book_id>', methods=['POST'])
def remove_book(book_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM book WHERE id = ?', (book_id,))
    conn.commit()
    conn.close()

    flash(f'Book ID {book_id} removed.', 'danger')
    return redirect(url_for('manager'))

@app.route('/edit_book', methods=['POST'])
def edit_book():
    book_id = request.form['id']
    title = request.form['title']
    author = request.form['author']
    genre = request.form['genre']
    price = float(request.form['price'])
    stock = int(request.form['stock'])
    description = request.form['description']

    conn = get_db_connection()
    conn.execute('''
        UPDATE book 
        SET title = ?, author = ?, genre = ?, price = ?, stock = ?, description = ?
        WHERE id = ?
    ''', (title, author, genre, price, stock, description, book_id))
    conn.commit()
    conn.close()

    flash(f"Book '{title}' updated successfully!", 'success')
    return redirect(url_for('manager'))

if __name__ == '__main__':
    app.run(debug=True)
