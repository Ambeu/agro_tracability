function edit_btn(id,url) {
    
    event.preventDefault();
    var csrfToken = $('[name="csrfmiddlewaretoken"]').val();

    $.ajax({
        url: url,
        method: "GET",
        data:{
          'id':id,
          //csrfmiddlewaretoken: csrfToken,
        },

        dataType : "json",
        success:function(response){
         
           $('#DetailPlantingModal').html(response.templateStr)
            $('#DetailPlantingModal').modal('show')
           
        }
    });
}



function delete_semence(url) {
    event.preventDefault();
        swal({
				title: "Voulez vous vraiment supprimer cet enregistrement ?",
				icon: "warning",
				buttons: true,
				dangerMode: true,
			})
				.then((willDelete) => {
				if (willDelete) {
					$.get(url , { });//code : code, agence : agence
					swal("supprimer avec succès", {
						icon: "success",
					})
                    .then((ok) => {
                        if(ok) {
                            location.reload();
                        }
                    });
                    
				} else {

		}
		});

}

function edit_monitoring(url) {
    event.preventDefault();
    var csrfToken = $('[name="csrfmiddlewaretoken"]').val();

    $.ajax({
        url: url,
        method: "GET",

        dataType : "json",
        success:function(response){
         //console.log(response.templateStr);
           $('#MonitoringModal').html(response.templateStr)
           $('#MonitoringModal').modal('show')
           
        }
    });
}

function reload() {
    location.reload();
}



function edit_prod(url) {

    event.preventDefault();
    var csrfToken = $('[name="csrfmiddlewaretoken"]').val();

    $.ajax({
        url: url,
        method: "GET",
        dataType : "json",
        success:function(response){
         //console.log(response.templateStr);
           $('#ProducteursModal').html(response.templateStr)
           $('#ProducteursModal').modal('show')
           
        }
    });

}

function edit_formatoin(url) {
    event.preventDefault();
    var csrfToken = $('[name="csrfmiddlewaretoken"]').val();

    $.ajax({
        url: url,
        method: "GET",
        dataType : "json",
        success:function(response){
         //console.log(response.templateStr);
           $('#FormationModal').html(response.templateStr)
           $('#FormationModal').modal('show')
           
        }
    });
}






