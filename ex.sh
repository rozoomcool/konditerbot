curl -X 'POST' \
  'http://127.0.0.1:3000/order' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'order_data={"to": "1", "deadline": "2023-12-31T23:59:59", "name": "Order Name", "client": "Client Name", "communication": "Phone", "prepayment": "50%", "delivery": "Courier", "address": "123 Main St", "comment": "This is a comment", "items": [{"name": "Item1", "count": 3, "price": 445.0}, {"name": "Item2", "count": 1, "price": 100.0}]}' \
  -F 'images=@/path/to/image1.jpg' \
  -F 'images=@/path/to/image2.jpg'
