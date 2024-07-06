import os
import sqlite3
import streamlit as st
import pandas as pd
from PIL import Image

# データベースファイルの名前
database = 'blog.db'

# データベースファイルが存在しない場合に作成
if not os.path.exists(database):
    conn = sqlite3.connect(database)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        author TEXT NOT NULL,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        date DATE NOT NULL
    )
    ''')
    conn.commit()
    c.close()
    conn.close()

# 新しい投稿を追加する関数を定義します
def add_post(author, title, content, date):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('''
        INSERT INTO posts (author, title, content, date)
        SELECT ?, ?, ?, ?
        WHERE NOT EXISTS (
            SELECT 1 FROM posts WHERE author = ? AND title = ? AND content = ? AND date = ?
        )
        ''', (author, title, content, date, author, title, content, date))
        conn.commit()
        c.close()
        conn.close()
    except sqlite3.Error as e:
        st.write(e)

# すべての投稿を取得する関数を定義します
def get_all_posts():
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('SELECT * FROM posts ORDER BY id DESC')
        data = c.fetchall()
        c.close()
        conn.close()
        return data
    except sqlite3.Error as e:
        st.write(e)
        return []

# 投稿を削除する関数を定義します
def delete_post(post_id):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('DELETE FROM posts WHERE id=?', (post_id,))
        conn.commit()
        c.close()
        conn.close()
    except sqlite3.Error as e:
        st.write(e)

# Define some HTML templates for displaying the posts
title_temp = """
<div style="background-color:#c7c9cf;padding:10px;border-radius:10px;margin:10px;">
<h4 style="color:black;text-align:center;">{}</h4>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;float:left;width: 50px;height: 50px;border-radius: 50%;">
<h6>Author: {}</h6>
<br/>
<br/>
<p style="text-align:justify"> {}</p>
</div>
"""

post_temp = """
<div style="background-color:#c7c9cf;padding:10px;border-radius:5px;margin:10px;">
<h4 style="color:black;text-align:center;">{}</h4>
<h6>Author: {}</h6>
<h6>Date: {}</h6>
<img src="https://www.w3schools.com/howto/img_avatar.png" alt="Avatar" style="vertical-align: middle;width: 50px;height: 50px;border-radius: 50%;">
<br/>
<br/>
<p style="text-align:justify"> {}</p>
</div>
"""

# Predefined password for deletion and creation
delete_password = "shuta0105"
create_password = "shuta0105"

# Create a sidebar menu with different options
menu = ["Home", "View Posts", "Add Post", "Manage"]
choice = st.sidebar.selectbox("Menu", menu)

# Display the selected option
if choice == "Home":
    st.title("Welcome to my blog")
    st.write("This is a simple blog app built with streamlit and python.")
    st.write("You can view, add, and manage posts using the sidebar menu.")
    image = Image.open('Image/図2.png')
    st.image(image)

elif choice == "View Posts":
    st.title("View Posts")
    st.write("Here you can see all the posts in the blog.")
    # Get all the posts from the database
    posts = get_all_posts()
    # Display each post as a card
    for post in posts:
        st.markdown(title_temp.format(post[2], post[1], post[3][:10] + "..."), unsafe_allow_html=True)
        # Add a button to view the full post
        button_key = f"read_more_{post[0]}"  # Generate a unique key here
        if st.button("Read More", key=button_key):
            st.markdown(post_temp.format(post[2], post[1], post[4], post[3]), unsafe_allow_html=True)
elif choice == "Add Post":
    st.title("Add Post")
    st.write("Here you can add a new post to the blog.")
    # Create a form to get the post details
    with st.form(key="add_form"):
        author = st.text_input("Author")
        title = st.text_input("Title")
        content = st.text_area("Content")
        date = st.date_input("Date")
        password = st.text_input("Enter password", type="password")
        submit = st.form_submit_button("Submit")
    # If the form is submitted, add the post to the database
    if submit:
        if password == create_password:
            add_post(author, title, content, date)
            st.success("Post added successfully")
        else:
            st.error("Invalid password")
elif choice == "Manage":
    st.title("Manage")
    st.write("Here you can delete posts or view some statistics.")
    # Create a selectbox to choose a post to delete
    posts = get_all_posts()
    titles = [f"{post[0]}: {post[2]}" for post in posts]  # Display post ID and title
    selected = st.selectbox("Select a post to delete", titles)
    post_id = int(selected.split(":")[0])  # Extract post ID
    # Add a password input
    password = st.text_input("Enter password", type="password")
    # Add a button to confirm the deletion
    if st.button("Delete"):
        if password == delete_password:
            delete_post(post_id)
            st.success("Post deleted successfully")
        else:
            st.error("Invalid password")
    # Create a checkbox to show some statistics
    if st.checkbox("Show statistics"):
        # Get all the posts from the database
        posts = get_all_posts()
        # Convert the posts to a dataframe
        df = pd.DataFrame(posts, columns=["id", "author", "title", "content", "date"])
        # Display some basic statistics
        st.write("Number of posts:", len(posts))
        st.write("Number of authors:", len(df["author"].unique()))
        st.write("Most recent post:", df["date"].max())
        st.write("Oldest post:", df["date"].min())
        # Display a bar chart of posts by author
        st.write("Posts by author:")
        author_count = df["author"].value_counts()
        st.bar_chart(author_count)
