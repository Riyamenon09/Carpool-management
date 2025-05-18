from flask import Flask, render_template, request, redirect, url_for, g, flash, session
import sqlite3
import os
from flask_mail import Mail, Message
from email.message import EmailMessage
import smtplib 
import urllib.parse

from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Used for session management

# Function to connect to the SQLite database
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect('carpool.db', timeout=10)  # Set timeout for database connection
        g.db.row_factory = sqlite3.Row  # To access columns by name
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']

        # Hash the password before storing it
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Insert the data into the database
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO users (name, email, phone, password)
            VALUES (?, ?, ?, ?)
        ''', (name, email, phone, hashed_password))
        
        conn.commit()
        flash('Registration successful! You can now log in.')
        return redirect(url_for('signin'))  # Redirect to the sign-in page after successful registration

    return render_template('register.html')  # Render the registration form

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE name = ?", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            session['user_email'] = user['email']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')

    return render_template('signin.html')

@app.route('/vehicles')
def vehicles():
    return render_template('vehicle.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/find_ride')
def find_ride():
    return render_template('find_ride.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return render_template('dashboard.html')  # Render dashboard.html content
    return redirect(url_for('signin'))  # Redirect to sign-in if not authenticated

# Example rides data
# Example rides data with license numbers and without profile pictures
rides_data = [
    {'id': 1, 'driver_name': 'Rajesh Kumar', 'gender': 'Male', 'vehicle': 'Maruti Suzuki Swift', 
     'seats_available': 3, 'source': 'Dollygunj', 'destination': 'School line', 'fare': 20, 
     'rating': 4.8, 'contact_number': '9876543210', 'license_number': 'ABC1234', 'profile_pic': 'P1.png', 'vehicle_pic': 'V1.png','map': 'https://www.google.com/maps/dir/Dollygunj,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/School+line,+Minnie+Bay,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6368116,92.7143437,1706m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x3088943e8bbb551b:0x1015638fe2d50e42!2m2!1d92.7120575!2d11.6357989!1m5!1m1!1s0x308895001979dda5:0xc580de1a85a398c3!2m2!1d92.7268437!2d11.6395596!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 2, 'driver_name': 'Sita Devi', 'gender': 'Female', 'vehicle': 'Hyundai Creta', 
     'seats_available': 2, 'source': 'Dollygunj', 'destination': 'Minnie Bay', 'fare': 15, 
     'rating': 4.5, 'contact_number': '9123456780', 'license_number': 'XYZ5678', 'profile_pic': 'P2.png', 'vehicle_pic': 'V2.png','map':'https://www.google.com/maps/dir/Dollygunj,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands+744103/Minnie+Bay,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6377283,92.7138582,1706m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x3088943e8bbb551b:0x1015638fe2d50e42!2m2!1d92.7120575!2d11.6357989!1m5!1m1!1s0x30889449650875fb:0xe345003f72582ac4!2m2!1d92.7220024!2d11.64139!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 3, 'driver_name': 'Amit Sharma', 'gender': 'Male', 'vehicle': 'Honda City', 
     'seats_available': 4, 'source': 'Garacharma', 'destination': 'Bathubasti', 'fare': 25, 
     'rating': 4.7, 'contact_number': '9876123456', 'license_number': 'JKL9101', 'profile_pic': 'P3.png', 'vehicle_pic': 'V3.png','map':'https://www.google.com/maps/dir/Garacharama,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/Bhathu+Basti,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6154545,92.7010675,3412m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x308894732302e919:0x31a2d6119c7de7b7!2m2!1d92.7058431!2d11.6060191!1m5!1m1!1s0x308894147d04cb01:0x1a75469bd7547eed!2m2!1d92.7108146!2d11.6230219!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 4, 'driver_name': 'Priya Singh', 'gender': 'Female', 'vehicle': 'Toyota Innova', 
     'seats_available': 1, 'source': 'Prem Nagar', 'destination': 'Goalghar', 'fare': 30, 
     'rating': 4.6, 'contact_number': '9988776655', 'license_number': 'MNO2345', 'profile_pic': 'P4.png', 'vehicle_pic': 'V4.png','map':'https://www.google.com/maps/dir/Prem+Mandir,+Vrindavan,+Sri+Kripalu+Maharaj+Ji+Marg,+Raman+Reiti,+Vrindavan,+Rajpur+Khadar,+Uttar+Pradesh/Golghar,+Opp.-Govt.+Girls+High+school,+Ashok+Rajpath+Rd,+Patna,+Bihar+800001/@26.3442921,78.765639,799169m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x39736fb46ad6718b:0x59edc7620411f9f3!2m2!1d77.6720096!2d27.5718524!1m5!1m1!1s0x39ed58504978e8f3:0x18cd15ae7d0e6cd!2m2!1d85.139448!2d25.620337!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 5, 'driver_name': 'Vikram Joshi', 'gender': 'Male', 'vehicle': 'Mahindra Scorpio', 
     'seats_available': 5, 'source': 'Prem Nagar', 'destination': 'Junglighat', 'fare': 40, 
     'rating': 4.9, 'contact_number': '9871234567', 'license_number': 'PQR6789', 'profile_pic': 'P5.png', 'vehicle_pic': 'V5.png','map':'https://www.google.com/maps/dir/Prem+nagar,+JPFG%2B9H5,+Prothrapur,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands+744103/Junglighat,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6411439,92.7094148,6824m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x308895bf1e5864e3:0xb96b35df25682778!2m2!1d92.7264828!2d11.6233774!1m5!1m1!1s0x308895a53cd9c2b3:0xbf8cf981cf27ab62!2m2!1d92.7294624!2d11.6612173!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 6, 'driver_name': 'Nisha Patel', 'gender': 'Female', 'vehicle': 'Tata Nexon', 
     'seats_available': 3, 'source': 'Dollygunj', 'destination': 'School line', 'fare': 35, 
     'rating': 4.4, 'contact_number': '8765432109', 'license_number': 'STU3456', 'profile_pic': 'P6.png', 'vehicle_pic': 'V6.png','map': 'https://www.google.com/maps/dir/Dollygunj,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/School+line,+Minnie+Bay,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6368116,92.7143437,1706m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x3088943e8bbb551b:0x1015638fe2d50e42!2m2!1d92.7120575!2d11.6357989!1m5!1m1!1s0x308895001979dda5:0xc580de1a85a398c3!2m2!1d92.7268437!2d11.6395596!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 7, 'driver_name': 'Anil Verma', 'gender': 'Male', 'vehicle': 'Kia Seltos', 
     'seats_available': 2, 'source': 'Dollygunj', 'destination': 'Minnie Bay', 'fare': 22, 
     'rating': 4.8, 'contact_number': '7654321098', 'license_number': 'VWX1234', 'profile_pic': 'P7.png', 'vehicle_pic': 'V1.png','map':'https://www.google.com/maps/dir/Dollygunj,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands+744103/Minnie+Bay,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6377283,92.7138582,1706m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x3088943e8bbb551b:0x1015638fe2d50e42!2m2!1d92.7120575!2d11.6357989!1m5!1m1!1s0x30889449650875fb:0xe345003f72582ac4!2m2!1d92.7220024!2d11.64139!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 8, 'driver_name': 'Sunita Rani', 'gender': 'Female', 'vehicle': 'Renault Duster', 
     'seats_available': 4, 'source': 'Garacharma', 'destination': 'Bathubasti' , 'fare': 18, 
     'rating': 4.3, 'contact_number': '6543210987', 'license_number': 'YZA5678', 'profile_pic': 'P2.png', 'vehicle_pic': 'V2.png','map':'https://www.google.com/maps/dir/Garacharama,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/Bhathu+Basti,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6154545,92.7010675,3412m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x308894732302e919:0x31a2d6119c7de7b7!2m2!1d92.7058431!2d11.6060191!1m5!1m1!1s0x308894147d04cb01:0x1a75469bd7547eed!2m2!1d92.7108146!2d11.6230219!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 9, 'driver_name': 'Ravi Choudhury', 'gender': 'Male', 'vehicle': 'Skoda Octavia', 
     'seats_available': 1, 'source': 'Prem Nagar', 'destination': 'Goalghar', 'fare': 28, 
     'rating': 4.5, 'contact_number': '5432109876', 'license_number': 'BCD9101', 'profile_pic': 'P1.png', 'vehicle_pic': 'V3.png','map':'https://www.google.com/maps/dir/Prem+Mandir,+Vrindavan,+Sri+Kripalu+Maharaj+Ji+Marg,+Raman+Reiti,+Vrindavan,+Rajpur+Khadar,+Uttar+Pradesh/Golghar,+Opp.-Govt.+Girls+High+school,+Ashok+Rajpath+Rd,+Patna,+Bihar+800001/@26.3442921,78.765639,799169m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x39736fb46ad6718b:0x59edc7620411f9f3!2m2!1d77.6720096!2d27.5718524!1m5!1m1!1s0x39ed58504978e8f3:0x18cd15ae7d0e6cd!2m2!1d85.139448!2d25.620337!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 10, 'driver_name': 'Meera Sharma', 'gender': 'Female', 'vehicle': 'Ford EcoSport', 
     'seats_available': 3, 'source': 'Prem Nagar', 'destination': 'Junglighat', 'fare': 32, 
     'rating': 4.6, 'contact_number': '4321098765', 'license_number': 'EFG2345', 'profile_pic': 'P4.png', 'vehicle_pic': 'V4.png','map':'https://www.google.com/maps/dir/Prem+nagar,+JPFG%2B9H5,+Prothrapur,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands+744103/Junglighat,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6411439,92.7094148,6824m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x308895bf1e5864e3:0xb96b35df25682778!2m2!1d92.7264828!2d11.6233774!1m5!1m1!1s0x308895a53cd9c2b3:0xbf8cf981cf27ab62!2m2!1d92.7294624!2d11.6612173!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 11, 'driver_name': 'Karan Bansal', 'gender': 'Male', 'vehicle': 'Nissan Magnite', 
     'seats_available': 4, 'source': 'Dollygunj', 'destination': 'School line', 'fare': 24, 
     'rating': 4.7, 'contact_number': '3210987654', 'license_number': 'HIJ6789', 'profile_pic': 'P3.png', 'vehicle_pic': 'V5.png','map': 'https://www.google.com/maps/dir/Dollygunj,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/School+line,+Minnie+Bay,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6368116,92.7143437,1706m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x3088943e8bbb551b:0x1015638fe2d50e42!2m2!1d92.7120575!2d11.6357989!1m5!1m1!1s0x308895001979dda5:0xc580de1a85a398c3!2m2!1d92.7268437!2d11.6395596!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 12, 'driver_name': 'Geeta Mehta', 'gender': 'Female', 'vehicle': 'Volkswagen Polo', 
     'seats_available': 5,  'source': 'Dollygunj', 'destination': 'Minnie Bay', 'fare': 38, 
     'rating': 4.4, 'contact_number': '2109876543', 'license_number': 'KLM9101', 'profile_pic': 'P6.png', 'vehicle_pic': 'V6.png','map':'https://www.google.com/maps/dir/Dollygunj,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands+744103/Minnie+Bay,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6377283,92.7138582,1706m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x3088943e8bbb551b:0x1015638fe2d50e42!2m2!1d92.7120575!2d11.6357989!1m5!1m1!1s0x30889449650875fb:0xe345003f72582ac4!2m2!1d92.7220024!2d11.64139!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 13, 'driver_name': 'Suresh Iyer', 'gender': 'Male', 'vehicle': 'Hyundai Verna', 
     'seats_available': 2, 'source': 'Garacharma', 'destination': 'Bathubasti', 'fare': 19, 
     'rating': 4.8, 'contact_number': '1098765432', 'license_number': 'NOP1234', 'profile_pic': 'P7.png', 'vehicle_pic': 'V1.png','map':'https://www.google.com/maps/dir/Garacharama,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/Bhathu+Basti,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6154545,92.7010675,3412m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x308894732302e919:0x31a2d6119c7de7b7!2m2!1d92.7058431!2d11.6060191!1m5!1m1!1s0x308894147d04cb01:0x1a75469bd7547eed!2m2!1d92.7108146!2d11.6230219!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
    
    {'id': 14, 'driver_name': 'Lakshmi Nair', 'gender': 'Female', 'vehicle': 'Maruti Suzuki Baleno', 
     'seats_available': 3, 'source': 'Prem Nagar', 'destination': 'Goalghar', 'fare': 27, 
     'rating': 4.6, 'contact_number': '9876543211', 'license_number': 'QRS5678', 'profile_pic': 'P2.png', 'vehicle_pic': 'V2.png','map':'https://www.google.com/maps/dir/Prem+Mandir,+Vrindavan,+Sri+Kripalu+Maharaj+Ji+Marg,+Raman+Reiti,+Vrindavan,+Rajpur+Khadar,+Uttar+Pradesh/Golghar,+Opp.-Govt.+Girls+High+school,+Ashok+Rajpath+Rd,+Patna,+Bihar+800001/@26.3442921,78.765639,799169m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x39736fb46ad6718b:0x59edc7620411f9f3!2m2!1d77.6720096!2d27.5718524!1m5!1m1!1s0x39ed58504978e8f3:0x18cd15ae7d0e6cd!2m2!1d85.139448!2d25.620337!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 15, 'driver_name': 'Devendra Rao', 'gender': 'Male', 'vehicle': 'Mahindra Thar', 
     'seats_available': 4, 'source': 'Prem Nagar', 'destination': 'Junglighat', 'fare': 36, 
     'rating': 4.9, 'contact_number': '8765432100', 'license_number': 'TUV9101', 'profile_pic': 'P3.png', 'vehicle_pic': 'V3.png','map':'https://www.google.com/maps/dir/Prem+nagar,+JPFG%2B9H5,+Prothrapur,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands+744103/Junglighat,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6411439,92.7094148,6824m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x308895bf1e5864e3:0xb96b35df25682778!2m2!1d92.7264828!2d11.6233774!1m5!1m1!1s0x308895a53cd9c2b3:0xbf8cf981cf27ab62!2m2!1d92.7294624!2d11.6612173!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 16, 'driver_name': 'Aarti Sharma', 'gender': 'Female', 'vehicle': 'Tata Harrier', 
     'seats_available': 1, 'source': 'Dollygunj', 'destination': 'School line', 'fare': 33, 
     'rating': 4.3, 'contact_number': '7654321099', 'license_number': 'WXY1234', 'profile_pic': 'P4.png', 'vehicle_pic': 'V4.png','map': 'https://www.google.com/maps/dir/Dollygunj,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/School+line,+Minnie+Bay,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6368116,92.7143437,1706m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x3088943e8bbb551b:0x1015638fe2d50e42!2m2!1d92.7120575!2d11.6357989!1m5!1m1!1s0x308895001979dda5:0xc580de1a85a398c3!2m2!1d92.7268437!2d11.6395596!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 17, 'driver_name': 'Raj Kumar', 'gender': 'Male', 'vehicle': 'Toyota Fortuner', 
     'seats_available': 2, 'source': 'Dollygunj', 'destination': 'Minnie Bay', 'fare': 26, 
     'rating': 4.7, 'contact_number': '6543210988', 'license_number': 'ZAB5678', 'profile_pic': 'P5.png', 'vehicle_pic': 'V5.png','map':'https://www.google.com/maps/dir/Dollygunj,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands+744103/Minnie+Bay,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6377283,92.7138582,1706m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x3088943e8bbb551b:0x1015638fe2d50e42!2m2!1d92.7120575!2d11.6357989!1m5!1m1!1s0x30889449650875fb:0xe345003f72582ac4!2m2!1d92.7220024!2d11.64139!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 18, 'driver_name': 'Sneha Yadav', 'gender': 'Female', 'vehicle': 'Honda Amaze', 
     'seats_available': 3, 'source': 'Garacharma', 'destination': 'Bathubasti', 'fare': 29, 
     'rating': 4.8, 'contact_number': '5432109877', 'license_number': 'CDE9101', 'profile_pic': 'P6.png', 'vehicle_pic': 'V6.png','map':'https://www.google.com/maps/dir/Garacharama,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/Bhathu+Basti,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6154545,92.7010675,3412m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x308894732302e919:0x31a2d6119c7de7b7!2m2!1d92.7058431!2d11.6060191!1m5!1m1!1s0x308894147d04cb01:0x1a75469bd7547eed!2m2!1d92.7108146!2d11.6230219!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 19, 'driver_name': 'Pankaj Singh', 'gender': 'Male', 'vehicle': 'Nissan Kicks', 
     'seats_available': 4, 'source': 'Prem Nagar', 'destination': 'Goalghar', 'fare': 31, 
     'rating': 4.5, 'contact_number': '4321098766', 'license_number': 'FGH2345', 'profile_pic': 'P7.png', 'vehicle_pic': 'V6.png','map':'https://www.google.com/maps/dir/Prem+Mandir,+Vrindavan,+Sri+Kripalu+Maharaj+Ji+Marg,+Raman+Reiti,+Vrindavan,+Rajpur+Khadar,+Uttar+Pradesh/Golghar,+Opp.-Govt.+Girls+High+school,+Ashok+Rajpath+Rd,+Patna,+Bihar+800001/@26.3442921,78.765639,799169m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x39736fb46ad6718b:0x59edc7620411f9f3!2m2!1d77.6720096!2d27.5718524!1m5!1m1!1s0x39ed58504978e8f3:0x18cd15ae7d0e6cd!2m2!1d85.139448!2d25.620337!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'},
     
    {'id': 20, 'driver_name': 'Rani Mehta', 'gender': 'Female', 'vehicle': 'Maruti Suzuki Ertiga', 
     'seats_available': 5, 'source': 'Prem Nagar', 'destination': 'Junglighat', 'fare': 34, 
     'rating': 4.9, 'contact_number': '3210987655', 'license_number': 'IJK6789', 'profile_pic': 'P2.png', 'vehicle_pic': 'V6.png','map':'https://www.google.com/maps/dir/Prem+nagar,+JPFG%2B9H5,+Prothrapur,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands+744103/Junglighat,+Sri+Vijaya+Puram,+Andaman+and+Nicobar+Islands/@11.6411439,92.7094148,6824m/data=!3m2!1e3!4b1!4m14!4m13!1m5!1m1!1s0x308895bf1e5864e3:0xb96b35df25682778!2m2!1d92.7264828!2d11.6233774!1m5!1m1!1s0x308895a53cd9c2b3:0xbf8cf981cf27ab62!2m2!1d92.7294624!2d11.6612173!3e0!5m1!1e1?entry=ttu&g_ep=EgoyMDI0MTAyOS4wIKXMDSoASAFQAw%3D%3D'}
]

# Function to prepare rides data and handle star ratings
def prepare_rides(rides):
    for ride in rides:
        # Calculate full stars by rounding down the rating
        full_stars = int(ride['rating'])

        # Determine if there's a half star based on the decimal part
        decimal_part = ride['rating'] - full_stars

        # A half star is shown if the decimal is between 0.3 and 0.6
        half_star = 1 if 0.3 <= decimal_part <= 0.6 else 0

        # If decimal part is greater than 0.6, count it as a full star
        if decimal_part > 0.6:
            full_stars += 1
            half_star = 0  # No half star in this case

        # Calculate remaining empty stars
        empty_stars = 5 - full_stars - half_star

        # Attach these calculated values to the ride
        ride['full_stars'] = full_stars
        ride['half_star'] = half_star
        ride['empty_stars'] = empty_stars

    return rides

# Prepare the rides data with the star calculations
rides_data = prepare_rides(rides_data)

@app.route('/search_rides', methods=['POST'])
def search_rides():
    pickup_location = request.form['pickup_location']
    destination_location = request.form['destination_location']
    passengers = request.form['passengers']
    female_drivers = request.form.get('female_drivers')  # Get the checkbox value

    # Filter rides based on the input for source and destination
    available_rides = [
        ride for ride in rides_data
        if ride['source'].lower() == pickup_location.lower() and
           ride['destination'].lower() == destination_location.lower()
    ]

    # Filter by female drivers if the option is selected
    if female_drivers == 'yes':
        available_rides = [ride for ride in available_rides if ride['gender'] == 'Female']

    # If no rides are found, you can flash a message or handle it as you prefer
    if not available_rides:
        flash('No rides available for the specified route.')
    
    return render_template('results.html', rides=available_rides)

@app.route('/payment/<int:ride_id>')
def payment(ride_id):
    # Find the ride based on the ride_id
    ride = next((ride for ride in rides_data if ride['id'] == ride_id), None)
    if ride:
        return render_template('payment.html', ride=ride)  # Pass the ride info to payment.html
    else:
        flash('Ride not found.')
        return redirect(url_for('find_ride'))  # Redirect back to find ride if not found

# @app.route('/book_ride/<int:ride_id>', methods=['GET'])
# def book_ride(ride_id):
#     # Find the ride based on the ride_id
#     ride = next((ride for ride in rides_data if ride['id'] == ride_id), None)
#     if ride:
#         return render_template('book_ride.html', ride=ride)
#     else:
#         flash('Ride not found.')
#         return redirect(url_for('find_ride'))  # Redirect back to find ride if not found
# @app.route('/book_ride/<int:ride_id>', methods=['GET', 'POST'])
# def book_ride(ride_id):
#     if request.method == 'POST':
#         user_id = session.get('user_id')  # Access user ID from the session
#         user_email = session.get('user_email')  # Ensure email is also available
#         ride = next((ride for ride in rides_data if ride['id'] == ride_id), None)

#         if ride:
#             # Here you can add logic to save booking information in your history database
#             # Example: save_booking(user_id, ride)

#             # Send confirmation email
#             msg = Message("Booking Confirmation", sender=app.config['MAIL_USERNAME'], recipients=[user_email])
#             msg.body = f"Dear {session['user_name']},\n\nYour ride has been successfully booked!\n\n" \
#                         f"Driver: {ride['driver_name']}\n" \
#                         f"Vehicle: {ride['vehicle']}\n" \
#                         f"From: {ride['source']}\n" \
#                         f"To: {ride['destination']}\n" \
#                         f"Fare: ${ride['fare']}\n\n" \
#                         f"Thank you for using our service!\n\nBest,\nCarpool Team"
#             # mail.send(msg)

#             flash("Ride booked successfully! A confirmation email has been sent.")
#             return redirect(url_for('dashboard'))
#         else:
#             flash('Ride not found.')
#             return redirect(url_for('find_ride'))

    # Render the booking page if GET request
    # ride = next((ride for ride in rides_data if ride['id'] == ride_id), None)
    # if ride:
    #     return render_template('book_ride.html', ride=ride)
    # else:
    #     flash('Ride not found.')
    #     return redirect(url_for('find_ride'))


@app.route('/book_ride/<int:ride_id>', methods=['GET', 'POST'])
def book_ride(ride_id):
    # If the method is POST, handle the booking logic
    if request.method == 'POST':
        user_id = session.get('user_id')  # Get the user ID from the session
        if not user_id:
            flash('You need to be logged in to book a ride.')
            return redirect(url_for('signin'))  # Redirect to sign-in if not logged in

        # You can also retrieve additional info from the session if needed
        ride = next((ride for ride in rides_data if ride['id'] == ride_id), None)
        
        if ride:
            # Here, you can add code to save the booking to the database
            # e.g., save to a 'bookings' table with ride ID and user ID
            
            flash('Booking confirmed for ride: ' + ride['vehicle'])  # Add a success message
            return redirect(url_for('dashboard'))  # Redirect to dashboard after booking
        else:
            flash('Ride not found.')
            return redirect(url_for('find_ride'))  # Redirect back to find ride if not found

    # If it's a GET request, simply display the booking page
    ride = next((ride for ride in rides_data if ride['id'] == ride_id), None)
    if ride:
        return render_template('book_ride.html', ride=ride)
    else:
        flash('Ride not found.')
        return redirect(url_for('find_ride'))  # Redirect back if the ride isn't found


# Function to execute database operations
@app.route('/driver')
def driver():
    return render_template('driver.html')
# Function to insert data into the SQLite database
def insert_driver_data(driver_data):
    connection = sqlite3.connect('drivers.db')
    cursor = connection.cursor()

    cursor.execute('''
        INSERT INTO drivers (driver_name, gender, contact_number, address, dob, vehicle_type, license_plate, insurance_number, registration_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', driver_data)

    connection.commit()
    connection.close()

@app.route('/')
def index():
    return render_template('driver.html')  # Ensure `driver.html` is in the templates folder

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve form data
    driver_name = request.form['driver_name']
    gender = request.form['Gender:']
    contact_number = request.form['contact_number']
    address = request.form['address']
    dob = request.form['dob']
    vehicle_type = request.form['vehicle_type']
    license_plate = request.form['license_plate']
    insurance_number = request.form['insurance_number']
    registration_date = request.form['registration_date']

    # Prepare the data as a tuple
    driver_data = (driver_name, gender, contact_number, address, dob, vehicle_type, license_plate, insurance_number, registration_date)

    # Insert the data into the database
    insert_driver_data(driver_data)

    # Redirect or show a success message
    return "Driver and vehicle information submitted successfully!"
@app.route('/safety')
def safety():
    ride_id = request.args.get('ride_id')
    driver_name = request.args.get('ride_drivername')
    return render_template('safety.html', ride_id=ride_id, driver_name=driver_name)
@app.route('/confirm_booking', methods=['POST'])
def confirm_booking():
    # Get details from the request
    ride_id = request.form['ride_id']
    driver_name = request.form['driver_name']
    fare = request.form['fare']
    source = request.form['source']
    destination = request.form['destination']
    
    # Connect to your database
    conn = sqlite3.connect('history.db')  # or your database file
    cursor = conn.cursor()
    
    # Insert booking details into the history table
    cursor.execute('''
        INSERT INTO book (ride_id, driver_name, fare, source, destination)
        VALUES (?, ?, ?, ?, ?)
    ''', (ride_id, driver_name, fare, source, destination))
    
    conn.commit()
    conn.close()
    
    # Redirect to a success page or the safety page
    return redirect(url_for('safety', ride_id=ride_id, driver_name=driver_name))
# Database connection function
def get_db_connection():
    conn = sqlite3.connect('history.db')  # Adjust the path if necessary
    conn.row_factory = sqlite3.Row  # This allows us to access columns by name
    return conn

@app.route('/ridehistory')
def ridehistory():
    conn = get_db_connection()
    books = conn.execute('SELECT * FROM book').fetchall()  # Fetch all records from the book table
    conn.close()
    return render_template('ridehistory.html', books=books)  # Pass the records to the template
# Forget Password Route - renders the forget password page
@app.route('/forget_password', methods=['GET', 'POST'])
def forget_password():
    if request.method == 'POST':
        email = request.form['email']
        new_password = request.form['new_password']

        # Hash the new password
        hashed_new_password = generate_password_hash(new_password, method='pbkdf2:sha256')

        conn = get_db()
        cursor = conn.cursor()
        
        # Update the password in the database for the given email
        cursor.execute('''
            UPDATE users
            SET password = ?
            WHERE email = ?
        ''', (hashed_new_password, email))
        
        conn.commit()
        flash('Password updated successfully! Please log in with your new password.')
        return redirect(url_for('signin'))

    return render_template('forget_password.html')
# # Email configuration
# SMTP_SERVER = ''
# SMTP_PORT = 
# SMTP_USER = os.getenv('SMTP_USER', 'ur mail id')  # Replace with your email
# SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', 'maidid pwd')  # Replace with your app-specific password (2FA)


# # Function to send email
# def send_email_alert(subject, body, recipient):
#     msg = EmailMessage()
#     msg.set_content(body)
#     msg['Subject'] = subject
#     msg['To'] = recipient
#     msg['From'] = SMTP_USER

#     try:
#         with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
#             server.login(SMTP_USER, SMTP_PASSWORD)
#             server.send_message(msg)
#             print("Email sent successfully.")
#     except Exception as e:
#         print(f"Failed to send email: {e}")

# # Route to display the track driver form
# @app.route('/track_driver', methods=['GET'])
# def track_driver_form():
#     return render_template('track_driver.html')

# # Route to handle the form submission
# @app.route('/track_driver', methods=['POST'])
# def track_driver():
#     user_email = request.form['email']
    
#     # Prepare the email content
#     subject = "Your Ride is Booked"
#     body = "Your ride is confirmed! You can now track your driver. Thank you for using our service."
    
#     # Send the email
#     send_email_alert(subject, body, user_email)
    
#     return f"An email has been sent to {user_email} with your driver tracking details."

# Email configuration for Gmail
SMTP_SERVER = ''
SMTP_PORT = ''  #give a port value
SMTP_USER = ''  # Replace with your Gmail
SMTP_PASSWORD = ''  # Replace with your app-specific password

@app.route('/track')
def track():
    if 'user_email' in session:
        user_email = session['user_email']

        # Create the email
        subject = "Your Carpool Ride is Confirmed!"
        body = f"Dear {session['user_name']},\n\nYour ride has been successfully booked! .\n\nThank you for choosing Carpool!...."
        
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = user_email

        try:
            # Send the email
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as smtp:
                smtp.login(SMTP_USER, SMTP_PASSWORD)
                smtp.send_message(msg)
            
            flash('Tracking email sent successfully!', 'success')
        except Exception as e:
            flash(f"Error sending email: {str(e)}", 'danger')

    return redirect(url_for('dashboard'))
if __name__ == '__main__':
    app.run(debug=True)
