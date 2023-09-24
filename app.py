import sqlite3
from flask import Flask, render_template, request,session
from datetime import date

app = Flask(__name__)
app.config['DATABASE'] = 'Make My Trip(Telaverge)/flight_prices.db'  # Set the database file name



# Create Database
def create_database():
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    sql_query = '''
        CREATE TABLE IF NOT EXISTS flights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_location TEXT NOT NULL,
            start_time TEXT NOT NULL,
            to_location TEXT NOT NULL,
            end_time TEXT NOT NULL,
            current_price REAL NOT NULL,
            airline TEXT NOT NULL
        )
    '''
    # Create a table to store flight information
    cursor.execute(sql_query)
    conn.commit()
    conn.close()

# create_database()

def insert(from_location, start_time, to_location, end_time, price, airline):
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()
    
    # Check if a record with the same from_location, to_location, and airline already exists
    cursor.execute('''
        SELECT id FROM flights
        WHERE from_location = ? AND to_location = ? AND airline = ?
    ''', (from_location, to_location, airline))
    
    existing_record = cursor.fetchone()

    if existing_record:
        # If a record exists, update the price
        cursor.execute('''
            UPDATE flights
            SET current_price = ?
            WHERE id = ?
        ''', (price, existing_record[0]))
        message = "Price updated"
    else:
        # If no matching record exists, insert a new record
        sql_query = '''
            INSERT INTO flights (from_location, start_time, to_location, end_time, current_price, airline)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        cursor.execute(sql_query, (from_location, start_time, to_location, end_time, price, airline))
        message = "Values inserted"

    conn.commit()
    conn.close()

    return message


@app.route('/')
def home():
    current_date = date.today()  # Get the current date
    return render_template('index.html', current_date=current_date)

# Refer to add_price page from home
@app.route('/add_price')
def add_price_home():
    return render_template('add_price.html')

@app.route('/add_price', methods=['POST'])
def add_price():
    from_location = request.form.get('from')
    start_time = request.form.get('start_time')
    to_location = request.form.get('to')
    end_time = request.form.get('end_time')
    price = request.form.get('price')
    airline = request.form.get('airline')

    current_date = date.today()

    if from_location == to_location:
        error_message = "The 'From' and 'To' locations cannot be the same."
        print(error_message)
        return render_template('index.html', error_message=error_message,current_date=current_date)

    


    # Initialize the message as an empty string
    message = ""

    try:
        message = insert(from_location, start_time, to_location, end_time, price, airline)
        # Insert the form data into the database
    except Exception as e:
        # Handle the exception, e.g., log the error
        print(f"Error inserting values: {e}")
        # You can also set a different message if an error occurs
        message = "Error inserting values"

    # Pass the message to the template
    return render_template('add_price.html', message=message)



# WHERE from_location = ? AND to_location = ? AND start_time >= ?
@app.route('/search', methods=['POST'])
def search():
    from_location = request.form.get('from')
    to_location = request.form.get('to')
    num_passengers = int(request.form.get('passengers'))
    departure_date = request.form.get('departure_date')

    current_date = date.today()  # Get the current date

    # Check if "From" and "To" locations are the same
    if from_location == to_location:
        error_message = "The 'From' and 'To' locations cannot be the same."
        print(error_message)
        return render_template('index.html', error_message=error_message,current_date=current_date)

    # Connect to the database
    conn = sqlite3.connect(app.config['DATABASE'])
    cursor = conn.cursor()

    # Query the database to fetch flight data based on user's search criteria
    cursor.execute('''
        SELECT * FROM flights
        WHERE from_location = ? AND to_location = ? 
    ''', (from_location, to_location))

    # Fetch all matching flight records
    flight_data = cursor.fetchall()

    # Close the database connection
    conn.close()

    # Render the "result.html" template and pass the flight data as a variable
    # print(flight_data)
    # print(type(flight_data))
   

    # return render_template('result.html', flight_data=flight_data, num_passengers=num_passengers, departure_date=departure_date)
    return render_template('index.html', flight_data=flight_data, num_passengers=num_passengers, departure_date=departure_date,current_date=current_date)


if __name__ == '__main__':
    create_database()  # Initialize the database when the application starts
    app.run(debug=True)
