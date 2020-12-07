window.addEventListener("DOMContentLoaded", function() {
    //Get all the list buttons
    let searchButtons = document.querySelectorAll(".list-button")

    for (var i = 0; i < searchButtons.length; i++) {
        //For each button attach an event listener
        searchButtons[i].addEventListener("click", function(e) {
            var PID = e.target.id //The product ID associated with the button
            var listingValue = e.target.text //What action take on the button click

            if (listingValue == "List Product") {
                //List the product
                updateListing(PID, 1)
                e.target.text = "Unlist Product"
                e.target.style = "background-color: red"
            } else {
                //Unlist the product
                updateListing(PID, 0)
                e.target.text = "List Product"
                e.target.style = "background-color: green"
            }
            
        })
    }

});

//Fetch the sales data
fetch('/sales_data/')
    .then(function (response) {
    if (response.ok) {
        return response.json();
    } else {
        return Promise.reject(response);
    }})
    .then(function (data) {

        //Get the chart div
        let chartDiv = document.getElementById("chartdiv")

        // Create chart instance
        var chart = am4core.create("chartdiv", am4charts.XYChart);

        //Create the Axis
        var categoryAxis = chart.xAxes.push(new am4charts.DateAxis());
        categoryAxis.dataFields.category = "Date";
        var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
        
        //Create the series
        var series2 = chart.series.push(new am4charts.LineSeries());
        series2.name = "Sales($)";
        series2.stroke = am4core.color("#CDA2AB");
        series2.strokeWidth = 3;

        //Which fields to use
        series2.dataFields.valueY = "Total";
        series2.dataFields.dateX = "Date";
        series2.connect = false;
        series2.tensionX = 0.8;

        //Adds the bullet circle
        series2.bullets.push(new am4charts.CircleBullet());
        
        //Use the json data passed to it
        chart.data = data

        // And, for a good measure, let's add a legend
        chart.legend = new am4charts.Legend();
        
    }).catch(function (err) {
        console.log("Something went wrong!", err);
    }
);


//AJAX call to update the listing
function updateListing(PID, listingValue) {

    const listing = {
        "PID": PID,
        "listingValue": listingValue
    };
    
    fetch("/changelisting/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(listing)
    }).then(function(response) {
        if (response.ok) {
            console.log("Successfully Posted!");
        } else {
            return Promise.reject(response);
        }
    })
}
