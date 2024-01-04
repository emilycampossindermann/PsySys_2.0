window.downloadCytoscapeImage = function() {
    var cytoscapeElement = document.getElementById('my-mental-health-map'); // Replace with your Cytoscape element ID
    html2canvas(cytoscapeElement).then(function(canvas) {
        var link = document.createElement('a');
        link.download = 'cytoscape-graph.png';
        link.href = canvas.toDataURL('image/png').replace('image/png', 'image/octet-stream');
        link.click();
    });
};
