search_query = """search index="{}" sourcetype="akamai" Status_code=* Client_IP=* NOT (Request_path="*sureRoute*" OR Request_path="*akamai%2ftestObject*" OR Request_path="*.js" OR Request_path="*.png" OR Request_path="*.css" OR Request_path="*.jpg" OR Request_path="*.svg" OR Request_path="icons/favicon.ico" OR Request_path="*.json" OR Request_path="*Analytics-Start*" OR Request_path="*on/demandware.static*" OR Request_path=".well-known/assetlinks.json") Request_path="*" NOT (Request_path="*.gif") Status_code!="412" Request_host IN ("www.coachoutlet.com") 
| stats count as TotalCount,count(eval(Status_code>199 AND Status_code<400)) as Success_Count,count(eval(Status_code>399)) as Failure_Count, count(eval(Status_code>399 AND Status_code < 500 )) as Count_4XX, count(eval(Status_code >= 500 )) as Count_5XX by Request_path 
| table Request_path, TotalCount,Success_Count,Failure_Count, Count_4XX, Count_5XX 
| sort -TotalCount 
| eval Failure_Ratio(%)=round((Failure_Count/(Failure_Count+Success_Count))*100,2) 
| eval Failure_Ratio_4XX(%)=round((Count_4XX/(Failure_Count+Success_Count))*100,2) 
| eval Failure_Ratio_5XX(%)=round((Count_5XX/(Failure_Count+Success_Count))*100,2) 
| where Count_5XX>0
| sort -Failure_Ratio(%) , -Failure_Ratio_5XX(%)
""".format("Akamai")
print(search_query)