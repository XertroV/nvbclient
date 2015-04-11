initialize_network = function(){
    $.get('/initialize_network', function(r){
        $("#init_network").html('Success, txid: ' + r);
    });
}