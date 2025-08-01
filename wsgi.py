from app import app, start_background_tasks

if __name__ == "__main__":
    start_background_tasks()
    app.run()
