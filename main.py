from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import praw, sqlite3, atexit
from prawcore.exceptions import NotFound
from threading import Thread, Timer
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import timedelta

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins="http://localhost:3000/",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Connect to the database
conn = sqlite3.connect('posts.db')
cursor = conn.cursor()

# Create table for posts if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS posts
                (title TEXT, url TEXT, comment_url TEXT, selftext TEXT, subreddit TEXT)''')
conn.commit()

templates = Jinja2Templates(directory="templates")


def update_posts():
    # Connect to the database
    conn = sqlite3.connect('posts.db')
    # Create a cursor object
    cursor = conn.cursor()
    # Delete all records from the database
    cursor.execute("DELETE FROM posts")
    conn.commit()

    # Code for getting top posts and saving to the database goes here
    # ...

#@app.get("/")
#def root():
    #return {"msg": "Ground control to Major Tom 🚀"}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # Connect to the database
    conn = sqlite3.connect('posts.db')
    # Create a cursor object
    cur = conn.cursor()
    # Retrieve all posts from the database
    cur.execute("SELECT * FROM posts")
    posts = cur.fetchall()

    # Close the connection to the database
    conn.close()

    # Render the template with the retrieved posts
    return templates.TemplateResponse("index.html", {"request": request, "posts": posts})


if __name__ == "__main__":
    update_posts()

    # Create a background scheduler to refresh the subreddit information
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=update_posts, trigger="interval", minutes=15)
    scheduler.start()

    # Shut down the scheduler when the application closes
    atexit.register(lambda: scheduler.shutdown())

    uvicorn.run(app, host="0.0.0.0", port=5000)
