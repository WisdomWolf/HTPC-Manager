#if $os.path.isfile($webdir + "./header.tpl"):
#include $webdir + "./header.tpl"#
#else
#include $defaultwebdir + "./header.tpl"#
#end if


<div class="container">

    <div class="content maincontent">
        
        <div class="page-header page-title">
            <h1>$getVar('nzb_name', 'SABnzbd')
                <small>
                    <strong>Speed:</strong> <span id="queue_speed"></span>
                    <strong>Status:</strong> <span id="queue_state"></span>
                </small>
            </h1>
        </div>

        <div id="notification_area"></div>

        <form name="add_nzb_form" id="add_nzb_form" method="post" class="well form-inline" action="">
            <input class="span6" id="nzb_url" name="nzb_url" type="text" placeholder="Paste NZB url" />
            <select class="span2" name="nzb_category" id="nzb_category">
            </select>
            <a class="btn btn-success" id="add_nzb_button"><i class="icon-plus icon-white"></i> Add NZB</a>
            <a class="btn" id="nzb_pause_button"><i class="icon-pause"></i> Pause</a>
            <input type="text" class="span1" id="nzb_get_speed" placeholder="Kb/s" value="" />
            <a class="btn" id="nzb_set_speed"><i class="icon-cog"></i> Set speed</a>
        </form>

        <ul class="nav nav-tabs">
            <li class="active"><a href="#active" data-toggle="tab">Active</a></li>
            <li><a href="#history" data-toggle="tab">History</a></li>
            <li><a href="#warnings" data-toggle="tab">Warnings</a></li>
        </ul>

        <div class="tab-content">

            <div class="tab-pane active" id="active">

                <table class="table table-striped">
                    <thead>
                    <tr>
                        <th>File</th>
                        <th>Category</th>
                        <th>Progress</th>
                        <th>Remaining</th>
                        <th>&nbsp;</th>
                    </tr>
                    </thead>
                    <tbody id="active_table_body">

                    </tbody>
                </table>

            </div>

            <div id="history" class="tab-pane">

                <table class="table table-striped">
                    <thead>
                    <tr>
                        <th>File</th>
                        <th>Status</th>
                        <th>Size</th>
                        <th>&nbsp;</th>
                    </tr>
                    </thead>
                    <tbody id="history_table_body">

                    </tbody>
                </table>

            </div>

            <div id="warnings" class="tab-pane">

                <table class="table table-striped">
                    <thead>
                    <tr>
                        <th>Warnings</th>
                    </tr>
                    </thead>
                    <tbody id="warning_table_body">

                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

#if $os.path.isfile($webdir + "./footer.tpl"):
#include $webdir + "./footer.tpl"#
#else
#include $defaultwebdir + "./footer.tpl"#
#end if
