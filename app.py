from flask import Flask, render_template, request, redirect, url_for, flash
from people import get_customer_by_id
from meat import meat_items

app = Flask(__name__)
app.secret_key = "your_secret_key"

orders = []

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        customer_id = request.form.get("customer_id")
        customer = get_customer_by_id(customer_id)
        if customer:
            return redirect(url_for("hand", customer_id=customer_id))
        else:
            flash("올바르지 않은 아이디입니다.")
    return render_template("index.html")

@app.route("/hand/<customer_id>", methods=["GET", "POST"])
def hand(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return redirect(url_for("index"))

    # 기존 주문이 있는지 확인
    existing_order = next((order for order in orders if order["customer"]["id"] == customer_id), None)
    
    if existing_order:
        flash("이 고객은 이미 주문을 완료하였습니다.")
        return redirect(url_for("hi"))
    
    if request.method == "POST":
        selected_items = request.form.getlist("items")
        quantities = request.form.getlist("quantities")
        order_details = []
        total_price = 0
        
        for item, quantity in zip(selected_items, quantities):
            quantity = int(quantity)
            meat_item = next(m for m in meat_items if m["name"] == item)
            price = meat_item["price"] * quantity
            order_details.append({"item": item, "quantity": quantity, "price": price})
            total_price += price
        
        orders.append({"customer": customer, "details": order_details, "total_price": total_price})
        flash("주문이 완료되었습니다.")
        return redirect(url_for("hand", customer_id=customer_id))

    # 주문 내역을 같은 페이지에 표시
    existing_order = next((order for order in orders if order["customer"]["id"] == customer_id), None)
    return render_template("hand.html", customer=customer, meat_items=meat_items, existing_order=existing_order)

@app.route("/hi")
def hi():
    return render_template("hi.html", orders=orders)

@app.route("/delete_order/<int:order_index>", methods=["POST"])
def delete_order(order_index):
    if 0 <= order_index < len(orders):
        del orders[order_index]
    return redirect(url_for("hi"))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    admin_password = "admin123"
    if request.method == "POST":
        password = request.form.get("password")
        if password == admin_password:
            return redirect(url_for("hi"))
        else:
            flash("잘못된 관리자 비밀번호입니다.")
    return render_template("admin.html")

if __name__ == "__main__":
    app.run(debug=True)
