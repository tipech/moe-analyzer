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
        
        // bind listeners for parameters/selections changed by user
        window.addEventListener('selection_changed', update_panels)
        $(".metric-checkbox").click(function(){ update_panels() })

        // set the entire network as the default element
        set_behavior('groups-tab')
        $('.metrics-view tr[data-group-id="0"]').addClass('selected')
        reset_selections()
        update_panels()
    }

    // console.log($('.metrics-view tr[data-group-id="0"]').attr("class"))
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