function generateName() {
    fetch("/generate_name")
        .then(response => response.json())
        .then(data => {
            if (data.name) {
                document.getElementById("code_name").value = data.name;
            } else {
                alert(data.error);
            }
        })
        .catch(error => {
            console.error("Ошибка:", error);
        });
}