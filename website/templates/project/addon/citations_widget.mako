<script type="text/javascript">
window.contextVars = $.extend(true, {}, window.contextVars, {
    ${short_name}: {
        folder_id: ${list_id | json}
    }
});

</script>
<div class="citation-picker">
    <input id="${short_name}StyleSelect" type="hidden" />
</div>
<div id="${short_name}Widget" class="citation-widget">
	<div class="citation-loading"> <i class="fa fa-spinner citation-spin"></i> <p class="m-t-sm fg-load-message"> Loading citations...  </p> </div>
</div>
