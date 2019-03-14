pyloco.loadJavascript("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/highlight.min.js");
pyloco.loadJavascript("https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.15.6/languages/fortran.min.js");
pyloco.loadJavascript("https://cdnjs.cloudflare.com/ajax/libs/d3/4.13.0/d3.min.js");

hljs.initHighlightingOnLoad();

var casenumber = null, totalsize = null, completed = 0
var refsrc = null, refout = null, refmeasure = null
var maxetime = 100
var algorithm = "Undefined", algoparams="Not specified"

const measures = [
];

function closeTab () {
    window.close();
}

iconpoweroff = "<img alt='Close this tab' onclick='closeTab()' src='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABoAAAAaCAYAAACpSkzOAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAIWSURBVEhLtZZNiE5RGIA/f1kojLBAjQVl4a802ZHVlCSlpjSllLJSLLGxkSWiqZEFC4XUJH8rNhZTE2UxTLNiKwqzmkF4ntu843y3+/fNN556Ft973u997z33nHNvq0PO4Fd8i9sM/A/W4i/8M+sD7IrFeBQPZb/+sQOjib7ClBV4HLdnv2pYjg8xivVjUNfoNhqfxgEDZSzBR5gWO4hBXaN7GGNO8WEs5BymhS5jSl2jdfgOY/w7bsY2tuAMRtIlzFPXSNbje4ycZ9jGHYzBUXQa8zRpJHswXZ37MMNbTu9mJxbRtJFcx8i7a0BckhH0bsropJEXG3nfcBm2hmYDetZACZ00kgmM3N0GXiaBdDnncSNGntY1GsHIzfbV6ySwy0AJ7vwpjFxnooprGLmnDLxIAn0GKjiAz3EY1xio4CZG3WMGXBUROGJggXiKUXe/gYtJ4IqBBcBV5mqz5m/cgNkGi0YfcCl2i4sqaroGMhbhR4yBk9gN1hvDqHce57B4DHzCTThfTmPU+oKrcQ6naxwj4Q32YKf4/krPucIDwJ3v0R5Jk9j0u8Dp8k5+Yvz/MRYdzhm+rH5gJHvY3sCtWISrywefPhP142UVVuKx/hnTP6rvmft4Fd2w7hO/iPJ5T3AlNqIXLeoeyBcq04vzmZROVxV78Ra6EouKeyHukwvYtrrmi1fp6e3zOIGD6BRvxAa0Wn8BJ7HbFzTgSOMAAAAASUVORK5CYII='>";

var bodyHtml = "" +
"<h1><center>DG Kernel Automatic Performance Optimization(Prototype)</center></h1>" +
"<div><br></div>" +
"<div id='searchspace'></div>" +
"<div><br></div>" +
"<div id='status' class='box'>Experiment Status :" + iconpoweroff + "</div>" +
"<div><br></div>" +
"<div class='wrapper'>" +
"  <div class='box'>Current Optimization<br><br>" +
"    <div id='options'></div>" +
"    <pre><code id='sourcefile' class='Fortran'></code></pre>" +
"  </div>" +
"  <div class='handler'></div>" +
"  <div class='box'>Current Mesurement<br><svg/></div>" +
"</div>" +
"<div><br></div>" +
"<div class='box'>Selecting Next Optimization<br><br><div id='nextcase'></div></div>"


document.body.innerHTML = bodyHtml;

var handler = document.querySelector('.handler');
var wrapper = handler.closest('.wrapper');
var boxA = wrapper.querySelector('.box');
var isHandlerDragging = false;

document.addEventListener('mousedown', function(e) {
  // If mousedown event is fired from .handler, toggle flag to true
  if (e.target === handler) {
    isHandlerDragging = true;
  }
});

document.addEventListener('mousemove', function(e) {
  // Don't do anything if dragging flag is false
  if (!isHandlerDragging) {
    return false;
  }

  // Get offset
  var containerOffsetLeft = wrapper.offsetLeft;

  // Get x-coordinate of pointer relative to container
  var pointerRelativeXpos = e.clientX - containerOffsetLeft;
  
  // Arbitrary minimum width set on box A, otherwise its inner content will collapse to width of 0
  var boxAminWidth = 60;

  // Resize box A
  // * 8px is the left/right spacing between .handler and its inner pseudo-element
  // * Set flex-grow to 0 to prevent it from growing
  boxA.style.width = (Math.max(boxAminWidth, pointerRelativeXpos - 8)) + 'px';
  boxA.style.flexGrow = 0;
});

document.addEventListener('mouseup', function(e) {
  // Turn off dragging flag when user mouse is up
  isHandlerDragging = false;
});


function updateStatus () {
    var status = document.getElementById("status");
    status.innerHTML = "Experiment Status :  current case = " + casenumber +
        " (completed " + completed + " / " + totalsize + ")" + iconpoweroff;
}

function updateNextcase () {
    var nextcase = document.getElementById("nextcase");
    nextcase.innerHTML = "Case selection algorithm : " + algorithm +
        "<br>Algorithm parameters : " + algoparams;
}

pyloco.onOpen(function openHandler (evt) {
    window.console.log(evt);
});

pyloco.onClose(function closeHandler (evt) {
    window.console.log(evt);
});

pyloco.onMessage("dgkernel", "searchspace", function messageHandler (msgId, ts, msg) {
    var sspace = document.getElementById("searchspace");
/*
    sspace.innerHTML = "Search-space : " +
        "total size = " + msg[0] +
        ", no. of code transformations = " + msg[1] +
        ", no. of env. variable selections = " + msg[2] + "<br>" +
        "        " + 
        "no. of compiler option selections  = " + msg[3] +
        ", no. of link option selections = " + msg[4] +
        ", no. of run configurations = " + msg[5]
*/

    totalsize = msg[0]

    sspace.innerHTML = "<font size='3' face='Verdana' >" +
    "<table style='width:100%'>" +
    "  <tr>" +
    "      <th>total search-space size</th>" +
    "      <th>code transformations</th> " +
    "      <th>env. variable selections</th>" +
    "      <th>compiler option selections</th>" +
    "      <th>linker option selections</th>" +
    "      <th>run configurations</th>" +
    "    </tr>" +
    "    <tr>" +
    "      <td>" + msg[0] + "</td>" +
    "      <td>" + msg[1] + "</td>" +
    "      <td>" + msg[2] + "</td>" +
    "      <td>" + msg[3] + "</td>" +
    "      <td>" + msg[4] + "</td>" +
    "      <td>" + msg[5] + "</td>" +
    "    </tr>" +
    "  </table>" +
    "  </font>"

    updateStatus();
});

pyloco.onMessage("dgkernel", "refsrc", function messageHandler (msgId, ts, msg) {
    refsrc = msg;
});

pyloco.onMessage("dgkernel", "refout", function messageHandler (msgId, ts, msg) {
    // result, stdout, stderr
    refout = msg;
});

pyloco.onMessage("dgkernel", "refmeasure", function messageHandler (msgId, ts, msg) {
    // [(maxflx, minfly), etime]
    refmeasure = msg;
    maxetime = msg[1];
});

pyloco.onMessage("dgkernel", "nextcase", function messageHandler (msgId, ts, msg) {

    casenumber = msg["params"]["nextindex"];
    updateStatus();
    algorithm = msg["algorithm"];
    algoparams = "";

    for (var param in msg["params"]) {
        if (msg["params"].hasOwnProperty(param)) {
            algoparams = algoparams.concat(param + " = " + msg["params"][param]);
        }
    }
    updateNextcase();

});

pyloco.onMessage("dgkernel", "src", function messageHandler (msgId, ts, msg) {
    var srcfile = document.getElementById("sourcefile");
    for (var path in msg) {
        if (msg.hasOwnProperty(path)) {
            srcfile.innerHTML = msg[path];
        }
    }
    //window.console.log(srcs);
});

pyloco.onMessage("dgkernel", "buildopts", function messageHandler (msgId, ts, msg) {
    var opts = document.getElementById("options");
    opts.innerHTML = msg;
    //window.console.log(srcs);
});

pyloco.onMessage("dgkernel", "out", function messageHandler (msgId, ts, msg) {
    measures.push({result: msg[0]});
});

pyloco.onMessage("dgkernel", "measure", function messageHandler (msgId, ts, msg) {
    var cur = measures[measures.length - 1];

    cur.caseid = casenumber.toString();

    if (cur.result == null) {
        cur.etime = 0;
        cur.color = "red";
    } else if (msg[0][0] == refmeasure[0][0] && msg[0][1] == refmeasure[0][1]) {
        cur.etime = msg[1][0];
        cur.color = "blue";
    } else {
        cur.etime = msg[1][0];
        cur.color = "red";
    }

    if (msg[1][0] > maxetime) {
        maxetime = msg[1][0];
    }

    completed = completed + 1;
    updateStatus();
    window.console.log(measure)
    updateBarChart();

    //window.console.log(measures);
});

pyloco.onError(function errorHandler (evt) {
    window.console.log(evt);
});

// from: https://blog.risingstack.com/d3-js-tutorial-bar-charts-with-javascript/
/*
  {
    caseid: 'Rust',
    etime: 78.9,
    color: 'red'
  },
*/


function updateBarChart() {

    d3.selectAll("svg > *").remove();

    const svg = d3.select('svg');
    //const svgContainer = d3.select('#container');


    const margin = 80;
    const width = 1000 - 2 * margin;
    const height = 600 - 2 * margin;

    svg
      .append('text')
      .attr('class', 'label')
      .attr('x', -(height / 2) - margin)
      .attr('y', margin / 2.4)
      .attr('transform', 'rotate(-90)')
      .attr('text-anchor', 'middle')
      .text('Elapsed time (sec.)')

    svg.append('text')
      .attr('class', 'label')
      .attr('x', width / 2 + margin)
      .attr('y', height + margin * 1.7)
      .attr('text-anchor', 'middle')
      .text('Case number')

    svg.append('text')
      .attr('class', 'title')
      .attr('x', width / 2 + margin)
      .attr('y', 40)
      .attr('text-anchor', 'middle')
      .text('DG Kernel Optimizations')

    svg.append('text')
      .attr('class', 'source')
      .attr('x', width - margin / 2)
      .attr('y', height + margin * 1.7)
      .attr('text-anchor', 'start')
      .text('')

    const chart = svg.append('g')
      .attr('transform', `translate(${margin}, ${margin})`);

    const xScale = d3.scaleBand()
      .range([0, width])
      .domain(measures.map((s) => s.caseid))
      .padding(0.4)

    const yScale = d3.scaleLinear()
      .range([height, 0])
      .domain([0, maxetime]);

    // vertical grid lines
     const makeXLines = () => d3.axisBottom()
       .scale(xScale)

    const makeYLines = () => d3.axisLeft()
      .scale(yScale)

    chart.append('g')
      .attr('transform', `translate(0, ${height})`)
      .call(d3.axisBottom(xScale));

    chart.append('g')
      .call(d3.axisLeft(yScale));

    // vertical grid lines
     chart.append('g')
       .attr('class', 'grid')
       .attr('transform', `translate(0, ${height})`)
       .call(makeXLines()
         .tickSize(-height, 0, 0)
         .tickFormat('')
       )

    chart.append('g')
      .attr('class', 'grid')
      .call(makeYLines()
        .tickSize(-width, 0, 0)
        .tickFormat('')
      )

    const barGroups = chart.selectAll()
      .data(measures)
      .enter()
      .append('g')

    barGroups
      .append('rect')
      .attr('class', 'bar')
      .attr('x', (g) => xScale(g.caseid))
      .attr('y', (g) => yScale(g.etime))
      .attr('fill', (g) => g.color)
      .attr('height', (g) => height - yScale(g.etime))
      .attr('width', xScale.bandwidth())
      .on('mouseenter', function (actual, i) {
        d3.selectAll('.etime')
          .attr('opacity', 0)

        d3.select(this)
          .transition()
          .duration(300)
          .attr('opacity', 0.6)
          .attr('x', (a) => xScale(a.caseid) - 5)
          .attr('width', xScale.bandwidth() + 10)

        //const y = yScale(actual.etime)
        const y = yScale(refmeasure[1])

        line = chart.append('line')
          .attr('id', 'limit')
          .attr('x1', 0)
          .attr('y1', y)
          .attr('x2', width)
          .attr('y2', y)

        barGroups.append('text')
          .attr('class', 'divergence')
          .attr('x', (a) => xScale(a.caseid) + xScale.bandwidth() / 2)
          .attr('y', (a) => yScale(a.etime) + 30)
          .attr('fill', 'white')
          .attr('text-anchor', 'middle')
          .text((a, idx) => {
              //return a.etime.toFixed(2).toString();
              return idx == i ? a.etime.toFixed(2).toString() : '';
          })

      })
      .on('mouseleave', function () {
        d3.selectAll('.etime')
          .attr('opacity', 1)

        d3.select(this)
          .transition()
          .duration(300)
          .attr('opacity', 1)
          .attr('x', (a) => xScale(a.caseid))
          .attr('width', xScale.bandwidth())

        chart.selectAll('#limit').remove()
        chart.selectAll('.divergence').remove()
      })

    /*
    barGroups 
      .append('text')
      .attr('class', 'etime')
      .attr('x', (a) => xScale(a.caseid) + xScale.bandwidth() / 2)
      .attr('y', (a) => yScale(a.etime) + 30)
      .attr('text-anchor', 'middle')
      .text((a) => `${a.etime}%`)
    */
}

updateBarChart();
