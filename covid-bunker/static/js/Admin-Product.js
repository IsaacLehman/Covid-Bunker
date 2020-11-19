

var openFile = function(event) {
    var input = event.target;

    // Instantiate FileReader
    var reader = new FileReader();
    reader.onload = function(){
        TheFileContents = reader.result;
        // Update the output to include the <img> tag with the data URL as the source

        image = document.querySelector(".admin-product-picture"); 
        image.src = TheFileContents;
        image.style.visibility = "visible";

    };
    // Produce a data URL (base64 encoded string of the data in the file)
    // We are retrieving the first file from the FileList object
    reader.readAsDataURL(input.files[0]);
};