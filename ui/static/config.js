$(document).ready(config_load_handler)


// function responsible for all config actions after page load
function config_load_handler() {


    // update DOM when network parameters change
    $('#network').change(reload_config)
    $('#shortest_paths').change(reload_config)

    // hide simulation parameters when no simulation is selected
    $('#simulation').change(function(){

        if ( $(this).val() != "none"){
            $(".sim_parameters").removeClass("hidden")
        } else {
            $(".sim_parameters").addClass("hidden")
        }
    })

    // load map (check ther actually is one)
    map = get_map("roadMap")
    if(map){

        // read edges and draw the road network map
        edges_bounds = read_edges()
        map.draw(edges_bounds[0], edges_bounds[1])

        // set the table's behavior
        set_behavior('edges-tab')

        // $('.content ul.tabs li').off('click')
        $('.content ul.tabs li').click(function(){
            deselect_all()
            set_behavior($(this).attr('data-tab'))
        })

        // common deselection button
        $('.desel_all').click(function(){
            deselect_all()
        })
    }

    $('#analyze').click(load_metrics)
}


function reload_config(){
// reload the entire config page

    $.get("/config", 
        {'network': $('#network').val(),
        'shortest_paths': $("#shortest_paths").is(":checked")},
        function( data ) {
            var data = data.replace('<body', '<body><div id="body"')
                .replace('</body>','</div></body>');
            var body = $(data).filter('#body');
            $("body").html(body)
        });
}


function get_map(element='map', center=[0,0], zoom=10,
    colors={'default': "black", 'highlighted': "red", 'selected': "blue"}){
// get a new map object instance if possible

    // check if object existed and, if so , delete it
    if (typeof window._map !== 'undefined' && window._map) { 
        window._map.map.remove()
        delete window._map
    }

    // check if the map element actually exists
    if ($("#" + element).length > 0) {
        
        // make a new Map obj and store it at global window level
        window._map = new Map(element, center, zoom, colors)
    
    // otherwise store an empty object
    } else {
        window._map = null
    }

    return window._map
}


function read_edges(){
// Read edge data attributes and return them as an array

    var edges = {}
    var lats = []
    var lngs = []

    $('.edge').each(function(){

        // get edge id, number of lanes and shape
        id = $(this).attr("data-edge-id")
        lanes = $(this).attr("data-edge-lanes")
        shapestr = $(this).attr("data-edge-shape").split(" ")
        shape = shapestr.map(x => x.split(",").reverse())

        // store latitude, longitude values separately for bounds calculation
        lats.push(shape[0][0])
        lngs.push(shape[0][1])
        
        edges[id] = {'id': id, 'shape': shape, 'lanes': lanes}
    })

    // calculate bounding box corner coordinates
    var bounds = [[Math.min(...lats), Math.min(...lngs)],
        [Math.max(...lats), Math.max(...lngs)]]

    return [edges, bounds]
}


function deselect_all(element_type="") {
// remove all selections
    
    $(element_type + '.selected').removeClass("selected")
    reset_selections()
}


function set_behavior(tab_id) {
// Set the appropriate behavior based on the tab the user is viewing
    
    $('.edge').off()
    $('.path').off()
    $('.group').off()
    map.off()

    if (tab_id == "edges-tab") {
        edge_list_behavior()
        
    } else if (tab_id == "paths-tab") {
        path_list_behavior()
        
    } else if (tab_id == "custom-tab") {
        group_list_behavior()
        
    }
}


function edge_list_behavior() {
// Handle the map and table's behavior when in the edges tab

    // handle edge highlighting when mousing over map
    map.on('mouseover', function(ev){
        $(`.edge[data-edge-id="${ev.edge}"]`).addClass("highlighted")
        map.set_highlighted(ev.edge, true)
    })
    map.on('mouseout', function(ev){
        $(`.edge[data-edge-id="${ev.edge}"]`).removeClass("highlighted")
        map.set_highlighted(ev.edge, false)  
    })

    // handle edge highlighting when mousing over table
    $('.edge').on('mouseover', function(){ 
        $(this).addClass("highlighted") // highlighting on
        map.set_highlighted( $(this).attr("data-edge-id"), true)
    })
    $('.edge').on('mouseout', function(){ 
        $(this).removeClass("highlighted") // highlighting off
        map.set_highlighted( $(this).attr("data-edge-id"), false)
    })

    // handle edge selecting when mousing over map
    map.on('click', function(ev){
        $(`.edge[data-edge-id="${ev.edge}"]`).toggleClass("selected")
        reset_selections()
    })

    // handle edge selecting function when mousing over table
    $('.edge').on('click', function(){ // toggle selected
        // $(this).off('click')
        $(this).toggleClass("selected")

        reset_selections()
    })


    // select all edges
    $('#sel_all_edges').click(function(){
        $('.edge').addClass("selected")
        reset_selections()
    })

    // add group button listener
    $('#group_edges_btn').click(function(){
    
        // get new custom group name and edges
        var name = $('#group_edges_input').val()
        var edges = []
        $('.edge.selected').each(function(){
            edges.push($(this).attr("data-edge-id"));
        });

        add_group(name, edges)
    })
}


function path_list_behavior() {
// Handle the map and table's behavior when in the paths tab

    // index paths by the edges they contain
    map.edge_groups = {}
    $('.path').each(function(){
        
        // get path id and all edges in this path
        path_id = $(this).attr("data-path-id")
        edges = $(this).attr("data-path-edges").split(",")

        // iterate through edges and index the paths each one belongs to
        for (index in edges){
            edge = edges[index]

            // if entry existed, i.e. edge is also part of another path
            if (edge in map.edge_groups){
                map.edge_groups[edge].push(path_id)
            
            // if no entry existed, i.e. it's the first path this edge is in
            } else {
                map.edge_groups[edge] = [path_id]
            }
        }
    })

    // handle path highlighting when mousing over map
    map.on('mouseover', function(ev){

        // get all paths that contain this edge
        path_elements = []
        paths = map.edge_groups[ev.edge]

        // if there were some paths, get the respective path elements 
        if (paths !== undefined) {
            paths.forEach(function(path){
                path_elements.push($(`.path[data-path-id="${path}"]`))
            })

            // get all edges in each individual path
            path_elements.forEach(function(path_element){
                path_edges = path_element.attr("data-path-edges").split(",")

                // highlight appropriate path and edges
                path_element.addClass("highlighted")
                map.set_highlighted(path_edges, true)
            })
        }
    })

    // handle path highlighting when the mouse leaves the map
    map.on('mouseout', function(ev){

        // get all paths that contain this edge
        path_elements = []
        paths = map.edge_groups[ev.edge]

        // if there were some paths, get the respective path elements 
        if (paths !== undefined) {
            paths.forEach(function(path){
                path_elements.push($(`.path[data-path-id="${path}"]`))
            })

            // get all edges in each individual path
            path_elements.forEach(function(path_element){
                path_edges = path_element.attr("data-path-edges").split(",")

                // highlight appropriate path and edges
                path_element.removeClass("highlighted")
                map.set_highlighted(path_edges, false)   
            })
        }
    })

    // handle edge highlighting when mousing over table
    $('.path').on('mouseover', function(){ 
        $(this).addClass("highlighted") // highlighting on
        map.set_highlighted($(this).attr("data-path-edges").split(","), true)
    })
    $('.path').on('mouseout', function(){ 
        $(this).removeClass("highlighted") // highlighting off
        map.set_highlighted($(this).attr("data-path-edges").split(","), false)
    })

    // handle path selecting when mousing over map
    map.on('click', function(ev){

        // get all paths that contain this edge
        path_elements = []
        paths = map.edge_groups[ev.edge]

        // if there were some paths, get the respective path elements 
        if (paths !== undefined) {
            paths.forEach(function(path){
                path_elements.push($(`.path[data-path-id="${path}"]`))
            })

            // select/deselect each individual path
            path_elements.forEach(function(path_element){
                path_element.toggleClass("selected")
            })
            
            reset_selections()
        }
    })
    
    // handle path selecting function when mousing over table
    $('.path').on('click', function(){ // toggle selected
        $(this).toggleClass("selected")
        reset_selections()
    })

    // select all paths
    $('#sel_all_paths').click(function(){
        $('.path').addClass("selected")
        reset_selections()
    })

    // add group button listener
    $('#group_paths_btn').click(function(){

        // get new custom group name and edges
        var name = $('#group_paths_input').val()
        var edges = []
        $('.path.selected').each(function(){
            edges = edges.concat($(this).attr("data-path-edges").split(","))
        });

        add_group(name, edges)
    })
}



function group_list_behavior() {
// Handle the map and table's behavior when in the groups tab

    // index groups by the edges they contain
    map.edge_groups = {}
    $('.group').each(function(){
        
        // get group id and all edges in this group
        group_id = $(this).attr("data-group-id")
        edges = $(this).attr("data-group-edges").split(",")

        // iterate through edges and index the groups each one belongs to
        for (index in edges){
            edge = edges[index]

            // if entry existed, i.e. edge is also part of another group
            if (edge in map.edge_groups){
                map.edge_groups[edge].push(group_id)
            
            // if no entry existed, i.e. it's the first group this edge is in
            } else {
                map.edge_groups[edge] = [group_id]
            }
        }
    })

    // handle group highlighting when mousing over map
    map.on('mouseover', function(ev){

        // get all groups that contain this edge
        group_elements = []
        groups = map.edge_groups[ev.edge]

        // if there were some groups, get the respective group elements 
        if (groups !== undefined) {
            groups.forEach(function(group){
                group_elements.push($(`.group[data-group-id="${group}"]`))
            })

            // get all edges in each individual group
            group_elements.forEach(function(group_element){
                group_edges = group_element.attr("data-group-edges").split(",")

                // highlight appropriate group and edges
                group_element.addClass("highlighted")
                map.set_highlighted(group_edges, true)
            })
        }
    })

    // handle group highlighting when the mouse leaves the map
    map.on('mouseout', function(ev){

        // get all groups that contain this edge
        group_elements = []
        groups = map.edge_groups[ev.edge]

        // if there were some groups, get the respective group elements 
        if (groups !== undefined) {
            groups.forEach(function(group){
                group_elements.push($(`.group[data-group-id="${group}"]`))
            })

            // get all edges in each individual group
            group_elements.forEach(function(group_element){
                group_edges = group_element.attr("data-group-edges").split(",")

                // highlight appropriate group and edges
                group_element.removeClass("highlighted")
                map.set_highlighted(group_edges, false)   
            })
        }
    })

    // handle edge highlighting when mousing over table
    $('.group').on('mouseover', function(){ 
        $(this).addClass("highlighted") // highlighting on
        map.set_highlighted($(this).attr("data-group-edges").split(","), true)
    })
    $('.group').on('mouseout', function(){ 
        $(this).removeClass("highlighted") // highlighting off
        map.set_highlighted($(this).attr("data-group-edges").split(","), false)
    })

    // handle group selecting when mousing over map
    map.on('click', function(ev){

        // get all groups that contain this edge
        group_elements = []
        groups = map.edge_groups[ev.edge]

        // if there were some groups, get the respective group elements 
        if (groups !== undefined) {
            groups.forEach(function(group){
                group_elements.push($(`.group[data-group-id="${group}"]`))
            })

            // select/deselect each individual group
            group_elements.forEach(function(group_element){
                group_element.toggleClass("selected")
            })
            
            reset_selections()
        }
    })
    
    // handle group selecting function when mousing over table
    $('.group').on('click', function(){ // toggle selected
        $(this).toggleClass("selected")
        reset_selections()
    })

    // select all groups
    $('#sel_all_groups').click(function(){
        $('.group').addClass("selected")
        reset_selections()
    })
}


function reset_selections(){
// clear all map line selections and reselect based on selected elements

    map.set_selected(Object.values(map.edges), false)

    // find selected edges
    $('.edge.selected').each(function(){
        edge_id = $(this).attr("data-edge-id")
        map.set_selected(edge_id, true)
    })
    // find selected paths and set all their edges to selected
   $('.path.selected').each(function(){
        path_edges = $(this).attr("data-path-edges").split(",")
        map.set_selected(path_edges, true)
    })
    // find selected groups and set all their edges to selected
   $('.group.selected').each(function(){
        group_edges = $(this).attr("data-group-edges").split(",")
        map.set_selected(group_edges, true)
    })

    window.dispatchEvent(new Event('selection_changed'))
}


function add_group(name, edges){
// Create a custom group of edge systems and add it to the model    

    if (edges.length > 0 && name != "") {

        $('.selected').removeClass("selected")
        reset_selections()
        
        $.post({
            url: "/add_edge_group",
            data: JSON.stringify({'name': name, 'edges': edges}),
            contentType: "application/json; charset=utf-8",
            dataType: "html",
            success: function( data ) {
                var custom_groups = $(data).find('#custom-tab');
                $("#custom-tab").html(custom_groups.first().html());
                config_load_handler()
            }})
    }
}


function load_metrics(){
// reload the entire metrics page

    $.get("/metrics", 
        {'simulation': $('#simulation').val(),
        'obs_window': $("#obs_window").val(),
        'obs_rate': $("#obs_rate").val()},
        function( data ) {
            var data = data.replace('<body', '<body><div id="body"')
                .replace('</body>','</div></body>');
            var body = $(data).filter('#body');
            $("body").html(body);
            config_load_handler();
        });
}