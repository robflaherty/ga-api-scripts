#
# Finds multi-device users in GA using a custom user ID dimension
#

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from collections import defaultdict

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './credentials/credentials.json'

VIEW_ID = ''

START_DATE = '2020-07-1'
END_DATE   = '2020-07-23'

def initialize_analyticsreporting():
  credentials = ServiceAccountCredentials.from_json_keyfile_name(
    KEY_FILE_LOCATION, SCOPES)

  analytics = build('analyticsreporting', 'v4', credentials=credentials)

  return analytics

# Adjust the query details; comment out segments if not needed
def fetch_data(start_date = START_DATE, end_date = END_DATE):

  return API.reports().batchGet(
    body={
      'reportRequests': [
      {
        'viewId': VIEW_ID,
        'pageSize': 100000,
        'samplingLevel':  'LARGE',
        'dateRanges': [{'startDate': start_date, 'endDate': end_date}],
        'metrics': [{'expression': 'ga:users'}],
        # Set this to the custom dimension used for the user ID
        # If using segments, have to add {'name': 'ga:segment'} to the dimensions
        'dimensions': [{'name': 'ga:dimension4'}, {'name': 'ga:deviceCategory'}],

        # Optional, filter out unwanted user IDs
        # 'dimensionFilterClauses': [
        #   {'filters': [
        #     {
        #       'dimensionName': 'ga:dimension4',
        #       'not': 'true',
        #       'operator': 'EXACT',
        #       'expressions': [ '0' ]
        #     }
        #   ]}
        # ],
        # 'segments':[
        # {
        #   'dynamicSegment':
        #   {
        #     'name': 'Page path filter',
        #     'sessionSegment':
        #     {
        #       'segmentFilters':[
        #       {
        #         'simpleSegment':
        #         {
        #           'orFiltersForSegment':
        #           {
        #             'segmentFilterClauses': [
        #             {
        #               'dimensionFilter':
        #               {
        #                 'dimensionName':'ga:pagePath',
        #                 'operator':'PARTIAL',
        #                 'expressions':['.jsp']
        #               }
        #             }]
        #           }
        #         }
        #       }]
        #     }
        #   }
        # }]
      }]
    }
  ).execute().get('reports')[0].get('data').get('rows')

# Main
def main():
  global API
  API = initialize_analyticsreporting()

  cache = defaultdict(list)
  counts = defaultdict(int)
  percentages = {}

  result = fetch_data()

  # Build dictionary of devices per user id
  for row in result:
    id = row.get('dimensions')[0]
    device = row.get('dimensions')[1]
    cache[id].append(device)

  # Total number of user ids in query
  total_users = len(cache)

  # Get counts of each device combination
  for k,v in cache.items():
    deviceKey = '-'.join(v)
    counts[deviceKey] += 1

  # Display as percentage of users
  for k,v in counts.items():
    percentages[k] = int(round(v / total_users * 100, 0))

  # Print results
  print('Total Users:')
  print(total_users)
  print('\n')
  print('Device Combination Counts:')
  print(dict(counts))
  print('\n')
  print('Device Combination Percentages:')
  print(percentages)


if __name__ == '__main__':
  main()
