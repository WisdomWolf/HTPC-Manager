function removeHistoryItem(id) {
    if (confirm('Are you sure?')) {
        $.ajax({
            url: '/json/?which=sabnzbd&action=deletehistory&id=' + id,
            type: 'get',
            dataType: 'json',
            success: function (data) {
                loadQueue(1);
                loadHistory();
            }
        });
    }
}

function retryHistoryItem(id) {
    if (confirm('Are you sure?')) {
        $.ajax({
            url: '/json/?which=sabnzbd&action=retry&id=' + id,
            type: 'get',
            dataType: 'json',
            success: function (data) {
                loadQueue(1);
                loadHistory();
            }
        });
    }
}

function loadHistory() {
    $.ajax({
        url: '/json/?which=sabnzbd&action=history&limit=25',
        type: 'get',
        dataType: 'json',
        success: function (data) {
            if (data.status == false) {
                $('#notification_area').addClass('alert alert-error');
                $('#notification_area').html('<strong>Error</strong> Could not connect to SABnzbd, go to <a href="/settings">settings</a>');
                return false;
            }
            $('#history_table_body').html('');
            $.each(data.history.slots, function (i, slot) {

                var deleteImage = makeIcon('icon-remove', 'Delete');
                deleteImage.click(function () {
                    removeHistoryItem(slot.nzo_id);
                });

                var retryImage = null;
                if (slot.status == 'Failed') {
                    var retryImage = makeIcon('icon-repeat', 'Retry');
                    retryImage.click(function () {
                        retryHistoryItem(slot.nzo_id);
                    });
                }

                var failMessage = $('<span>');
                failMessage.addClass('label');
                failMessage.addClass('label-important');
                failMessage.html(slot.fail_message);
                failMessage.find('a').remove();

                var row = $('<tr>')
                if (slot.status == 'Failed') {
                    row.append($('<td>').html(slot.name).append('&nbsp;').append(failMessage));
                } else {
                    row.append($('<td>').html(slot.name));
                }
                row.append($('<td>').html(slot.status));
                row.append($('<td>').html(slot.size));
                row.append($('<td>').append(deleteImage));
                row.append($('<td>').append(retryImage));

                $('#history_table_body').append(row);
            });

        }
    });
}

function removeQueueItem(id) {
    if (confirm('Are you sure?')) {
        $.ajax({
            url: '/json/?which=sabnzbd&action=delete&id=' + id,
            type: 'get',
            dataType: 'json',
            success: function (data) {

                loadQueue(1);
                loadHistory();
            }
        });
    }
}

function changeCategory(id, cat) {
    $.ajax({
        url: '/json/?which=sabnzbd&action=change_cat&id=' + id + '&value=' + cat,
        type: 'get',
        dataType: 'json'
    });
}

var queueToggleStatusAction = '';

function loadQueue(once) {
    $.ajax({
        url: '/json/?which=sabnzbd&action=status',
        type: 'get',
        dataType: 'json',
        success: function (object) {

            if (object.status == false) {

                $('#notification_area').addClass('alert alert-error');
                $('#notification_area').html('<strong>Error</strong> Could not connect to SABnzbd, go to <a href="/settings">settings</a>');
                return false;
            }
            data = object.queue;
            if (once == 1) {
                $('#nzb_get_speed').val(data.speedlimit);
            }

            $('#nzb_pause_button').button('reset');
            if (data.status == 'Paused') {
                $('#nzb_pause_button').html('<i class="icon-play"></i> Resume');
                queueToggleStatusAction = 'resume';
            } else {
                $('#nzb_pause_button').html('<i class="icon-pause"></i> Pause')
                queueToggleStatusAction = 'pause';
            }

            var state = data.status.toLowerCase();
            var formattedState = state.charAt(0).toUpperCase() + state.slice(1);

            $('#queue_state').html(formattedState);
            $('#queue_speed').html(data.speed + 'B/Sec');

            $('#active_table_body').html('');

            if (data.slots.length == 0) {
                var row = $('<tr>')
                row.append($('<td>').html('Queue is empty').attr('colspan', 5));
                $('#active_table_body').append(row);
            }

            $.each(data.slots, function (i, job) {

                var progressBar = $('<div>');
                progressBar.addClass('bar');
                progressBar.css('width', job.percentage + '%').text(job.percentage + '%');

                var  progress = $('<div>');
                progress.addClass('progress');
                progress.append(progressBar);

                var row = $('<tr>')
                row.append($('<td>').html(job.filename));

                // Juiste categorie weergeven en kunnen aanpassen

                var categories = $('<select>');
                categories.addClass('span2');
                categories.change(function() {
                    changeCategory(job.nzo_id, $(this).val());
                });
                setCategories(categories, job.cat);

                row.append($('<td>').html(categories));

                row.append($('<td>').html(progress));
                row.append($('<td>').html(job.timeleft + ' / ' + job.mbleft + 'MB').addClass('span3'));

                var deleteImage = $('<a>');
                deleteImage.html('&times;');
                deleteImage.attr('alt', 'Remove');
                deleteImage.addClass('close');
                deleteImage.attr('href', '#');
                deleteImage.click(function () {
                    removeQueueItem(job.nzo_id);
                });

                row.append($('<td>').html(deleteImage));

                $('#active_table_body').append(row);
            });

        }
    });
}

function loadWarnings() {
    $.ajax({
        url: '/json/?which=sabnzbd&action=warnings',
        type: 'get',
        dataType: 'json',
        success: function (data) {

            if (data.warnings == 0) {
                var row = $('<tr>')
                row.append($('<td>').html('No warnings'));
                $('#warning_table_body').append(row);
            }

            $.each(data.warnings, function (i, warning) {
                var row = $('<tr>')
                row.append($('<td>').html(warning));
                $('#warning_table_body').append(row);
            });

        }
    });
}

// Haal categorieen op
function setCategories(selector, select) {
    $.ajax({
        url: '/json/?which=sabnzbd&action=categories',
        type: 'post',
        dataType: 'json',
        success: function (data) {

            // return false;
            $.each(data.categories, function (i, cat) {

                var option = $('<option>');
                if (select == cat) {
                    option.attr('selected', true);
                }
                option.attr('value', cat);
                option.html(cat);
                $(selector).append(option);
            });
        }
    });
}
