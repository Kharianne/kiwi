import api_calling as ap
import urllib3


config = ap.read_configuration('book_flight.ini')
passenger = ap.read_configuration('passenger.ini')
passenger_dict = ap.prepare_passenger(passenger)
parser = ap.Parser()
values = parser.argument_parser()
validator = ap.Validator(values)

if validator.date_validator() is False:
    print("Invalid date format. Example: YYYY-MM-DD")
    exit(1)

if validator.is_date_in_future() is False:
    print("Date is in the past. Example: YYYY-MM-DD")
    exit(1)

params = {'api_key': config['IATA_validation_api']['api_key'], 'code': values['from']}
try:
    validator.iata_validation(config['IATA_validation_api']['url'], params)
except urllib3.exceptions.MaxRetryError:
    print("Max retries achieved - probably network error.")
    exit(1)
except Exception as e:
    print("Error occurred:", e)
    exit(1)

flight = ap.Flight(values)
url_params = flight.flight_params_builder()

try:
    booking_token = flight.find_flight(url_params, config['Flight_api']['url'])
    if booking_token is False:
        print("No results found!")
        exit(1)
    else:
        try:
            pnr = ap.Booking(booking_token).make_booking(config['Booking_api']['url'], passenger_dict)
            print(pnr)
        except urllib3.exceptions.MaxRetryError:
            print("Max retries achieved - probably network error.")
            exit(1)
except urllib3.exceptions.MaxRetryError:
    print("Max retries achieved - probably network error.")
    exit(1)



