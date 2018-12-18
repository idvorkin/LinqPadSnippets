LogChange = () =>{
    titleClass =  "PresenceAndName__nameText"
    elems = document.getElementsByClassName(titleClass)
    text = elems[elems.length-1].innerHTML
    console.log(text)
    document.title = "Chime:" + text
}
window.setInterval(LogChange,1000)


// ==UserScript==
// @name         New Userscript
// @namespace    http://tampermonkey.net/
// @version      0.1
// @description  try to take over the world!
// @author       You
// @match        //https://app.chime.aws/*
// @grant        none
// ==/UserScript==
  window.LogChange = () =>{
    titleClass =  "PresenceAndName__nameText"
    elems = document.getElementsByClassName(titleClass)
    text = elems[elems.length-1].innerHTML
    console.log(text)
    document.title = "Chime:" + text
}
(function() {

window.setInterval(window.LogChange,1000)

})();
