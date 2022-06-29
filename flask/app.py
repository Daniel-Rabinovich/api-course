import mysql.connector, random, string, redis
from flask import Flask, request, render_template, redirect
from datetime import datetime

app = Flask(__name__)

r = redis.Redis(host="127.0.0.1",port=6379)


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        port="3306",
        user="root",
        password="123",
        database="site"
    )

@app.route("/")
def index():

    # get info
    search_place = request.args.get('place', '')
    search_category = request.args.get('category', '')
    search_free = request.args.get('free', '')

    data = {
        "categories": {},
        "places": {},
        "posts": [],
    }

    # connect to db
    mydb = get_connection()
    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM categories")
    myresult = mycursor.fetchall()
    for x in myresult:
        data["categories"][x[0]] = x[1]

    # get places
    mycursor.execute("SELECT * FROM places")
    myresult = mycursor.fetchall()
    for x in myresult:
        data["places"][x[0]] = x[1]

    # get posts
    flag_add = False
    query = f"SELECT * FROM posts"
    if search_category or search_place != "":
        query += f" WHERE"
    if search_category != "":
        query += f" category = {search_category}"
        flag_add = True
    if search_place != "":
        if flag_add == True:
            query += f" AND place = {search_place}"
        else:
            query += f" place = {search_place}"

    if search_free != "":
        if flag_add == True:
            query += f" AND text LIKE '%{search_free}%' or title LIKE '%{search_free}%'"
        else:
            query += f" WHERE text LIKE '%{search_free}%' or title LIKE '%{search_free}%'"

    query += f" ORDER BY date DESC"

    mycursor.execute(query)
    myresult = mycursor.fetchall()
    for x in myresult:
        data["posts"].append(x)

    # close connection and return data
    mydb.close()
    return render_template("index.html", data = data)

@app.route("/create", methods=['POST','GET'])
def create():

    if request.method == "GET":

        data = {
            "categories": {},
            "places": {},
            "link": ''.join(random.choices(string.ascii_uppercase +
                             string.digits, k=30))
        }

        # connect to db
        mydb = get_connection()
        mycursor = mydb.cursor()

        # get categories
        mycursor.execute("SELECT * FROM categories")
        myresult = mycursor.fetchall()
        for x in myresult:
            data["categories"][x[0]] = x[1]

        # get places
        mycursor.execute("SELECT * FROM places")
        myresult = mycursor.fetchall()
        for x in myresult:
            data["places"][x[0]] = x[1]

        # close connection and return data
        mydb.close()

        return render_template("create.html", data = data)

    if request.method == "POST":

        # get time for posts
        now = datetime.now()

        title = request.form["title"]
        place = request.form["places"]
        category = request.form["categories"]
        date = now.strftime('%Y-%m-%d %H:%M:%S')
        description = request.form["desc"]
        price = request.form["price"]
        contact = request.form["contact"]
        link = request.form["link"]

        val = (title , place, category, description, contact, date, price, link)

        mydb = get_connection()
        mycursor = mydb.cursor()
        query ="""
        INSERT INTO posts
        (title, place, category, text, contact, date, price, link)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        try :
            mycursor.execute(query, val)
        except Exception as e:
            print(e)

        # close connection and return data
        mydb.commit()
        mydb.close()

        return redirect("/")


@app.route("/edit/<link>", methods=['POST','GET'])
def edit(link = None):

    if link == None:
        return redirect("/")

    if request.method == "GET":

        data = {
            "categories": {},
            "places": {},
            "post": {}
        }

        # connect to db
        mydb = get_connection()
        mycursor = mydb.cursor()

        # check valid link
        mycursor.execute(f"SELECT * FROM posts WHERE link = '{link}'")
        myresult = mycursor.fetchall()
        if (myresult == None):
            return redirect("/")
        else:
            for x in myresult:
                data["post"] = x

        # get categories
        mycursor.execute("SELECT * FROM categories")
        myresult = mycursor.fetchall()
        for x in myresult:
            data["categories"][x[0]] = x[1]

        # get places
        mycursor.execute("SELECT * FROM places")
        myresult = mycursor.fetchall()
        for x in myresult:
            data["places"][x[0]] = x[1]

        # close connection and return data
        mydb.close()

        return render_template("edit.html", data = data)

    if request.method == "POST":

        # get time for posts
        now = datetime.now()

        title = request.form["title"]
        place = request.form["places"]
        category = request.form["categories"]
        description = request.form["desc"]
        price = request.form["price"]
        contact = request.form["contact"]

        val = (title , place, category, description, contact, price)

        mydb = get_connection()
        mycursor = mydb.cursor()
        query ="""
        UPDATE posts SET
        title = %s, place = %s, category=%s , text=%s, contact=%s, price=%s
        WHERE link = '{}'
        """.format(link)

        try :
            mycursor.execute(query, val)
        except Exception as e:
            print(e)

        # close connection and return data
        mydb.commit()
        mydb.close()

        return redirect("/")



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
