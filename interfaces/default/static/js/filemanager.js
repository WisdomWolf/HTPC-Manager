$(document).ready(function () {
    loadMounts();
});

function loadMounts() {

    $.ajax({
        url: 'json/?which=system&action=diskspace',
        type: 'post',
        dataType: 'json',
        beforeSend: function () {
            $('#filemanager_table_body').html('');
        },
        success: function (data) {
            $.each(data, function (path, info) {

                var icon = $('<i>')
                icon.addClass('icon-folder-close');
                var iconCell = $('<td>');
                iconCell.append(icon);

                var pathAnchor = $('<a>');
                pathAnchor.attr('href', 'javascript:;');
                pathAnchor.html(path);
                pathAnchor.click(function () {
                    loadPath({path : path})
                });

                var pathCell = $('<td>');
                pathCell.append(pathAnchor);

                var actionsCell = $('<td>');
                actionsCell.html('&nbsp;');

                var row = $('<tr>');
                row.append(iconCell);
                row.append(pathCell);
                row.append(actionsCell);

                $('#filemanager_table_body').append(row);

            });
        }
    });
}

function loadPath(options) {

    var postdata = {
        path : ''
    };
    $.extend(postdata, options)

    $.ajax({
        url: 'json/?which=system&action=diskspace',
        type: 'post',
        data: postdata,
        dataType: 'json',
        beforeSend: function () {
            $('#filemanager_table_body').html('');
        },
        success: function (data) {

            var previousAnchor = $('<a>');
            previousAnchor.attr('href', 'javascript:;');
            previousAnchor.html('..');
            if (data.parent != '') {
                previousAnchor.click(function () {
                    loadPath({
                        path : data.parent
                    });
                });
            } else {
                previousAnchor.click(function () {
                    loadMounts();
                });
            }
            var row = $('<tr>');
            row.append($('<td>').html('&nbsp;'));
            row.append($('<td>').html(previousAnchor));
            row.append($('<td>').html('&nbsp;'));
            $('#filemanager_table_body').append(row);

            $.each(data.dirs, function (path, name) {

                var icon = $('<i>')
                icon.addClass('icon-folder-close');
                var iconCell = $('<td>');
                iconCell.append(icon);

                var pathAnchor = $('<a>');
                pathAnchor.attr('href', 'javascript:;');
                pathAnchor.html(name);
                pathAnchor.click(function () {
                    loadPath({
                        path : path
                    })
                });

                var pathCell = $('<td>');
                pathCell.append(pathAnchor);

                var actionsCell = $('<td>');
                actionsCell.html('&nbsp;');

                var row = $('<tr>');
                row.append(iconCell);
                row.append(pathCell);
                row.append(actionsCell);

                $('#filemanager_table_body').append(row);

            });

            $.each(data.files, function (path, name) {

                var icon = $('<i>')
                icon.addClass('icon-file');
                var iconCell = $('<td>');
                iconCell.append(icon);

                var pathAnchor = $('<a>');
                pathAnchor.attr('href', 'javascript:;');
                pathAnchor.html(name);

                var pathCell = $('<td>');
                pathCell.append(pathAnchor);

                var actionDelete = makeIcon('icon-remove', 'Delete')
                var actionEdit = makeIcon('icon-pencil', 'Rename')
                var actionMove = makeIcon('icon-share-alt', 'Move')

                var actionsCell = $('<td>');
                actionsCell.css('white-space', 'nowrap');
                actionsCell.append(actionEdit);
                actionsCell.append('&nbsp;');
                actionsCell.append(actionDelete);
                actionsCell.append('&nbsp;');
                actionsCell.append(actionMove);

                var row = $('<tr>');
                row.append(iconCell);
                row.append(pathCell);
                row.append(actionsCell);

                $('#filemanager_table_body').append(row);

            });

        }
    });
}
