import pandas as pd

class Utils():

    def getLable(self, region_label):
        df = pd.read_csv('resources/Hostname_mapping.csv')
        df = df[(df['region_label']==region_label)]
        return df
        
    def getRequestPath(self, region_label, lable):
        df = pd.read_csv('resources/Hostname_mapping.csv')
        df = df[(df['region_label']== region_label) & (df['label']== lable)]
        return df

    # lable = getLable('North America')