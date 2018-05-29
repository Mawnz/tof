(function(){
    // For easier printouts in console
    let log = console.log;
    // Set eventhandlers
    $('#kill_btn').click(kill);

    let model = {
        run: run,
        update: update
    }

    let utils = {
        // https://stackoverflow.com/questions/951021/what-is-the-javascript-version-of-sleep
        sleep: function(ms) {
            return new Promise(resolve => setTimeout(resolve, ms));
        }
    }
    // Run the program
    model.run()

    // Functions
    async function run(){
        while(true){
            // Get current times from our TOF
            times = getTimes()
            // Update our texts
            if(times['failed']) log(times['failed'])
            else update(times);

            await utils.sleep(500);
        }
    }
    function update(times){
        $('#stopwatch_flight').text(times['flight']);  
        $('#stopwatch_total').text(times['total']); 
    }
    function getTimes(){
        let response = {'failed': 'Something went wrong'}

        $.ajax({
            url: '/times',
            type: 'GET',
            success: function(response){
                // Response like: {'flight': Float, 'total': Float, 'mat': null || Float}
                response = JSON.parse(response);
            }
        })

        return response;
    }
    function kill(){
        $.ajax({
            url: 'kill',
            type: 'GET',
            success: function(response) {
                log(response)
            }
        })
    }


})();