function calculateSolar(){


let bill = document.getElementById("bill").value;


let kw = Math.ceil(bill / 1000);


let monthlySaving = bill * 0.85;


let yearlySaving = monthlySaving * 12;



document.getElementById("solarResult").innerHTML =

`

☀ Recommended Solar System: ${kw} KW <br><br>

💰 Monthly Saving Approx: ₹${monthlySaving} <br><br>

⚡ Yearly Saving Approx: ₹${yearlySaving}


`;



}

window.onload=function(){


setTimeout(()=>{


document.getElementById("loader").style.display="none";


},1000)


}

function searchLead(){


let input = document
.getElementById("leadSearch")
.value
.toLowerCase();



let rows = document
.querySelectorAll("#leadTable tbody tr");



rows.forEach(row=>{


row.style.display =

row.innerText.toLowerCase().includes(input)

?

""

:

"none";


})


}
window.addEventListener("load",()=>{


document.getElementById("loader")
.style.display="none";


});
// ADMIN CHART


let chartBox =
document.getElementById("leadChart");


if(chartBox){


new Chart(chartBox,{


type:"line",


data:{


labels:[

"Jan",

"Feb",

"Mar",

"Apr",

"May",

"Jun"

],



datasets:[{


label:"Solar Leads",


data:[

12,

25,

40,

55,

80,

120

],


borderWidth:3,


tension:.4


}]


},



options:{


responsive:true,


plugins:{


legend:{


display:true


}


}


}


});


}