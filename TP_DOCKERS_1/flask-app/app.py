from flask import Flask, render_template
import random

app = Flask(__name__)

# list of cat images
images = [
"https://c.tenor.com/GTcT7HODLRgAAAAM/smiling-cat-creepy-cat.gif",
"https://media0.giphy.com/media/10dU7AN7xsi1I4/giphy.webp?cid=ecf05e47gk63rd81vzlot57qmebr7drtgf6a3khmzvjsdtu7&rid=giphy.webp&ct=g",
"https://media0.giphy.com/media/S6VGjvmFRu5Qk/giphy.webp?cid=ecf05e478yofpawrhffnnvb3sgjkos96vyfo5mtqhds35as6&rid=giphy.webp&ct=g",
"https://media3.giphy.com/media/JIX9t2j0ZTN9S/200w.webp?cid=ecf05e47gk63rd81vzlot57qmebr7drtgf6a3khmzvjsdtu7&rid=200w.webp&ct=g"
    ]

@app.route('/')
def index():
    url = random.choice(images)
    return render_template('index.html', url=url)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
