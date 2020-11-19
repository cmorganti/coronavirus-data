import pandas as pd
import datetime

TOTAL_CASES_FILE = "totals/data-by-modzcta.csv"

TOTAL_ZIP_COL = "MODIFIED_ZCTA"
TOTAL_PARAMS_DICT = {'zip_code': "MODIFIED_ZCTA",'neighborhood_name': "NEIGHBORHOOD_NAME", 
                          'borough': "BOROUGH_GROUP", "total_case_count": "COVID_CASE_COUNT", 'total_case_rate':
                          "COVID_CASE_RATE", "population": "POP_DENOMINATOR", "total_deaths": "COVID_DEATH_COUNT", 
                          "total_death_rate": "COVID_DEATH_RATE", "pct_pos_total": "PERCENT_POSITIVE", "total_tests":
                          "TOTAL_COVID_TESTS"}
totals_df = pd.read_csv(TOTAL_CASES_FILE)

LATEST_CASES_FILE = "latest/last7days-by-modzcta.csv"
latest_cases_df = pd.read_csv(LATEST_CASES_FILE)

LATEST_ZIP_COL = "modzcta"
LATEST_PARAMS_DICT = {'zip_code': "modzcta", "neighborhood_name": "modzcta_name", "pct_pos_7_days": "percentpositivity_7day",
                      "people_tested_7_days": "people_tested", "people_positive_7_days": "people_positive", 
                      "median_daily_test_rate_7_days": "median_daily_test_rate", "adequately_tested_7_days": "adequately_tested",
                      "daterange_7_days_str": "daterange"}


POSITIVITY_FILE = "latest/pp-by-modzcta.csv"

# NYS "cluster" metric thresholds
AVG_NEW_DAILY_CASES_PER_100K_THRESHOLD = 10

POP_THRESHOLD = 10000
AVG_NEW_DAILY_CASES_THRESHOLD = 5

class ZipCodeInfo():
    
    def parse_date_range(self):
        daterange_list = self.daterange_7_days_str.split("-")
        assert(len(daterange_list) == 2)
        start_date_str, end_date_str = daterange_list
        cur_year = datetime.datetime.now().year
        end_date = pd.to_datetime(", ".join([end_date_str, str(cur_year)]))
        # assume intervals are contiguous, seven days
        if start_date_str.lower().find("dec") != -1 and end_date_str.lower().find("jan") != -1:
            start_date = pd.to_datetime(", ".join([start_date_str, str(cur_year - 1)]))
        else:
            start_date = pd.to_datetime(", ".join([start_date_str, str(cur_year)]))
        return start_date, end_date
         
        
    def parse_df(self, df, params_to_cols):
        for k, v in params_to_cols.items():
            assert(len(list(df[v].values)) == 1)
            setattr(self, k, list(df[v].values)[0])
        
    
    def __init__(self, zip_code):
        self.zip_code = int(zip_code)
        zip_totals = totals_df.loc[totals_df[TOTAL_ZIP_COL] == self.zip_code]
        zip_latest = latest_cases_df.loc[latest_cases_df[LATEST_ZIP_COL] == self.zip_code]
        
        ##### LAST SEVEN DAYS ##### 
        self.parse_df(zip_latest, LATEST_PARAMS_DICT)
        
        # parse date range string
        self.start_date_7_days, self.end_date_7_days = self.parse_date_range()
        
        ##### TOTALS ##### 
        self.parse_df(zip_totals, TOTAL_PARAMS_DICT)
        
    @property
    def case_rate_7_days(self):
        return (self.people_positive_7_days / self.population) * 100000
   
    @property
    def case_rate_7_days_daily_avg(self):
        return self.case_rate_7_days / 7.0
    
    @property
    def avg_case_nums_7_days(self):
        return self.people_positive_7_days / 7.0
    
    def case_rate_over_threshold(self):
        return self.case_rate_7_days_daily_avg > AVG_NEW_DAILY_CASES_PER_100K_THRESHOLD
    
    def case_nums_over_threshold(self):
        if self.population > POP_THRESHOLD:
            return self.avg_case_nums_7_days > AVG_NEW_DAILY_CASES_THRESHOLD
        return False

       
        
        
        
    