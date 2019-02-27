$(document).ready(base_load_handler)


// function responsible for all common actions after page load
function base_load_handler() {
    
    // generic tab functionality
    $('ul.tabs li').click(function(){
        var tab_id = $(this).attr('data-tab');

        $('ul.tabs li').removeClass('current');
        $('.tab-content').removeClass('current');

        $(this).addClass('current');
        $("#"+tab_id).addClass('current');
    })
}



// Map object
function Map(element='map', center=[0,0], zoom=10,
    colors={'default': "black", 'highlighted': "red", 'selected': "blue"}) {

    //  properties
    this.map = L.map(element, {center: center, zoom: zoom})  // map element
    this.lines = {}       // line objects dictionary, keyed by edge id
    this.edges = {}       // edge ids dictionary, keyed by line object id
    this.edge_groups = {} // multi-edge groups dictionary, indexed by edges
    this.colors = colors  // default/highlight/select colors

    this.draw = function(edges, bounds) { 
    // Draw/refresh the map element

        // draw edges
        for (var id in edges) {
            edge = edges[id]

            // draw line according to edge shape
            var line = L.polyline(edge.shape, {
                color: this.colors.default,
                weight: 1.5 * edge.lanes
            }).addTo(this.map);

            // store line object and associated id
            this.lines[id] = {
                'edge_id': id,
                'line': line,
                'selected': false,
                'highlighted': false}

            this.edges[line._leaflet_id] = id
        }

        // pan nad zoom map to fit to bounds
        this.map.fitBounds(bounds);
    }


    this.on = function(event_type, callback) {
    // Assign an event callback to all lines

        // iterate through edges
        for (var edge_id in this.lines){
            line = this.lines[edge_id].line

            // handle event, proxy passes the context (this map obj) to it
            line.on(event_type, $.proxy(function(ev){
                
                // when event fires, append edge id to it
                ev.edge = this.edges[ev.target._leaflet_id]
                callback(ev)

            }, this))
        }
    }


    this.off = function(){
    // Clear listeners for all lines

        for (var edge_id in this.lines){
            this.lines[edge_id].line.off()
        }
    }


    this.set_highlighted = function(edges, highlighted) {
    // Set the status of a line as highlighted or not

        // check if argument is array or just single edge
        if (edges.constructor !== Array){
            edges = [edges]
        }

        // iterate through given edges and set highlighted property
        for (index in edges){
            edge_id = edges[index]
            this.lines[edge_id].highlighted = highlighted
            this.set_color(edge_id)
        }
    }


    this.set_selected = function(edges, selected) {
    // Set the status of a line as selected or not

        // check if argument is array or just single edge
        if (edges.constructor !== Array){
            edges = [edges]
        }


        // iterate through given edges and set selected property
        for (index in edges){
            edge_id = edges[index]
            this.lines[edge_id].selected = selected
            this.set_color(edge_id)
        }
    
    }


    this.set_color = function(edge_id) {
    // Set the color of a line based on its selected and highlighted status

        // if line is highlighted
        if (this.lines[edge_id].highlighted) {
            this.lines[edge_id].line.setStyle({'color': this.colors.highlighted})

        // if line is selected
        } else if (this.lines[edge_id].selected) {
            this.lines[edge_id].line.setStyle({'color': this.colors.selected})

        // if line isn't highlighted or selected
        } else {
            this.lines[edge_id].line.setStyle({'color': this.colors.default})
        }
    }
}