from flask import Flask, jsonify, request

app = Flask(__name__)

books = [
    {"id": 1, "title": "1984", "author": "George Orwell", "available": True},
    {"id": 2, "title": "To Kill a Mockingbird", "author": "Harper Lee", "available": False},
    {"id": 3, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "available": True},
]

members = [
    {"id": 1, "name": "Alice Johnson"},
    {"id": 2, "name": "Bob Smith"},
]

@app.route("/books", methods=["GET"])
def get_books():
    return jsonify({"books": books})

@app.route("/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book)

@app.route("/members", methods=["GET"])
def get_members():
    return jsonify({"members": members})

@app.route("/borrow", methods=["POST"])
def borrow_book():
    data = request.get_json(silent=True) or {}
    book_id = data.get("book_id")
    member_id = data.get("member_id")

    book = next((b for b in books if b["id"] == book_id), None)
    member = next((m for m in members if m["id"] == member_id), None)

    if not book:
        return jsonify({"error": "Book not found"}), 404
    if not member:
        return jsonify({"error": "Member not found"}), 404
    if not book["available"]:
        return jsonify({"error": "Book is already borrowed"}), 400

    book["available"] = False
    return jsonify({
        "message": "Book borrowed successfully",
        "book": book,
        "member": member
    })

if __name__ == "__main__":
    app.run(debug=True)