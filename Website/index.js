function callApi() {
    const apiUrl = 'http://127.0.0.1:5000/date';

    // Make a GET request
    fetch(apiUrl)
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function getTrackingData() {
    dates = ["February 5, 2024", "February 29, 2024", "March 7, 2024", "March 14, 2024", "March 21, 2024", "March 28, 2024", "April 04, 2024"]

    allData = {}

    completeCount = 0

    for(let i = 0; i < dates.length;i++) {
        let apiUrl = 'http://127.0.0.1:5000/tracking?date=' + dates[i];

        // Make a GET request
        fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
            throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            allData[dates[i]] = data["data"];

            completeCount++;

            if(completeCount == dates.length)
            {
                createDataTable(dates, allData);
            }
            
        })
        .catch(error => {
            console.error('Error:', error);
        });
    }
}

function getStockOptionData(stock) 
{
    let apiUrl = 'http://127.0.0.1:5000/option_data?symbol=' + stock + '&daysOut=30&strikePercentage=1.05';

    // Make a GET request
    fetch(apiUrl)
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function startOptionData()
{
    let apiUrl = 'http://127.0.0.1:5000/smp500';

    // Make a GET request
    fetch(apiUrl)
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);

        getAllStockOptionData(data["data"]);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function getAllStockOptionData(smp500)
{
    if(smp500.length == 0) return;

    allData = {};
    
    completeCount = 0;

    let parentElement = document.getElementById("data-parent");
    
    for(let i = 0; i < smp500.length;i++) {
        let apiUrl = 'http://127.0.0.1:5000/option_data?symbol=' + smp500[i] + '&daysOut=30&strikePercentage=1.05';

        // Make a GET request
        fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
            throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log(data);
            allData[smp500[i]] = data['data'];
            
            completeCount++;

            parentElement.innerHTML = "<h2>" + completeCount + "/" + smp500.length + "(" + round(completeCount / smp500.length * 100, 2) + "%)</h2>";

            if(completeCount == smp500.length)
            {
                createNewStockTable(smp500, allData);
            }
        })
        .catch(error => {
            console.error('Error:', error);

            completeCount++;

            parentElement.innerHTML = "<h2>" + completeCount + "/" + smp500.length + "(" + round(completeCount / smp500.length * 100, 2) + "%)</h2>";

            if(completeCount == smp500.length)
            {
                createNewStockTable(smp500, allData);
            }
        });
    }
}

currentStockData = {};
smp500Tickers = [];
reverseSort = false;
compareIndex = 0;
volatilityThreshold = .25;

function dataSortByIndex(index)
{
    compareIndex = index;

    if(compareIndex == 7) reverseSort = true;
    else reverseSort = false;

    for(let i = smp500Tickers.length - 1; i >= 0;i --)
    {
        if(currentStockData[smp500Tickers[i]] == undefined) smp500Tickers.splice(i, 1);
    }

    smp500Tickers.sort(compareFunction);

    createNewStockTable(smp500Tickers, currentStockData);
}

function compareFunction(a, b)
{
    if(currentStockData[a] == undefined) return 1;
    if(currentStockData[b] == undefined) return 1;

    if(currentStockData[a][compareIndex] == currentStockData[b][compareIndex]) return 0;

    let val = 1;

    if(currentStockData[a][compareIndex] < currentStockData[b][compareIndex]) val = -1;
    else val = 1;

    if(reverseSort) val *= -1;

    return val;
}

function createNewStockTable(smp500, data)
{
    currentStockData = data;
    smp500Tickers = smp500;

    let parentElement = document.getElementById("data-parent");
    parentElement.innerHTML = "<h2>Stock Option Data</h2>";

    let table = "<table class=\"data-table\">";

    table += "<tr>";
    table += "<th class=\"data-box\">Stock</th>";
    table += "<th class=\"data-box\">Close Price</th>";
    table += "<th class=\"data-box\">Date</th>";
    table += "<th class=\"data-box\">Strike Price</th>";
    table += "<th class=\"data-box\">Bid</th>";
    table += "<th class=\"data-box\" onclick='dataSortByIndex(7)'>Premium/Cost Ratio</th>";
    table += "<th class=\"data-box\" onclick='dataSortByIndex(5)'>Volatility</th>";
    table += "<th class=\"data-box\">Implied Volatility</th>";
    table += "<th class=\"data-box\">Odds to Excersize</th>";
    table += "</tr>"

    for(let i = 0; i < smp500.length;i++)
    {
        if(data[smp500[i]] !== undefined)
        {
            if(data[smp500[i]][5] < volatilityThreshold) table+="<tr bgcolor='Green'>";
            else table+="<tr>";

            table+="<td class=\"data-box\">" + smp500[i] +"</td>";
            table+="<td class=\"data-box\">$" + round(data[smp500[i]][3], 2) +"</td>";
            table+="<td class=\"data-box\">" + data[smp500[i]][4] +"</td>";
            table+="<td class=\"data-box\">$" + round(data[smp500[i]][1], 2) +"</td>";
            table+="<td class=\"data-box\">$" + data[smp500[i]][2] +"</td>";
            table+="<td class=\"data-box\">" + round(data[smp500[i]][7] * 100, 3) +"%</td>";
            table+="<td class=\"data-box\">" + round(data[smp500[i]][5], 3) +"</td>";
            table+="<td class=\"data-box\">" + data[smp500[i]][6] +"</td>";
            table+="<td class=\"data-box\">" + round(data[smp500[i]][8], 3) +"%</td>";

            table+="</tr>"
        }
    }

    table+= "</table>"

    parentElement.innerHTML += table;
}

function createNewDataSet()
{
    let moneyThreshold = 50000;
    let stocksToExport = [];

    for(let i = 0; i < smp500Tickers.length;i++)
    {
        if(currentStockData[smp500Tickers[i]][5] < volatilityThreshold && currentStockData[smp500Tickers[i]][3] * 100 <= moneyThreshold)
        {
            console.log(smp500Tickers[i] + ": " + currentStockData[smp500Tickers[i]][5] + " " + (currentStockData[smp500Tickers[i]][3] * 100));
            stocksToExport.push(smp500Tickers[i]);
            moneyThreshold = moneyThreshold - (currentStockData[smp500Tickers[i]][3] * 100);
        }
    }

    tickerArg = "";
    strikeArg = "";
    bidArg = "";
    closePriceArg = "";
    dateArg = "";
    volatilityArg = "";
    implied_volatilityArg = "";

    delimiter = ';';

    for(let i = 0;i < stocksToExport.length;i++)
    {
        tickerArg += stocksToExport[i];
        strikeArg += currentStockData[stocksToExport[i]][1];
        bidArg += currentStockData[stocksToExport[i]][2];
        closePriceArg += currentStockData[stocksToExport[i]][3];
        dateArg += currentStockData[stocksToExport[i]][4];
        volatilityArg += currentStockData[stocksToExport[i]][5];
        implied_volatilityArg += currentStockData[stocksToExport[i]][6];
        
        if(i != stocksToExport.length - 1)
        {
            tickerArg += delimiter;
            strikeArg += delimiter;
            bidArg += delimiter;
            closePriceArg += delimiter;
            dateArg += delimiter;
            volatilityArg += delimiter;
            implied_volatilityArg += delimiter;
        }
    }

    let apiUrl = 'http://127.0.0.1:5000/create_new_data_set?tickers=' + tickerArg + '&strikes=' + strikeArg + '&bids=' + bidArg + '&closePrices=' + closePriceArg + '&dates=' + dateArg + '&volatilities=' + volatilityArg + '&implied_volatilities=' + implied_volatilityArg;

    // Make a GET request
    fetch(apiUrl)
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {

    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function createDataTable(dates, data) 
{
    let parentElement = document.getElementById("data-parent");
    parentElement.innerHTML = "";

    let overallProfit = 50000;

    for(let i = 0; i < dates.length;i++)
    {

        let dateTitle = "<h2>" + dates[i] + "</h2>";

        let dataTable = "<table class=\"data-table\" id=\"table-" + i + "\">";

        dataTable += "<tr><th class=\"data-box\">Stock</th><th class=\"data-box\">Current Status</th><th class=\"data-box\">High Status</th><th class=\"data-box\">Expiration Date</th><th class=\"data-box\">Premium</th><th class=\"data-box\">Profit</th><th class=\"data-box\">Target Profit</th><th class=\"data-box\">Is Final</th></tr>";

        // console.log(data);
        for(let x = 0; x < data[dates[i]][0].length;x++)
        {
            let rowString = "<tr>"

            rowString += "<td class=\"data-box\">" + data[dates[i]][0][x][0] + "</td>"
            rowString += "<td class=\"data-box\" bgcolor=\"" + data[dates[i]][0][x][1] + "\">" + data[dates[i]][0][x][1] + "</td>"
            rowString += "<td class=\"data-box\" bgcolor=\"" + data[dates[i]][0][x][2] + "\">" + data[dates[i]][0][x][2] + "</td>"
            rowString += "<td class=\"data-box\">" + data[dates[i]][0][x][6] + "</td>"
            rowString += "<td class=\"data-box\">$" + data[dates[i]][0][x][4] + "</td>"
            rowString += "<td class=\"data-box\">$" + data[dates[i]][0][x][3] + "</td>"
            rowString += "<td class=\"data-box\">$" + data[dates[i]][0][x][5] + "</td>"
            if(data[dates[i]][0][x][7] == true) rowString += "<td class=\"data-box\" bgcolor='Red'>" + data[dates[i]][0][x][7] + "</td>"
            else rowString += "<td class=\"data-box\">" + data[dates[i]][0][x][7] + "</td>"
            rowString += "</tr>";

            dataTable += rowString;
        }

        dataTable += "</table>";

        let startingAmount = 50000;

        let summaryTable = "<table id=\"summary-table-" + i + "\">";
        
        summaryTable += "<tr><th>Total Premium:</th><td>$" + data[dates[i]][1] + " (" + (round(data[dates[i]][1] / startingAmount * 100, 2)) + "%)</td></tr>";
        summaryTable += "<tr><th>Total Profit:</th><td>$" + data[dates[i]][2] + " (" + (round(data[dates[i]][2] / startingAmount * 100, 2)) + "%)</td></tr>";

        overallProfit += data[dates[i]][2] / startingAmount * overallProfit;

        summaryTable += "<tr><th>Optimum Profit:</th><td>$" + data[dates[i]][3] + " (" + (round(data[dates[i]][3] / startingAmount * 100, 2)) + "%)</td></tr>";
        summaryTable += "<tr><th>Total Loss:</th><td>$-" + data[dates[i]][4] + " (-" + (round(data[dates[i]][4] / startingAmount * 100, 2)) + "%)</td></tr>";
        summaryTable += "</table>";

        parentElement.innerHTML += dateTitle + dataTable + summaryTable;
    }

    console.log("Overall Profit: $" + round((overallProfit - 50000), 2) + "(" + round((overallProfit - 50000) / 50000 * 100, 2) + "%)")
}

function round(val, decimalPoints)
{
    return Math.round(val * Math.pow(10, decimalPoints)) / Math.pow(10, decimalPoints);
}