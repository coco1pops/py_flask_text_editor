export function selectDropdownValue(inputId, buttonId, value, text) {
    document.getElementById(inputId).value = value;
    document.getElementById(buttonId).innerText = text;
}