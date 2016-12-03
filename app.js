var app = new Vue({
    el: '#weatherobs',

    data:{
        dtHeaders: ["Temperature", "Pressure", "Relative Humidity", "Lux",
                        "Altitude", "Timestamp"],
        title: "Weather Observations",
        observations: []
    },
    
    ready: function() {
        this.fetchData();
    },

    methods: {
        fetchData: function() {
            console.log("here");
            this.$http.get("api/observations").then(function( response ) {
                this.observations = response.data;
            }).error(function(error) {
                console.log(error);
            });
        },
    },

    mounted: function() {
        $('#obsTable').DataTable( {
            data: this.observations,
            columns: [
                { data: 'temp' },
                { data: 'prese' },
                { data: 'rhum' },
                { data: 'lux' },
                { data: 'alt' },
                { data: 'time' }
            ]
        });
    }
});
