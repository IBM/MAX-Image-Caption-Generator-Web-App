// javascript code for MAX webapp

function add_thumbnails(data) {
    img_object = "<img src='" + data["file_name"] + "' alt='" + data["caption"] + "' title='" + data["caption"] + "' >";
    $("#thumbnails").prepend(img_object);
}

$(function() {

    // Image upload form submit functionality
    $('#img_upload').on('submit', function(data){
        // Stop form from submitting normally
        event.preventDefault();

        // Get form data
        var form = event.target;
        var data = new FormData(form);

        // perform file upload
        $.ajax({
            url: "/upload",
            method: "post",
            processData: false,
            contentType: false,
            data: data,
            processData: false,
            dataType: "json",
            success: function(data) {
                add_thumbnails(data);
            }
        })
    })

});
