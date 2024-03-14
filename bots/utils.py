import pandas as pd

class Utils():

    def getLable(self, region_label):
        df_lable = pd.read_csv('resources/Hostname_mapping.csv')
        df_lable = df_lable[(df_lable['region_label']==region_label)]
        return df_lable
        
    def getRequestPath(self, region_label, lable):
        df_path = pd.read_csv('resources/Hostname_mapping.csv')
        df_path = df_path[(df_path['region_label']== region_label) & (df['label']== lable)]
        return df_path

    # lable = getLable('North America')