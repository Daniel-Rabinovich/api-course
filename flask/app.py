import mysql.connector, random, string, redis
from flask import Flask, request, render_template, redirect
from datetime import datetime

app = Flask(__name__)

r = redis.Redis(host="127.0.0.1",port=6379)
r.flushdb()

def add_categories_to_cache():
    # connect to db
    mydb = get_connection()
    mycursor = mydb.cursor()
    data = dict()
    
    mycursor.execute("SELECT * FROM categories")
    myresult = mycursor.fetchall()
    for x in myresult: 
        # populate cahce with categories
        r.rpush("categories",x[0])
        r.hset(f"category:{int(x[0])}","id",x[0])
        r.hset(f"category:{int(x[0])}","name",x[1])
        data[x[0]] = x[1]

    mydb.close()
    return data

def add_places_to_cache():
    # connect to db
    mydb = get_connection()
    mycursor = mydb.cursor()
    data = dict()
    
    mycursor.execute("SELECT * FROM places")
    myresult = mycursor.fetchall()
    for x in myresult: 
        # populate cahce with places
        r.rpush("places",x[0])
        r.hset(f"place:{x[0]}","id",x[0])
        r.hset(f"place:{x[0]}","name",x[1])
        data[x[0]] = x[1]
        
    mydb.close()
    return data

def add_posts_to_cache():
    # connect to db
    mydb = get_connection()
    mycursor = mydb.cursor()
    data = dict()
    last_id = 0
    mycursor.execute("SELECT * FROM posts ORDER BY date DESC LIMIT 10")
    myresult = mycursor.fetchall()
    for x in myresult:
        last_id = x[0]
        post_data = {
            "id": x[0]
            ,"title": x[1]
            ,"place": x[2]
            ,"category": x[3]
            ,"text": x[4]
            ,"date": str(x[5])
            ,"price": x[6]
            ,"contact": x[7]
            ,"link": x[8]
        }
        r.rpush("posts",x[0])
        r.hmset(f"post:{x[0]}",post_data)
        data[int(x[0])] = post_data
    mydb.close()
    
    r.set("last_id",last_id)
    return data

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

    #
    # "datas" will be sent to rendering engine
    #
    
    data = {
        "categories": {}
        ,"places": {}
        ,"posts": {}
    }
    
    #
    # Handle categories
    # pull from db to cache if cache empty 
    #
    if r.llen("categories") == 0:
        data["categories"] = add_categories_to_cache()
    else:   
        for category_id in r.lrange("categories",0,-1):       
            c_id = int(category_id)
            data["categories"][c_id] = r.hget(f"category:{c_id}","name").decode('utf-8')
    
    #   
    # Handle places  
    # pull from db to cache if cache empty 
    #  
    if r.llen("places") == 0:
        data["places"] = add_places_to_cache()
    else: 
        for place_id in r.lrange("places",0,-1): 
            p_id = int(place_id)
            data["places"][p_id] = r.hget(f"place:{p_id}","name").decode('utf-8')
    
    #
    # Handle posts
    # pull from db to cache if cache empty 
    #
    
    # GET parameters
    search_place = request.args.get('place', '')
    search_category = request.args.get('category', '')
    search_free = request.args.get('free', '')
    
    # check cache has posts
    if r.llen("posts") == 0:
        data["posts"] = add_posts_to_cache()
    else:
        r.ltrim("posts",0,10)
        for post_id in r.lrange("posts",0,9): 
            post_id = int(post_id)
            post_data = r.hmget(f"post:{post_id}",
                ("id","title","place","category","text","date","price","contact","link"))
            data["posts"][post_id] = dict()
            data["posts"][post_id]["id"] = int(post_data[0])
            data["posts"][post_id]["title"] = post_data[1].decode('utf-8')
            data["posts"][post_id]["place"] = int(post_data[2])
            data["posts"][post_id]["category"] = int(post_data[3])
            data["posts"][post_id]["text"] = post_data[4].decode('utf-8')
            data["posts"][post_id]["date"] = post_data[5].decode('utf-8')
            data["posts"][post_id]["price"] = int(post_data[6])
            data["posts"][post_id]["contact"] = post_data[7].decode('utf-8')
            data["posts"][post_id]["link"] = post_data[8].decode('utf-8')
                  
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

         #
        # Handle categories
        # pull from db to cache if cache empty 
        #
        if r.llen("categories") == 0:
            data["categories"] = add_categories_to_cache()
        else:   
            for category_id in r.lrange("categories",0,-1):       
                c_id = int(category_id)
                data["categories"][c_id] = r.hget(f"category:{c_id}","name").decode('utf-8')
        
        #   
        # Handle places  
        # pull from db to cache if cache empty 
        #  
        if r.llen("places") == 0:
            data["places"] = add_places_to_cache()
        else: 
            for place_id in r.lrange("places",0,-1): 
                p_id = int(place_id)
                data["places"][p_id] = r.hget(f"place:{p_id}","name").decode('utf-8')
       
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
            
            # add to cache
            r.incr("last_post")
            post_id = int(r.get("last_post"))
            r.lpush("posts", post_id)
            r.hmset(f"post:{post_id}",{
                "id":post_id
                ,"title": title
                ,"place": place
                ,"category": category
                ,"text": description
                ,"contact": contact
                ,"date": date
                ,"price": price
                ,"link": link           
            })
            
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
