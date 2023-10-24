if ($ === undefined) $ = django.jQuery;

function updateVisibility(wrapper, file_selected) {
    wrapper.find(".ddcu_choose_file").toggle(!file_selected);
    wrapper.find(".ddcu_choose_other_file").toggle(file_selected);
    wrapper.find(".ddcu_delete_file").toggle(file_selected);
    if (!file_selected) {
        wrapper.find(".ddcu_current_file_name").text("");
    }
}

$(document).ready(function($) {
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
            if (wrapper.data('immediatesubmit') === "yes") wrapper.closest("form").submit();
        }
        updateVisibility(wrapper, file_selected);
    });

    $('.ddcu_delete_file').on("click", function(e) {
        var wrapper = $(e.target).closest(".ddcu_wrapper");
        wrapper.find(".ddcu_file_input").val("");
        wrapper.find("input[type=hidden]").val("");
        updateVisibility(wrapper, false);
    });

    $('.ddcu_m_file_input').on('change', function(e) {
        var wrapper = $(e.target).closest(".ddcu_wrapper");
        $.each(e.target.files, function(i, file) {
            var div_elem = wrapper.find(".ddcu_m_new_file_template").clone();
            div_elem.removeClass("ddcu_m_new_file_template");
            div_elem.removeClass("ddcu_hidden");
            div_elem.find(".ddcu_m_filename").text(file.name);
            div_elem.data("fileobj", file);
            div_elem.appendTo(wrapper.find(".ddcu_m_file_list"));
            window.koen = div_elem;
        });
        $(this).val('');  // Remove the files from the input field
    });

    $('.ddcu_wrapper').on("click", '.ddcu_m_delete', function(e) {
        var entry = $(e.target).closest(".ddcu_m_file_entry");
        entry.addClass("ddcu_m_to_be_deleted");
        entry.find(".ddcu_m_marked_for_deletion").removeClass("ddcu_hidden");
        entry.find(".ddcu_m_delete").addClass("ddcu_hidden");
        entry.find(".ddcu_m_cancel_deletion").removeClass("ddcu_hidden");
    });

    $('.ddcu_wrapper').on("click", '.ddcu_m_cancel_deletion', function(e) {
        var entry = $(e.target).closest(".ddcu_m_file_entry");
        entry.removeClass("ddcu_m_to_be_deleted");
        entry.find(".ddcu_m_marked_for_deletion").addClass("ddcu_hidden");
        entry.find(".ddcu_m_delete").removeClass("ddcu_hidden");
        entry.find(".ddcu_m_cancel_deletion").addClass("ddcu_hidden");
    });

    $('form').submit(function(submitEvent){
        if (window.ddcu_ready === true) return true; // Don't intercept submission

        var ddcu_wrappers = [];
        window.ddcu_number_of_files = 0;
        $(submitEvent.target).find(".ddcu_wrapper").each(function(i, wrapper) {
            var file_objs = [];
            var keep_files = [];
            var allow_multiple = ($(wrapper).data('allowmultiple') === "yes");
            if (allow_multiple) {
                $(wrapper).find(".ddcu_m_file_entry").each(function(j, entry_elem) {
                    if (!$(entry_elem).hasClass("ddcu_m_to_be_deleted")) {
                        var file_obj = $(entry_elem).data("fileobj");
                        if (file_obj !== undefined) {
                            file_objs.push(file_obj);
                        }
                        if ($(entry_elem).data('path') !== undefined) {
                            keep_files.push($(entry_elem).data('path'));  // Already-uploaded file
                        }
                    }
                });
            } else {
                var input_elem = $(wrapper).find(".ddcu_file_input").get(0);
                if (input_elem.files.length === 1) {
                    file_objs.push(input_elem.files[0]);
                }
            }
            window.ddcu_number_of_files += file_objs.length;
            ddcu_wrappers.push({wrapper: wrapper, file_objs: file_objs, keep_files});
        });
        if (ddcu_wrappers.length === 0) return true; // No ddcu wrappers found.

        $(".ddcu_overlay").css('display', 'flex');
        submitEvent.preventDefault();

        $.each(ddcu_wrappers, function(wrapper_idx, ftu_obj) {
            var jqwrapper = $(ftu_obj.wrapper);
            var allow_multiple = (jqwrapper.data('allowmultiple') === "yes");
            var field = jqwrapper.find("input[type=hidden]");
            var keep_existing_paths = [];  // Will only be filled and used if allow_multiple is true
            jqwrapper.find(".ddcu_m_file_entry").each(function (j, entry_elem) {
                if (!$(entry_elem).hasClass("ddcu_m_to_be_deleted") && $(entry_elem).data("path") != undefined) {
                    keep_existing_paths.push($(entry_elem).data("path"));
                }
            });
            if (ftu_obj.file_objs.length > 0) {
                var params = {
                    token: jqwrapper.data("ddcu-token"),
                    csrfmiddlewaretoken: $("input[name=csrfmiddlewaretoken]").val()
                };
                var file_indexes = [];
                $.each(ftu_obj.file_objs, function (f_idx, f) {
                    file_indexes.push(f_idx);
                    params["filename_" + f_idx] = f.name;
                    params["content_type_" + f_idx] = f.type || "application/octet-stream";
                });
                $.post(jqwrapper.data("ddcu-guu-path"), params,
                    function (data) {
                        if (allow_multiple) {
                            var all_paths = keep_existing_paths.concat(JSON.parse(data.inputval));
                            field.val(JSON.stringify(all_paths));
                        } else {
                            field.val(data.inputval);
                        }
                        $(file_indexes).each(function () {  // We don't use a for loop here, because we need a new scope for each iteration. When dropping support for IE11, we can use `for (let f_idx=...` here instead.
                            var f_idx = this;
                            $.ajax({
                                url: data.urls[f_idx],
                                type: 'PUT',
                                data: ftu_obj.file_objs[f_idx],
                                contentType: params["content_type_" + f_idx],
                                success: function () {
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
                        });
                    },
                    "json"
                );
            } else {  // No files to upload, create a new JSON representation of the paths of the existing, non-removed files.
                if (allow_multiple) {
                    field.val(JSON.stringify(keep_existing_paths));
                }
            }
        });
        if (window.ddcu_number_of_files === 0) {
            window.ddcu_ready = true;
            $(submitEvent.target).submit();  // No files have been uploaded, so the success function of the ajax-call will never be executed.
        }
    });
});