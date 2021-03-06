import helper
import urllib3


config = helper.read_configuration('book_flight.ini')
passenger = helper.read_configuration('passenger.ini')
passenger_dict = helper.prepare_passenger(passenger)
parser = helper.Parser()
values = parser.argument_parser()
validator = helper.Validator(values, config)

if validator.validate_date() is False:
    print("Invalid date format. Example: YYYY-MM-DD")
    exit(1)

if validator.is_date_in_future() is False:
    print("Date is in the past. Example: YYYY-MM-DD")
    exit(1)

try:
    validator.iata_validation()
except urllib3.exceptions.MaxRetryError:
    print("Max retries achieved - probably network error.")
    exit(1)
except Exception as e:
    print("Error occurred:", e)
    exit(1)

flight = helper.Flight(values)

try:
    booking_token = flight.find_flight(config['Flight_api']['url'])
    if booking_token is False:
        print("No results found!")
        exit(1)
    else:
        try:
            pnr = helper.Booking(booking_token).make_booking(config['Booking_api']['url'], passenger_dict)
            print(pnr)
        except urllib3.exceptions.MaxRetryError:
            print("Max retries achieved - probably network error.")
            exit(1)
except urllib3.exceptions.MaxRetryError:
    print("Max retries achieved - probably network error.")
    exit(1)
