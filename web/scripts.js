// -----------------------------------------------------------------------------
//  Global Controller
// -----------------------------------------------------------------------------

function PringleGlobal() {
	this.network = {};
	this.network.state = 'off';
	this.network.source = 'webpage';
	this.network.freq = 10; //Hz
	this.network.timer = null;
	this.network.xval = 50;
	this.network.yval = 50;
	this.network.oval = 0;
	this.network.dval = 100;
	
	this.webcam = {};
	this.webcam.state = 'off';
	this.webcam.feed = 'raw';
	this.webcam.source = 'none';
	
	this.elements = {};
	this.elements.xval = $('#xval')[0];
	this.elements.yval = $('#yval')[0];
	this.elements.oval = $('#oval')[0];
	this.elements.dval = $('#dval')[0];
	this.elements.netInputs = $('form#form-network input[type=number]');
	this.elements.netOn = $('#flip-net-on')[0];
	this.elements.netSrc = $('#flip-net-src')[0];
	this.elements.webOn = $('#flip-web-on')[0];
	this.elements.webSrc = $('#combo-web-src')[0];
	this.elements.webFeed = $('#combo-web-feed')[0];
	
	//--------------------------------------------------------------------------
	// Methods
	// -------------------------------------------------------------------------
	
	this.network_timer_start = function(){
		var me = this;
		this.network.timer = setInterval(function(){
			me.network_timer_event();
		}, 1000/this.network.freq);
	};
	
	this.network_timer_stop = function(){
		this.network.timer = clearInterval(this.network.timer);
	};
	
	this.network_webcam_start = function(){
		//
		//TODO
		//
	};
	
	this.network_webcam_stop = function(){
		//
		//TODO
		//
	};
	
	/*	Some network config changed
	*/
	this.network_config_change = function() {
		
		// fetch UI values
		this.network.state = this.elements.netOn.value;
		this.network.source = this.elements.netSrc.value;

		// enable/disable elements
		this.elements.netInputs.prop('disabled', 
			(this.network.source != 'webpage'));
		
		// turn the alarm on/off
		if ((this.network.state != 'on') || (this.network.source != 'webpage')){
			this.network_timer_stop();
		} else {
			this.network_timer_start();
		}
		
		// if src is webcam, tell the server
		if ((this.network.state == 'on') && (this.network.source == 'webcam')){
			this.network_webcam_start();
		} else {
			this.network_webcam_stop();
		}
		//
		//TODO account for webcam config
		//
	};
	
	/*	Some webcam config changed
	*/
	this.webcam_config_change = function() {
		
		// fetch UI values
		this.webcam.state = this.elements.webOn.value;
		this.webcam.source = this.elements.webSrc.value;
		this.webcam.feed = this.elements.webFeed.value;

		// if src is webcam, tell the server
		//
		//TODO account for network config
		//
	};
	
	//--------------------------------------------------------------------------
	// Bindings
	// -------------------------------------------------------------------------
	
	this.events_bind = function(){
		var me=this;
		$(this.elements.webOn).bind( "change", function(){
			console.log('web-on val='+me.elements.webOn.value.toString());
			me.webcam_config_change();
		});
		$(this.elements.webSrc).bind( "change", function(){
			console.log('web-src val='+me.elements.webSrc.value.toString());
			me.webcam_config_change();
		});
		$(this.elements.webFeed).bind( "change", function(){
			console.log('web-feed val='+me.elements.webFeed.value.toString());
			me.webcam_config_change();
		});
		$(this.elements.netOn).bind( "change", function(){
			console.log('net-on val='+me.elements.netOn.value.toString());
			me.network_config_change();
		});
		$(this.elements.netSrc).bind( "change", function(){
			console.log('net-src val='+me.elements.netSrc.value.toString());
			me.network_config_change();
		});
		$(this.elements.netInputs).bind( "change", function(){
			console.log('net-val change');
			me.network_val_change();
		});
		$(this.elements.netInputs).bind( "keyup", function(){
			console.log('net-val change');
			me.network_val_change();
		});
	};
	
	/* Timer to send telemetry
	*/
	this.network_timer_event = function(){
		var d=new Date();
		var t=d.toLocaleTimeString();
		//console.log("time="+t);
	
		// check the timer should be running
		if ((this.network.state != 'on') || (this.network.source != 'webpage')){
			this.network_timer_stop();
			return;
		}
		
		// read telemetry values
		this.network.xval = this.elements.xval.value;
		this.network.yval = this.elements.yval.value;
		this.network.oval = this.elements.oval.value;
		this.network.dval = this.elements.dval.value;
		
		if (!(this.network.xval) || !(this.network.yval) ||
			!(this.network.oval) || !(this.network.dval)) {
				return;
			}
	
		// transmit
		//
		//TODO
		//
		console.log('transmit');
	};
	
	/*	User changed value in a telemetry field
	*/
	this.network_val_change = function(event, ui) {
		var elems = this.elements.netInputs;
		for (var i=0; i<elems.length; i++) {
			if (elems[i].value.length==0) {
				elems[i].value = elems[i].getAttribute('default');
			}
		}
	};
}

// -----------------------------------------------------------------------------
//  Runtime Execution
// -----------------------------------------------------------------------------

/* Execute after document loads
*/
$(document).ready(function() {
	
	// Init global controller(s)
	window.pringleGlobal = new PringleGlobal();
	pringleGlobal.events_bind();
	pringleGlobal.network_timer_start();
	
	// UI binding
	$("#hyper-network").bind("click", function(){
		$("#collapsible-network").collapsible("collapse");
		$("#collapsible-webcam").collapsible("expand");
	});
});

// -----------------------------------------------------------------------------
// -----------------------------------------------------------------------------

/*
$("#hyper-webcam").bind("click", function(){
	$("#collapsible-webcam").collapsible("collapse");
	$("#collapsible-network").collapsible("expand");
});

//var xx=0;
for (var i=0; i<elems.length; i++) {
	while (!(inputs[i].checkValidity())) {
		if (inputs[i].value.length > 0) {
			//inputs[i].value = inputs[i].value.replace('/[^\d]/','');
		} else {
			inputs[i].value = inputs[i].getAttribute('default');
		}
	}
}*/