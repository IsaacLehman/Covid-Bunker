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

    Some pip stuff:
    pip install --upgrade google-auth
    pip install --upgrade requests
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
from datetime import datetime
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import timedelta
import random
import urllib
import sqlite3
import os
import smtplib, ssl, email
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from google.oauth2 import id_token
from google.auth.transport import requests

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
'''                                EMAIL SET UP                                '''
''' ************************************************************************ '''
gmail_user = 'comp342gccf19@gmail.com'
gmail_password = 'P@$$word1!'
gmail_admin = 'ciremt58@gmail.com'

''' ************************************************************************ '''
'''                                LOGIN                                '''
''' ************************************************************************ '''
# define our login required wrapper
def login_required(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		# check that session has a uid that is still good
		uid = session.get("uid")
		try:
			exp_str = session.get("expires",'')
			exp = datetime.strptime(exp_str, "%Y-%m-%dT%H:%M:%SZ")
		except ValueError:
			exp = None
		# if uid or exp is missing or exp has passed . . .
		if uid is None or exp is None or exp < datetime.utcnow():
			# here I return a forbidden error - you could redirect to login
			return redirect(url_for("login_get"))
		# only if the user is logged in should the route handler run
		return f(*args, **kwargs)
	return wrapper


def is_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
	    # check that session has a uid that is still good
        admin = session.get("admin")
        print(admin)
        try:
            exp_str = session.get("expires",'')
            exp = datetime.strptime(exp_str, "%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            exp = None
        # if uid or exp is missing or exp has passed . . .
        print("Failed in final check")
        if admin is None or exp is None or exp < datetime.utcnow() or admin is False:
            # here I return a forbidden error - you could redirect to login
            print("SHould not be here")
            return redirect(url_for("login_get"))
        # only if the user is logged in should the route handler run
        return f(*args, **kwargs)
    return wrapper
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

def map_sale_query_results(sales):
    return [{'SID':sale[0], 'Total':sale[1], 'UID':sale[2], 'Date':sale[3], 'Status':sale[4]} for sale in sales]

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
    #Check the quantity
    try:
        quantity = int(quantity)
    except:
        flash("Quantity must be integer")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)

    #Check the price
    try:
        price = float(price)
    except:
        flash("Invalid price")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)

    #Check the product Name
    if productName is None or productName == "":
        flash("You need a product name")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)

    #Check the product Image
    if (productImg is None or productImg == "") and template_name == "admin_add_product.html":
        flash("Please insert a picture of the product")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)

    #Check that the quanity is nonnegative
    if quantity is None or quantity < 0:
        flash("Quanity must be at least 0")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)

    #Check that the price is greater than 0
    if price is None or price <= 0:
        flash("This is a for-profit business. Charity is not allowed")
        return render_template(template_name, productName=productName, productImg=productImg, description=description, quantity=quantity, price=price, category=category, PID=PID)

    #Check that the image file is of allowed type
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

    return render_template("home.html", products=modified_products, num_products=len(modified_products), featured_products=featured_products)

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
    uid = request.form.get("uid")
    c = get_db().cursor()
    users = c.execute("SELECT uid, isAdmin, email from Users where uid=?", (uid,)).fetchone()

    if len(users) == 0:
        flash("invalid uid")
        return redirect(url_for("login_get"))


    session['uid'] = request.form.get("uid")
    session['signed_in'] = True
    session['email'] = users[2]
    expires = datetime.utcnow()+timedelta(hours=24)
    session["expires"] = expires.strftime("%Y-%m-%dT%H:%M:%SZ")
    if users[1] == 0:
        session['admin'] = False
    else:
        session['admin'] = True
        return redirect(url_for("admin"))
    return redirect(url_for("profile"))

@app.route("/logout/", methods=['GET'])
def logout():
    session['uid'] = None
    session['email'] = None
    session['img'] = None
    session['name'] = None
    session['signed_in'] = False
    return redirect(url_for("home"))

### GOOGLE TOKEN AUTHENTICATION FOR LOGIN ###
@app.route('/tokensignin/', methods=["POST"])
def google_authentication_ajax():
    # (Receive token by HTTPS POST)
    token = request.form.get('idtoken')
    name = request.form.get('name')
    img = request.form.get('img')
    email = request.form.get('email')
    try:
        # Specify the CLIENT_ID of the app that accesses the backend:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), "128673522219-v8ul49r61i5u4ujdqhohspk0lq4b4a9t.apps.googleusercontent.com")

        # ID token is valid. Get the user's Google Account ID from the decoded token.
        userid = idinfo['sub']
        session['uid'] = userid
        session['name'] = name
        session['img'] = img
        session['email'] = email
        session['signed_in'] = True

        #Connect to the database
        conn = get_db()
        c = conn.cursor()

        # check if the user is admin or customer
        user = c.execute('''
        SELECT isAdmin FROM Users WHERE UID=?;
        ''', (userid, )).fetchone()

        if (user is None): # if not in db, add to db
            c.execute('''
            INSERT INTO Users (UID, isAdmin, Email, Address) VALUES (?, 0, ?, "")
            ''', (userid, email))
            conn.commit()
        elif user[0] == 1:
            session['admin'] = True
        else:
            session['admin'] = False

        return userid
    except Exception as e:
        print("Bad happened", e)
        return ""


# profile page
@app.route("/profile/")
def profile():
    if session['signed_in']:
        uid = session['uid']
        c = get_db().cursor()
        sales = c.execute('''
        SELECT SID, Total, Date, Status FROM Sales WHERE UID = ?;
        ''', (uid,)).fetchall()

""" TODO impliment products sold
        for sale in sales:
            sid = sale[0]
            products_sold = c.execute('''
            SELECT ProductsSold.pid, Name, ProductsSold.Qty, price FROM ProductsSold JOIN products ON Products.PID = ProductsSold.PID where SID = ?;
            ''', (sid,)).fetchall()
            s = list(sale)
            print(products_sold)
            s.append(products_sold)
            sale = tuple(s)
"""

        # attempt to get past purchases

    return render_template("profile.html", sales=sales)

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
    products = get_cart()
    return render_template("cart.html", products=products)

# checkout page
@app.route("/checkout/", methods=['GET'])
@app.route("/checkout/<int:PID>", methods=['GET'])
@app.route("/checkout/<int:PID>/<int:quantity>", methods=['GET'])
def checkout(PID=0, quantity=1):

    if session['signed_in'] == False:
        return redirect(url_for("login_get"))

    address = get_db().cursor().execute("select address from Users where uid = ?", (session['uid'],)).fetchone()[0]


    products = []
    total_price = 0.0
    if (PID == 0):
        #Get the cart
        products = get_cart()
        for p in products:
            total_price += p['price'] * p['quantity']
    else:
        #Connect to the database
        conn = get_db()
        c = conn.cursor()

        #Get the product that is being bought now
        product = c.execute('''
        SELECT * FROM Products WHERE PID=?;
        ''', (PID, )).fetchone()

        if (product is None or product==""):
            products = "" # no product was found
        else:
            #Set the product quantity to the quantity to be purchased
            product = map_product_query_result(product)
            total_price += product['price'] * quantity
            print(product['price'], product['quantity'])
            product['quantity']=quantity
            products.append(product)



    session['itemsPurchased'] = products
    session['purchaseCost'] = total_price
    return render_template("checkout.html", products=products, total_price=total_price, address=address)

@app.route("/checkout/", methods=['POST'])
def purchase():

    valid = True

    if request.form.get("ccn") is None or request.form.get("ccn") == "":
        valid = False
        flash("Credit Card Number is required!")
    if request.form.get("cvv") is None or request.form.get("cvv") == "":
        valid = False
        flash("CVV is required!")
    if request.form.get("exp-mon") is None or request.form.get("exp-mon") == "" or request.form.get("exp-year") is None or request.form.get("exp-year") == "":
        valid = False
        flash("Expiration date is required!")
    if request.form.get("address") is None or request.form.get("address") == "":
        valid = False
        flash("Shipping address is required!")
        print('here')
    try:
        int(request.form.get("ccn"))
        int(request.form.get("cvv"))
        int(request.form.get("exp-mon"))
        int(request.form.get("exp-year"))
    except:
        valid = False
        flash("Illegal input!")

    if valid == False:
        return redirect(url_for("checkout"))
    # if we mess up on an individual buy page, it won't take us back to it just yet

    address = request.form.get("address")
    get_db().cursor().execute("UPDATE Users SET address = ? WHERE uid = ?", (address, session['uid']))
    get_db().commit()


    purchasedItems = session.get("itemsPurchased")

    #THIS NEEDS TO BE CHANGED
    userID = session['uid']####''' ''''

    #Return to checkout if no items were puchased
    if (purchasedItems == ""):
        return redirect(url_for("checkout"))
    print(purchasedItems)

    #Find the total cost of the items purchased
    sum = 0
    for product in purchasedItems:
        costPerItem = product['price']
        sum += costPerItem*product['quantity']

    #Connect to the database
    conn = get_db()
    c = conn.cursor()

    #Create the sale
    #"""
    date = datetime.now()
    c.execute('''
    INSERT INTO Sales (Total, UID, Date, Status) VALUES (?, ?, ?, "Waiting to be shipped");
    ''', (sum, userID, date))
    conn.commit()

    #Find the sale ID
    sales = c.execute('''
    SELECT SID FROM Sales WHERE Total=? AND UID=? AND Date=?;
    ''', (sum, userID, date)).fetchone()
    saleID=sales[0]

    #For each product sold
    for product in purchasedItems:
        #Enter the purchase into the database
        c.execute('''
        INSERT INTO ProductsSold (SID, PID, Qty, PricePer) VALUES (?, ?, ?, ?);
        ''', (saleID, product['id'], product['quantity'], product['price']))
        conn.commit()

        #Update the quantity
        c.execute('''
        UPDATE Products SET Qty=Qty-? WHERE PID=?;
        ''', (product['quantity'], product['id']))
        conn.commit()

        #Remove the item from the cart
        if product in get_cart():
            print("Remove from cart")
            cart = remove_from_cart(get_cart(), product['id'])
            set_cart(cart)

    #Send an email to the admin
    message = MIMEMultipart("alternative")
    message["Subject"] = "Product purchased"
    message["From"] = "Covid Bunker"
    message["To"] = session.get("name")

    messageA = MIMEMultipart("alternative")
    messageA["Subject"] = "Product purchased"
    messageA["From"] = "Covid Bunker"
    messageA["To"] = "Admin"

    #The content of the email
    html = render_template("product_display.html", products=purchasedItems, admin="False")
    payload = MIMEText(html, "html")
    message.attach(payload)

    #The content of the email
    htmlA = render_template("product_display.html", products=purchasedItems, admin="True")
    payloadA = MIMEText(htmlA, "html")
    messageA.attach(payloadA)

    #Email the admin
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(gmail_user, gmail_password)
        server.sendmail(
            gmail_user, gmail_admin, messageA.as_string()
        )
        server.sendmail(
            gmail_user, session.get("email"), message.as_string()
        )
    #"""
    session['itemsPurchased'] = ""
    session['purchaseCost'] = 0
    return redirect(url_for("checkout_confirmation"))

# checkout confirmation page
@app.route("/checkout_confirmation/")
def checkout_confirmation():
    address = get_db().cursor().execute("select address from Users where uid = ?", (session['uid'],)).fetchone()[0]

    return render_template("checkout_confirmation.html", address=address)

### ADMIN ###
# admin overview page
@app.route("/admin/", methods=['GET'])
@is_admin
def admin():
    #Connect to the database
    conn = get_db()
    c = conn.cursor()

    #Get all the products in the database
    products = c.execute('''
    SELECT * FROM Products;
    ''').fetchall()

    #Total sales for each product
    sales = {}

    #The urls to edit a product
    urlsEdit = {}

    #The urls to delete a product
    urlsDelete={}

    #Make the products a dictionary
    products_dict = map_product_query_results(products)

    #For all the products in the sytem
    for product in products_dict:
        sum = 0
        #Find all the sales for a given item
        salePerItem = c.execute('''
        SELECT Qty, PricePer FROM ProductsSold WHERE PID=?;
        ''', (product['id'],)).fetchall()
        #Find the sum of all the sales
        for singleSale in salePerItem:
            sum += int(singleSale[0])*float(singleSale[1])
        #Store the sums to be displayed
        sales[product['id']] = "{:.2f}".format(sum)
        #Create the urls
        urlsEdit[product['id']] = url_for("admin_edit_product", PID=product['id'])
        urlsDelete[product['id']]= url_for("admin_delete_product", PID=product['id'])


    return render_template("admin.html", urlAddProduct=url_for("admin_add_product"), urlsForEditProduct=urlsEdit, urlsForDeleteProduct=urlsDelete, products=products_dict, sales=sales)

#Delete the product specified in the URL
@app.route("/admin/<int:PID>/")
@is_admin
def admin_delete_product(PID):
    #Connect to the database
    conn = get_db()
    c = conn.cursor()

    #Get the url of the image
    image_url = c.execute('''
    SELECT ImgURL FROM Products WHERE PID=?
    ''', (PID, )).fetchone()
    fullPath = os.path.join(app.config['UPLOAD_FOLDER'], image_url[0])

    #Delete the saved image
    if os.path.exists(fullPath):
        os.remove(fullPath)
    else:
        print("Image could not be found")

    #Delete the product from the database
    c.execute('''
    DELETE FROM Products WHERE PID=?
    ''', (PID, ))
    conn.commit()
    return redirect(url_for("admin"))

#Add the product to the database
@app.route("/admin-add-product/", methods=['POST'])
@is_admin
def admin_post():
    #Get the form fields
    productName = request.form.get("productName")
    productImg = request.files['product-img']
    description = request.form.get("description")
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    category = request.form.get("category")

    #Verify the fields
    verification = verify_admin_product("admin_add_product.html", productName, description, quantity, price, productImg, category, -1)
    if verification != "":
        return verification

    #Save the image to the file system
    filename = secure_filename(productImg.filename)
    productImg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    #Connect to the database
    conn = get_db()
    c = conn.cursor()

    #Insert the new product into the database
    c.execute('''
    INSERT INTO Products (Name, Description, Price, Qty, ImgURL, Category) VALUES (?, ?, ?, ?, ?, ?);
    ''', (productName, description, price, quantity, filename, category))
    conn.commit()

    return redirect(url_for("admin"))


# admin add product page
@app.route("/admin-add-product/", methods=['GET'])
@is_admin
def admin_add_product():
    return render_template("admin_add_product.html", productName="", productImg="", description="", quantity="", price="", category="toilet paper")

# admin edit product page
@app.route("/admin-edit-product/<int:PID>", methods=['GET'])
@is_admin
def admin_edit_product(PID):
    #Connect to the database
    conn = get_db()
    c = conn.cursor()

    #Get the selected product from the database
    product = c.execute('''
    SELECT * FROM Products WHERE PID=?;
    ''', (PID,)).fetchone()

    #Redirect to the admin main page if the product could not be found
    if product is None:
        flash("Product could not be found")
        return redirect(url_for("admin"))

    #Turn the product into a dictionary
    product_dict =map_product_query_result(product)

    return render_template("admin_edit_product.html", productName=product_dict['name'], productImg=product_dict['img'], description=product_dict['description'], quantity=product_dict['quantity'], price=product_dict['price'], category=product_dict['category'], PID=product_dict['id'])

#Save the edited product
@app.route("/admin-edit-product/<int:PID>", methods=['POST'])
@is_admin
def admin_save_edited_product(PID):
    #Get the field from the form
    productName = request.form.get("productName")
    productImg = request.files['product-img']
    description = request.form.get("description")
    quantity = request.form.get("quantity")
    price = request.form.get("price")
    category = request.form.get("category")

    #Verify the fields
    verification = verify_admin_product("admin_edit_product.html", productName, description, quantity, price, productImg, category, PID)
    if verification != "":
        return verification

    #Connect to the database
    conn = get_db()
    c = conn.cursor()

    #If the user did upload a new image
    if (not allowed_file(productImg.filename)):
        #Update the product
        c.execute('''
        UPDATE Products SET Name=?, Description=?, Price=?, Qty=?, Category=? WHERE PID=?;
        ''', (productName, description, price, quantity, category, PID))
    else:
        #Get the old image
        image_url = c.execute('''
        SELECT ImgURL FROM Products WHERE PID=?
        ''', (PID, )).fetchone()
        fullPath = os.path.join(app.config['UPLOAD_FOLDER'], image_url[0])

        #Remove the old image
        if os.path.exists(fullPath):
            os.remove(fullPath)
        else:
            print("Image could not be found")

        #Save the new image
        filename = secure_filename(productImg.filename)
        productImg.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        #Save the edited product to the database
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
        try:
            quantity = int(quantity)
        except Exception as e:
            return "ERROR: Quantity must be an integer", 400

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

@app.route("/sales_data/")
def sales_data():
    #Connect to the database
    conn = get_db()
    c = conn.cursor()

    #Get the sales
    sales = c.execute('''
    SELECT * FROM Sales''').fetchall()

    #Change to a dictionary
    salesDict = map_sale_query_results(sales)

    output = []

    for sale in salesDict:
        #Get just the date as a string
        date = str(datetime.strptime(sale.get("Date"), '%Y-%m-%d %H:%M:%S.%f').date())

        foundDate = False
        #Find the total for each date
        for data in output:

            if date == data.get("Date") or date in data.get("Date"):
                data['Total'] += float(sale.get("Total"))
                foundDate = True
                break
        if not foundDate:
            salePerDate = {
            'Date': date,
            'Total': float(sale.get("Total"))
            }
            output.append(salePerDate)
    return jsonify(output)


''' errors handlers '''
@app.errorhandler(400)
def page_not_found_400(e):
    return render_template("error.html", code=404, description="You Made A Bad Request"), 400

@app.errorhandler(401)
def page_not_found_401(e):
    return render_template("error.html", code=404, description="Unauthorized Access"), 401

@app.errorhandler(403)
def page_not_found_403(e):
    return render_template("error.html", code=404, description="Access Forbidden"), 403

@app.errorhandler(404)
def page_not_found_404(e):
    return render_template("error.html", code=404, description="Page Not Found"), 404

@app.errorhandler(500)
def page_not_found_500(e):
    return render_template("error.html", code=500, description="Internal Server Error"), 500


if __name__ == "__main__":
    app.run(debug=True)

# Having debug=True allows possible Python errors to appear on the web page
# run with $> python server.py

#FileReader
#FileList
#Select and display images using FileReader
