$(document).ready(function() {
    // Object containing prohibited words and their synonyms
    let prohibitedWords = {
        "meat": true,
        "food": true,
        "carnivore": true,
        "casino": true,
        "gambling house": true,
        "gambling": true,
        "scenes of violence": true,
        "bloodshed": true,
        "slaughter": true,
        "blood": true,
        "battle": true,
        "cold weapons": true,
        "edged weapons": true,
        "blade": true,
        "knives": true,
        "dagger": true,
        "firearms": true,
        "guns": true,
        "pistol": true,
        "rifle": true,
        // Add more prohibited words and synonyms as needed
    };
    
    $('#upload-form').submit(function(event) {
        event.preventDefault();
        let formData = new FormData($(this)[0]);

        $.ajax({
            url: '/upload',
            type: 'POST',
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                let ocrText = response.ocr_text.toLowerCase(); // Convert text to lowercase

                // Check if OCR text contains prohibited words
                for (let word in prohibitedWords) {
                    if (ocrText.includes(word)) {
                        $('#result').text('OCR text contains prohibited words.');
                        return; // Exit the function if any prohibited word is found
                    }
                }

                // Display OCR text if no prohibited words are found
                $('#result').text(ocrText);
            },
            error: function(xhr, status, error) {
                console.error(error); // Log any errors for debugging
                $('#result').text('Error: ' + error); // Display error message
            }
        });
    });
});
