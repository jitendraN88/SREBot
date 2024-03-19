from splunklib import client, results
from .graph_creator import create_graph, create_data_URI
from config import DefaultConfig

import os, json

CONFIG = DefaultConfig()
GRAPHADAPTIVECARDIMAGEPATH = "resources/graphnew1.png"

class SplunkOperations():
    def __init__(self):
        self._splunk_host = CONFIG.SPLUNK_HOST
        self._splunk_port = CONFIG.SPLUNK_PORT
        self._splunk_token = CONFIG.SPLUNK_TOKEN

    def get_splunk_service(self):
        service = client.connect(
            host=self._splunk_host,
            port=self._splunk_port,
            splunkToken=self._splunk_token
        )
        return service
    
    def splunk_oneshotaggregatedsearch(self,text):
        timeperiod = text[2].split("time")[1]
        service = self.get_splunk_service()
        # Search query
        trend = text[1]
        search_query = """search index="akamai" sourcetype="akamai" Request_host="www.coachoutlet.com"   NOT("3.18.82.183" OR "107.204.21.178") NOT (Request_path="*sureRoute*" OR Request_path="*akamai%2ftestObject*" OR Request_path="*.js" OR Request_path="*.png" OR Request_path="*.css" OR Request_path="*.jpg" OR Request_path="*.svg" OR Request_path="icons/favicon.ico" OR Request_path="*.json" OR Request_path="*Analytics-Start*" OR Request_path="*on/demandware.static*" OR Request_path=".well-known/assetlinks.json" OR Request_path="images/common/favicon2.ico" OR Request_path= "*/Product-Variation" OR Request_path="sw" OR Client_IP="43.153.65.191" OR Status_code="480" OR Status_code="481" OR User_agent="Screaming%20Frog%20SEO%20Spider*" OR Request_path="*.gif" OR User_agent="axios*" OR Status_code="412")
| stats count AS total, count(eval(like(Status_code, "2%"))) AS success2xx , count(eval(like(Status_code, "3%"))) AS success3xx, count(eval(like(Status_code, "5%"))) AS count_5xx, count(eval(like(Status_code, "4%"))) AS count_4xx 
| eval Stability=(((success2xx+success3xx)/total)*100)
| fields Stability
"""
        kwargs_oneshot = {
            "earliest_time": timeperiod,
            "latest_time": "now",
            "output_mode": 'json'
        }
        oneshotsearch_results = service.jobs.oneshot(search_query, **kwargs_oneshot)
        result = results.JSONResultsReader(oneshotsearch_results)
        return result

    def splunk_oneshotsearch(self,text):
        timeperiod = text[2].split("time")[1]
        service = self.get_splunk_service()
        # Search query
        trend = text[1]
        print("text data is ---------"+trend)
        search_query = """search index="akamai" sourcetype="akamai" Status_code=* Client_IP=* NOT (Request_path="*sureRoute*" OR Request_path="*akamai%2ftestObject*" OR Request_path="*.js" OR Request_path="*.png" OR Request_path="*.css" OR Request_path="*.jpg" OR Request_path="*.svg" OR Request_path="icons/favicon.ico" OR Request_path="*.json" OR Request_path="*Analytics-Start*" OR Request_path="*on/demandware.static*" OR Request_path=".well-known/assetlinks.json") Request_path="*" NOT (Request_path="*.gif") Status_code!="412" Request_host IN ("www.coachoutlet.com") 
| stats count as TotalCount,count(eval(Status_code>199 AND Status_code<400)) as Success_Count,count(eval(Status_code>399)) as Failure_Count, count(eval(Status_code>399 AND Status_code < 500 )) as Count_4XX, count(eval(Status_code >= 500 )) as Count_5XX by Request_path 
| table Request_path, TotalCount,Success_Count,Failure_Count, Count_4XX, Count_5XX 
| sort -TotalCount 
| eval Failure_Ratio(%)=round((Failure_Count/(Failure_Count+Success_Count))*100,2) 
| eval Failure_Ratio_4XX(%)=round((Count_4XX/(Failure_Count+Success_Count))*100,2) 
| eval Failure_Ratio_5XX(%)=round((Count_5XX/(Failure_Count+Success_Count))*100,2) 
| where Count_5XX>0
| sort -Failure_Ratio(%) , -Failure_Ratio_5XX(%) limit=10
"""
        kwargs_oneshot = {
            "earliest_time": timeperiod,
            "latest_time": "now",
            "output_mode": 'json'
        }
        oneshotsearch_results = service.jobs.oneshot(search_query, **kwargs_oneshot)
        result = results.JSONResultsReader(oneshotsearch_results)
        return result

    def splunk_oneshotsearch_path_graph(self,text):
       
        path_uri, timeperiod = str(text).split('|time')
        service = self.get_splunk_service()
        
        trend = path_uri.split("|")
        ch = "stability"
        y_axis = "5xx Count"
        
        if(ch in trend[1]):
            print("graph text is=1=",path_uri)
            y_axis = "Stability"
            search_query = """search index="akamai" sourcetype="akamai" Request_host IN ("www.coachoutlet.com" ) Status_code!="412" ,
| bin span=5m _time | stats count AS total, count(eval(like(Status_code, "2%"))) AS success2xx , count(eval(like(Status_code, "3%"))) AS success3xx by _time
| eval Stability=round(((success2xx+success3xx)/total)*100,3) 
| timechart span=5m avg(Stability) as stability"""
        else:
            print("graph text is=2=",path_uri)
            search_query = """search index="akamai" sourcetype="akamai" Request_host IN ("*") Status_code>499 NOT (Request_path="*.gif") NOT (Request_path="*sureRoute*" OR Request_path="*akamai%2ftestObject*" OR Request_path="*.js" OR Request_path="*.png" OR Request_path="*.css" OR Request_path="*.jpg" OR Request_path="*.svg" OR Request_path="icons/favicon.ico" OR Request_path="*.json" OR Request_path="*Analytics-Start*" OR Request_path="*on/demandware.static*" OR Request_path=".well-known/assetlinks.json")
| timechart span=5m count by Request_path useother=f usenull=f limit=10"""
        
        kwargs_oneshot = {
            "earliest_time": timeperiod,
            "latest_time": "now",
            "output_mode": 'json'
        }
        oneshotsearch_results = service.jobs.oneshot(search_query, **kwargs_oneshot)
        # print("oneshotsearch_results is ----"+oneshotsearch_results)
        result = results.JSONResultsReader(oneshotsearch_results)
        print("result size is",result)
        data = []
        for item in result:
            data.append(item)
        paths = list(data[1].keys())[:-1]
        sdata = {}
        for path in paths:
            sdata.update({path: []})

        for row in data:
            for path in paths:
                if path == "_time":
                    sdata[path].append(str(row[path]).split('T')[1].split('.')[0][:-3])
                else:
                    sdata[path].append(int(float(row[path])))

        timeslots = sdata.pop('_time')
        
        import matplotlib.pylab as plt
        
        for uri in sdata:
            plt.plot(timeslots, sdata[uri], label=uri)
        plt.xlabel("Time")
        plt.ylabel(y_axis)
        plt.legend()
        plt.title(y_axis)
        figure = plt.gcf()
        figure.set_size_inches(10, 8)
        graph_path = os.path.join(os.getcwd(), GRAPHADAPTIVECARDIMAGEPATH)
        os.system("rm -rf {}".format(graph_path))
        plt.savefig(graph_path, dpi=100, bbox_inches='tight')
        del plt
        data_uri = create_data_URI(imagepath=graph_path)
        return data_uri
    
    def desgin_splunk_output_stability(self, timeslot):
        timeslot_new = timeslot.split("|")
        result = self.splunk_oneshotaggregatedsearch(timeslot_new)
        message = []
        for line in result:
            if isinstance(line, dict):
                new_row = {
                    'type': 'TableRow',
                    'cells': [
                        {
                            'type': 'TableCell',
                            'items': [
                                {
                                    'type': 'TextBlock',
                                    'text': line["Stability"],
                                    'wrap': True
                                }
                            ],
                            'style': 'accent'
                        }
                    ]
                }
                message.append(new_row)
        return dict(message=message)

    def desgin_splunk_output(self, timeslot):
        global status, startTime
        timeslot_new = timeslot.split("|")
        print("timeslot is===="+timeslot_new[1])
        result = self.splunk_oneshotsearch(timeslot_new)
        message = []
        data = {}
        for line in result:
            if isinstance(line, dict):
                new_row = {
                    'type': 'TableRow',
                    'cells': [
                       {
                            "type": "TableCell",
                            "items": [{
                                "type": "Container",
                                'wrap': True,
                                "border": True,
                                "items": [{
                                    "type": "ActionSet",
                                    "border": True,
                                    "actions": [{
                                        "type": "Action.Submit",
                                        "title": line["Request_path"],
                                        "data": {
                                            "action": line["Request_path"] + '|path'
                                        }
                                    }]
                                }]
                            }]
                        },
                        {
                            'type': 'TableCell',
                            'items': [
                                {
                                    'type': 'TextBlock',
                                    'text': line["TotalCount"],
                                    'wrap': True
                                }
                            ],
                            'style': 'accent'
                        },
                        {
                            'type': 'TableCell',
                            'items': [
                                {
                                    'type': 'TextBlock',
                                    'text': line["Success_Count"],
                                    'wrap': True
                                }
                            ],
                            'style': 'accent'
                        },
                        {
                            'type': 'TableCell',
                            'items': [
                                {
                                    'type': 'TextBlock',
                                    'text': line["Count_5XX"],
                                    'wrap': True
                                }
                            ],
                            'style': 'accent'
                        },
                        {
                            'type': 'TableCell',
                            'items': [
                                {
                                    'type': 'TextBlock',
                                    'text': line["Failure_Ratio_5XX(%)"],
                                    'wrap': True
                                }
                            ],
                            'style': 'accent'
                        }
                    ]
                }
                message.append(new_row)
        return dict(message=message)

    def get_graph_timewise_stats_for_path(self,path):
        path_uri, timeperiod = str(path).split('|time')
        service = self.get_splunk_service()
        search_query_hour_wise = ""

        kwargs_oneshot = {"earliest_time": timeperiod,
                          "latest_time": "now",
                          "output_mode": 'json'}
        # Run the search query
        oneshotsearch_results = service.jobs.oneshot(search_query_hour_wise, **kwargs_oneshot)

        # Get the results and display them using the JSONResultsReader
        reader = results.JSONResultsReader(oneshotsearch_results)
        data = {}
        for item in reader:
            data.update(
                {
                    str(item["_time"]).split('T')[1].split('.')[0][:-3]: int(item[path_uri])
                }
            )
            
        graph_path = os.path.join(os.getcwd(), GRAPHADAPTIVECARDIMAGEPATH)
        data_uri_graph = create_graph(title="{} 5xx Error Stats for {}".format(path_uri,timeperiod), xpoints=list(data.keys()),
                     ypoints=list(data.values()))
        # data_uri = create_data_URI(imagepath=graph_path)

        return data_uri_graph


if __name__ == '__main__':
    splunk = SplunkOperations()
    print(splunk.desgin_splunk_output())
