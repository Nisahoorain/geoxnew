type = ['primary', 'info', 'success', 'warning', 'danger'];

demo = {
  initPickColor: function() {
    $('.pick-class-label').click(function() {
      var new_class = $(this).attr('new-class');
      var old_class = $('#display-buttons').attr('data-class');
      var display_div = $('#display-buttons');
      if (display_div.length) {
        var display_buttons = display_div.find('.btn');
        display_buttons.removeClass(old_class);
        display_buttons.addClass(new_class);
        display_div.attr('data-class', new_class);
      }
    });
  },
  initDocChart: function() {
    chartColor = "#FFFFFF";
  },
  initDashboardPageCharts: function() {

//DealChart

function filterDataByDatedeal(dataArray, key) {
  const todaydeal = new Date().toISOString().slice(0, 10);
  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === todaydeal);
}

const reopendealstodayData = filterDataByDatedeal(dataFromServer.reopendeals, 'reopendeals');
console.log(reopendealstodayData)
const contractnotsignedtodayData = filterDataByDatedeal(dataFromServer.contractnotsigned, 'contracontractnotsigned');
console.log(contractnotsignedtodayData)
const contractsignedtodayData = filterDataByDatedeal(dataFromServer.contractsigned, 'contractsigned');
console.log(contractsignedtodayData)

function filterDataByYesterdaydeal(dataArray, key) {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayFormatted = yesterday.toISOString().slice(0, 10);

  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === yesterdayFormatted);
}

const reopendealsyesterdayData = filterDataByYesterdaydeal(dataFromServer.reopendeals, 'reopendeals');
const contractnotsignedyesterdayData = filterDataByYesterdaydeal(dataFromServer.contractnotsigned, 'contractnotsigned');
const contractsignedyesterdayData = filterDataByYesterdaydeal(dataFromServer.contractsigned, 'contractsigned');

function filterDataByLastNDaysdeal(dataArray, key, n) {
  const currentDate = new Date();
  const filteredData = [];

  for (let i = 1; i <= n; i++) {
    const day = new Date(currentDate);
    day.setDate(currentDate.getDate() - i);
    const dayFormatted = day.toISOString().slice(0, 10);
    const dayData = dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === dayFormatted);
    filteredData.push(...dayData);
  }

  return filteredData;
}

const daysToFilterdeal = 3;

const reopendealsLast3DaysData = filterDataByLastNDaysdeal(dataFromServer.reopendeals, 'reopendeals', daysToFilterdeal);
const contractnotsignedLast3DaysData = filterDataByLastNDaysdeal(dataFromServer.contractnotsigned, 'contractnotsigned', daysToFilterdeal);
const contractsignedLast3DaysData = filterDataByLastNDaysdeal(dataFromServer.contractsigned, 'contractsigned', daysToFilterdeal);


const dateFilterdealDropdown = document.getElementById("dateFilterfordeal");
dateFilterdealDropdown.addEventListener("change", handleDateFilterdeal);

const customDateFormfordeal = document.getElementById("customDateFormfordeal");
customDateFormfordeal.addEventListener("submit", handleCustomDateFilterdeal);

const usernameFilterdealDropdown = document.getElementById("selectUsernamefordeal");
usernameFilterdealDropdown.addEventListener("change", handleUsernameFilterdeal);

// Initialize the chart
var dealctx = document.getElementById("DealChart").getContext("2d");
var myChartdeal = new Chart(dealctx, {
  type: 'bar',
  responsive: true,
  legend: {
    display: false
  },
  data: {
    labels: dataFromServer.usernames,
    datasets: [
      {
        label: "contractsignedform",
        backgroundColor: '#4d0202',
        hoverBackgroundColor: '#4d0202',
        borderColor: '#4d0202',
//        data: contractsignedtodayData.map(item => item.count),
         data: dataFromServer.usernames.map(username => {
          var userPlacement = contractsignedtodayData.find(item => item.user_name === username);
          return userPlacement ? userPlacement.count : 0;
        }),
        barPercentage: 0.3,
      },
      {
        label: "contractnotsigned",
        backgroundColor: '#4e8757', // Red color with transparency
        hoverBackgroundColor: '#4e8757',
        borderColor: '#4e8757',
//        data: contractnotsignedtodayData.map(item => item.count),
        data: dataFromServer.usernames.map(username => {
          var userPlacement = contractnotsignedtodayData.find(item => item.user_name === username);
          return userPlacement ? userPlacement.count : 0;
        }),
        barPercentage: 0.3,
      },
      {
        label: "reopendeals",
        backgroundColor: '#9ea60d', // Green color with transparency
        hoverBackgroundColor: '#9ea60d',
        borderColor: '#9ea60d',
//        data: reopendealstodayData.map(item => item.count),
        data: dataFromServer.usernames.map(username => {
          var userPlacement = reopendealstodayData.find(item => item.user_name === username);
          return userPlacement ? userPlacement.count : 0;
        }),
        barPercentage: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    tooltips: {
      enabled: true,
    },
    scales: {

      xAxes: [

        {
        ticks: {
          maxRotation: 90, // Adjust the rotation angle as needed
          minRotation: 10,
        },
        gridLines: {
          display: false, // Remove the grid lines
        },
          barPercentage: 0.7, // Adjust the bar width as needed
        categoryPercentage: 0.6,

        },
      ],
    },
   plugins: {
      labels: false, // Disable rendering labels
    },

  },
});

// Filter data by custom date range
function filterDataByCustomRangedeal(dataArray, startDate, endDate) {
  return dataArray.filter(item => {
    const formattedItemDate = item.date.replace(/[\s,]+/g, '-');
    return formattedItemDate >= startDate && formattedItemDate <= endDate;
  });
}

// Filter data by username
function filterDataByUsernamedeal(dataArray, username) {
  return dataArray.filter(item => item.user_name === username);
}

// Update chart with filtered data
function updateChartdeal(reopendealsData, contractsignedData, contractnotsignedData) {
  myChartdeal.data.datasets[0].data = dataFromServer.usernames.map(username => {
    const userPlacement = contractsignedData.find(item => item.user_name === username);
    return userPlacement ? userPlacement.count : 0;
  });

  myChartdeal.data.datasets[1].data = dataFromServer.usernames.map(username => {
    const userPlacement = contractnotsignedData.find(item => item.user_name === username);
    return userPlacement ? userPlacement.count : 0;
  });

  myChartdeal.data.datasets[2].data = dataFromServer.usernames.map(username => {
    const userPlacement = reopendealsData.find(item => item.user_name === username);
    return userPlacement ? userPlacement.count : 0;
  });

  myChartdeal.update();
}

function handleDateFilterdeal() {
  const selectedValue = dateFilterdealDropdown.value;
    customDateFormfordeal.style.display = 'none';
  if (selectedValue === "all2") {
    updateChartdeal(contractsignedtodayData, contractnotsignedtodayData, reopendealstodayData);
  } else if (selectedValue === "yesterday2") {
    updateChartdeal(contractsignedyesterdayData, contractnotsignedyesterdayData, reopendealsyesterdayData);
  } else if (selectedValue === "last3days2") {
    updateChartdeal(contractsignedLast3DaysData, contractnotsignedLast3DaysData, reopendealsLast3DaysData);
  }else if (selectedValue === "custom2") {
    // Show the customDateFormfordeal form when "Custom" is selected
    customDateFormfordeal.style.display = 'block';
  }
}

function handleCustomDateFilterdeal(event) {
  event.preventDefault();
  const startDate = document.getElementById("startDate2").value;
  const endDate = document.getElementById("endDate2").value;

  const customReopendealsData = filterDataByCustomRangedeal(reopendealstodayData, startDate, endDate);
  const customContractsignedData = filterDataByCustomRangedeal(contractsignedtodayData, startDate, endDate);
  const customContractnotsignedData = filterDataByCustomRangedeal(contractnotsignedtodayData, startDate, endDate);

  updateChartdeal(customReopendealsData, customContractsignedData, customContractnotsignedData);
}

function handleUsernameFilterdeal(event) {
  const selectedUsername = event.target.value;
  const selectedDateFilter = dateFilterdealDropdown.value;

  if (selectedUsername === "No filter") {
    if (selectedDateFilter === "yesterday2") {
      updateChartdeal(contractsignedyesterdayData, contractnotsignedyesterdayData, reopendealsyesterdayData);
    } else if (selectedDateFilter === "last3days2") {
      updateChartdeal(contractsignedLast3DaysData, contractnotsignedLast3DaysData, reopendealsLast3DaysData);
    } else if (selectedDateFilter === "custom2") {
      const startDate = document.getElementById("startDate2").value;
      const endDate = document.getElementById("endDate2").value;

      const customReopendealsData = filterDataByCustomRangedeal(reopendealstodayData, startDate, endDate);
      const customContractsignedData = filterDataByCustomRangedeal(contractsignedtodayData, startDate, endDate);
      const customContractnotsignedData = filterDataByCustomRangedeal(contractnotsignedtodayData, startDate, endDate);

      updateChardeal(customReopendealsData, customContractsignedData, customContractnotsignedData);
    } else {
      updateChartdeal(contractsignedtodayData, contractnotsignedtodayData, reopendealstodayData);
    }
  } else {
    if (selectedDateFilter === "yesterday2") {
          console.log("yesdtrgtdf")

      var userDataYesterday = contractsignedyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataContractnotsignedYesterday = contractnotsignedyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataRReopendealsYesterday = reopendealsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartdeal(userDataRReopendealsYesterday, userDataContractnotsignedYesterday, userDataYesterday);
    } else if (selectedDateFilter === "last3days2") {
      var userDataLast3Days = contractsignedLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataContractnotsignedLast3Days = contractnotsignedLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataRReopendealsLast3Days = reopendealsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartdeal(userDataRReopendealsLast3Days, userDataContractnotsignedLast3Days, userDataLast3Days);
    } else if (selectedDateFilter === "custom2") {
      const startDate = document.getElementById("startDate2").value;
      const endDate = document.getElementById("endDate2").value;

      var customUserData = reopendealstodayData.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      var customUserDataContractnotsigned = contractsignedtodayData.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      var customUserDataReopendeals = contractnotsignedtodayData.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      updateChartdeal(customUserDataReopendeals, customUserDataContractnotsigned, customUserData);
    } else {
      var userData = reopendealstodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataContractnotsigned = contractsignedtodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataReopendeals = contractnotsignedtodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartdeal(userDataReopendeals, userDataContractnotsigned, userData);
    }
  }
}



//candidateChart


function filterDataByDate(dataArray, key) {
  const today = new Date().toISOString().slice(0, 10);
  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === today);
}
const interviewstodayData = filterDataByDate(dataFromServer.interviews, 'interviews');
const resumesentstodayData = filterDataByDate(dataFromServer.resumesents, 'resumesents');
const helpingstodayData = filterDataByDate(dataFromServer.helpings, 'helpings');
function filterDataByYesterday(dataArray, key) {
  const yesterday = new Date();
  yesterday.setDate(yesterday.getDate() - 1);
  const yesterdayFormatted = yesterday.toISOString().slice(0, 10);

  return dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === yesterdayFormatted);
}
const interviewsyesterdayData = filterDataByYesterday(dataFromServer.interviews, 'interviews');
const resumesentsyesterdayData = filterDataByYesterday(dataFromServer.resumesents, 'resumesents');
const helpingsyesterdayData = filterDataByYesterday(dataFromServer.helpings, 'helpings');
function filterDataByLastNDays(dataArray, key, n) {
  const currentDate = new Date();
  const filteredData = [];

  for (let i = 1; i <= n; i++) {
    const day = new Date(currentDate);
    day.setDate(currentDate.getDate() - i);
    const dayFormatted = day.toISOString().slice(0, 10);
    const dayData = dataArray.filter(item => item.date.replace(/[\s,]+/g, '-') === dayFormatted);
    filteredData.push(...dayData);
  }

  return filteredData;
}
const daysToFilter = 3;
const interviewsLast3DaysData = filterDataByLastNDays(dataFromServer.interviews, 'interviews', daysToFilter);
const resumesentsLast3DaysData = filterDataByLastNDays(dataFromServer.resumesents, 'resumesents', daysToFilter);
const helpingsLast3DaysData = filterDataByLastNDays(dataFromServer.helpings, 'helpings', daysToFilter);
const dateFilterDropdown = document.getElementById("dateFilterforcan");
dateFilterDropdown.addEventListener("change", handleDateFilter);
const customDateFormforcan = document.getElementById("customDateFormforcan");
customDateFormforcan.addEventListener("submit", handleCustomDateFilter);
const usernameFilterDropdown = document.getElementById("selectUsernamefor");
usernameFilterDropdown.addEventListener("change", handleUsernameFilter);
// Initialize the chart
var candidatectx = document.getElementById("candidateChart").getContext("2d");
var myChartcandidate = new Chart(candidatectx, {
  type: 'bar',
  responsive: true,
  legend: {
    display: false
  },
  data: {
    labels: dataFromServer.usernames,
    datasets: [
      {
        label: "helpingsform",
        backgroundColor: '#4d0202',
        hoverBackgroundColor: '#4d0202',
        borderColor: '#4d0202',
//        data: helpingstodayData.map(item => item.count),
         data: dataFromServer.usernames.map(username => {
          var userPlacement = helpingstodayData.find(item => item.user_name === username);
          return userPlacement ? userPlacement.count : 0;
        }),
        barPercentage: 0.3,
      },
      {
        label: "resumesents",
        backgroundColor: '#4e8757', // Red color with transparency
        hoverBackgroundColor: '#4e8757',
        borderColor: '#4e8757',
//        data: resumesentstodayData.map(item => item.count),
        data: dataFromServer.usernames.map(username => {
          var userPlacement = resumesentstodayData.find(item => item.user_name === username);
          return userPlacement ? userPlacement.count : 0;
        }),
        barPercentage: 0.3,
      },
      {
        label: "interviews",
        backgroundColor: '#9ea60d', // Green color with transparency
        hoverBackgroundColor: '#9ea60d',
        borderColor: '#9ea60d',
//        data: interviewstodayData.map(item => item.count),
        data: dataFromServer.usernames.map(username => {
          var userPlacement = interviewstodayData.find(item => item.user_name === username);
          return userPlacement ? userPlacement.count : 0;
        }),
        barPercentage: 0.3,
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    tooltips: {
      enabled: true,
    },
    scales: {

      xAxes: [

        {
        ticks: {
          maxRotation: 90, // Adjust the rotation angle as needed
          minRotation: 10,
        },
        gridLines: {
          display: false, // Remove the grid lines
        },
          barPercentage: 0.7, // Adjust the bar width as needed
        categoryPercentage: 0.6,

        },
      ],
    },
   plugins: {
      labels: false, // Disable rendering labels
    },

  },
});
function filterDataByCustomRange(dataArray, startDate, endDate) {
  return dataArray.filter(item => {
    const formattedItemDate = item.date.replace(/[\s,]+/g, '-');
    return formattedItemDate >= startDate && formattedItemDate <= endDate;
  });
}
function filterDataByUsername(dataArray, username) {
  return dataArray.filter(item => item.user_name === username);
}
function updateChartcandi(interviewsData, helpingData, resumesentData) {
  myChartcandidate.data.datasets[0].data = dataFromServer.usernames.map(username => {
    const userPlacement = helpingData.find(item => item.user_name === username);
    return userPlacement ? userPlacement.count : 0;
  });

  myChartcandidate.data.datasets[1].data = dataFromServer.usernames.map(username => {
    const userPlacement = resumesentData.find(item => item.user_name === username);
    return userPlacement ? userPlacement.count : 0;
  });

  myChartcandidate.data.datasets[2].data = dataFromServer.usernames.map(username => {
    const userPlacement = interviewsData.find(item => item.user_name === username);
    return userPlacement ? userPlacement.count : 0;
  });

  myChartcandidate.update();
}
function handleDateFilter() {
  const selectedValue = dateFilterDropdown.value;

  if (selectedValue === "all1") {
    updateChartcandi(helpingstodayData, resumesentstodayData, interviewstodayData);
  } else if (selectedValue === "yesterday1") {
    updateChartcandi(helpingsyesterdayData, resumesentsyesterdayData, interviewsyesterdayData);
  } else if (selectedValue === "last3days1") {
    updateChartcandi(helpingsLast3DaysData, resumesentsLast3DaysData, interviewsLast3DaysData);
  } else if (selectedValue === "custom1") {
    // Show the customDateFormfordeal form when "Custom" is selected
     customDateFormforcan.style.display = 'block';
  }
}
function handleCustomDateFilter(event) {
  event.preventDefault();
  const startDate = document.getElementById("startDate1").value;
  const endDate = document.getElementById("endDate1").value;

  const customInterviewsData = filterDataByCustomRange(interviewstodayData, startDate, endDate);
  const customHelpingData = filterDataByCustomRange(helpingstodayData, startDate, endDate);
  const customResumesentData = filterDataByCustomRange(resumesentstodayData, startDate, endDate);

  updateChartcandi(customInterviewsData, customHelpingData, customResumesentData);
}
function handleUsernameFilter(event) {
  const selectedUsername = event.target.value;
  const selectedDateFilter = dateFilterDropdown.value;

  if (selectedUsername === "No filter") {
    if (selectedDateFilter === "yesterday1") {
      updateChartcandi(helpingsyesterdayData, resumesentsyesterdayData, interviewsyesterdayData);
    } else if (selectedDateFilter === "last3days1") {
      updateChartcandi(helpingsLast3DaysData, resumesentsLast3DaysData, interviewsLast3DaysData);
    } else if (selectedDateFilter === "custom1") {
      const startDate = document.getElementById("startDate1").value;
      const endDate = document.getElementById("endDate1").value;

      const customInterviewsData = filterDataByCustomRange(interviewstodayData, startDate, endDate);
      const customHelpingData = filterDataByCustomRange(helpingstodayData, startDate, endDate);
      const customResumesentData = filterDataByCustomRange(resumesentstodayData, startDate, endDate);

      updateChartcandi(customInterviewsData, customHelpingData, customResumesentData);
    } else {
      updateChartcandi(helpingstodayData, resumesentstodayData, interviewstodayData);
    }
  } else {
    if (selectedDateFilter === "yesterday1") {
      var userDataYesterday = helpingsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataResumesentsYesterday = resumesentsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataInterviewsYesterday = interviewsyesterdayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartcandi(userDataInterviewsYesterday, userDataResumesentsYesterday, userDataYesterday);
    } else if (selectedDateFilter === "last3days1") {
      var userDataLast3Days = helpingsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataResumesentsLast3Days = resumesentsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataInterviewsLast3Days = interviewsLast3DaysData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartcandi(userDataInterviewsLast3Days, userDataResumesentsLast3Days, userDataLast3Days);
    } else if (selectedDateFilter === "custom1") {
      const startDate = document.getElementById("startDate1").value;
      const endDate = document.getElementById("endDate1").value;

      var customUserData = interviewstodayData.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      var customUserDataResumesents = helpingstodayData.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      var customUserDataInterviews = resumesentstodayData.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });
      updateChartcandi(customUserDataInterviews, customUserDataResumesents, customUserData);
    } else {
      var userData = interviewstodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataResumesents = helpingstodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      var userDataInterviews = resumesentstodayData.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChartcandi(userDataInterviews, userDataResumesents, userData);
    }
  }
}





//placementChart
//console.log(dataFromServer.candidateplacement);
var today = new Date();
var formattedToday = today.toISOString().slice(0, 10);
//console.log("formattedToday:", formattedToday);
var todayData = dataFromServer.candidateplacement.filter(function(item) {
  var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
//  console.log("formattedItemDate:", formattedItemDate);
  return formattedItemDate === formattedToday;
});
//console.log("todayData:", todayData);
//yesterday
var yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
var formattedYesterday = yesterday.toISOString().slice(0, 10);
filteredDatayesterday = dataFromServer.candidateplacement.filter(function(item) {
            var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
            return formattedItemDate === formattedYesterday;
});
//console.log("yesterday:", filteredDatayesterday);


//last 3 days
var today = new Date();
var yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);
var yesterdaybefore = new Date();
yesterdaybefore .setDate(yesterdaybefore .getDate() - 2);
var formattedToday = today.toISOString().slice(0, 10);
var formattedYesterday = yesterday.toISOString().slice(0, 10);
var formattedyesterdaybefore = yesterdaybefore.toISOString().slice(0, 10);
var formattedDatesLast3Days = [
  formattedToday,
  formattedYesterday,
  formattedyesterdaybefore
];

filteredlast3days = dataFromServer.candidateplacement.filter(function(item) {
  var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
  return formattedDatesLast3Days.includes(formattedItemDate);
});
//console.log("filteredlast3days:", filteredlast3days);

var ctx = document.getElementById("placementChart").getContext("2d");
function generateLabelColors(numColors) {
  var colors = [];
  for (var i = 0; i < numColors; i++) {
    var hue = (i * 37) % 360; // You can adjust the hue calculation
    var color = 'hsl(' + hue + ', 70%, 50%)';
    colors.push(color);
  }
  return colors;
}
var numUsernames = dataFromServer.usernames.length;
var labelColors = generateLabelColors(numUsernames);
var myChartpalcement = new Chart(ctx, {
  type: 'pie',
  responsive: true,
  legend: {
    display: true,
  },
  data: {
    labels: dataFromServer.usernames,
    datasets: [
      {
        backgroundColor: labelColors,
        hoverBackgroundColor: labelColors.map(color => color.replace('0.6', '0.8')),
        borderWidth: 2,
        borderDash: [],
        borderDashOffset: 0.0,
        data: dataFromServer.usernames.map(username => {
          var userPlacement = todayData.find(item => item.user_name === username);
          return userPlacement ? userPlacement.count : 0;
        }),
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    tooltips: {
      enabled: true,
    },
    plugins: {
      labels: {
        render: function (args) {
          return args.label + ', ' + args.value + ' (' + args.percentage.toFixed(2) + '%)';
        },
        fontColor: 'black',
        position: 'outside',
        textMargin: 8,
        overlap: true,
      },
    },
  },
});

var startDateInput = document.getElementById("startDate");
var endDateInput = document.getElementById("endDate");
var customDateForm = document.getElementById("customDateForm");
customDateForm.style.display = "none";


var dateFilterSelect = document.getElementById("dateFilter");
dateFilterSelect.addEventListener("change", function () {
  var selectedValue = dateFilterSelect.value;

  if (selectedValue === "all") {
    updateChart(todayData);
     customDateForm.style.display = "none";// Show all data
  } else if (selectedValue === "yesterday") {
    updateChart(filteredDatayesterday);
      customDateForm.style.display = "none";// Show data for yesterday
  } else if (selectedValue === "last3days") {
    updateChart(filteredlast3days);
      customDateForm.style.display = "none";// Show data for last 3 days
  } else if (selectedValue === "custom") {
    // Display the custom date form
    customDateForm.style.display = "block";
  } else {
    // Hide the custom date form for other options
    customDateForm.style.display = "none";
  }
});
customDateForm.addEventListener("submit", function (event) {
  event.preventDefault();

  var startDate = startDateInput.value;
  var endDate = endDateInput.value;
  var customData = dataFromServer.candidateplacement.filter(function(item) {
    var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
    return formattedItemDate >= startDate && formattedItemDate <= endDate;
  });

  updateChart(customData);
});
var selectUsername = document.getElementById("selectUsername");
selectUsername.addEventListener("change", function () {
  var selectedUsername = selectUsername.value;
  var selectedDateFilter = dateFilterSelect.value;

  if (selectedUsername === "No filter") {
    if (selectedDateFilter === "yesterday") {
      updateChart(filteredDatayesterday); // Show data for yesterday for all users
    } else if (selectedDateFilter === "last3days") {
      updateChart(filteredlast3days); // Show data for last 3 days for all users
    } else if (selectedDateFilter === "custom") {
      // Handle custom date filter case if needed
    } else {
      updateChart(todayData); // Show all data for all users
    }
  } else {
    if (selectedDateFilter === "yesterday") {
      var userDataYesterday = filteredDatayesterday.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChart(userDataYesterday);
    } else if (selectedDateFilter === "last3days") {
      var userDataLast3Days = filteredlast3days.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChart(userDataLast3Days);
    } else if (selectedDateFilter === "custom") {
      var startDate = startDateInput.value;
      var endDate = endDateInput.value;

      var customUserData = dataFromServer.candidateplacement.filter(function(item) {
        var formattedItemDate = item.date.replace(/[\s,]+/g, '-');
        return formattedItemDate >= startDate && formattedItemDate <= endDate && item.user_name === selectedUsername;
      });

      updateChart(customUserData);
    } else {
      var userData = dataFromServer.candidateplacement.filter(function(item) {
        return item.user_name === selectedUsername;
      });
      updateChart(userData);
    }
  }
});
function updateChart(filteredData) {
     var usernameCounts = {};

  filteredData.forEach(item => {
    if (!usernameCounts[item.user_name]) {
      usernameCounts[item.user_name] = 0;
    }
    usernameCounts[item.user_name] += item.count;
  });

  myChartpalcement.data.datasets[0].data = dataFromServer.usernames.map(username => {
    return usernameCounts[username] || 0;
  });
   myChartpalcement.update();
}
}
}