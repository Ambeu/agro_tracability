const icon = L.icon({
  iconSize: [25, 41],
  iconAnchor: [10, 41],
  popupAnchor: [2, -40],
  iconUrl: "https://unpkg.com/leaflet@1.6/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.6/dist/images/marker-shadow.png"
});

Promise.all([
  fetch("http://127.0.0.1:8000/api/v1/map_parcelles/"),
]).then(async ([response1]) => {
  const responseData1 = await response1.json();
  const data1 = responseData1;
  const parcelles = L.featureGroup().addTo(map);

data1.forEach(({code, producteur, latitude, longitude, culture, certification, superficie, id  }) => {
    parcelles.addLayer(
      L.marker([latitude, longitude], { icon }).bindPopup(
        `
          <table class="table table-striped table-bordered">
            <thead style="align-items: center">
                <tr>           
                  <th scope="col" class="center">ID</th>
                  <th scope="col" class="center">INFORMATIONS</th>                  
                </tr>
            </thead>
            <tbody style="align-items: center">            
                <tr>
                    <th scope="col"><b>LOCALITE :</b></th>
                    <td class="text-uppercase"><strong>${producteur.localite}</strong></td>                    
                </tr>
                <tr>
                    <th scope="col"><b>PRODUCTEUR :</b></th>
                    <td class="text-uppercase"><strong>${producteur.code} - ${producteur.nom}</strong></td>                    
                </tr>
                <tr>
                    <th scope="col"><b>CODE PARCELLE :</b></th>
                    <td class="text-uppercase"><strong>${code}</strong></td>                    
                </tr>
                <tr>
                    <th scope="col"><b>COORDONNEES :</b></th>
                    <td class="text-uppercase">(${longitude},${latitude})</td>
                </tr>
                <tr>
                    <th scope="col"><b>CERTIFICATION : </b></th>
                    <td class="text-uppercase">${certification}</td>                    
                </tr>
                <tr>
                    <th scope="col"><b>CULTURE :</b></th>
                    <td class="text-uppercase">${culture}</td>                    
                </tr>
                <tr>
                    <th scope="col"><b>SUPERFICIE</b></th>
                    <td class="text-uppercase">${superficie} (Ha)</td>
                </tr>
                <tr>
                    <th scope="col"><b>ESPECES</b></th>
                    <td class="text-uppercase text-center">
                        <a class="btn btn-info" href="#" role="button">Afficher</a>
                        <a class="btn btn-success" href="#" role="button"><i class="glyphicon glyphicon-tree-deciduous"></i></a>
                    </td>
                </tr>
                <tr>
                    <th scope="col"><b>CONTOURS</b></th>
                    <td class="text-uppercase text-center">
                        <a class="btn btn-info" href="#" role="button">Afficher</a>
                        <a class="btn btn-success" href="#" role="button"><i class="glyphicon glyphicon-tree-deciduous"></i></a>
                    </td>
                </tr>
            </tbody>
          </table>    
        `
      )
    );
  });

  map.fitBounds(parcelles.getBounds());
});

//Initialisation de la Map
var map = L.map('map').setView([7.539989, -5.547080], 7);
map.zoomControl.setPosition('topright');

var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
 maxZoom: 22,
 attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors - @Copyright - Agro-Map CI'
}).addTo(map);

//map Climat
var climat = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
 maxZoom: 22,
 attribution: '@Copyright - Agro-Map CI - Map'
});


// Ajouter Popup de Marquage
var singleMarker = L.marker([5.349390, -4.017050])
 .bindPopup("Bienvenus en .<br> Côte d'Ivoire.")
 .openPopup();

// Ajouter Calcul de Distance
L.control.scale().addTo(map);

//Afficher les Coordonnées sur la carte
map.on('mousemove', function (e) {
 //console.log(e);
 $('.coordinates').html(`lat: ${e.latlng.lat}, lng: ${e.latlng.lng}`)
});


//Charger les Villes sur la Carte
//L.geoJSON(data).addTo(map);
var marker = L.markerClusterGroup();
marker.addTo(map);

// Laeflet Layer control
var baseMaps = {
 'ROUTE': osm,
 'COUVERT FORESTIER': climat,
}

var markers = L.markerClusterGroup({
	spiderfyShapePositions: function(count, centerPt) {
        var distanceFromCenter = 35,
            markerDistance = 45,
            lineLength = markerDistance * (count - 1),
            lineStart = centerPt.y - lineLength / 2,
            res = [],
            i;

        res.length = count;

        for (i = count - 1; i >= 0; i--) {
            res[i] = new Point(centerPt.x + distanceFromCenter, lineStart + markerDistance * i);
        }

        return res;
    }
});

var overLayMaps = {
 // 'VILLES' : marker,
 // 'ABIDJAN': singleMarker
}
L.control.layers(baseMaps, overLayMaps, {collapse :false, position: 'topleft'}).addTo(map);




