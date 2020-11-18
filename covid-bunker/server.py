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

    return render_template("search.html", products=modified_products)

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
    product = map_product_query_result(product)
    return render_template("product_single.html", product=product)

# cart page
@app.route("/cart/")
def cart():
    return render_template("cart.html")

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
@app.route("/admin/")
def admin():
    conn = get_db()
    c = conn.cursor()
    products = c.execute('''
    SELECT * FROM Products;
    ''').fetchall()
    sales = {}
    urls = {}
    products_dict = map_product_query_results(products)

    for product in products_dict:
        sum = 0
        salePerItem = c.execute('''
        SELECT Qty, PricePer FROM ProductsSold WHERE PID=?;
        ''', (product['id'],)).fetchall()
        for singleSale in salePerItem:
            sum += int(singleSale[0])*float(singleSale[1])
        sales[product['id']] = "{:.2f}".format(sum)
        urls[product['id']] = url_for("admin_edit_product", PID=product['id'])
    return render_template("admin.html", urlAddProduct=url_for("admin_add_product"), urlsForEditProduct=urls, products=products_dict, sales=sales)

@app.route("/admin-add-product/", methods=['POST'])
def admin_post():
    productName = request.form.get("productName")
    productImg = request.files['product-img']
    description = request.form.get("description")
    quantity = request.form.get("quantity")
    price = request.form.get("price")

    try:
        quantity = int(quantity)
    except:
        flash("Quantity must be integer")
        return render_template("admin_add_product.html", productName=productName, productImg=productImg, description=description, quantity=quantity, price=price)
    try:
        price = float(price)
    except:
        flash("Invalid price")
        return render_template("admin_add_product.html", productName=productName, productImg=productImg, description=description, quantity=quantity, price=price)

    if productName is None or productName == "":
        flash("You need a product name")
        return render_template("admin_add_product.html", productName=productName, productImg=productImg, description=description, quantity=quantity, price=price)
    if productImg is None or productImg == "":
        flash("Please insert a picture of the product")
        return render_template("admin_add_product.html", productName=productName, productImg=productImg, description=description, quantity=quantity, price=price)
    if quantity is None or quantity < 0:
        flash("Quanity must be at least 0")
        return render_template("admin_add_product.html", productName=productName, productImg=productImg, description=description, quantity=quantity, price=price)
    if price is None or price <= 0:
        flash("This is a for-profit business. Charity is not allowed")
        return render_template("admin_add_product.html", productName=productName, productImg=productImg, description=description, quantity=quantity, price=price)

    if not allowed_file(productImg.filename):
        flash("Please upload a jpg or a png")
        return render_template("admin_add_product.html", productName=productName, productImg=productImg, description=description, quantity=quantity, price=price)

    filename = secure_filename(productImg.filename)
    productImg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


    conn = get_db()
    c = conn.cursor()
    c.execute('''
    INSERT INTO Products (Name, Description, Price, Qty, ImgURL) VALUES (?, ?, ?, ?, ?);
    ''', (productName, description, price, quantity, filename))
    conn.commit()
    return redirect(url_for("admin"))


# admin add product page
@app.route("/admin-add-product/", methods=['GET'])
def admin_add_product():
    return render_template("admin_add_product.html", productName="", productImg="", description="", quantity="", price="")

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
    return render_template("admin_edit_product.html", productName=product_dict['name'], productImg=product_dict['img'], description=product_dict['description'], quantity=product_dict['quantity'], price=product_dict['price'])




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
