from flask import Flask, render_template, request, redirect, session, flash, url_for
import hashlib
import uuid
import boto3

app = Flask(__name__)
app.secret_key = 'super-secret-key'

# -------- Mock Data --------
# ✅ AWS Configuration (insert this here)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
users_table = dynamodb.Table("MovieMagic_Users")
bookings_table = dynamodb.Table("MovieMagic_Bookings")
sns = boto3.client('sns', region_name='us-east-1')
sns_topic_arn = 'arn:aws:sns:us-east-1:724772095615:MovieMagicNotifications'  # Replace with real ARN


# -------- Helper Functions --------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def send_mock_email(email, booking_info):
    message = (f"Booking confirmed for {booking_info['movie']}\n"
               f"Seat: {booking_info['seat']}, Date: {booking_info['date']}, Time: {booking_info['time']}\n"
               f"Booking ID: {booking_info['id']}")

    print(f"[MOCK EMAIL] Sent to {email}:\n{message}")

    # Send to SNS
    try:
        sns.publish(
            TopicArn=sns_topic_arn,
            Subject="🎟 MovieMagic Booking Confirmation",
            Message=message
        )
    except Exception as e:
        print("SNS error:", e)

# -------- Routes --------
@app.route('/')
def index():
    return render_template('index.html')


# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed = hash_password(password)

        # Check if user exists
        response = users_table.get_item(Key={'email': email})
        if 'Item' in response:
            flash("Account already exists.")
            return redirect(url_for('login'))

        # Save new user
        users_table.put_item(Item={
            'email': email,
            'password': hashed
        })

        flash("Account created! Please login.")
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        hashed = hash_password(password)

        response = users_table.get_item(Key={'email': email})
        user = response.get('Item')

        if user and user['password'] == hashed:
            session['user'] = email
            return redirect(url_for('home'))
        else:
            flash("Invalid email or password.")
            return render_template('login.html')
    return render_template('login.html')
    
@app.route('/home')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))

    now_showing = [
        {"title": "The Grand Premiere", "genre": "Drama", "poster": "posters/movie1.jpeg", "duration": "2h 10m", "rating": "4.5", "synopsis": "A heartfelt journey of dreams and destiny."},
        {"title": "Engaging", "genre": "Drama", "poster": "posters/movie2.jpg", "duration": "1h 45m", "rating": "4.2", "synopsis": "A hilarious ride through everyday chaos."}
    ]
    coming_soon = [
        {"title": "Future Flick", "genre": "Sci-Fi", "poster": "posters/upcoming1.jpg", "duration": "2h 20m", "rating": "N/A", "synopsis": "A mind-bending tale of time and technology."}
    ]
    top_rated = [
        {"title": "Edge of Tomorrow", "genre": "Action", "poster": "posters/movie3.jpeg", "duration": "2h", "rating": "4.8", "synopsis": "A soldier relives the same day in a war against aliens."}
    ]
    return render_template('home.html', now_showing=now_showing, coming_soon=coming_soon, top_rated=top_rated)


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    if 'user' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Temporarily store booking form in session
        session['pending_booking'] = {
            'movie': 'Example Movie',
            'seat': request.form['seat'],
            'date': request.form['date'],
            'time': request.form['time']
        }
        return redirect(url_for('payment'))

    return render_template('booking_form.html', movie='Example Movie')

@app.route('/payment', methods=['GET', 'POST'])
def payment():
    if 'user' not in session or 'pending_booking' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Pretend to process the fake payment
        booking_info = session['pending_booking']
        booking_info['user'] = session['user']
        booking_info['id'] = str(uuid.uuid4())[:8]

        bookings_table.put_item(Item=booking_info)

        session['last_booking'] = booking_info
        send_mock_email(session['user'], booking_info)
        session.pop('pending_booking', None)
        flash("Payment successful. Ticket booked!")

        return redirect(url_for('confirmation'))

    return render_template('payment.html')

@app.route('/confirmation')
def confirmation():
    if 'user' not in session or 'last_booking' not in session:
        return redirect(url_for('login'))

    booking = session['last_booking']
    return render_template('confirmation.html', booking=booking)

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for('index'))


#@app.route('/debug/users')
#def debug_users():
  #  return f"Registered users: {list(mock_users.keys())}"

# 🔍 Debug Route: View all mock bookings
#@app.route('/debug/bookings')
#def debug_bookings():
    #if not mock_bookings:
       # return "No bookings yet."

   # html = "<h2>All Bookings</h2><ul>"
    #for b in mock_bookings:
     #   html += f"<li><b>User:</b> {b['user']}, <b>Movie:</b> {b['movie']}, <b>Seat:</b> {b['seat']}, <b>Date:</b> {b['date']}, <b>Time:</b> {b['time']}, <b>ID:</b> {b['id']}</li>"
    #html += "</ul>"
    #return html

if __name__ == '__main__':
    print("🚀 Mock MovieMagic running at http://127.0.0.1:5000")
    app.run(debug=True)

