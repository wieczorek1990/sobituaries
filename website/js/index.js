jQuery(document).ready(function() {
    jQuery.getJSON('js/envs.json', function(data) {
        let environment = data['environment'];
        let apiRoot= '/api'
        if (environment == 'development') {
            apiRoot = 'http://localhost:8000/api'
        }

        function assignPageHref(name, data) {
            let elementData = data[name];
            let $element = jQuery(`#${name}`);
            if (elementData != null) {
                $element.removeClass('d-none');
                $element.click(function() {
                    jQuery.get(elementData, function(data) {
                        processResults(data);
                    })
                })
            } else {
                $element.addClass('d-none');
            }
        }

        function generateCemeteryRegistry(element) {
            let title = element['title'];
            let slug = element['slug'];
            let url = `cemetery-register.html/?slug=${slug}`
            return `<p>
                <a href="${url}">${title}</a>
            </p>`;
        }

        function processResults(data) {
            let $resultsTitle = jQuery('#results-title');
            $resultsTitle.removeClass('d-none')

            let $results = jQuery('#results');
            $results.empty();

            if (data['count'] == 0) {
                $results.append('<p>Nic nie znaleziono!</p>');
            } else {
                let results = data['results']
                results.forEach(function(element) {
                    $results.append(generateCemeteryRegistry(element));
                });
            }

            assignPageHref('next', data);
            assignPageHref('previous', data);
        };

        jQuery('#cemetery-registers-button').click(function() {
            let search = jQuery('#cemetery-registers-search').val()
            jQuery.get(`${apiRoot}/cemetery-registers/?search=${search}`, function(data) {
                processResults(data);
            })
        });
    });
});
