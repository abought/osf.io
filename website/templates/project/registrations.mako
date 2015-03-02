<%inherit file="project/project_base.mako"/>
<%def name="title()">${node['title']} Registrations</%def>

<div class="page-header  visible-xs">

  <h2 class="text-300">Registrations</h2>
</div>

<div class="row">
  <div class="col-sm-9">

  <p>Registrations are permanent, read only copies of a project. Registration saves the state of a project at a particular point in time - such as right before data collection, or right when a manuscript is submitted.</p>
     % if node["registration_count"]:
        <div mod-meta='{
            "tpl": "util/render_nodes.mako",
            "uri": "${node["api_url"]}get_registrations/",
            "replace": true
            }'></div>
    % elif node['node_type'] != 'project':
        <p>To register this component, you must <a href="${parent_node['url']}registrations"><b>register its parent project</b></a> (<a href="${parent_node['url']}">${parent_node['title']}</a>).</p>
    % else:

        <p>There have been no registrations of this ${node['node_type']}.
        See a list of the <a href="/explore/activity/#newPublicRegistrations">newest</a> 
        and <a href="/explore/activity/#popularPublicRegistrations">most viewed</a> public registrations on the
        Open Science Framework.</p>
    % endif

  </div>
  <div class="col-sm-3">
    <div>
      % if 'admin' in user['permissions'] and node['node_type'] == 'project' and not disk_saving_mode:
      <a href="${node['url']}register" class="btn btn-default" type="button">New Registration</a>
    % endif
  </div>

  </div>
</div>
