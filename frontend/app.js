const display = document.getElementById("display");

appendToDisplay = (input) => {
    display.value += input;
}

backspace = (input) => {
    console.log(display.value);
    display.value = display.value.slice(0, -1);
    console.log(display.value); 
}

clearDisplay = () => {
    display.value = "";
}

calculate = () =>{
    try{
        display.value = eval(display.value);
    } catch(error){
        display.value = "Error";
    }
}