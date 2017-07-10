import urllib3
import json
import argparse
import re
import datetime
import configparser

# For real purpose I would handle this adding certificate verification
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def read_configuration(config_file):
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(config_file)
    return config


def prepare_passenger(passenger):
    passenger_dict = {}
    for option in passenger.options('Passenger'):
        passenger_dict.update({option: passenger.get('Passenger', option)})
    return passenger_dict


class Parser:
    def __init__(self):
        self.parser = argparse.ArgumentParser("Flight options")

    def argument_parser(self):
        self.parser.add_argument("--date", action="store", required=True)
        self.parser.add_argument("--from", action="store", required=True)
        self.parser.add_argument("--to", action="store", required=True)
        flight_direction = self.parser.add_mutually_exclusive_group()
        flight_direction.add_argument("--one-way", action="store_true", default=True)
        flight_direction.add_argument("--return", action="store", default=False, type=int)
        sorting = self.parser.add_mutually_exclusive_group()
        sorting.add_argument("--cheapest", action="store_true", default=True)
        sorting.add_argument("--shortest", action="store_true")
        args = self.parser.parse_args()
        values = vars(args)
        return values


class Validator:
    def __init__(self, values, config):
        self.values = values
        self.config = config

    def validate_date(self):
        date = str(self.values['date'])
        date_pattern = re.compile("^[0-9]{4}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])$")
        if date_pattern.match(date) is None:
            return False
        else:
            return True

    def is_date_in_future(self):
        today = datetime.datetime.now()
        today = str(today.strftime("%Y-%m-%d"))
        if today <= self.values['date']:
            splited_date = self.values["date"].split("-")
            self.values['date'] = splited_date[2] + "/" + splited_date[1] + "/" + splited_date[0]
            return True
        else:
            return False

    def iata_validation(self):
        params = {'api_key': self.config['IATA_validation_api']['api_key'],
                  'code': self.values['from']}
        http = RequestHelper()
        destinations = [self.values['from'], self.values['to']]
        for destination in destinations:
            params = edit_params(destination, params)
            response = http.post_request(self.config['IATA_validation_api']['url'], params)
            airport_data = response['response']
            if not airport_data:
                raise Exception(destination + " is not a valid IATA code")
            else:
                continue


class RequestHelper:
    def __init__(self):
        self.http = urllib3.PoolManager()

    def post_request(self, endpoint_url, params):
        encoded_params = json.dumps(params).encode('utf-8')
        request = self.http.request('POST', endpoint_url, body=encoded_params,
                                    headers={'Content-Type': 'application/json'})
        response = json.loads(request.data.decode('utf-8'))
        return response

    def get_request(self, endpoint_url, params):
        request = self.http.request('GET', endpoint_url, params)
        response = json.loads(request.data.decode('utf-8'))
        return response


def edit_params(new_value, params):
    params['code'] = new_value
    return params


class Flight:
    def __init__(self, values):
        self.values = values

    def make_flight_params(self):
        url_params = {
            'v': 3,
            'flyFrom': self.values['from'],
            'to': self.values['to'],
            'dateFrom': self.values['date'],
            'dateTo': self.values['date'],
            'passengers': 1,
            'adults': 1,
            'asc': 1}
        if self.values['return'] is not False:
            url_params.update({'typeFlight': 'return'})
            url_params.update({'daysInDestinationFrom': self.values['return']})
            url_params.update({'daysInDestinationTo': self.values['return']})
        else:
            url_params.update({'typeFlight': 'oneway'})
        if self.values['shortest'] is True:
            url_params.update({'sort': 'duration'})
        else:
            url_params.update({'sort': 'price'})
        return url_params

    def find_flight(self, url):
        url_params = self.make_flight_params()
        http = RequestHelper()
        response = http.get_request(url, url_params)
        if response["_results"] == 0:
            return False
        else:
            booking_token = response['data'][0]['booking_token']
            return booking_token


class Booking:
    def __init__(self, booking_token):
        self.booking_token = booking_token

    def make_booking(self, endpoint_url, passenger):
        booking_params = {
            "currency": "EUR",
            "booking_token": self.booking_token,
            "passengers": [
                passenger
            ]
        }
        http = RequestHelper()
        response = http.post_request(endpoint_url, booking_params)
        if 'pnr' not in response:
            return "Cannot make booking"
        else:
            return response['pnr']
