var createButton = document.querySelector("#show-create-button");
var searchButton = document.querySelector("#show-search-button");

var createForm = document.querySelector(".create-form");
var searchForm = document.querySelector(".search-form");

createButton.addEventListener("click", function(){
    createForm.style.display = "";
    searchForm.style.display = "none";
})

searchButton.addEventListener("click", function(){
    searchForm.style.display = "";
    createForm.style.display = "none";
})

