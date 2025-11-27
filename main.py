


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import Base, engine, SessionLocal
from models import Message
from schemas import MessageCreate
from config import SMTP_EMAIL, SMTP_PASSWORD, SMTP_SERVER, SMTP_PORT
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import traceback
app = FastAPI()
@app.get("/")
def root():
    return {"message": "Welcome to AdebisiAdebola Portfolio API"}
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def send_email(subject: str, body: str, to_email: str = SMTP_EMAIL):
    msg = MIMEMultipart("alternative")
    msg["From"] = f"AdebisiAdebola Portfolio <{SMTP_EMAIL}>"
    msg["To"] = to_email
    msg["Reply-To"] = SMTP_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    html_body = f"""
    <html>
      <body>
        <h2>{subject}</h2>
        <pre>{body}</pre>
      </body>
    </html>
    """
    msg.attach(MIMEText(html_body, "html"))
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.set_debuglevel(1)
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"Email sent successfully to {to_email}!")
    except smtplib.SMTPAuthenticationError:
        print("SMTP Authentication failed. Check your App Password and email.")
        traceback.print_exc()
    except Exception as e:
        print(f"Error sending email: {e}")
        traceback.print_exc()
@app.post("/contact")
def receive_message(data: MessageCreate, db: Session = Depends(get_db)):
    new_msg = Message(
        name=data.name,
        email=data.email,
        phone=data.phone,
        message=data.message
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    email_body = f"""
New Portfolio Contact Message:
Name: {data.name}
Email: {data.email}
Phone: {data.phone}
Message:
{data.message}
    """
    send_email("New Portfolio Message", email_body, to_email=SMTP_EMAIL)
    return {"success": True, "message": "Message delivered successfully!"}


@app.post("/send-email")
def send_email_endpoint(data: MessageCreate, db: Session = Depends(get_db)):
    """Compatibility endpoint for clients posting to /send-email (port 5000).
    Saves message to DB and sends notification email. Returns JSON success message.
    """
    try:
        new_msg = Message(
            name=data.name,
            email=data.email,
            phone=data.phone,
            message=data.message
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)

        email_body = f"""
New Portfolio Contact Message:
Name: {data.name}
Email: {data.email}
Phone: {data.phone or ''}
Message:
{data.message}
        """

        send_email("New Portfolio Message", email_body, to_email=SMTP_EMAIL)

        return {"success": True, "message": "Message delivered successfully!"}
    except Exception as e:
       
        print(f"Error in /send-email: {e}")
        traceback.print_exc()
        from fastapi import HTTPException
      
        if os.getenv("DEV", "false").lower() in ("1", "true", "yes"):
            raise HTTPException(status_code=500, detail=str(e))
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


projects = [
    {
  "id": 1,
  "title": "my_task",
  "description": "Working with html and css.",
  "tech": ["HTML",  "CSS"],
  "repoLink": "https://github.com/adebolaadebisi/CSS-Ass/tree/master/codebook3",
  "image": "\\Screenshot 2025-09-18 155734.png" 
},

    {
     "id": 3,
  "title": "Assignment",
  "description": "This React app displays three pricing plans with their features, highlighting the Pro plan and letting users choose a plan.",

  "tech": ["React", "Tailwindcss"],
  "repoLink": "https://github.com/adebolaadebisi/react-practices/blob/main/tailwindcss/tailwindday2/exercise4/src/App.jsx",
  "image": "\\Screenshot 2025-11-12 122913.png" 
    },
   
]

@app.get("/projects")
def get_projects():
    return projects


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
