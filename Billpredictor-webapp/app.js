const API="http://127.0.0.1:5000"

function login(){

fetch(API+"/login",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
email:email.value,
password:password.value
})
})
.then(r=>r.json())
.then(data=>{

if(data.status==="success"){

localStorage.setItem("user_id",data.user_id)
window.location="dashboard.html"

}else{
alert(data.message)
}

})

}

function register(){

fetch(API+"/register",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
name:name.value,
email:email.value,
password:password.value
})
})
.then(r=>r.json())
.then(data=>{
alert(data.message)
window.location="login.html"
})

}

function loadDashboard(){

let user=localStorage.getItem("user_id")

fetch(API+"/monthly_summary/"+user)
.then(r=>r.json())
.then(data=>{

summary.innerHTML=
"Total Expense: ₹"+data.total_month_expense+
"<br>Daily Avg: ₹"+data.daily_average

})

}

function addExpense(){

fetch(API+"/add_expense",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
user_id:localStorage.getItem("user_id"),
category_id:category.value,
amount:amount.value
})
})
.then(r=>r.json())
.then(data=>{
alert(data.message)
})

}

function loadHistory(){

let user=localStorage.getItem("user_id")

fetch(API+"/history/"+user)
.then(r=>r.json())
.then(data=>{

let html=""

data.expenses.forEach(e=>{

html+=
e.category_name+
" ₹"+e.amount+
" <button onclick='deleteExpense("+e.expense_id+")'>Delete</button><br>"

})

history.innerHTML=html

})

}

function deleteExpense(id){

fetch(API+"/delete_expense/"+id,{
method:"DELETE"
})
.then(r=>r.json())
.then(()=>{
loadHistory()
})

}

function addEvent(){

fetch(API+"/add_event",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({

user_id:localStorage.getItem("user_id"),
event_name:event_name.value,
event_date:event_date.value,
estimated_cost:cost.value

})
})
.then(r=>r.json())
.then(data=>{
alert(data.message)
})

}

function loadEvents(){

let user=localStorage.getItem("user_id")

fetch(API+"/events/"+user)
.then(r=>r.json())
.then(data=>{

let html=""

data.forEach(e=>{

html+=e.event_name+
" ₹"+e.estimated_cost+
"<br>"

})

events.innerHTML=html

})

}

function predict(){

fetch(API+"/ai_predict",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({
user_id:localStorage.getItem("user_id")
})
})
.then(r=>r.json())
.then(data=>{

result.innerHTML=
"Predicted Next Month Expense: ₹"+
data.ai_predicted_next_month_expense

})

}