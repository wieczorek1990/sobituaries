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
                $element.unbind();
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
            let url = `#/cemetery-registers/${slug}/`
            return `<p>
                <a href="${url}">${title}</a>
            </p>`;
        }

        function processResults(data) {
            jQuery('#results-title').removeClass('d-none');
            jQuery('#cemetery-register-create').removeClass('d-none');

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

        function runSearch() {
            let search = jQuery('#cemetery-registers-search').val()
            jQuery.get(`${apiRoot}/cemetery-registers/?search=${search}`, function(data) {
                processResults(data);
            })
        }

        function runCreate() {
            let title = jQuery('#cemetery-register-title').val();
            let description = jQuery('#cemetery-register-description').val();
            jQuery.post(`${apiRoot}/cemetery-registers/`, {
                'title': title,
                'description': description,
            }).done(function() {
                jQuery('#cemetery-register-create-form').addClass('d-none');
                jQuery('#cemetery-register-create-success').removeClass('d-none');
                jQuery('#cemetery-register-create-failure').addClass('d-none');
            }).fail(function() {
                jQuery('#cemetery-register-create-failure').removeClass('d-none');
            });
        }

        jQuery('#cemetery-registers-button').click(runSearch);
        $(document).on('keypress',function(e) {
            if(e.which == 13) {
                runSearch();
            }
        });
        jQuery('#cemetery-register-create-button').click(runCreate);

        // Without it first usage is not triggered
        window.location.hash = '#/';

        function searchSite(params) {
            jQuery('#search-site').removeClass('d-none');
            jQuery('#retrieve-site').addClass('d-none');
            jQuery('#create-site').addClass('d-none');
        }

        function generateCemeteryRegistryRetrieve(data) {
            let title = data['title'];
            let description = data['description'];
            return `<h3>
                ${title}
            </h3><p>
                ${description}
            </p>`;
        }

        function retrieveSite(params) {
            jQuery('#search-site').addClass('d-none');
            jQuery('#retrieve-site').removeClass('d-none');
            jQuery('#create-site').addClass('d-none');

            let slug = params['slug'];
            $results = jQuery('#results-retrieve');
            $results.empty()
            jQuery.get(`${apiRoot}/cemetery-registers/${slug}`, function(data) {
                $results.append(generateCemeteryRegistryRetrieve(data));
            })
        }

        function createSite(params) {
            jQuery('#search-site').addClass('d-none');
            jQuery('#retrieve-site').addClass('d-none');
            jQuery('#create-site').removeClass('d-none');
            jQuery('#cemetery-register-create-form').removeClass('d-none');
            jQuery('#cemetery-register-create-success').addClass('d-none');
            jQuery('#cemetery-register-create-failure').addClass('d-none');
            jQuery('#cemetery-register-title').val('');
            jQuery('#cemetery-register-description').val('');
        }

        jQuery(window).on('hashchange', function() {
            const config = {
                'search': ['', searchSite],
                'cemetery-register-retrieve': ['cemetery-registers/(?<slug>[\\w-]+)/', retrieveSite],
                'cemetery-register-create': ['cemetery-register-create/', createSite],
            }

            for (const [hashName, hashRoute] of Object.entries(config)) {
                let hashRegex = '^#/' + hashRoute[0] + '$';
                let regex = RegExp(hashRegex);
                let hash = window.location.hash;
                let params = hash.match(regex);
                let hashFunction = hashRoute[1];
                if (params != null) {
                    hashFunction(params.groups);
                }
            }
        })
    });
});
