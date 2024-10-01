function showFilters(){
    var filter = document.querySelector('.filters');
    
    if(filter.style.display === 'block'){
        filter.style.display = 'none';
    }
    else{
        filter.style.display = 'block';
    }
}

function changeTheme(){
    const currentTheme = document.body.getAttribute("data-theme");
    const newTheme = currentTheme === "light" ? "dark" : "light";

    document.getElementById("themeToggle").setAttribute("src", currentTheme === "light" ? "./static/mode.png" : "./static/mode (1).png");
    document.getElementById("loginButton").setAttribute("src", currentTheme === "light" ? "./static/power-light.png" : "./static/power-dark.png");

    document.body.setAttribute("data-theme", newTheme);
}