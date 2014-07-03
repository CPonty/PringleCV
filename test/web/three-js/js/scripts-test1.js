var container, stats, camera, scene, renderer;
var WIDTH, HEIGHT, VIEW_ANGLE, ASPECT, NEAR, FAR;
var cylinder, plane, light;

var mouseX = 0;
var mouseY = 0;
var mouseXOnMouseDown = 0;
var mouseYOnMouseDown = 0;

var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------

threejsInit = function() {

	console.log("we run!");

	/* SETUP */
	// set the scene size
	//WIDTH = 640,
	//HEIGHT = 480,
	WIDTH = window.innerWidth, 
	HEIGHT = window.innerHeight,
	VIEW_ANGLE = 60,
	ASPECT = WIDTH / HEIGHT,
 	NEAR = 0.1,
 	FAR = 10000;
	// get the DOM element to attach to
	// - assume we've got jQuery to hand
	$container = $('#container3d');
	// create a WebGL renderer, camera
	// and a scene
	renderer = new THREE.WebGLRenderer();
	camera = new THREE.PerspectiveCamera(
	    VIEW_ANGLE, ASPECT, NEAR, FAR);
	scene = new THREE.Scene();
	// add the camera to the scene
	scene.add(camera);
	camera.position.z = 300;
	camera.position.y = 150;
	camera.rotation.x -= 15 * (Math.PI/ 180)
	// start the renderer & attach its DOM element
	renderer.setSize(WIDTH, HEIGHT);
	renderer.setClearColor( 0xe0e0e0 );
	$container.append(renderer.domElement);


	/* CYLINDER */
	var radius = 50,
		height = 75,
	    radialSegments = 32,
	    heightSegments = 1,
	    openEnded = false;
	// create the 'material'
	var cylinderMaterial = new THREE.MeshPhongMaterial(
	    {
	    	color: 0xFF0000
	    });
	var cylinder = new THREE.Mesh(
		new THREE.CylinderGeometry(
	    	radius, radius, height, radialSegments, heightSegments, openEnded),
	  cylinderMaterial);
	// add the object to the scene
	scene.add(cylinder);
	cylinder.position.set(0,height,0)


	/* PLANE */


/*
// create the sphere's material
var sphereMaterial =
  new THREE.MeshLambertMaterial(
    {
      color: 0xFF0000
    });


// set up the sphere vars
var radius = 50,
    segments = 16,
    rings = 16;

// create a new mesh with
// sphere geometry - we will cover
// the sphereMaterial next!
var sphere = new THREE.Mesh(

  new THREE.SphereGeometry(
    radius,
    segments,
    rings),

  sphereMaterial);

// add the sphere to the scene
scene.add(sphere);
*/

/*
// create a point light
var pointLight =
  new THREE.PointLight(0xFFFFFF);

// set its position
pointLight.position.x = 10;
pointLight.position.y = 50;
pointLight.position.z = 130;

// add to the scene
scene.add(pointLight);
*/

var pointLight = new THREE.PointLight(0xFFFFFF);
pointLight.position.set(10,50,130);
scene.add(pointLight);
light = pointLight;


hemiLight = new THREE.HemisphereLight( 0xffffff, 0xffffff, 0.6 ); //0.6
hemiLight.color.setHSL( 0.0, 1, 0.6 );
hemiLight.groundColor.setHSL( 0.095, 1, 0.75 );
hemiLight.position.set( 0, 500, 0 );
scene.add( hemiLight );


var groundGeo = new THREE.PlaneGeometry( 1000, 1000 );
var groundMat = new THREE.MeshPhongMaterial( { ambient: 0xffffff, color: 0xffffff, specular: 0x7f7f7f } );
groundMat.color.setHSL( 0.25, 1, 0.6 );

var ground = new THREE.Mesh( groundGeo, groundMat );
ground.rotation.x = -Math.PI/2;
ground.position.y = 0; /*-33*/
scene.add( ground );

ground.receiveShadow = true;


/*
dirLight = new THREE.DirectionalLight( 0xffffff, 1 );
dirLight.color.setHSL( 0.1, 1, 0.95 );
dirLight.position.set( -1, 1.75, 1 );
dirLight.position.multiplyScalar( 50 );
scene.add( dirLight );


dirLight.castShadow = true;

dirLight.shadowMapWidth = 2048;
dirLight.shadowMapHeight = 2048;

var d = 50;

dirLight.shadowCameraLeft = -d;
dirLight.shadowCameraRight = d;
dirLight.shadowCameraTop = d;
dirLight.shadowCameraBottom = -d;

dirLight.shadowCameraFar = 3500;
dirLight.shadowBias = -0.0001;
dirLight.shadowDarkness = 0.35;
dirLight.shadowCameraVisible = true;
*/




	renderer.render(scene, camera);

	document.addEventListener( 'mousemove', onDocumentMouseMove, false );

	stats = new Stats();
	stats.domElement.style.position = 'absolute';
	stats.domElement.style.top = '0px';
	$container.append( stats.domElement );

	animate();

	console.log("we done!");

}

function onDocumentMouseMove( event ) {
	mouseX = event.clientX;
	mouseY = event.clientY;
}

function animate() {
	requestAnimationFrame( animate );
	renderer.render( scene, camera );
	stats.update();

	//camera.rotation.x = (mouseY - windowHalfY)/3/180;
	//camera.rotation.y = (mouseX - windowHalfX)/3/180;
	//camera.rotation.y = /*10+*/mouseY/3*ASPECT;
	camera.position.x = (mouseX - windowHalfX)/3;
	camera.position.y = /*10+*/mouseY/3*ASPECT;
	light.position.set(camera.position.x, camera.position.y, camera.position.z);
	//light.position.set(-50, camera.position.y-50, 50);
	//light.position.set( -1, 1.75, 1 );
	//light.position.multiplyScalar( 50 );
}

// -----------------------------------------------------------------------------
//  Runtime Execution
// -----------------------------------------------------------------------------

/* Execute after document loads
*/

$(document).ready(threejsInit);
