import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import pandas as pd

POSITIVITY_FILE = "latest/pp-by-modzcta.csv"
LOOKBACK_WINDOW = 20 # days

# COLORS
RED = '#ff8282'
ORANGE = '#ffbc82'
YELLOW = '#fff082'
BG_OPACITY = 0.5
GRID_COLOR = 'LightGrey'
LINE_COLOR = 'blue'

# INFO
X_TITLE = 'Date'
Y_TITLE = 'Positivity rate, seven-day average'
FIG_TITLE_STUB = "COVID-19 test positivity rate, seven-day average, ZIP code: "
MOST_RECENT_LABEL = '(tentative)'

# THRESHOLDS
POS_RED = 4.0
POS_ORANGE = 3.0
POS_YELLOW = 2.5

class PositivityVisualization:
    
    def __init__(self, zip_code):
        self.zip_code = zip_code
        
        pos_rate_by_zip = pd.read_csv(POSITIVITY_FILE)
        df = pos_rate_by_zip[['End date', zip_code]]

        df.loc[:,'end_datetime'] = pd.to_datetime(df['End date'], format='%m/%d/%Y')
        df = df.set_index('end_datetime')

        self.df_10_days = df.sort_index().last('10D')
        self.df_to_graph = df.sort_index().last(str(LOOKBACK_WINDOW) + 'D')

        self.df_tentative = self.df_to_graph.sort_index().last('3D')
        self.df_established = self.df_to_graph.iloc[:-2,:]

    def create_color_zone_background(self):
        self.fig.add_hrect(
            y0=POS_RED, y1="6",
            fillcolor=RED, opacity=BG_OPACITY,
            layer="below", line_width=0,
        )
        self.fig.add_hrect(
            y0=POS_ORANGE, y1=POS_RED,
            fillcolor=ORANGE, opacity=BG_OPACITY,
            layer="below", line_width=0,
        ),
        self.fig.add_hrect(
            y0=POS_YELLOW, y1=POS_ORANGE,
            fillcolor=YELLOW, opacity=BG_OPACITY,
            layer="below", line_width=0,
        )

    def label_graph(self):
        for index, row in self.df_10_days.iterrows():
            self.fig.add_annotation(x=index, y=row[self.zip_code],
                        text=row[self.zip_code],
                        showarrow=False,
                        yshift=15)
        self.fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor=GRID_COLOR, title_text=X_TITLE)
        self.fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=GRID_COLOR, title_text=Y_TITLE)
        self.fig.update_layout(title_text=FIG_TITLE_STUB + self.zip_code)
        self.fig.update_layout(showlegend=False)

    def create_positivity_graph(self):
        self.fig = go.Figure()
        fig = self.fig
        fig.add_trace(go.Scatter(x=self.df_established.index, y=self.df_established[self.zip_code].values,
                                mode="lines+markers+text", line={'color': LINE_COLOR}, name=''))
        fig.add_trace(go.Scatter(x=self.df_tentative.index, y=self.df_tentative[self.zip_code].values,
                                mode="lines+markers+text",line={'dash': 'dash', 'color': LINE_COLOR}, name=MOST_RECENT_LABEL))
        #fig.update_layout(plot_bgcolor='white')
        self.create_color_zone_background()
        self.label_graph()
        fig.show()
        
    # https://www.governor.ny.gov/sites/governor.ny.gov/files/atoms/files/MicroCluster_Metrics_10.21.20_FINAL.pdf?fbclid=IwAR21KmAzZRVT4h6m_NTwUhsPMi7zoXsu2SDoHgruVC8W1mmezUV4Jqz-gd0
    # TODO this doesn't account for places already meeting the criteria of microcluster zones who need to meet more 
    # stringent exit criteria. Only places that haven't yet become zones...
    def get_zone_metrics(self):
        zones = ["YELLOW", "ORANGE", "RED"]
        yellow_days = 0
        orange_days = 0
        red_days = 0
        day_list = []
        for index, row in self.df_10_days.iterrows():
            pos_i = row[self.zip_code]
            if pos_i > POS_RED:
                red_days += 1
                orange_days += 1
                yellow_days += 1
                day_list.append("RED")
            elif pos_i > POS_ORANGE:
                red_days = 0
                orange_days += 1
                yellow_days += 1
                day_list.append("ORANGE")
            elif pos_i > POS_YELLOW:
                red_days = 0
                orange_days = 0
                yellow_days += 1
                day_list.append("YELLOW")
        warning_message = "NOTE: this only takes into account qualification metrics for areas that have not yet been designated by the DOH as microclusters, or those that might qualify for a stricter/more severe designation. It does NOT yet take into account exit metrics for areas *already* designated as microcluster red/orange/yellow zones!\n"
        print(warning_message)
        
        return_msg = "*** ZIP code " + str(self.zip_code) + " currently meets quantitative metrics for zone: "
        day_list_msg = "\nAssuming case numbers are high enough, positivity rates suggest that over the last ten days, ZIP code has met criteria for the following zones: " 
        explanation_msg = "\nIf an area gets ten consecutive days of a more severe color than their current rating (e.g. orange -> red), they will meet the quantitative metrics for the new color."
        if red_days == 10:
            print(return_msg + "RED", day_list_msg + str(day_list), explanation_msg)
        elif orange_days == 10:
            print(return_msg + "ORANGE", day_list_msg + str(day_list), explanation_msg)
        elif yellow_days == 10:
            print(return_msg + "YELLOW",  day_list_msg + str(day_list), explanation_msg)
        else:
            print(return_msg + "NONE", day_list, explanation_msg)