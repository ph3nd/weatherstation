var app = new Vue({
    el: '#weatherobs',

    data:{
        dtHeaders: ["Temperature", "Pressure", "Relative Humidity", "Lux",
                        "Altitude", "Timestamp"],
        title: "Weather Observations",
        observations: []
    },
    
    methods: {
        fetchData: function() {
            let vm = this;
            this.$http.get("api/observations").then(function( response ) {
                vm.observations = JSON.parse(response.body);
            });
        },
    },

    mounted: function() {
        let vm = this;
        this.fetchData();

        vm.datatable = $('#obsTable').DataTable( {
            data: vm.observations,
            columns: [
                { data: 'temp' },
                { data: 'prese' },
                { data: 'rhum' },
                { data: 'lux' },
                { data: 'alt' },
                { data: 'time' }
            ]
        });

        vm.datatable.search('').draw();
    }
});
