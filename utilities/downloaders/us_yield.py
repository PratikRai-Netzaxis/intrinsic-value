from datapackage import Package
from decimal import *


def get_10y_us_bond_yield():
    try:
        package = Package(
            'https://datahub.io/core/bond-yields-us-10y/datapackage.json')

        for resource in package.resources:
            if resource.descriptor['datahub']['type'] == 'derived/csv':
                all_data = resource.read()

                # Get latest 10 year yield and convert to float
                latest_data = all_data[len(all_data) - 1][1] * 1
                return float(latest_data)

    except Exception as e:
        print(e)
