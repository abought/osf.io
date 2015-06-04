<%inherit file="project/addon/widget.mako"/>
<%page expression_filter="h"/>

<div id="markdownRender" class="break-word">
    % if wiki_content:
        ${wiki_content | n}  ## Relies on the view to pass in HTML-sanitized data
    % else:
        <p><em>No wiki content</em></p>
    % endif
</div>

<script>
    window.contextVars = $.extend(true, {}, window.contextVars, {
        wikiWidget: true,
        usePythonRender: ${use_python_render | json},
        urls: {
            wikiContent: ${wiki_content_url | json}
        }
    })
</script>
