#
# Uses a custom user ID dimension to caclulate how many days within the date range users visited the site
#

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from datetime import date, timedelta, datetime
from collections import defaultdict, Counter

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
KEY_FILE_LOCATION = './credentials/credentials.json'

VIEW_ID = ''

START_DATE = '2020-03-01'
END_DATE   = '2020-03-31'

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
        'dimensions': [{'name': 'ga:dimension7'}],

        # Optional, filter out unwanted user IDs
        # 'dimensionFilterClauses': [
        #   {'filters': [
        #     {
        #       'dimensionName': 'ga:dimension7',
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

  start_date = datetime.strptime(START_DATE, '%Y-%m-%d').date()
  end_date = datetime.strptime(END_DATE, '%Y-%m-%d').date()

  cache = defaultdict(int)
  counts = []

  # Adjust this to change between daily, weekly, etc
  delta = timedelta(days=1)

  # Make a query for each day and get the users who visited that day
  while start_date <= end_date:
    print (start_date.strftime('%Y-%m-%d'))
    result = fetch_data(start_date.strftime('%Y-%m-%d'), start_date.strftime('%Y-%m-%d'))

    # Add users to the dictionary
    for row in result:
      id = row.get('dimensions')[0]
      cache[id] += 1

    # Increment start date
    start_date += delta

  # Total number of user ids in query
  total_users = len(cache)

  # Make a list of all the counts
  for k, v in cache.items():
    counts.append(v)

  # Calculate the visit counts and sort by key (day)
  counted = sorted(Counter(counts).items())

  # Flatten to a list
  output = [i[1] for i in counted]

  # Display as percentages
  percentages = [int(round(i/total_users * 100, 0)) for i in output]

  # Print results
  print('Total Users:')
  print(total_users)
  print('\n')
  print('Daily Visit Counts:')
  print(output)
  print('\n')
  print('Daily Visit Percentages:')
  print(percentages)


if __name__ == '__main__':
  main()
