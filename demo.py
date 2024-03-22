# text = """search index={name} sourcetype={age} Request_host="www.coachoutlet.com"   NOT("3.18.82.183" OR "107.204.21.178") NOT (Request_path="*sureRoute*" OR Request_path="*akamai%2ftestObject*" OR Request_path="*.js" OR Request_path="*.png" OR Request_path="*.css" OR Request_path="*.jpg" OR Request_path="*.svg" OR Request_path="icons/favicon.ico" OR Request_path="*.json" OR Request_path="*Analytics-Start*" OR Request_path="*on/demandware.static*" OR Request_path=".well-known/assetlinks.json" OR Request_path="images/common/favicon2.ico" OR Request_path= "*/Product-Variation" OR Request_path="sw" OR Client_IP="43.153.65.191" OR Status_code="480" OR Status_code="481" OR User_agent="Screaming%20Frog%20SEO%20Spider*" OR Request_path="*.gif" OR User_agent="axios*" OR Status_code="412")
# | stats count AS total, count(eval(like(Status_code, "2%"))) AS success2xx , count(eval(like(Status_code, "3%"))) AS success3xx, count(eval(like(Status_code, "5%"))) AS count_5xx, count(eval(like(Status_code, "4%"))) AS count_4xx 
# | eval Stability=(((success2xx+success3xx)/total)*100)
# | fields Stability
# """
# print(text.format(name="akami", age="123"))

import pandas as pd

df_label = pd.read_csv('resources/query_data.csv')
# print(df_label.head)
df_label = df_label[(df_label['trends']=='Stability')]
# df_label = df_label(['trends'=='Stability'])
search = str(df_label['graph_query']).format(request_host='123', time_spa='5m')
print(search)
    
    
    