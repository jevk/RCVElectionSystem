//functions to convert timestamp (seconds) to different time units
function getMinutes(delta){
    return parseInt(delta/60);
}
function getHours(delta){
    return parseInt(delta/60/60);
}
function getDays(delta){
    return parseInt(delta/60/60/24);
}
function getWeeks(delta){
    return parseInt(delta/60/60/24/7);
}
function needsS(number)
{
    if (number == 1){
        return "";
    }
    return "s";
}

function generateDelta(delta) //why do I have to do this myself
{
    weeks = getWeeks(delta);
    days = getDays(delta)-weeks*7;
    hours = getHours(delta)-(weeks*7+days)*24;
    minutes = getMinutes(delta)-((weeks*7+days)*24+hours)*60;
    seconds = delta-(((weeks*7+days)*24+hours)*60+minutes)*60;
    
    let buildString = "";
    if (weeks>0){
        buildString = buildString + weeks.toString()+" week"+needsS(weeks)+", ";
    }
    if (days>0){
        buildString = buildString + days.toString()+" day"+needsS(days)+", ";
    }
    if (hours>0){
        buildString = buildString + hours.toString()+" hour"+needsS(hours)+", ";
    }
    if (minutes>0){
        buildString = buildString + minutes.toString()+" minute"+needsS(minutes)+", ";
    }
    
    buildString = buildString + seconds.toString()+" second"+needsS(seconds);
    
    return buildString;
}


let timeStamp = parseInt(document.getElementById("counter").innerText.split(" ")[0]); //timestamp will be placed inside the counter element on page load
let which = document.getElementById("counter").innerText.split(" ")[1];
function updateDelta()
{
    let delta = parseInt((timeStamp - new Date().getTime())/1000); //delta to date in seconds
    
    if (which == "close")
    {
        document.getElementById("counter").innerText = generateDelta(-delta).concat(" since voting closed");
    }
    else if (which == "open")
    {
        document.getElementById("counter").innerText = generateDelta(delta).concat(" until voting opens");
    }
    else if (which == "running")
    {
        document.getElementById("counter").innerText = generateDelta(delta).concat(" until voting closes");
    }
    
    if (delta == 0)
    {    
        document.getElementById("counter").style.visibility = "hidden";
        setTimeout(function() {
            location.reload(true);
        }, 1000*Math.random()*10+1000); //random, to eliminate the biggest spikes
    }
}


updateDelta();
var t = setInterval(updateDelta,1000);