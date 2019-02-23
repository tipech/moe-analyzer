var hl_color = "rgba(255, 0, 0, 0.7)"
var hl_width = 4
var sel_color = "rgba(0, 51, 255, 0.7)"
var sel_width = 4
var def_color = "black"
var def_width = 1



$(document).ready(handle_loading)


function handle_loading(){

    var area = document.querySelector('#canvas_container')
    if (area) { panzoom(area, { maxZoom: 4, minZoom: 1}) }

    // tab functionality
    $('ul.tabs li').click(function(){
        var tab_id = $(this).attr('data-tab');

        $('ul.tabs li').removeClass('current');
        $('.tab-content').removeClass('current');

        $(this).addClass('current');
        $("#"+tab_id).addClass('current');
    })


    // update DOM when network selection changes
    $('#network').change(get_config_DOM)
    // draw map
    redraw($('#map')[0], $('.edge'), def_width, def_color)

    // set edge hover listeners
    $('.edge').hover(function(){ // handlerIn

        hl_canvas = $('#highlight')[0]
        const hl_ctx = hl_canvas.getContext('2d');
        draw_shape(hl_ctx,$(this).attr("data-edge-shape"), hl_width, hl_color)

    },function(){ // handlerOut

        hl_canvas = $('#highlight')[0]
        const hl_ctx = hl_canvas.getContext('2d');
        hl_ctx.clearRect(0, 0, hl_canvas.width, hl_canvas.height);
    })

    // edge click listeners
    $('.edge').click(function(){ // toggle selected
        $(this).toggleClass("selected")
        redraw($('#selection')[0], $('.selected'), sel_width, sel_color)
    })

    // selection buttons
    $('#sel_all_edges').click(function(){
        $('.edge').addClass("selected")
        redraw($('#selection')[0], $('.selected'), sel_width, sel_color)
    })
    $('.desel_all').click(function(){
        $('.selected').removeClass("selected")
        redraw($('#selection')[0], $('.selected'), sel_width, sel_color)
    })

    // add group listener
    $('#group_edges_btn').click(function(){

        var name = $('#group_edges_input').val()
        var edges = []
        $('.edge.selected').each(function(){
            edges.push($(this).attr("data-edge-id"));
        });

        if (edges.length > 0 && name != "") {

            $('.selected').removeClass("selected");
            redraw($('#selection')[0], $('.selected'), sel_width, sel_color);

            console.log({'name':name, 'edges': edges});

            $.post("/add_edge_group",
                {'name':name, 'edges': edges},
                get_config_DOM)
        }
    })
}

function get_config_DOM(){

    $.get("/config", 
        {'network': $('#network').val()},
        function( data ) {
            var data = data.replace('<body', '<body><div id="body"')
                .replace('</body>','</div></body>');
            var body = $(data).filter('#body');
            $("body").html(body);
            handle_loading();
        });
}


function redraw(canvas, objects, width, color){

    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    objects.each(function(){
        draw_shape(ctx, $(this).attr("data-edge-shape"), width, color)
    })
}


function draw_shape(ctx, shape, width=1, color){

    ctx.lineWidth = width;
    ctx.strokeStyle = color;
    ctx.fillStyle = color;

    shape = shape.split(" ")
    x_coords = []
    y_coords = []

    // retrieve coordinates
    for (var i = 0; i < shape.length; i++) {
        point = shape[i].split(",")
        x_coords.push(point[0])
        y_coords.push(point[1])
    }

    // if it's a very short edge, draw circle instead of arrow
    if(Math.pow(x_coords[1]-x_coords[0],2)
        + Math.pow(y_coords[1]-y_coords[0],2) < 3){

        // draw start circle
        ctx.beginPath();
        ctx.arc(x_coords[0], y_coords[0], width, 0, 6.28)
        ctx.fill();
    
    } else { // otherwise draw an arrow

        ctx.beginPath();
        canvas_arrow(ctx, x_coords[1], y_coords[1],
            x_coords[0], y_coords[0], 5*Math.sqrt(width))

        ctx.moveTo(x_coords[1], y_coords[1]);
        for (var i = 2; i < x_coords.length; i++) {
            ctx.lineTo(x_coords[i], y_coords[i]);
        }
        ctx.stroke();
    }

}

function canvas_arrow(ctx, fromx, fromy, tox, toy, headlen){

    var angle = Math.atan2(toy-fromy,tox-fromx);
    ctx.moveTo(fromx, fromy);
    ctx.lineTo(tox, toy);
    ctx.lineTo(tox-headlen*Math.cos(angle-Math.PI/6),
        toy-headlen*Math.sin(angle-Math.PI/6));
    ctx.moveTo(tox, toy);
    ctx.lineTo(tox-headlen*Math.cos(angle+Math.PI/6),
        toy-headlen*Math.sin(angle+Math.PI/6));
}
