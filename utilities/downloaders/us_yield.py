from datapackage import Package
import os
from decimal import *


def save_10y_us_bond_yield():
    try:
        package = Package(
            'https://datahub.io/core/bond-yields-us-10y/datapackage.json')

        file = open("../10y_us_bond_yield.txt", "w")
        for resource in package.resources:
            if resource.descriptor['datahub']['type'] == 'derived/csv':
                all_data = resource.read()

                # Get latest 10 year yield and convert to float
                latest_data = all_data[len(all_data) - 1][1] * 1

                file.write(str(latest_data))
                print(resource.read())

        file.close()

    except Exception as e:
        print(e)


def get_10y_us_bond_yield():
    file_location = '../10y_us_bond_yield.txt'

    if os.path.exists(file_location):
        file = open(file_location, 'r')
        return float(file.read())
