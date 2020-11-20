"""
    COVID BUNKER
    By: Phillip Applegate, Isaac Lehman, Eric Martin, and Nathaniel Shi

    Your one stop shop for all things Covid.

    Options to run server:
    1.
        set FLASK_APP=server.py       (set the current server file to run)
        python -m flask run           (run the server)
    2.
        python server.py              (runs in debug mode)
"""
# set FLASK_APP=hello_world.py  (set the current server file to run)
# python -m flask run           (run the server)

''' ************************************************************************ '''
'''                                   IMPORTS                                '''
''' ************************************************************************ '''
from flask import Flask, render_template
from flask import request, session, flash
from flask import redirect, url_for
from flask import g
from flask import jsonify
from werkzeug.utils import secure_filename
import random
import urllib
import sqlite3
import os

''' ************************************************************************ '''
'''                                APP SET UP                                '''
''' ************************************************************************ '''

''' set app, cache time, and session secret key '''
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0 # no cache
app.config["SECRET_KEY"] = "!kn4fs%dkl#JED*BKS89" # Secret Key for Sessions
UPLOAD_FOLDER = 'static\img'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'gif'}
''' ************************************************************************ '''
'''                              DATABASE SET UP                             '''
''' ************************************************************************ '''

''' set database path '''
# get the path to the directory this script is in
scriptdir = os.path.dirname(__file__)
# add the relative path to the database file from there
dbpath = os.path.join(scriptdir, "db/db.sqlite3")

''' define databse functions for opening/closing connections '''
# Get db connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(dbpath)
    return db

# Close db connection (done automaticly)
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

''' ************************************************************************ '''
'''                               PYTHON FUNCTIONS                           '''
''' ************************************************************************ '''

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# returns a dictionary of the products: {id, name, description, price, quantity, img}
# for .fetchall
def map_product_query_results(products):
    return [{'id':product[0], 'name':product[1], 'description':product[2], 'price':product[3], 'quantity':product[4], 'img':product[5], 'category':product[6]} for product in products]

#if you did .fetchone
def map_product_query_result(product):
    return {'id':product[0], 'name':product[1], 'description':product[2], 'price':product[3], 'quantity':product[4], 'img':product[5], 'category':product[6]}


# filter products to only include ones in stock
def filter_in_stock(products):
    return [p for p in products if p['quantity'] > 0]


''' ************************************************************************ '''
'''                                 CART REUSE                               '''
''' ************************************************************************ '''
# check if single product has enough stock to sell
def is_in_stock(product, quantity):
    return product['quantity'] >= quantity

# returns a list of dictionaries (i.e. products)
def get_cart():
    # check if there is already a cart
    if 'cart' not in session or session['cart'] == None: # check if there already is a cart
        session['cart'] = []
    # get current contents of cart
    cart = session['cart']
    return cart

# sets session variable with cart list of dictionaries
def set_cart(cart):
    session['cart'] = cart
# returns true if product is in cart
def in_cart(cart, pid):
    try:
        return any(cart_item.get('id', -1) == pid for cart_item in cart)
    except Exception as e:
        return False


# set the value of a specific product in the cart
def set_cart_value(pid, key, value):
    for cart_item in cart:
        if cart_item.get('id', -1) == pid:
            cart_item[key] = value

# update the value of a specific product in the cart
def update_cart_value(cart, pid, key, value):
    for cart_item in cart:
        if cart_item.get('id', -1) == pid:
            cart_item[key] += value

# remove an item from the cart
def remove_from_cart(cart, pid):
    return [product for product in cart if product.get('id') != pid]

# return a dictionary of a product given a pID
def get_product(pid):
    try:
        pid = int(pid)
    except Exception as e:
        return "ERROR: Could not convert product key to integer", 403
    ### db stuff
    # get db connection
    conn = get_db()
    c = conn.cursor()
    # look up product in db
    product = c.execute('''
    SELECT * FROM Products WHERE PID=?;
    ''', (pid,)).fetchone()
    # check if bad product id
    if product is None:
        return "ERROR: product does not exist", 403
    # convert result into a dictionary
    product_dict = map_product_query_result(product)
    return product_dict

# add an item to cart Session and return the cart
# cart stores id, price, quantity
def add_product_to_cart_session(pid, quantity):
    # get a dictionary of the product from db
    product_dict = get_product(pid)
    # check if the requested quantity is available
    if not is_in_stock(product_dict, quantity):
        return "ERROR: there is only " + product_dict['quantity'] + ' available'

    ### add item to cart
    cart = get_cart()
    # check if product is not already in cart
    if not in_cart(cart, pid):
        # if item not already in cart
        cart.append(
            {
                'id':pid,
                'name':product_dict['name'],
                'price':product_dict['price'],
                'img':product_dict['img'],
                'description':product_dict['description'],
                'quantity':quantity
            }
        )
    else:
        # update quantity in cart
        update_cart_value(cart, pid,'quantity', quantity)
    # set the session variable to the updated cart
    set_cart(cart)

    return cart

# removes an item to cart Session and return the cart
# cart stores id, price, quantity
def remove_product_from_cart_session(pid):
    # get a dictionary of the product from db
    product_dict = get_product(pid)

    ### add item to cart
    cart = get_cart()
    # check if product is not already in cart
    if not in_cart(cart, pid):
        # no product to remove, just return the cart
        return cart
    else:
        # update quantity in cart
        cart = remove_from_cart(cart, pid)
    # set the session variable to the updated cart
    set_cart(cart)

    return cart




''' ************************************************************************ '''
'''                               VERIFICATION REUSE                         '''
''' ************************************************************************ '''
def verify_admin_product(template_name, productName, description, quantity, price, productImg, category, PID):
    try:
        quantity = int(quantity)
    except:
        flash("Quantity must be integer")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)
    try:
        price = float(price)
    except:
        flash("Invalid price")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)

    if productName is None or productName == "":
        flash("You need a product name")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)
    if (productImg is None or productImg == "") and template_name == "admin_add_product.html":
        flash("Please insert a picture of the product")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)
    if quantity is None or quantity < 0:
        flash("Quanity must be at least 0")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)
    if price is None or price <= 0:
        flash("This is a for-profit business. Charity is not allowed")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)

    if not allowed_file(productImg.filename) and template_name == "admin_add_product.html":
        flash("Please upload a jpg or a png")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)
    return ""
''' ************************************************************************ '''
'''                               ROUTE HANDLERS                             '''
''' ************************************************************************ '''

''' page handlers '''
### HOME ###
# home page
@app.route("/")
def home():
    # get all products
    conn = get_db()
    c = conn.cursor()
    products = c.execute('''
    SELECT pID, name, description, price, qty, ImgURL, category FROM Products;
    ''').fetchall()

    # convert products to dictionary
    modified_products = map_product_query_results(products)

    # filter out of stock products
    modified_products = filter_in_stock(modified_products)

    # choose random products to be featured
    num_random_products = 3 # number of featured products to choose
    featured_products = []
    try:
        featured_products = random.sample(modified_products, num_random_products)
    except IndexError as e:
        print('ERROR: Not enough products to choose 3 random featured ones. (Called from home)')

    # TODO: FILTER out products that are out of stock

    return render_template("home.html", products=modified_products, num_products=len(modified_products), featured_products=featured_products, signed_in=False)

### SEARCH ###
# search results
@app.route("/search/", methods=['GET'])
def search():
    query = None
    error_msg = "No results found..."
    try:
        if request.method == "GET":
            # get query
            query = request.args.get('s')
            num_query = query # if a number
            query = '%' + query + '%'

            # get searched products
            conn = get_db()
            c = conn.cursor()
            # execute query
            products = c.execute('''
            SELECT pID, name, description, price, qty, ImgURL, category FROM Products
            WHERE pID = ? OR
            name like ? OR
            description like ? OR
            category like ?''', (num_query, query, query, query)).fetchall()

            # convert products to dictionary
            modified_products = map_product_query_results(products)
            # filter out, out-of-stock products
            modified_products = filter_in_stock(modified_products)

            return render_template("search.html", products=modified_products, error_msg=error_msg)
    except Exception as e:
        print(e)
        error_msg = "Something went wrong..."

    return render_template("search.html", error_msg=error_msg)

### LOGIN ###
# login page
@app.route("/login/", methods=['GET'])
def login_get():
    return render_template("login.html")

# login page (after login submission)
@app.route("/login/", methods=['POST'])
def login_post():
    return render_template("login.html")

### REGISTER ###
# register page
@app.route("/register/", methods=['GET'])
def register_get():
    return render_template("register.html")

# register page (after login submission)
@app.route("/register/", methods=['POST'])
def register_post():
    return render_template("register.html")

# profile page
@app.route("/profile/")
def profile():
    return render_template("profile.html")

### PRODUCTS ###
# product page
@app.route("/product/<int:pid>/")
def product(pid):
    conn = get_db()
    c = conn.cursor()
    product = c.execute('''
    SELECT pID, name, description, price, qty, ImgURL, category FROM Products where pID = ?;
    ''', (pid,)).fetchone()
    if(product):
        product = map_product_query_result(product)
        return render_template("product_single.html", product=product)
    else:
        return

# cart page
@app.route("/cart/")
def cart():
    products = get_cart()
    return render_template("cart.html", products=products)

# checkout page
@app.route("/checkout/")
def checkout():
    return render_template("checkout.html")

# checkout confirmation page
@app.route("/checkout_confirmation/")
def checkout_confirmation():
    return render_template("checkout_confirmation.html")

### ADMIN ###
# admin overview page
@app.route("/admin/", methods=['GET'])
def admin():
    conn = get_db()
    c = conn.cursor()
    products = c.execute('''
    SELECT * FROM Products;
    ''').fetchall()
    sales = {}
    urlsEdit = {}
    urlsDelete={}
    products_dict = map_product_query_results(products)

    for product in products_dict:
        sum = 0
        salePerItem = c.execute('''
        SELECT Qty, PricePer FROM ProductsSold WHERE PID=?;
        ''', (product['id'],)).fetchall()
        for singleSale in salePerItem:
            sum += int(singleSale[0])*float(singleSale[1])
        sales[product['id']] = "{:.2f}".format(sum)
        urlsEdit[product['id']] = url_for("admin_edit_product", PID=product['id'])
        urlsDelete[product['id']]= url_for("admin_delete_product", PID=product['id'])


    return render_template("admin.html", urlAddProduct=url_for("admin_add_product"), urlsForEditProduct=urlsEdit, urlsForDeleteProduct=urlsDelete, products=products_dict, sales=sales)

@app.route("/admin/<int:PID>/")
def admin_delete_product(PID):
    conn = get_db()
    c = conn.cursor()
    image_url = c.execute('''
    SELECT ImgURL FROM Products WHERE PID=?
    ''', (PID, )).fetchone()
    fullPath = os.path.join(app.config['UPLOAD_FOLDER'], image_url[0])
    if os.path.exists(fullPath):
        os.remove(fullPath)
    else:
        print("Image could not be found")
    c.execute('''
    DELETE FROM Products WHERE PID=?
    ''', (PID, ))
    conn.commit()
    return redirect(url_for("admin"))

@app.route("/admin-add-product/", methods=['POST'])
def admin_post():
    productName = request.form.get("productName")
    productImg = request.files['product-img']
    description = request.form.get("description")
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    category = request.form.get("category")
    verification = verify_admin_product("admin_add_product.html", productName, description, quantity, price, productImg, category, -1)
    if verification != "":
        return verification

    filename = secure_filename(productImg.filename)
    productImg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO Products (Name, Description, Price, Qty, ImgURL, Category) VALUES (?, ?, ?, ?, ?, ?);
    ''', (productName, description, price, quantity, filename, category))
    conn.commit()
    return redirect(url_for("admin"))


# admin add product page
@app.route("/admin-add-product/", methods=['GET'])
def admin_add_product():
    return render_template("admin_add_product.html", productName="", productImg="", description="", quantity="", price="", category="toilet paper")

# admin edit product page
@app.route("/admin-edit-product/<int:PID>", methods=['GET'])
def admin_edit_product(PID):
    conn = get_db()
    c = conn.cursor()
    product = c.execute('''
    SELECT * FROM Products WHERE PID=?;
    ''', (PID,)).fetchone()
    if product is None:
        flash("Product could not be found")
        return redirect(url_for("admin"))
    product_dict =map_product_query_result(product)
    return render_template("admin_edit_product.html", productName=product_dict['name'], productImg=product_dict['img'], description=product_dict['description'], quantity=product_dict['quantity'], price=product_dict['price'], category=product_dict['category'], PID=product_dict['id'])


@app.route("/admin-edit-product/<int:PID>", methods=['POST'])
def admin_save_edited_product(PID):
    productName = request.form.get("productName")
    productImg = request.files['product-img']
    description = request.form.get("description")
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    category = request.form.get("category")
    print(PID)
    verification = verify_admin_product("admin_edit_product.html", productName, description, quantity, price, productImg, category, PID)
    if verification != "":
        return verification

    conn = get_db()
    c = conn.cursor()

    if (not allowed_file(productImg.filename)):
        c.execute('''
        UPDATE Products SET Name=?, Description=?, Price=?, Qty=?, Category=? WHERE PID=?;
        ''', (productName, description, price, quantity, category, PID))
    else:
        image_url = c.execute('''
        SELECT ImgURL FROM Products WHERE PID=?
        ''', (PID, )).fetchone()
        fullPath = os.path.join(app.config['UPLOAD_FOLDER'], image_url[0])
        if os.path.exists(fullPath):
            os.remove(fullPath)
        else:
            print("Image could not be found")
        filename = secure_filename(productImg.filename)
        productImg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        c.execute('''
        UPDATE Products SET Name=?, Description=?, Price=?, Qty=?, ImgURL=?, Category=? WHERE PID=?;
        ''', (productName, description, price, quantity, filename, category, PID))

    conn.commit()
    return redirect(url_for("admin"))

''' ajax requests '''
@app.route('/ajax_add_to_cart/', methods=['POST'])
def ajax_add_to_cart():
    pid = request.form.get('pid')

    quantity = 1
    if 'quantity' in request.form:
        quantity = request.form.get('quantity')

    cart = add_product_to_cart_session(pid, quantity)

    return jsonify(cart)

@app.route('/ajax_get_cart/', methods=['GET'])
def ajax_get_cart():
    cart = get_cart()
    return jsonify(cart)

@app.route('/ajax_remove_item_from_cart/', methods=['POST'])
def ajax_remove_item_from_cart():
    pid = request.form.get('pid')
    cart = remove_product_from_cart_session(pid)
    return jsonify(cart)


''' errors handlers '''
@app.errorhandler(404)
def page_not_found_404(e):
    return render_template("error.html", code=404, description="Not Found"), 404

@app.errorhandler(500)
def page_not_found_500(e):
    return render_template("error.html", code=500, description="server error"), 500


if __name__ == "__main__":
    app.run(debug=True)

# Having debug=True allows possible Python errors to appear on the web page
# run with $> python server.py

#FileReader
#FileList
#Select and display images using FileReader
