document.addEventListener("DOMContentLoaded", function () {

    const form = document.getElementById("waterForm");

    const button =
        document.getElementById("waterSubmitButton");


    if (!form || !button) {
        return;
    }


    form.addEventListener("submit", function () {

        button.disabled = true;

        button.innerHTML =
            '<i class="fas fa-spinner fa-spin"></i> ' +
            'Analyzing Water Requirement...';

    });

});