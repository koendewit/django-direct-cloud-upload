if ($ === undefined) $ = django.jQuery;

function updateVisibility(wrapper, file_selected) {
    wrapper.find(".ddcu_choose_file").toggle(!file_selected);
    wrapper.find(".ddcu_choose_other_file").toggle(file_selected);
    wrapper.find(".ddcu_delete_file").toggle(file_selected);
    if (!file_selected) {
        wrapper.find(".ddcu_current_file_name").text("");
    }
}

$(document).ready(function() {
    $(".ddcu_wrapper").each(function(i, wrapper) {
        var file_selected = ($(wrapper).find(".ddcu_current_file_name").text() !== "");
        updateVisibility($(wrapper), file_selected);
    });

    $('.ddcu_overlay').slice(1).remove(); // Multiple widgets may exist on the page, but we only need one overlay.
    $('.ddcu_overlay').appendTo('body');

    $('.ddcu_file_input').on("change", function(e) {
        var wrapper = $(e.target).closest(".ddcu_wrapper");
        var file_selected = false;
        if (e.target.files.length === 1) {
            var f = e.target.files[0];
            wrapper.find(".ddcu_current_file_name").text(f.name);
            file_selected = true;
        }
        updateVisibility(wrapper, file_selected);
    });

    $('.ddcu_delete_file').on("click", function(e) {
        var wrapper = $(e.target).closest(".ddcu_wrapper");
        wrapper.find(".ddcu_file_input").val("");
        wrapper.find("input[type=hidden]").val("");
        updateVisibility(wrapper, false);
    });

    $('form').submit(function(submitEvent){
        if (window.ddcu_ready === true) return true; // Don't intercept submission

        var fields_to_upload = [];
        $(submitEvent.target).find(".ddcu_wrapper").each(function(i, wrapper) {
            if ($(wrapper).find(".ddcu_file_input").get(0).files.length === 1)
                fields_to_upload.push(wrapper);
        });
        if (fields_to_upload.length === 0) return true; // No files to upload; submit immediately.

        $(".ddcu_overlay").css('display', 'flex');
        submitEvent.preventDefault();
        window.ddcu_number_of_files = fields_to_upload.length;

        $.each(fields_to_upload, function(i, wrapper) {
            var jqwrapper = $(wrapper);
            var field = jqwrapper.find("input[type=hidden]");
            var f = jqwrapper.find(".ddcu_file_input").get(0).files[0];
            $.post(jqwrapper.data("ddcu-guu-path"), {
                    token: jqwrapper.data("ddcu-token"),
                    filename: f.name,
                    content_type: f.type || "application/octet-stream",
                    csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
                },
                function(data) {
                    $.ajax({
                        url: data.url,
                        type: 'PUT',
                        data: f,
                        contentType: f.type,
                        success: function () {
                            field.val(data.path);
                            window.ddcu_number_of_files--;
                            if (window.ddcu_number_of_files === 0) {
                                window.ddcu_ready = true;
                                $(submitEvent.target).submit();
                            }
                        },
                        error: function (result) {
                            console.log(result);
                            alert("Error while uploading.");
                        },
                        processData: false
                    });
                },
                "json"
            );
        });
    });
});