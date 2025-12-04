// Only simple login checks (frontend)
// Flask backend will be added later

function studentLogin() {
    let email = document.getElementById("studentEmail").value;
    let pass = document.getElementById("studentPass").value;

    if (email === "" || pass === "") {
        alert("Enter all details");
        return;
    }

    alert("Student Login Successful (Demo)");
}

function teacherLogin() {
    let email = document.getElementById("teacherEmail").value;
    let pass = document.getElementById("teacherPass").value;

    if (email === "" || pass === "") {
        alert("Enter all details");
        return;
    }

    alert("Teacher Login Successful (Demo)");
}
