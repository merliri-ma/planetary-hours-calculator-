
document.addEventListener('DOMContentLoaded', function() {
    const resultDiv = document.getElementById('result');

    // Prompt user for time period
    const timePeriod = prompt("Calculate planetary hours for:\n1. Day\n2. Week\n3. Month\n4. Year\nEnter 1, 2, 3, or 4:");

    let requestData = { choice: timePeriod };

    if (timePeriod === "1") {
        // Single Day
        const year = prompt("Enter year (YYYY):");
        const month = prompt("Enter month (1-12):");
        const day = prompt("Enter day (1-31):");
        const sunrise = prompt("Enter sunrise time (HH:MM):");
        const sunset = prompt("Enter sunset time (HH:MM):");

        requestData = {
            choice: timePeriod,
            year: parseInt(year),
            month: parseInt(month),
            day: parseInt(day),
            sunrise: sunrise,
            sunset: sunset
        };
    } else if (timePeriod === "2") {
        // Week
        const year = prompt("Enter year (YYYY):");
        const month = prompt("Enter month (1-12):");
        const day = prompt("Enter day (1-31):");
        let sunrise_sunset_times = [];
        for (let i = 0; i < 7; i++) {
            const current_date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day) + i);
            const sunrise = prompt(`Enter sunrise time for ${current_date.toLocaleDateString()} (HH:MM):`);
            const sunset = prompt(`Enter sunset time for ${current_date.toLocaleDateString()} (HH:MM):`);
            sunrise_sunset_times.push([sunrise, sunset]);
        }
        requestData = {
            choice: timePeriod,
            year: parseInt(year),
            month: parseInt(month),
            day: parseInt(day),
            sunrise_sunset_times: sunrise_sunset_times
        };
    } else if (timePeriod === "3") {
        // Month
        const year = prompt("Enter year (YYYY):");
        const month = prompt("Enter month (1-12):");
        let sunrise_sunset_times = [];
        const daysInMonth = new Date(parseInt(year), parseInt(month), 0).getDate();
        for (let day = 1; day <= daysInMonth; day++) {
            const sunrise = prompt(`Enter sunrise time for ${year}-${month}-${day} (HH:MM):`);
            const sunset = prompt(`Enter sunset time for ${year}-${month}-${day} (HH:MM):`);
            sunrise_sunset_times.push([sunrise, sunset]);
        }
        requestData = {
            choice: timePeriod,
            year: parseInt(year),
            month: parseInt(month),
            sunrise_sunset_times: sunrise_sunset_times
        };
    } else if (timePeriod === "4") {
        // Year
        const year = prompt("Enter year (YYYY):");
        let all_sunrise_sunset_times = {};
        for (let month = 1; month <= 12; month++) {
            let sunrise_sunset_times = [];
            const daysInMonth = new Date(parseInt(year), month, 0).getDate();
            for (let day = 1; day <= daysInMonth; day++) {
                const sunrise = prompt(`Enter sunrise time for ${year}-${month}-${day} (HH:MM):`);
                const sunset = prompt(`Enter sunset time for ${year}-${month}-${day} (HH:MM):`);
                sunrise_sunset_times.push([sunrise, sunset]);
            }
            all_sunrise_sunset_times[`sunrise_sunset_times_${month}`] = sunrise_sunset_times;
        }
        requestData = {
            choice: timePeriod,
            year: parseInt(year),
            ...all_sunrise_sunset_times
        };
    }

    fetch('/api/calculate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
        } else if (timePeriod === "1") {
            let output = "<p>Planetary Hours:</p>";
            data.planetary_hours.forEach(hour => {
                output += `<p>${hour[0]} - ${hour[1]}</p>`;
            });
            resultDiv.innerHTML = output;
        } else if (timePeriod === "2") {
            let output = "";
            data.weekly_hours.forEach(day => {
                output += `<p>Planetary Hours for ${day.date}:</p>`;
                day.planetary_hours.forEach(hour => {
                    output += `<p>${hour[0]} - ${hour[1]}</p>`;
                });
            });
            resultDiv.innerHTML = output;
        } else if (timePeriod === "3") {
            let output = "";
            data.monthly_hours.forEach(day => {
                output += `<p>Planetary Hours for ${day.date}:</p>`;
                day.planetary_hours.forEach(hour => {
                    output += `<p>${hour[0]} - ${hour[1]}</p>`;
                });
            });
            resultDiv.innerHTML = output;
        } else if (timePeriod === "4") {
            let output = "";
            data.yearly_hours.forEach(day => {
                output += `<p>Planetary Hours for ${day.date}:</p>`;
                day.planetary_hours.forEach(hour => {
                    output += `<p>${hour[0]} - ${hour[1]}</p>`;
                });
            });
            resultDiv.innerHTML = output;
        }
    })
    .catch(error => {
        console.error("Error:", error);
        resultDiv.innerHTML = "<p>An error occurred.</p>";
    });
});
