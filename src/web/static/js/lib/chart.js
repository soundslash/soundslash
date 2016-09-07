
function Chart(width, height, data, dataset, display_time) {

    // Piechart data example
    // { "x": [65, 35], "legend": ["A", "B"] }
    // Linechart data example
    // {
    // "x": [["2012-10-8 00:00:00", "2012-10-9 00:00:00", "2012-10-10 00:00:00", "2012-10-11 00:00:00", "2012-10-12 00:00:00", "2012-10-13 00:00:00", "2012-10-14 00:00:00"],     ["2012-10-8 00:00:00", "2012-10-9 00:00:00", "2012-10-10 00:00:00", "2012-10-11 00:00:00", "2012-10-12 00:00:00", "2012-10-13 00:00:00", "2012-10-14 00:00:00"],      ["2012-10-8 00:00:00", "2012-10-9 00:00:00", "2012-10-10 00:00:00", "2012-10-11 00:00:00", "2012-10-12 00:00:00", "2012-10-13 00:00:00", "2012-10-14 00:00:00"]],
    // "y": [[5, 50, 2, 9, 10, 50, 10], [0, 10, 20, 5, 20, 60, 1],  [10, 10, 20, 45, 10, 10, 10]],
    // "legend": [ "odoslané", "zrušené", "dokončené"],
    // "time": 1
    // }


    Raphael.fn.roundedRectangle = function (x, y, w, h, r1, r2, r3, r4){
        var array = [];
        array = array.concat(["M",x,r1+y, "Q",x,y, x+r1,y]); //A
        array = array.concat(["L",x+w-r2,y, "Q",x+w,y, x+w,y+r2]); //B
        array = array.concat(["L",x+w,y+h-r3, "Q",x+w,y+h, x+w-r3,y+h]); //C
        array = array.concat(["L",x+r4,y+h, "Q",x,y+h, x,y+h-r4, "Z"]); //D

        return this.path(array);
    };

    this.data = data;
    this.dataset = dataset;
    this.r = Raphael(this.dataset);
    this.txtattr = { "font-family": "Open Sans", "font-size": "12px", "fill": "#fff" };
    this.width = width;
    this.height = height;
    this.axisxstep = 25;
    this.axisystep = 5;
    this.symbol = 'circle'; // 'circle'
    this.colors = ['#5A86DC', '#d8301b', '#75ba23'];
//    this.colors = ['#bcbf7d', '#8fc7b9', '#ffa28f']
    this.resizable = true;
    this.resizing = false;
    this.xresize = 0;
    this.lastResizedWidth = this.width;
    this.typeChart = null;
    this.display_time = display_time;


    this.lastDiff = 0;

//    this.initResizing = function() {
//
//        if (this.resizable)
//        {
//
//
//            this.lastResizedWidth = $('#'+this.dataset).parent().width();
//
//
//            var that = this;
//
//            $(window).bind('resize', function() {
//
//                that.xresize = $('#'+that.dataset).parent().width() - that.lastResizedWidth;
//
////                    console.log(that.xresize);
//
//                if (that.resizing) return;
//                that.resizing = true;
//
//
//                var that2 = that;
//
////                setTimeout(function () {
////                    if (that2.typeChart == 'line')
////                        that2.redrawLinechart(that2.width + that2.xresize, that2.height);
////                    if (that2.typeChart == 'pie')
////                        that2.redrawPiechart(that2.width + that2.xresize, that2.height + that2.xresize);
////                    that2.resizing = false;
////                }, 300);
//
//            });
//
//        }
//    }


    this.redrawLinechart = function(width, height) {
        this.width = width;
        this.height = height;
        $('#'+this.dataset).empty();
        this.r = Raphael(this.dataset);
        this.drawLinechart();
    }

    this.redrawPiechart = function(width, height) {
        this.width = width;
        this.height = height;
        $('#'+this.dataset).empty();
        this.r = Raphael(this.dataset);
        this.drawPiechart();
    }



    this.getTimestamp = function(str)
    {
        var d = str.match(/\d+/g); // extract date parts
        return +new Date(d[0], d[1] - 1, d[2], d[3], d[4], d[5]); // build Date object
    }

    this.prepareData = function() {

        // Timestamp to number
        if (this.data["time"] === 1)
        {

            for(var i=0;i<this.data["x"].length;i++)
            {

                for(var j=0;j<this.data["x"][i].length;j++)
                {
                    this.data["x"][i][j] = this.getTimestamp(this.data["x"][i][j]);
                }
            }



        }
    }

    this.prepareData();

    this.drawLinechart = function()  {

        if (this.width == -1) {
//            console.log(this.dataset);
            this.width = $('#'+this.dataset).width()
                    -parseInt($('#'+this.dataset).css("padding-left"))
                    -parseInt($('#'+this.dataset).css("padding-right"))-9;
//            this.width = $('#'+this.dataset).parent().width()
//                -parseInt($('#'+this.dataset).parent().css("padding-left"))
//                -parseInt($('#'+this.dataset).css("padding-left"))
//                -parseInt($('#'+this.dataset).parent().css("padding-right"))
//                -parseInt($('#'+this.dataset).css("padding-right"))
//                -parseInt($('#'+this.dataset).css("margin-left"))
//                -parseInt($('#'+this.dataset).css("margin-right"))-20;
        }

        this.typeChart = 'line';

        var opts = { nostroke: false,
            shade: true,
            axis: "0 0 1 1",
            //                    symbol: "circle",
            smooth: false,
            colors: this.colors
        };

        if (this.symbol !== null)
        {
            opts["symbol"] = this.symbol;
        }


        // Count biggest element od left
        var max = 0;
        for(var i=0;i<this.data["y"].length;i++)
            for(var j=0;j<this.data["y"][i].length;j++)
                if (max<this.data["y"][i][j])
                    max=this.data["y"][i][j];




        var a = this.r["text"](0, -1000, max);
//        a.hide();

        // Draw chart



        var chart = this.r.linechart(
                a.getBBox().width+10, 20,
                this.width-35, this.height-20,
                this.data["x"],
                this.data["y"],
                opts);


//        console.log(chart);

        var y_axis = this.height;

        // Change x axis from number to time
        if (this.data["time"] == 1)
        {
            // Change the x-axis labels
            chart.axis[0].text.hide();
//            var axisItems = chart.axis[0].text.items;
            var startx = -1;
//            for( var i = 0, l = axisItems.length; i < l; i++ )
//            {
////                var date = new Date(parseInt(axisItems[i].attr("text")));
//                // using the excellent dateFormat code from Steve Levithan
//
////                if (this.display_time == "day") {
////                    axisItems[i].attr("text", dateFormat(date, "HH:00")).attr(this.txtattr);
////                    axisItems[i].translate(-50, 0);
////
////                }
////                if (this.display_time == "month") {
////                    axisItems[i].attr("text", dateFormat(date, "dd.mm.")).attr(this.txtattr);
////                }
////                if (this.display_time == "year") {
////                    axisItems[i].attr("text", dateFormat(date, "mm.yy.")).attr(this.txtattr);
////                }
//                y_axis = axisItems[i].attrs["y"];
//                axisItems[i].hide();
////                axisItems[i].attr("text", dateFormat(date, "dd.mm.yy")).attr(this.txtattr);
//            }
        }



        var shades = chart.shades;



        // Draw legend
        var labels = this.data["legend"];
        chart.labels = this.r.set();
        var x = 15; var h = 5;
        var that = this;
//        for( var i = 0; i < labels.length; ++i ) {
        jQuery.eachAsync(labels, { delay: 100, bulk: 0,
            loop: function(i, value)
            {
            var clr = chart.lines[i].attr("stroke");
            chart.labels.push(that.r.set());
            var c;
            chart.labels[i].push(c = that.r["circle"](x, h, 5)
                    .attr({fill: clr, stroke: "none"}));
            var a = that.r["text"](x, h-1000, labels[i]);
            a.hide();
            var d;
            chart.labels[i].push(d = that.r["text"](x+a.getBBox().width/2+13, h, labels[i]).attr(that.txtattr));
            x += chart.labels[i].getBBox().width+10;

            c.node.lines=d.node.lines=chart.symbols[i];
            c.node.shade=d.node.shade=shades[i];

            var a = function() {

                this.shade.attr({opacity: '0.9'});
                this.shade.toFront();

                for( var j = 0; j<this.lines.length; j++ ) {
                    this.lines[j].node.hover.show().toFront();
                    this.lines[j].node.hoverrect.show().toFront();
                    this.lines[j].node.hovertext.show().toFront();
                }
            };
            var b = function() {
                this.shade.attr({opacity: '0.3'});
                this.shade.toBack();
                for( var j = 0; j<this.lines.length; j++ ) {
                    this.lines[j].node.hover.hide();
                    this.lines[j].node.hovertext.hide();
                    this.lines[j].node.hoverrect.hide();
                }
            };
            c.node.onmouseover = a;
            c.node.onmouseout = b;
            d.node.onmouseover = a;
            d.node.onmouseout = b;

            }
        });





        // Hide x, y axis
        for( var i = 0, l = chart.axis.length; i < l; i++ )
        {
            chart.axis[i].hide();
        }
        // Move x, y axis
        var axisItems = chart.axis[0].text.items;
        for( var i = 0, l = axisItems.length; i < l; i++ )
        {
            axisItems[i].translate(0,5);

        }
        var axisItems = chart.axis[1].text.items;
        for( var i = 0, l = axisItems.length; i < l; i++ )
        {
            axisItems[i].translate(-10,0);
            axisItems[i].attr(this.txtattr);
        }

        // Draw grid
//        var axisItems = chart.axis[1].text.items;
//        for( var i = 0, l = axisItems.length; i < l; i++ ) {
//            if (startx == -1)
//                startx = axisItems[i].getBBox().x+10+10;
//            axisItems[i].attr(this.txtattr);
//            this.drawLine(startx,
//                    axisItems[i].getBBox().y+axisItems[i].getBBox().height/2,
//                    this.width-20,
//                    axisItems[i].getBBox().y+axisItems[i].getBBox().height/2,
//                    this.r,
//                    0.07);
//
//        }






        if (this.symbol !== null)
        {

            // Resize circles
            var symbols = chart.symbols;
            var line;

            var tooltip = $('body').append('<div class="tooltip"></div>');
            tooltip = $('.tooltip');
            tooltip.attr('style', 'visibility:hidden');

            var that = this;
//            for( var i = 0, l = symbols.length; i < l; i++ ) {
            jQuery.eachAsync(symbols, { delay: 100, bulk: 0,
                loop: function(i, value)
                {
                var line = symbols[i];

//                for( var j = 0; j<line.length; j++ ) {
                    jQuery.eachAsync(line, { delay: 10, bulk: 0,
                        loop: function(j, value2)
                        {

//                    DRAW X AXIS
                    if (i==0) {
                        var date = that.data["x"][0][j];
                        if (that.display_time == "day") {
                            var text = dateFormat(date, "HH:00");
                        }
                        if (that.display_time == "month") {
                            var text = dateFormat(date, "dd.mm.");
                        }
                        if (that.display_time == "year") {
                            var text = dateFormat(date, "mm.yyyy");
                        }

                        var skip = 1;
                        if (that.width < 1100) {
                            skip = 2;
                        }
                        if (that.width < 500) {
                            skip = 3;
                        }
                        if (that.width < 350) {
                            skip = 4;
                        }
                        if (line.length <= 31) {
                            skip = 4;
                        }
                        if (line.length <= 24) {
                            skip = 3;
                        }
                        if (line.length <= 12) {
                            skip = 2;
                        }

                        if (j%skip == 0)
                            that.r["text"](symbols[i][j].attrs["cx"], y_axis+10, text).attr(that.txtattr);
                    }


                    symbols[i][j].attr({'r': 20});
                    var bgcolor = symbols[i][j].attr("fill");
                    symbols[i][j].attr({ fill: '#fff' , stroke: 'transparent', 'stroke-width': 1, 'opacity': '0' });

                    symbols[i][j].node.symbol = symbols[i][j];



                    var x = symbols[i][j].node.getBBox().x+(symbols[i][j].node.getBBox().width/2);
                    var y = symbols[i][j].node.getBBox().y+(symbols[i][j].node.getBBox().height/2);


                    var h = that.r.text( x,  y,  data["y"][i][j])
                    h.hide();
                    // inverse this.invertColor(this.txtattr["fill"])
                    chart.symbols.push(
                            hoverorect = that.r.roundedRectangle( x+10,  y-7,  h.getBBox().width+5, 15, 5, 5, 5, 5).attr({fill: '#333', 'stroke-width':0, 'opacity': 1.00})
                    );
                    hoverorect.hide();
                    var movex = h.getBBox().width/2+2;
                    chart.symbols.push(
                            hoverotext = that.r.text( x+movex+10,  y+7-7,  data["y"][i][j]).attr({fill: '#fff'})
                    );
                    hoverotext.hide();



                    var hover = that.r.set(), hovero, hoverotext, hoverorect;

                    chart.symbols.push(
                            hovero = that.r.circle( x,  y, 4 ).attr({ fill: bgcolor, stroke: 'transparent' })
                    );



                    hovero.hide();
                    symbols[i][j].node.hover = hovero;
                    symbols[i][j].node.hovertext = hoverotext;
                    symbols[i][j].node.hoverrect = hoverorect;

                    hovero.node.hover = hovero;
                    hovero.node.hovertext = hoverotext;
                    hovero.node.hoverrect = hoverorect;

                    var lock = false;
                    symbols[i][j].node.lock = hovero.node.lock = lock;

                    var over = function(e) {
                        this.hover.show();
                        this.hovertext.show();
                        this.hoverrect.show();
                    }
                    var out = function(e) {
                        this.hover.hide();
                        this.hovertext.hide();
                        this.hoverrect.hide();
                    }

                    hovero.node.onmouseover = over;
                    hovero.node.onmouseout = out;

                    symbols[i][j].node.onmouseover = over;
                    symbols[i][j].node.onmouseout = out;

                        }
                    })
                },
                end: function() {chart.labels.translate(that.width-chart.labels.getBBox().width,0);}
            });


        }





        if (this.resizable)
        {
            this.lastResizedWidth = $('#'+this.dataset).parent().width();
        }
    }

    this.drawPiechart = function() {

        this.typeChart = 'pie';


        if (this.width == -1)
            this.width = $('#'+this.dataset).parent().width()
                    -parseInt($('#'+this.dataset).parent().css("padding-left"))
                    -parseInt($('#'+this.dataset).css("padding-left"))
                    -parseInt($('#'+this.dataset).parent().css("padding-right"))
                    -parseInt($('#'+this.dataset).css("padding-right"))
                    -parseInt($('#'+this.dataset).css("margin-left"))
                    -parseInt($('#'+this.dataset).css("margin-right"));


        this.r = Raphael(this.dataset);

        // Object to array
        var data = JSON.parse(JSON.stringify(this.data["x"]));


        var chart = this.r.piechart(this.width, this.height, this.height-10, data,
                {
                    'strokewidth' : 0,
                    legend: this.data["legend"],
                    legendcolor: this.txtattr["fill"],
                    colors: this.colors
                });


        for( var i = 0; i < chart.labels.length; ++i ) {
            chart.labels[i][1].attr(this.txtattr);
            chart.labels[i].translate(10,0);
        }

        chart.hover(function () {
            this.sector.stop();
            this.sector.scale(1.1, 1.1, this.cx, this.cy);

            if (this.label) {
                this.label[0].stop();
                this.label[0].attr({ r: 7.5 });
                this.label[1].attr({ "font-weight": 800 });
            }
        }, function () {
            this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 500, "bounce");

            if (this.label) {
                this.label[0].animate({ r: 5 }, 500, "bounce");
                this.label[1].attr({ "font-weight": 400 });
            }
        });


        if (this.resizable)
        {
            this.lastResizedWidth = $('#'+this.dataset).parent().width();
        }

    }

    this.drawLine = function(startX, startY, endX, endY, raphael, opacity) {
        var start = {
            x: startX,
            y: startY
        };
        var end = {
            x: endX,
            y: endY
        };
        var getPath = function() {
            return "M" + start.x + " " + start.y + " L" + end.x + " " + end.y;
        };
        var redraw = function() {
            node.attr("path", getPath());
        }

        var node = raphael.path(getPath());
        // Fix to 1px line stroke-width
        node.attr('opacity', opacity).attr('stroke-width', 1);
        return node;
    };

    this.invertColor = function(hex) {

        var color = hex;
        var inverse = "#";
        var pieces = color.match(/\w{2}/g);

        for(var i in pieces) {
            inverse += ("0" + (255 - parseInt(pieces[i], 16)).toString(16)).slice(-2);
        }
        return inverse;

    }

}
