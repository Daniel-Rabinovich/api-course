SET CHARSET UTF8;
DROP DATABASE IF EXISTS site;
CREATE DATABASE site;

use site;

DROP TABLE IF EXISTS places;
CREATE TABLE places(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(50)
);

DROP TABLE IF EXISTS categories;
CREATE TABLE categories(
    id INT AUTO_INCREMENT PRIMARY KEY,
    name varchar(50)
);

DROP TABLE IF EXISTS images;
CREATE TABLE images(
    id INT AUTO_INCREMENT PRIMARY KEY,
    post_id INT
);

DROP TABLE IF EXISTS posts;
CREATE TABLE posts(
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(50),
    place INT,
    category INT,
    text TEXT,
    date DATETIME,
    price INT,
    contact TEXT,
    link TEXT,
    FOREIGN KEY (place) REFERENCES places(id),
    FOREIGN KEY (category) REFERENCES categories(id)
);



INSERT INTO places (name) VALUES ('Tel Aviv');
INSERT INTO places (name) VALUES ('Haifa');
INSERT INTO places (name) VALUES ('Beer Sheva');
INSERT INTO categories (name) VALUES ('Electronics');
INSERT INTO categories (name) VALUES ('Furniture');
INSERT INTO posts (title, place, category, text, date, price, contact, link) VALUES ("Used phone", 2, 2, "This is just a test!", now(), 500, "+972 000000000", "a");
INSERT INTO posts (title, place, category, text, date, price, contact, link) VALUES ("Used Laptop", 3, 2, "This is another test", now(), 999, "+972 000000000", "b");
