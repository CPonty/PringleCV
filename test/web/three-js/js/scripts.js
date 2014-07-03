var container, controls, stats, camera, scene, renderer;
var WIDTH, HEIGHT, VIEW_ANGLE, ASPECT, NEAR, FAR;
var cylinder, plane, lights, lightspheres, shadow;
var panOffset, panDir, doPanMove;
var canOffset, canDir, doCanMove;
var cylinder;

var SCROLL_SCALER = 0.25;
var PAN_SPEED = 10;
var CAN_SPEED = 15;
var TURBO = 1;
var MAX_FPS = 30;
var frameDelay = 1000 / MAX_FPS;
var frameTime = Date.now();

var GRID_LARGE = 500;
var DIST_LIGHTS = 0.8*GRID_LARGE;
var MAX_DISTANCE = 2*GRID_LARGE;

var AXIS_Y = new THREE.Vector3( 0, 1, 0 );
var AXIS_Z = new THREE.Vector3( 0, 0, -1 );
var MATRIX_ROTATE_90Y = new THREE.Matrix4().makeRotationAxis( AXIS_Y, Math.PI / 2 );
var MATRIX_ROTATE_90Z = new THREE.Matrix4().makeRotationAxis( AXIS_Z, Math.PI / 2 );

var paused = false;
var pauseDiv = $("#pauseDiv");

var windowHalfX = window.innerWidth / 2;
var windowHalfY = window.innerHeight / 2;
var mouseX = windowHalfX;
var mouseY = windowHalfY;
var mouseXOnMouseDown = 0;
var mouseYOnMouseDown = 0;

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------

threejsInit = function() {

	if ( ! Detector.webgl ) Detector.addGetWebGLMessage();

	console.log("we run!");

	/* SETUP */
	// set the scene size
	//WIDTH = 640,
	//HEIGHT = 480,
	WIDTH = window.innerWidth, 
	HEIGHT = window.innerHeight,
	VIEW_ANGLE = 50,
	ASPECT = WIDTH / HEIGHT,
 	NEAR = 0.1,
 	FAR = 10000;
	// get the DOM element to attach to
	// - assume we've got jQuery to hand
	$container = $('#container3d');
	// create a WebGL renderer, camera,
	// scene, controls...
	renderer = new THREE.WebGLRenderer();
	camera = new THREE.PerspectiveCamera(
	    VIEW_ANGLE, ASPECT, NEAR, FAR);
	scene = new THREE.Scene();
	// add the camera to the scene
	scene.add(camera);
	camera.position.set(0, GRID_LARGE/4, -GRID_LARGE*1.5);
	//camera.position.z = 300;
	//camera.position.y = windowHalfY/6*ASPECT;
	//camera.position.x = 0;
	camera.rotation.x -= 15 * (Math.PI/ 180)
	// start the renderer & attach its DOM element
	renderer.setSize(WIDTH, HEIGHT);
	renderer.setClearColor( 0xe0e0e0 );
	$container.append(renderer.domElement);
	console.log(camera);
	console.log(renderer.domElement);
	//controls = new THREE.TrackballControls(camera, renderer.domElement);

	/* CONTROLS */
	//controls = new THREE.TrackballControls( camera , container );
	//controls = new THREE.TrackballControls( camera );
	controls = new THREE.OrbitControls( camera, renderer.domElement );
	//controls = new THREE.OrbitControls( camera );
	// disable arrow keys' 3d movement - don't like it!
	controls.rotateSpeed = 0.3;
	controls.noPan = false; // don't do this one - it disables click-drag
	controls.noKeys = true;
	//renderer.domElement.removeEventListener( 'keydown', controls.onKeyDown, false );
	// disable scroll-zoom
	controls.noZoom = true;
	//renderer.domElement.removeEventListener( 'mosewheel', controls.onMouseWheel, false );
	//renderer.domElement.removeEventListener( 'DOMMouseScroll', controls.onMouseWheel, false );
	controls.zoomSpeed = 0.5;
	//controls.target = new THREE.Vector3( GRID_LARGE/2, 0, 0 );;
	controls.target = new THREE.Vector3( 
		camera.position.x, camera.position.y-0.25, camera.position.z+1 );;
	panOffset = new THREE.Vector3(0,0,0);
	panDir = new THREE.Vector3(0,0,0);
	doPanMove = false;
	/*
	controls.rotateSpeed = 1.0;
	controls.zoomSpeed = 1.2;
	controls.panSpeed = 0.8;

	controls.noZoom = false;
	controls.noPan = false;

	controls.staticMoving = true;
	controls.dynamicDampingFactor = 0.3;

	controls.keys = [ 65, 83, 68 ];
	*/
	controls.addEventListener( 'change', render );

	/* CYLINDER */
	var radius = 40,
		height = 80,
	    radialSegments = 32,
	    heightSegments = 1,
	    openEnded = false;
	// create the 'material'
	var cylinderMaterial = new THREE.MeshPhongMaterial( { color: 0xCC0000 } );
	var cylinderGeometry = new THREE.CylinderGeometry(
	    	radius, radius, height, radialSegments, heightSegments, openEnded);
	cylinder = new THREE.Mesh( cylinderGeometry, cylinderMaterial );
	// add the object to the scene
	scene.add(cylinder);
	cylinder.position.set(0,height/2,0)

	canOffset = new THREE.Vector3(0,0,0);
	canDir = new THREE.Vector3(0,0,0);
	doCanMove = false;


var circleMaterial = new THREE.MeshBasicMaterial( { color: 0x7f7f7f } ); //LineBasicMaterial
var circleGeometry = new THREE.CircleGeometry( radius, radialSegments );
// Remove center vertex
//geometry.vertices.shift();
shadow = new THREE.Mesh( circleGeometry, circleMaterial ); //Lines
shadow.rotation.x = -90 * Math.PI/180;
scene.add( shadow );
shadow.position.set(0,0,0);
shadow.renderDepth = 0;


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

lights = [];
lightspheres = [];
lightx = [-1,-1,1,1];
lightz = [-1,1,1,-1];
for (var i=0; i<4; i++) {
	var pointLight = new THREE.PointLight(0xFFFFFF, 1.25, GRID_LARGE*2);
	pointLight.position.set(lightx[i]*DIST_LIGHTS, DIST_LIGHTS/2, lightz[i]*DIST_LIGHTS);
	scene.add(pointLight);
	lights.push(pointLight);

	var sphereMaterial =
	  new THREE.MeshBasicMaterial({color: 0xFFFFFF});
	var sphereGeometry = new THREE.SphereGeometry(25,16,16); //radius, segments, rings
	var sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
	sphere.position.set(lightx[i]*DIST_LIGHTS, DIST_LIGHTS/2, lightz[i]*DIST_LIGHTS);
	scene.add(sphere);
	lightspheres.push(sphere);
};
//camlight = new THREE.PointLight(0xFFFFFF, 1, 1000);
//camlight.position.set(0,0,0);
//scene.add(camlight);
//lights = pointLight;


hemiLight = new THREE.HemisphereLight( 0xffffff, 0xffffff, 0.6 ); //0.6
hemiLight.color.setHSL( 0.0, 1, 0.6 );
hemiLight.groundColor.setHSL( 0.095, 1, 0.75 );
hemiLight.position.set( 0, 5000, 0 );
scene.add( hemiLight );



for ( var j=0; j<2; j++) {
	var groundGeo = new THREE.Geometry();
	groundGeo.vertices.push(new THREE.Vector3( -GRID_LARGE, j*GRID_LARGE, 0 ) );
	groundGeo.vertices.push(new THREE.Vector3(  GRID_LARGE, j*GRID_LARGE, 0 ) );

	var linesMaterial = new THREE.LineBasicMaterial( { color: 0x7f7f7f, opacity: .2, linewidth: .1 } );

	for ( var i=0; i<=(GRID_LARGE/25); i++ ) {

	    var line = new THREE.Line( groundGeo, linesMaterial );
	    line.position.z = ( i * 50 ) - GRID_LARGE;
	    scene.add( line );

	    var line = new THREE.Line( groundGeo, linesMaterial );
	    line.position.x = ( i * 50 ) - GRID_LARGE;
	    line.rotation.y = 90 * Math.PI / 180;
	    scene.add( line );
	}
}

/*
var groundGeo = new THREE.PlaneGeometry( 1000, 1000 );
var groundMat = new THREE.MeshPhongMaterial( { ambient: 0xffffff, color: 0xffffff, specular: 0x7f7f7f } );
groundMat.color.setHSL( 0.25, 1, 0.6 );

var ground = new THREE.Mesh( groundGeo, groundMat );
ground.rotation.x = -Math.PI/2;
ground.position.y = 0; //-33
scene.add( ground );

ground.receiveShadow = true;
*/


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
	document.addEventListener( 'mousewheel', onDocumentScroll, false );
	document.addEventListener( 'DOMMouseScroll', onDocumentScroll, false );
	window.addEventListener( 'resize', onWindowResize, false );

	stats = new Stats();
	stats.domElement.style.position = 'absolute';
	stats.domElement.style.top = '0px';
	$container.append( stats.domElement );

	animate();

	console.log("we done!");

}

function render() {
	renderer.render( scene, camera );
	stats.update();
	camera.updateProjectionMatrix();
}

function onDocumentMouseMove( event ) {
	mouseX = event.clientX;
	mouseY = event.clientY;
}

function onDocumentScroll( event ) {
	var scrollDist = 0;
	if ( event.wheelDelta ) { 		// WebKit / Opera / Explorer 9
		scrollDist = event.wheelDelta;
	} else if ( event.detail ) { 	// Firefox
		scrollDist = -event.detail;
	}
	controls.target.y += scrollDist*SCROLL_SCALER;
	camera.position.y += scrollDist*SCROLL_SCALER;
		/*
			var delta = 0;

		if ( event.wheelDelta ) { // WebKit / Opera / Explorer 9

			delta = event.wheelDelta;

		} else if ( event.detail ) { // Firefox

			delta = - event.detail;

		}
	*/
}

function onWindowResize() {
	camera.aspect = window.innerWidth / window.innerHeight;
	camera.updateProjectionMatrix();
	renderer.setSize( window.innerWidth, window.innerHeight );
	controls.handleResize();

	WIDTH = window.innerWidth;
	HEIGHT = window.innerHeight;
	ASPECT = WIDTH / HEIGHT;
	windowHalfX = WIDTH / 2;
	windowHalfY = HEIGHT / 2;
	mouseX = windowHalfX;
	mouseY = windowHalfY;
}

function panVectorGen() {
	var te = controls.object.matrix.elements;
	var panVectX = new THREE.Vector3(te[0], te[1], te[2]);
	var panVectZ = panVectX.clone();
	var panVectY = new THREE.Vector3(te[4], te[5], te[6]);
	panVectZ.applyMatrix4( MATRIX_ROTATE_90Y );
	//panY.applyMatrix4( MATRIX_ROTATE_90Z );

	panOffset.set(0,0,0);
	panOffset.add( new THREE.Vector3( panDir.x*panVectX.x, 0, panDir.x*panVectX.z ) );
	panOffset.add( new THREE.Vector3( 0, panDir.y*panVectY.y, 0 ) );
	panOffset.add( new THREE.Vector3( panDir.z*panVectZ.x, 0, panDir.z*panVectZ.z ) );
	//panOffset = panOffset.normalize();
	panOffset.multiplyScalar( PAN_SPEED*TURBO );
	//panDir = new THREE.Vector3(xx, yy, zz);
}

function panDirSet(xx, yy, zz) {
	doPanMove = true;
	// don't bother doing calculations if we don't need to
	if (xx==panDir.x && yy==panDir.y && zz==panDir.z) return;
	if (xx!=0) panDir.x = xx;
	if (yy!=0) panDir.y = yy;
	if (zz!=0) panDir.z = zz;
	//panVectorGen();
}

function panDirUnset(xx, yy, zz) {
	
	// don't bother doing calculations if we don't need to
	//if (panDir.x==0 && panDir.x==0 && panDir.x==0) return;
	if (xx!=0) panDir.x = 0;
	if (yy!=0) panDir.y = 0;
	if (zz!=0) panDir.z = 0;
	if (panDir.x==0 && panDir.x==0 && panDir.x==0) {
		doPanMove = false;
		return;
	}
	//panVectorGen();
}

function canDirSet(xx, yy, zz) {
	doCanMove = true;
	// don't bother doing calculations if we don't need to
	if (xx==canDir.x && yy==canDir.y && zz==canDir.z) return;
	if (xx!=0) canDir.x = xx;
	if (yy!=0) canDir.y = yy;
	if (zz!=0) canDir.z = zz;
	//panVectorGen();
}

function canDirUnset(xx, yy, zz) {
	
	// don't bother doing calculations if we don't need to
	//if (panDir.x==0 && panDir.x==0 && panDir.x==0) return;
	if (xx!=0) canDir.x = 0;
	if (yy!=0) canDir.y = 0;
	if (zz!=0) canDir.z = 0;
	if (canDir.x==0 && canDir.x==0 && canDir.x==0) {
		doCanMove = false;
		return;
	}
	//panVectorGen();
}
/*
	doPanMove = false;
	panOffset.set(0,0,0);
	panDir.set(0,0,0);
*/

/*
	Returns movement vector required to get vector vect back in the box
*/
function keepInBox( lowerY, upperY, vect ) {
	var displaceVect = new THREE.Vector3(0,0,0);
	if (vect.x > MAX_DISTANCE) displaceVect.x = MAX_DISTANCE-vect.x;
	if (vect.x <-MAX_DISTANCE) displaceVect.x =-MAX_DISTANCE-vect.x;
	if (vect.y > upperY) displaceVect.y = upperY-vect.y;
	if (vect.y <-lowerY) displaceVect.y =-lowerY-vect.y;
	if (vect.z > MAX_DISTANCE) displaceVect.z = MAX_DISTANCE-vect.z;
	if (vect.z <-MAX_DISTANCE) displaceVect.z =-MAX_DISTANCE-vect.z;
	return displaceVect;
}

function zeroVect( vect ) {
	return (vect.x==0 && vect.y==0 && vect.z==0);
}

function animate() {

//var MAX_FPS = 30;
//var frameDelay = 1000 / MAX_FPS;
//var frameTime = Date.now();

	/* FRAMERATE */
	var timeNow = Date.now();
	if ((timeNow-frameTime) > (1000 / MAX_FPS)) {
		frameDelay -= 1;
	} else {
		frameDelay += 1;
	}
	frameTime = timeNow;
	setTimeout( function() {
        requestAnimationFrame( animate );
    }, frameDelay );
	//requestAnimationFrame( animate );
	
	if (paused==true) {
		//camera.updateMatrixWorld();
		$("#pauseDiv").show();
		return;
	} else {
		$("#pauseDiv").hide();
		//pauseDiv.css({display: "none",visibility: "hidden"});
	}

	/* MOTION HANDLING */
	if (doPanMove) {
		panVectorGen();
		controls.target.add(panOffset);
		camera.position.add(panOffset);
		//console.log(controls.object.matrix.elements);
	}
	if (doCanMove) {
		var canMovement = canDir.clone();
		canMovement.multiplyScalar( CAN_SPEED );
		cylinder.position.add(canMovement);
		shadow.position.x = cylinder.position.x;
		shadow.position.z = cylinder.position.z;
		//cylinder.update();
		//console.log(controls.object.matrix.elements);
	}
	var displace = keepInBox( MAX_DISTANCE*0.06, MAX_DISTANCE*0.66, controls.target );
	if (!zeroVect(displace)) {
		controls.target.add(displace);
		camera.position.add(displace);
	}
	displace = keepInBox( 0, MAX_DISTANCE*0.5, cylinder.position );
	if (!zeroVect(displace)) {
		cylinder.position.add(displace);
		shadow.position.x = cylinder.position.x;
		shadow.position.z = cylinder.position.z;
	}

	/*
	if (controls.target.length() > MAX_DISTANCE*1.1 ) {
		controls.target = controls.target.normalize();
		controls.target.multiplyScalar( MAX_DISTANCE*0.9 );
	}
	*/
	//controls.target.x = (mouseY - windowHalfY)/windowHalfY*GRID_LARGE;
	//controls.target.z = (mouseX - windowHalfX)/windowHalfX*GRID_LARGE;
	//camera.rotation.x = (mouseY - windowHalfY)/3/180;
	//camera.rotation.y = (mouseX - windowHalfX)/3/180;
	//camera.rotation.y = /*10+*/mouseY/3*ASPECT;
	//camera.position.x = (mouseX - windowHalfX)/3;
	//camera.position.y = /*10+*/(mouseY - windowHalfY/2)/3*ASPECT; //
	/*
	lightx = [-1,-1,1,1];
	lightz = [-1,1,1,-1];
	for (var i=0; i<4; i++){
		lights[i].position.set( lightx[i]*DIST_LIGHTS*(0.5+mouseX/windowHalfX), 
								(mouseY - windowHalfY/2)/3*ASPECT, 
								lightz[i]*DIST_LIGHTS*(0.5+mouseX/windowHalfX));
		lightspheres[i].position.set( lightx[i]*DIST_LIGHTS*(0.5+mouseX/windowHalfX), 
								(mouseY - windowHalfY/2)/3*ASPECT, 
								lightz[i]*DIST_LIGHTS*(0.5+mouseX/windowHalfX));	}
	*/
	//camlight.position.set(camera.position.x, camera.position.y, camera.position.z);
	//light.position.set(-50, camera.position.y-50, 50);
	//light.position.set( -1, 1.75, 1 );
	//light.position.multiplyScalar( 50 );

	/* MAIN RENDERER */
	controls.update();
	render();
}

function threejsKeyDown( event ) {
	//var doPanMove = false;
	//var panOffset = THREE.Vector3(0,0,0);
	//panOffset.multiplyScalar(-panSpeed);
	var c = String.fromCharCode(event.which);
	//console.log(c+" down");
	/*
	var camVector = new THREE.Vector3( 0, 0, -1 );
	camVector.applyQuaternion( camera.quaternion );
	camVector.y = 0;
	camVector = camVector.normalize();
	camVector.multiplyScalar(0.0000001);
	*/

	if(event.keyCode === 32){ // pause/play
		paused = !paused;
	} else if(event.keyCode == 39){  //next key

	} else if(event.keyCode == 13){  //enter key
	    //$('#submit_p').live('click',function(event){...}  
	} else if(event.keyCode == 27){  //escape key

	} else if(event.keyCode == 16){ //shift key
		TURBO = 2;
	} else if(c == 'W'){
		panDirSet(0,0,1);
	} else if(c == 'A'){
		panDirSet(-1,0,0);
	} else if(c == 'S'){
		panDirSet(0,0,-1);
	} else if(c == 'D'){
		panDirSet(1,0,0);
	} else if(c == 'R'){
		panDirSet(0,1,0);
	} else if(c == 'F'){
		panDirSet(0,-1,0);
	} else if(event.keyCode == 221){ // ]
		canDirSet(0,1,0);
	} else if(event.keyCode == 219){ // [
		canDirSet(0,-1,0);
	} else if(c == 'O'){ //up arrow key
		canDirSet(0,0,1);
	} else if(c == 'J'){ //left arrow key
		canDirSet(1,0,0);
	} else if(c == 'L'){ //down arrow key
		canDirSet(0,0,-1);
	} else if(c == 'K'){ //right arrow key
		canDirSet(-1,0,0);
	} else if(event.keyCode == 189){ // -
		DIST_LIGHTS = Math.max(GRID_LARGE/4,DIST_LIGHTS-CAN_SPEED);
		for (var i=0; i<4; i++) {
			lights[i].position.set(lightx[i]*DIST_LIGHTS, DIST_LIGHTS/2, lightz[i]*DIST_LIGHTS);
			lightspheres[i].position.set(lightx[i]*DIST_LIGHTS, GRID_LARGE/2, lightz[i]*DIST_LIGHTS);
		}
	} else if(event.keyCode == 187){ // +
		DIST_LIGHTS = Math.min(MAX_DISTANCE,DIST_LIGHTS+CAN_SPEED);
		for (var i=0; i<4; i++) {
			lights[i].position.set(lightx[i]*DIST_LIGHTS, DIST_LIGHTS/2, lightz[i]*DIST_LIGHTS);
			lightspheres[i].position.set(lightx[i]*DIST_LIGHTS, GRID_LARGE/2, lightz[i]*DIST_LIGHTS);
		}
	}
}

function threejsKeyUp( event ) {
	var c = String.fromCharCode(event.which);
	//console.log(c+" up");
	if(c == 'W'){
		panDirUnset(0,0,1);
	} else if(c == 'A'){
		panDirUnset(1,0,0);
	} else if(c == 'S'){
		panDirUnset(0,0,1);
	} else if(c == 'D'){
		panDirUnset(1,0,0);
	} else if(c == 'R'){
		panDirUnset(0,1,0);
	} else if(c == 'F'){
		panDirUnset(0,1,0);
	} else if(c == ']'){
		canDirUnset(0,1,0);
	} else if(c == '['){
		canDirUnset(0,1,0);
	} else if(event.keyCode == 16){ //shift key
		TURBO = 1;
	} else if(event.keyCode == 221){ // ]
		canDirUnset(0,1,0);
	} else if(event.keyCode == 219){ // [
		canDirUnset(0,1,0);
	} else if(c == 'O'){ //up arrow key
		canDirUnset(0,0,1);
	} else if(c == 'J'){ //left arrow key
		canDirUnset(1,0,0);
	} else if(c == 'L'){ //down arrow key
		canDirUnset(0,0,1);
	} else if(c == 'K'){ //right arrow key
		canDirUnset(1,0,0);
	}
}

// -----------------------------------------------------------------------------
//  Runtime Execution
// -----------------------------------------------------------------------------

/* Execute after document loads
*/
$(document).ready(threejsInit);

/* Bind key events
*/
$(document).keydown(threejsKeyDown);
$(document).keyup(threejsKeyUp);
