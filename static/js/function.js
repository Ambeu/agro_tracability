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






