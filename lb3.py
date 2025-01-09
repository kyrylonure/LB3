from flask import Flask, jsonify, request, abort
from flask_httpauth import HTTPBasicAuth

app = Flask(__name__)
auth = HTTPBasicAuth()

# Дані для аутентифікації
users = {
    "admin": "password123",
    "user": "pass123"
}

# Дані каталогу товарів
catalog = {
    1: {"name": "Cofe1", "price": 100.25, "weight": 1.0},
    2: {"name": "Cofe2", "price": 80.50, "weight": 1.2},
    3: {"name": "Cofe3", "price": 120.75, "weight": 0.8}
}


# Аутентифікація
@auth.get_password
def get_password(username):
    return users.get(username)


@auth.error_handler
def unauthorized():
    return jsonify({"error": "Unauthorized access"}), 401


# Головна сторінка
@app.route('/')
def home():
    return jsonify({"message": "Welcome to the catalog API!"})


# Ендпоінт для роботи з усіма товарами
@app.route('/items', methods=['GET', 'POST'])
@auth.login_required
def items():
    if request.method == 'GET':
        return jsonify(catalog)

    elif request.method == 'POST':
        data = request.get_json()
        if not data or not all(k in data for k in ("id", "name", "price", "weight")):
            abort(400, "Invalid data format")
        item_id = data["id"]
        if item_id in catalog:
            abort(400, "Item with this ID already exists")
        catalog[item_id] = {
            "name": data["name"],
            "price": data["price"],
            "weight": data["weight"]
        }
        return jsonify({"message": "Item added successfully", "item": catalog[item_id]}), 201


# Ендпоінт для роботи з конкретним товаром
@app.route('/items/<int:item_id>', methods=['GET', 'PUT', 'DELETE'])
@auth.login_required
def item(item_id):
    if item_id not in catalog:
        abort(404, "Item not found")

    if request.method == 'GET':
        return jsonify(catalog[item_id])

    elif request.method == 'PUT':
        data = request.get_json()
        if not data or not any(k in data for k in ("name", "price", "weight")):
            abort(400, "Invalid data format")
        catalog[item_id].update(data)
        return jsonify({"message": "Item updated successfully", "item": catalog[item_id]})

    elif request.method == 'DELETE':
        deleted_item = catalog.pop(item_id)
        return jsonify({"message": "Item deleted successfully", "item": deleted_item})


# Запуск сервера
if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8000)
