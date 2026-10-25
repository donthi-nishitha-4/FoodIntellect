document
.getElementById("barcodeForm")
.addEventListener("submit", async function(e) {

    e.preventDefault();


    const barcode =
        document.getElementById("barcode").value;


    const formData =
        new FormData();

    formData.append(
        "barcode",
        barcode
    );


    const response =
        await fetch(
            "/api/ingest/barcode",
            {
                method: "POST",
                body: formData
            }
        );


    const data =
        await response.json();


    if (data.success) {

        await analyzeProduct(
            data.product
        );

    }

});


document
.getElementById("imageForm")
.addEventListener("submit", async function(e) {

    e.preventDefault();


    const image =
        document.getElementById(
            "foodImage"
        ).files[0];


    const formData =
        new FormData();

    formData.append(
        "image",
        image
    );


    const response =
        await fetch(
            "/api/ingest/image",
            {
                method: "POST",
                body: formData
            }
        );


    const data =
        await response.json();


    if (data.success) {

        await analyzeProduct(
            data.product
        );

    }

});


async function analyzeProduct(product) {

    const response =
        await fetch(
            "/api/analyze/",
            {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify(product)

            }
        );


    const data =
        await response.json();


    sessionStorage.setItem(
        "analysis",
        JSON.stringify(data)
    );


    window.location.href =
        "/result";

}