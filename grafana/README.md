## Run Grafana for Metrics Visualization

We use OSS version of Grafana.

> **Link:** [localhost:3001](http://localhost:3001)<br>**Default username:** admin<br>**Password:** admin

### Setup the Data Source

1- Enter the **Toggle menu** on the left side of the screen and click on the "**Connections**" button. Then, click on the "**Add new connection**" button.
And then from the **Data Source** dropdown menu, select "**Prometheus**".

2- Add the following configurations for the Prometheus data source:
|Field|Value|
|---|---|
|Name|Prometheus (Or whatever you want)|
|Prometheus Server URL|http://$METRICS_IP:9090 (http://172.22.0.36:9090 in our case)|

3 - Click on the "**Save & Test**" button. If everything is OK, you should see a green message saying "**Data source is working**".


### Create a Dashboard

1- Enter the **Toggle menu** on the left side of the screen and click on the "**Dashboards**" button. Then, click on the "**New Dashboard**" button.

2- Click on the "**Add Visualization**" button and select The **Prometheus data source**.


3- After That you can add your own visualization and query; by clicking on the "**Add Query**" button, and Then click on the "**Select metric**" button to select the metric you want to visualize, and then click on the "**Run queries**" button to see the result.

> **Note:** Save your dashboard by clicking on the "**Save**" button on the top of the screen.