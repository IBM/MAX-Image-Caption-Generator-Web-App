// javascript code for MAX webapp

function add_thumbnails(data) {
    var img_object = "<img src='" + data["file_name"] + "' alt='" + data["caption"] + "' title='" + data["caption"] + "' >";
    $("#thumbnails").prepend(img_object);
}

function get_words() {
    var all_words = [];
    $('#thumbnails').children('img').each(function () {
        capt_text = $(this).attr('title');
        word_arr = capt_text.split(' ');
        $.merge(all_words, word_arr);
    });
    return all_words;
}

function get_word_entries() {
    var words = get_words();

    var word_count = {};

    if (words.length == 1){
        word_count[words[0]] = 1;
    } else {
        words.forEach(function (word) {
            var word = word.toLowerCase();
            if (word != "" && word.length > 1) {
                if (word_count[word]) {
                    word_count[word]++;
                } else {
                    word_count[word] = 1;
                }
            }
        });
    }

    return d3.entries(word_count);
}

function word_cloud() {
    $('#word-cloud').empty();

    var fill = d3.scaleOrdinal(d3.schemeCategory10);

    var width = 800;
    var height = 500;

    var word_entries = get_word_entries();

    var xScale = d3.scaleLinear()
        .domain([0, d3.max(word_entries, function(d) {
            return d.value;
            })
        ])
        .range([10,100]).clamp(true);

    var layout = d3.layout.cloud()
        .size([width, height])
        .words(word_entries)
        .text(function(d) { return d.key; })
        .rotate(function() { return ~~(Math.random() * 2) * 0; })
        .font("Impact")
        .fontSize(function(d) { return xScale(+d.value); })
        .on("end", draw);

    layout.start();

    function draw(words) {
        d3.select('#word-cloud').append("svg")
                .attr("width", width)
                .attr("height", height)
            .append("g")
                .attr("transform", "translate(" + [width >> 1, height >> 1] + ")")
            .selectAll("text")
                .data(words)
            .enter().append("text")
                .style("font-size", function(d) { return xScale(+d.value) + "px"; })
                .style("font-family", "Impact")
                .style("fill", function(d, i) { return fill(i); })
                .attr("text-anchor", "middle")
                .attr("transform", function(d) {
                    return "translate(" + [d.x, d.y] + ")rotate(" + d.rotate + ")";
                })
                .text(function(d) { return d.key; });
    }
}

$(function() {
    word_cloud();

    // Image upload form submit functionality
    $('#img-upload').on('submit', function(data){
        // Stop form from submitting normally
        event.preventDefault();

        // Get form data
        var form = event.target;
        var data = new FormData(form);

        // perform file upload
        $.ajax({
            url: "/upload",
            method: "post",
            processData: false,
            contentType: false,
            data: data,
            processData: false,
            dataType: "json",
            success: function(data) {
                add_thumbnails(data);
                word_cloud();
            }
        })
    })

});
