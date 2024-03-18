import pandas as pd

class Utils():

    def getLabel(self, region_label):
        df_label = pd.read_csv('resources/Hostname_mapping.csv')
        df_label = df_label[(df_label['region_label']==region_label)]
        return df_label['label']
        
    def getRequestPath(self, region_label, label):
        df_path = pd.read_csv('resources/Hostname_mapping.csv')
        df_path = df_path[(df_path['region_label']== region_label) & (df_path['label']== label)]
        return df_path

    # lable = getLable('North America')