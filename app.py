import os
import sqlite3
import streamlit as st
import pandas as pd
from PIL import Image

# データベースファイルの名前
database = 'blog.db'

# データベースファイルを削除して新しいテーブルを作成するオプション
reset_database = st.sidebar.checkbox("Reset Database")

if reset_database:
    if os.path.exists(database):
        os.remove(database)

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
        date DATE NOT NULL,
        parent_id INTEGER
    )
    ''')
    conn.commit()
    c.close()
    conn.close()

# 新しい投稿を追加する関数を定義します
def add_post(author, title, content, date, parent_id=None):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        c.execute('''
        INSERT INTO posts (author, title, content, date, parent_id)
        VALUES (?, ?, ?, ?, ?)
        ''', (author, title, content, date, parent_id))
        conn.commit()
        c.close()
        conn.close()
    except sqlite3.Error as e:
        st.write(e)

# すべての投稿を取得する関数を定義します
def get_all_posts(parent_id=None):
    try:
        conn = sqlite3.connect(database)
        c = conn.cursor()
        if parent_id is not None:
            c.execute('SELECT * FROM posts WHERE parent_id = ? ORDER BY id DESC', (parent_id,))
        else:
            c.execute('SELECT * FROM posts WHERE parent_id IS NULL ORDER BY id DESC')
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

# Get all the posts to create dynamic menu
posts = get_all_posts()
titles = [post[2] for post in posts]  # Extract titles for the menu

# Create a sidebar menu with different options
st.sidebar.header("Main Menu")
main_menu = ["Home", "Add Post", "Manage"]
main_choice = st.sidebar.selectbox("Main Menu", main_menu, index=0)  # Default to "Home" initially

# Reset post_choice if main_choice changes
if main_choice != "Manage":
    post_choice = "Select a post"
else:
    post_choice = st.sidebar.selectbox("Posts Menu", ["Select a post"] + titles)

# Display the selected option from the main menu
if main_choice == "Home":
    st.title("Welcome to my blog")
    st.write("This is a simple blog app built with streamlit and python.")
    st.write("You can view, add, and manage posts using the sidebar menu.")
    image = Image.open('Image/図2.png')
    st.image(image)

elif main_choice == "Add Post":
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
            st.experimental_rerun()  # Refresh the page to update the menu
        else:
            st.error("Invalid password")

elif main_choice == "Manage":
    st.title("Manage")
    st.write("Here you can delete posts or view some statistics.")
    # Create a selectbox to choose a post to delete
    titles = [f"{post[0]}: {post[2]}" for post in posts]  # Display post ID and title
    selected = st.selectbox("Select a post to delete", titles)
    if selected:
        post_id = int(selected.split(":")[0])  # Extract post ID
        # Add a password input
        password = st.text_input("Enter password", type="password")
        # Add a button to confirm the deletion
        if st.button("Delete"):
            if password == delete_password:
                delete_post(post_id)
                st.success("Post deleted successfully")
                st.experimental_rerun()  # Refresh the page to update the menu
            else:
                st.error("Invalid password")
    # Create a checkbox to show some statistics
    if st.checkbox("Show statistics"):
        # Get all the posts from the database
        posts = get_all_posts()
        # Convert the posts to a dataframe
        df = pd.DataFrame(posts, columns=["id", "author", "title", "content", "date", "parent_id"])
        # Display some basic statistics
        st.write("Number of posts:", len(posts))
        st.write("Number of authors:", len(df["author"].unique()))
        st.write("Most recent post:", df["date"].max())
        st.write("Oldest post:", df["date"].min())
        # Display a bar chart of posts by author
        st.write("Posts by author:")
        author_count = df["author"].value_counts()
        st.bar_chart(author_count)

# Display the selected option from the posts menu
if post_choice != "Select a post":
    st.title(post_choice)
    # Find the post details by title
    for post in posts:
        if post[2] == post_choice:
            # Add form to create a new child post
            st.write("Add a comment")
            with st.form(key=f"add_form_{post[0]}"):
                author = st.text_input("Author", key=f"author_{post[0]}")
                title = st.text_input("Title", key=f"title_{post[0]}")
                content = st.text_area("Content", key=f"content_{post[0]}")
                date = st.date_input("Date", key=f"date_{post[0]}")
                password = st.text_input("Enter password", type="password", key=f"password_{post[0]}")
                submit_comment = st.form_submit_button("Submit")
            if submit_comment:
                if password == create_password:
                    add_post(author, title, content, date, post[0])
                    st.success("Comment added successfully")
                    st.experimental_rerun()  # Refresh the page to update the comments
                else:
                    st.error("Invalid password")
            st.markdown(post_temp.format(post[2], post[1], post[4], post[3]), unsafe_allow_html=True)
            # Display child posts
            child_posts = get_all_posts(post[0])
            for child_post in child_posts:
                st.markdown(post_temp.format(child_post[2], child_post[1], child_post[4], child_post[3]), unsafe_allow_html=True)
            break
