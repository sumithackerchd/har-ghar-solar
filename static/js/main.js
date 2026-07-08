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