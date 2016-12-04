var app = new Vue({
    el: '#weatherobs',

    data: function () {
        return {
            dtHeaders: ["Temperature", "Pressure", "Relative Humidity", "Lux",
                            "Altitude", "Timestamp"],
            title: "Weather Observations",
            observations: []
        }
    },
    
    methods: {
        fetchData: function() {
            let vm = this;
            this.$http.get("api/observations").then(function( response ) {
                vm.observations = JSON.parse(response.body);
            });
        },
    },

   watch: { 
        observations: function() {
            let vm = this;
            vm.datatable = $('#obsTable').DataTable( {
                data: vm.observations,
                columns: [
                    { 'data': 'temp' },
                    { 'data': 'pres' },
                    { 'data': 'rhum' },
                    { 'data': 'lux' },
                    { 'data': 'alt' },
                    { 'data': 'time' }
                ]
            });

            vm.datatable.search('').draw();
        }
    },

    mounted: function() {
        let vm = this;

        this.fetchData();
    }
});
