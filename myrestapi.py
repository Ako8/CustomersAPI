from flask import Flask, request, jsonify, render_template, url_for, redirect, make_response
from custoemrs import Customer
import datetime
import sqlite3
import jwt


app = Flask(__name__)

cus_1 = Customer('Ako Gachechiladze', 'Puri, Yveli, Marili', 14.80)
cus_2 = Customer('Giorgi Mamasaxlisi', 'Tafli, Chai, Shaurma', 21.60)
cus_3 = Customer('Luka Manjavidze', 'Koptoni, Qeri, Mwvadi', 45.90)
cuss = [cus_1, cus_2, cus_3]


def default_customers(cuss):
	conn = database()
	c = conn.cursor()
	for cus in cuss:
		c.execute("INSERT INTO customers (name, items, price) VALUES (?, ?, ?)", 
			(cus.name, cus.items, cus.price))
		conn.commit()
	conn.close()


def database():
	conn = sqlite3.connect("customers.db")
	return conn


def table():
	try:
		conn = database()
		c = conn.cursor()
		c.execute("""CREATE TABLE customers (
			id INTEGER PRIMARY KEY,
			name TEXT,
			items TEXT,
			price REAL
			)""")
		default_customers(cuss)
	except:
		print("\n\n\n-----Table already exists-----\n\n\n")


@app.route("/customers/addnew", methods=['GET'])
def add_new():
	return render_template("addcus.html")


@app.route("/customers", methods=['GET', 'POST'])
def all_customer():
	conn = database()
	c = conn.cursor()
	c.execute("SELECT * FROM customers")

	rows = c.fetchall()
	customers = []

	for row in rows:
		customer = {'id': row[0], 'name': row[1], 'items': row[2], 'price': row[3]}
		customers.append(customer)

	if request.method == "POST":
		customer_id = request.form['nm']
		if customer_id.isdigit():
			if int(customer_id) <= len(customers) and int(customer_id) > 0:
				return redirect(url_for("customer_by_id", customer_id=customer_id))
			else:
				return render_template('customers.html', customers=customers)
		else:
			return render_template('customers.html', customers=customers)
	else:
		return render_template('customers.html', customers=customers)


@app.route("/customers/<int:customer_id>", methods=['GET', 'POST'])
def customer_by_id(customer_id):
	conn = database()
	c = conn.cursor()
	c.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
	customer = c.fetchone()
	
	return render_template("customer.html", customer=customer)


@app.route("/customers/add", methods=['POST'])
def add_customer():
	if request.method == "POST":
		name = request.form['name']
		items = request.form['items']
		price = request.form['price']
	conn = database()
	c = conn.cursor()
	if name and items and price:
		c.execute("INSERT INTO customers (name, items, price) VALUES (?, ?, ?)", (name, items, float(price)))
		conn.commit()
		conn.close()
	else:
		return redirect(url_for('add_new'))

	return redirect(url_for('all_customer'))


@app.route("/customers/delete/<int:customer_id>", methods=['DELETE','POST', 'GET'])
def delete_customer(customer_id):
	conn = database()
	c = conn.cursor()
	c.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
	conn.commit()
	conn.close()

	return redirect(url_for('all_customer'))


@app.route("/customers/update/<int:customer_id>", methods=['PUT','POST'])
def update_customer(customer_id):
	name = request.form['name']
	items = request.form['items']
	price = request.form['price']

	conn = database()
	c = conn.cursor()
	c.execute("UPDATE customers SET name = ?, items = ?, price = ? WHERE id = ?", (name, items, price, customer_id))
	conn.commit()
	conn.close()

	response = jsonify({'id': customer_id, 'name': name, 'items': items, 'price': price})
	response.status_code = 200
	return redirect(url_for('customer_by_id', customer_id=customer_id))

if __name__ == "__main__":
	table()
	app.run(debug=True)