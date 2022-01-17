jQuery(document).ready(function() {
    jQuery.getJSON('js/envs.json', function(data) {
        let environment = data['environment'];
        let debug = environment == 'development';
        let apiRoot= '/api'
        if (environment == 'development') {
            apiRoot = 'http://localhost:8000/api'
        }

        function generateEmptyResponse() {
            return '<p>Nic nie znaleziono!</p>'
        }

        function assignPageHref(prefix, name, callback, data, secondData) {
            let elementData = data[name];
            let $element = jQuery(`#${prefix}-${name}`);

            if (elementData != null) {
                $element.removeClass('d-none');

                $element.unbind();
                $element.click(function() {
                    jQuery.get(elementData, function(fetchedData) {
                        callback(fetchedData, secondData);
                    });
                });
            } else {
                $element.addClass('d-none');
            }
        }

        function generateCemeteryRegister(element) {
            let slug = element['slug'];
            let url = `#/cemetery-registers/${slug}/`
            let title = element['title'];
            return `<p>
                <a href="${url}">${title}</a>
            </p>`;
        }

        function processCemeteryRegisters(data) {
            jQuery('#results-title').removeClass('d-none');
            jQuery('#cemetery-register-create').removeClass('d-none');

            let $results = jQuery('#results');
            $results.empty();

            if (data['count'] == 0) {
                $results.append(generateEmptyResponse());
            } else {
                let results = data['results']
                results.forEach(function(element) {
                    $results.append(generateCemeteryRegister(element));
                });
            }

            assignPageHref('cemetery-register', 'next', processCemeteryRegisters, data);
            assignPageHref('cemetery-register', 'previous', processCemeteryRegisters, data);
        };

        function runSearch() {
            let search = jQuery('#cemetery-registers-search').val()
            jQuery.get(`${apiRoot}/cemetery-registers/?search=${search}`, function(data) {
                processCemeteryRegisters(data);
            });
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
        jQuery(document).on('keypress', function(event) {
            if(event.which == 13) {
                runSearch();
            }
        });
        jQuery('#cemetery-register-create-button').click(runCreate);

        // Without it first usage is not triggered
        if (window.location.hash == undefined) {
            window.location.hash = '#/';
        } else {
            hashChange();
        }

        function searchSite(params) {
            jQuery('#search-site').removeClass('d-none');
            jQuery('#retrieve-site').addClass('d-none');
            jQuery('#create-site').addClass('d-none');
            jQuery('#obituary-notice-create-site').addClass('d-none');
        }

        function generateCemeteryRegisterRetrieve(data) {
            let title = data['title'];
            let description = data['description'];

            return `<h3>
                ${title}
            </h3><p>
                ${description}
            </p>`;
        }

        function generateCemeteryRegisterCreateLink(slug) {
            return `
                <a id="obituary-notice-create" href="#/cemetery-registers/${slug}/obituary-notices/">Stwórz nekrolog</a>
            `;
        }

        function generateObituaryNotice(cemeteryRegisterSlug, element) {
            let slug = element['slug'];
            let url = `${apiRoot}/cemetery-registers/${cemeteryRegisterSlug}/obituary-notices/${slug}/`
            let firstName = element['first_name'];
            let lastName = element['last_name'];
            let yearsLived = element['years_lived'];

            return `<p>
                <a href="${url}">${firstName} ${lastName}, lat ${yearsLived}</a>
            </p>`;
        }

        function retrieveSite(params) {
            jQuery('#search-site').addClass('d-none');
            jQuery('#retrieve-site').removeClass('d-none');
            jQuery('#create-site').addClass('d-none');
            jQuery('#obituary-notice-create-site').addClass('d-none');

            let slug = params['slug'];

            function processObituaryNotices(obituaryNoticeData, cemeteryRegisterData) {
                $results = jQuery('#results-retrieve');
                $results.empty()
                $results.append(generateCemeteryRegisterRetrieve(cemeteryRegisterData));

                $obituaryNoticeCreateLink = jQuery('#obituary-notice-create');
                $obituaryNoticeCreateLink.empty();
                $obituaryNoticeCreateLink.append(generateCemeteryRegisterCreateLink(slug));

                if (obituaryNoticeData['count'] == 0) {
                    $results.append(generateEmptyResponse());
                } else {
                    console.log(obituaryNoticeData);
                    let results = obituaryNoticeData['results']
                    results.forEach(function(element) {
                        $results.append(generateObituaryNotice(slug, element));
                    });
                }

                assignPageHref('obituary-notice', 'next',
                    processObituaryNotices, obituaryNoticeData, cemeteryRegisterData);
                assignPageHref('obituary-notice', 'previous',
                    processObituaryNotices, obituaryNoticeData, cemeteryRegisterData);
            }

            jQuery.get(`${apiRoot}/cemetery-registers/${slug}/`, function(cemeteryRegisterData) {
                jQuery.get(`${apiRoot}/cemetery-registers/${slug}/obituary-notices/`, function(obituaryNoticeData) {
                    processObituaryNotices(obituaryNoticeData, cemeteryRegisterData);
                });
            });
        }

        function createSite(params) {
            jQuery('#search-site').addClass('d-none');
            jQuery('#retrieve-site').addClass('d-none');
            jQuery('#create-site').removeClass('d-none');
            jQuery('#obituary-notice-create-site').addClass('d-none');
            jQuery('#cemetery-register-create-form').removeClass('d-none');
            jQuery('#cemetery-register-create-success').addClass('d-none');
            jQuery('#cemetery-register-create-failure').addClass('d-none');
            jQuery('#cemetery-register-title').val('');
            jQuery('#cemetery-register-description').val('');
        }

        function createObituaryNotice(params) {
            jQuery('#search-site').addClass('d-none');
            jQuery('#retrieve-site').addClass('d-none');
            jQuery('#create-site').addClass('d-none');
            jQuery('#obituary-notice-create-site').removeClass('d-none');
        }

        function hashChange() {
            const config = {
                'search': ['', searchSite],
                'cemetery-register-retrieve': ['cemetery-registers/(?<slug>[\\w-]+)/', retrieveSite],
                'cemetery-register-create': ['cemetery-registers/', createSite],
                'obituary-notice-create': [
                    'cemetery-registers/(?<slug>[\\w-]+)/obituary-notices/', createObituaryNotice
                ],
            }

            for (const [hashName, hashRoute] of Object.entries(config)) {
                let hashRegex = '^#/' + hashRoute[0] + '$';
                let regex = RegExp(hashRegex);
                let hash = window.location.hash;
                let params = hash.match(regex);
                let hashFunction = hashRoute[1];
                if (params != null) {
                    if (debug) {
                        console.log(`Hit ${hashName}.`)
                    }
                    hashFunction(params.groups);
                    break;
                } else {
                    if (debug) {
                        console.log(`Tried ${regex} on ${hash}.`);
                    }
                }
            }
        }

        jQuery(window).on('hashchange', hashChange);
    });
});
