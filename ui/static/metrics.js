$(document).ready(metrics_load_handler)


// function responsible for all metrics actions after page load
function metrics_load_handler() {

    // edge deselection button
    $('.desel_edges').click(function(){
        deselect_all('.edge')
    })

    // path deselection button
    $('.desel_paths').click(function(){
        deselect_all('.path')
    })

    $('nav ul.tabs li').click(function(){
        set_behavior($(this).attr('data-tab'))
    })
    
    window.addEventListener('selection_changed', update_panels)
    $(".metric-checkbox").click(function(){ update_panels() })

    $('.tab-link[data-tab="custom-tab"]').click()
    $('tr[data-group-id="0"]').click()
    // update_panels()
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
        console.log(`.graph-panel[data-system-id="${system_id}"]`)
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