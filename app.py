from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi

app = Flask(__name__)

# MongoDB configuration
cluster = MongoClient("mongodb+srv://admin:admin@cluster0.3rtsl.mongodb.net/?retryWrites=true&w=majority&appName=cluster0",
                      tlsCAFile=certifi.where())
db = cluster["titan"]
products_collection = db["products"]


@app.route("/", methods=["GET", "POST"])
def home():
    # Get filter parameters
    category = request.args.get("category", "all")
    search_term = request.args.get("search", "")

    params = db["params"].find_one()
    profit_percent = params["profit_percent"]
    exchange_rate = params["exchange_rate"]

    if request.method == "POST":
        # Update profit_percent and exchange_rate in the params collection
        new_profit_percent = int(request.form.get("profit_percent"))
        new_exchange_rate = int(request.form.get("exchange_rate"))

        db["params"].update_one(
            {},
            {"$set": {"profit_percent": new_profit_percent, "exchange_rate": new_exchange_rate}}
        )

        return redirect(url_for("home"))

    # Build query
    query = {}
    if category != "all":
        query["category"] = category
    if search_term:
        query["name"] = {"$regex": search_term, "$options": "i"}

    # Get products and categories
    products = list(products_collection.find(query))
    categories = products_collection.distinct("category")

    for product in products:
        product["mnt"] = int((product["price"] + product["cargo"]) * (1 + profit_percent / 100) * exchange_rate)

    return render_template("index.html",
                           products=products,
                           categories=categories,
                           selected_category=category,
                           search_term=search_term,
                           profit_percent=profit_percent,
                           exchange_rate=exchange_rate)


@app.route("/add_product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        new_product = {
            "id": request.form["id"],
            "name": request.form["name"],
            "type": request.form["type"],
            "price": float(request.form["price"]),
            "cargo": float(request.form["cargo"]),
            "stock": int(request.form["stock"])
        }
        products_collection.insert_one(new_product)
        return redirect(url_for("home"))
    return render_template("add_product.html", categories=products_collection.distinct("category"))


@app.route("/edit_product/<product_id>", methods=["GET", "POST"])
def edit_product(product_id):
    product = products_collection.find_one({"_id": ObjectId(product_id)})

    if request.method == "POST":
        update_data = {
            "id": request.form["id"],
            "name": request.form["name"],
            "type": request.form["type"],
            "price": float(request.form["price"]),
            "cargo": float(request.form["cargo"]),
            "stock": int(request.form["stock"])
        }
        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        return redirect(url_for("home"))

    return render_template("edit_product.html",
                           product=product,
                           categories=products_collection.distinct("category"))


@app.route("/delete_product/<product_id>")
def delete_product(product_id):
    products_collection.delete_one({"_id": ObjectId(product_id)})
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

