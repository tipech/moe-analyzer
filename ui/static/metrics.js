$(document).ready(metrics_load_handler)


// function responsible for all metrics actions after page load
function metrics_load_handler() {

    // if we are on the metrics view
    if ($('nav.metrics-view').length > 0) {

        // edge deselection button
        $('.desel_edges').click(function(){
            deselect_all('.edge')
        })

        // path deselection button
        $('.desel_paths').click(function(){
            deselect_all('.path')
        })

        // group deselection button
        $('nav ul.tabs li').click(function(){
            set_behavior($(this).attr('data-tab'))
        })
        

        // set the entire network as the default element
        set_behavior('groups-tab')
        $('.metrics-view tr[data-group-id="0"]').addClass('selected')
        reset_selections()
        update_panels()

        // bind listeners for parameters/selections changed by user
        window.addEventListener('selection_changed', update_panels)
        $(".metric-checkbox").click(function(){ update_panels() })
        $("#beta").change(function(){
            draw_charts( 1 - $(this).val() )
        })

        draw_charts(1)
    }
}

function update_panels(){
// Update the graph panels based on user selected options

    update_selections()
    update_metrics()
}

function update_selections(){
// Show/hide all graph panels based on which elements are selected

    // get all selected edge systems
    var sel_systems = []
    $('.edge.selected').each(function(){
        sel_systems.push($(this).attr("data-edge-id"))
    })

    // get all selected paths
    $('.path.selected').each(function(){
        sel_systems.push($(this).attr("data-path-id"))
    })

    // get all selected groups
    $('.group.selected').each(function(){
        sel_systems.push($(this).attr("data-group-id"))
    })

    // hide all graph panels and show only the selected ones
    $(".graph-panel").addClass("hidden")
    sel_systems.forEach(function(system_id){
        $(`.graph-panel[data-system-id="${system_id}"]`).removeClass("hidden")
    })
}

function update_metrics(){

    $(".metric-checkbox").each(function(){
        id = $(this).attr("id")

        if ($(this).is(":checked")){
            $(".label." + id).removeClass("hidden")
            $(".graph." + id).removeClass("hidden")
        } else {
            $(".label." + id).addClass("hidden")
            $(".graph." + id).addClass("hidden")
        }
    })
}


function draw_charts(beta){

    var margin = {top: 20, right: 10, bottom: 20, left: 40}

    // get the width of any graph that isn't hidden
    var width = $("#roadMap").first().width() - margin.left - margin.right
    var height = $(".graph").first().height() - margin.top - margin.bottom

    // get common chart X scale
    var xScale = d3.scaleLinear()
        .domain([
            $(".metrics-view").attr("data-time-start"),
            $(".metrics-view").attr("data-time-end")]) // input
        .range([0, width]); // output


    // draw all edge charts
    $("tr.edge").each(function(){

        // get the id and metric values for this edge
        var edge_id = $(this).attr("data-edge-id")
        var dataset = JSON.parse($(this).attr("data-edge-metrics"))

        draw_chart(edge_id, dataset, margin, width, height, xScale, beta)        
    })

    // draw all path charts
    $("tr.path").each(function(){

        // get the id and metric values for this path
        var path_id = $(this).attr("data-path-id")
        var dataset = JSON.parse($(this).attr("data-path-metrics"))

        draw_chart(path_id, dataset, margin, width, height, xScale, beta)
    })

    // draw all group charts
    $("tr.group").each(function(){

        // get the id and metric values for this group
        var group_id = $(this).attr("data-group-id")
        var dataset = JSON.parse($(this).attr("data-group-metrics"))

        draw_chart(group_id, dataset, margin, width, height, xScale, beta)        
    })

}


function draw_chart(system_id, dataset, margin, width, height, xScale, beta){

    // get all the individual metrics
    Object.keys(dataset).forEach(function(metric) {

        var peak = Math.max(...dataset[metric].map(function(d){
                return d["y"]
            }))

        // Y scale will is based on maximum values
        var yScale = d3.scaleLinear()
            .domain([0, peak]) // input 
            .range([height, 0]); // output

        // Line generator
        var line = d3.line()  
            .x(function(d) { return xScale(d.x); })
            .y(function(d) { return yScale(d.y); })
            .curve(d3.curveBundle.beta(beta)) // smoothing


        // clear previous svg if it exists
        d3.selectAll(".graph-panel")
            .filter('[data-system-id="'+system_id+'"]')
            .select(".graph."+metric)
            .select("svg").remove()

        // Create the main svg element for the chart
        var svg = d3.selectAll(".graph-panel")
            .filter('[data-system-id="'+system_id+'"]')
            .select(".graph."+metric)
            .append("svg")
                .attr("width", width)
                .attr("height", height + margin.top + margin.bottom)
            .append("g")
                .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")")

        // Create X axis component
        svg.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(d3.axisBottom(xScale));

        // Create Y axis component
        svg.append("g")
            .attr("class", "y axis")
            .call(d3.axisLeft(yScale).ticks(5));

        // Append the path, bind the data, and call the line generator 
        svg.append("path")
            .datum(dataset[metric])
            .attr("class", "line")
            .attr("d", line);
    });

}