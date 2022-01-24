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

        function activateTooltips(xhr, prefix) {
            if (xhr.status == 400) {
                if (debug) {
                    console.log(xhr.responseJSON);
                }
                jQuery('div.tooltip > span.tooltiptext').addClass('d-none');
                for (const [fieldName, errors] of Object.entries(xhr.responseJSON)) {
                    let name = fieldName.replaceAll('_', '-');
                    let selector = `#${prefix}-${name}`;
                    let $tooltip = jQuery(selector);
                    $tooltip.text(errors.join(' '));
                    $tooltip.removeClass('d-none');
                }
            }
        }

        function assignPageHref(prefix, name, callback, data, secondData) {
            let elementData = data[name];
            let $element = jQuery(`#${prefix}-${name}`);

            if (elementData != null) {
                $element.removeClass('d-none');

                $element.unbind().click(function() {
                    jQuery.get(elementData, function(fetchedData) {
                        callback(fetchedData, secondData);
                    });
                });
            } else {
                $element.addClass('d-none');
            }
        }

        function report(category, slug, id) {
            jQuery.post(`${apiRoot}/reports/`, {
                'category': category,
                'slug': slug,
            }).done(function() {
                $popup = jQuery(`#${id}`).unbind().click(function() {
                    jQuery(this)[0].classList.toggle('show');
                });
                $popup.click();
            });
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
            jQuery('#cemetery-register-results-title').removeClass('d-none');
            jQuery('#cemetery-register-create').removeClass('d-none');

            let $results = jQuery('#cemetery-register-results');
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

        function runCreateCemeteryRegister() {
            let title = jQuery('#cemetery-register-title').val();
            let description = jQuery('#cemetery-register-description').val();
            jQuery.post(`${apiRoot}/cemetery-registers/`, {
                'title': title,
                'description': description,
            }).done(function() {
                jQuery('#cemetery-register-create-form').addClass('d-none');
                jQuery('#cemetery-register-create-success').removeClass('d-none');
                jQuery('#cemetery-register-create-failure').addClass('d-none');
            }).fail(function(xhr) {
                activateTooltips(xhr, 'cemetery-register-tooltip');
                jQuery('#cemetery-register-create-failure').removeClass('d-none');
            });
        }

        jQuery('#cemetery-registers-button').click(runSearch);
        jQuery(document).on('keypress', function(event) {
            if(event.which == 13) {
                runSearch();
            }
        });
        jQuery('#cemetery-register-create-button').click(runCreateCemeteryRegister);

        // Without it first usage is not triggered
        if (window.location.hash == undefined) {
            window.location.hash = '#/';
        } else {
            hashChange();
        }

        function searchSite() {}

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
            let slug = params['slug'];

            function processObituaryNotices(obituaryNoticeData, cemeteryRegisterData) {
                $results = jQuery('#cemetery-register-results-retrieve');
                $results.empty()
                $results.append(generateCemeteryRegisterRetrieve(cemeteryRegisterData));

                $obituaryNoticeCreateLink = jQuery('#obituary-notice-create');
                $obituaryNoticeCreateLink.empty();
                $obituaryNoticeCreateLink.append(generateCemeteryRegisterCreateLink(slug));

                if (obituaryNoticeData['count'] == 0) {
                    $results.append(generateEmptyResponse());
                } else {
                    let results = obituaryNoticeData['results']
                    results.forEach(function(element) {
                        $results.append(generateObituaryNotice(slug, element));
                    });
                }

                assignPageHref('obituary-notice', 'next',
                    processObituaryNotices, obituaryNoticeData, cemeteryRegisterData
                );
                assignPageHref('obituary-notice', 'previous',
                    processObituaryNotices, obituaryNoticeData, cemeteryRegisterData
                );
            }

            jQuery.get(`${apiRoot}/cemetery-registers/${slug}/`, function(cemeteryRegisterData) {
                jQuery.get(`${apiRoot}/cemetery-registers/${slug}/obituary-notices/`, function(obituaryNoticeData) {
                    processObituaryNotices(obituaryNoticeData, cemeteryRegisterData);
                });
            });
            jQuery('#cemetery-register-report-anchor').click(function() {
                report('cemetery_register', slug, 'cemetery-register-report-popup');
            });
        }

        function createSite(params) {
            jQuery('#cemetery-register-create-form').removeClass('d-none');
            jQuery('#cemetery-register-create-success').addClass('d-none');
            jQuery('#cemetery-register-create-failure').addClass('d-none');
            jQuery('#cemetery-register-title').val('');
            jQuery('#cemetery-register-description').val('');
        }

        function createObituaryNoticeSite(params) {
            let slug = params['slug'];

            let datepickerConfig = {
                dateFormat: 'yy-mm-dd',
            };
            jQuery('#obituary-notice-death-date').datepicker(datepickerConfig);
            jQuery('#obituary-notice-holy-mass-date').datepicker(datepickerConfig);
            let timepickerConfig = {
                timeFormat: 'H:mm',
                interval: 15,
                minTime: '6',
                maxTime: '22',
                defaultTime: '',
                startTime: '6:00',
                dynamic: false,
                dropdown: true,
                scrollbar: true,
            };
            jQuery('#obituary-notice-holy-mass-time').timepicker(timepickerConfig);
            timepickerConfig['interval'] = 5;
            jQuery('#obituary-notice-rosary-time').timepicker(timepickerConfig);

            function runCreateObituaryNotice() {
                let deathDate = jQuery('#obituary-notice-death-date').val();

                let titles = jQuery('div#obituary-notice-titles > input[type=checkbox]:checked').map(function(){
                    return jQuery(this).next().text();
                }).get().join(", ");

                let firstName = jQuery('#obituary-notice-first-name').val();
                let lastName = jQuery('#obituary-notice-last-name').val();
                let yearsLived = jQuery('#obituary-notice-years-lived').val();

                let holyMassDatetime;
                try {
                    let holyMassDate = jQuery('#obituary-notice-holy-mass-date').datepicker('getDate');
                    let holyMassTime = jQuery('#obituary-notice-holy-mass-time').val();
                    let splitTime = holyMassTime.split(':');
                    let hours = Number.parseInt(splitTime[0]);
                    let minutes = Number.parseInt(splitTime[1]);
                    holyMassDate.setHours(hours, minutes, 0);
                    holyMassDatetime = holyMassDate.toJSON();
                } catch (error) {
                    if (error instanceof TypeError) {
                        holyMassDatetime = null;
                    }
                }

                let holyMassPlace = jQuery('#obituary-notice-holy-mass-place').val();
                let rosaryTime = jQuery('#obituary-notice-rosary-time').val();
                let rosaryPlace = jQuery('#obituary-notice-rosary-place').val();
                let bodyOrAshes = jQuery('#obituary-notice-body-or-ashes').val();
                let funeralPlace = jQuery('#obituary-notice-funeral-place').val();

                jQuery.post(`${apiRoot}/cemetery-registers/${slug}/obituary-notices/`, {
                    'death_date': deathDate,
                    'titles': titles,
                    'first_name': firstName,
                    'last_name': lastName,
                    'years_lived': yearsLived,
                    'holy_mass_datetime': holyMassDatetime,
                    'holy_mass_place': holyMassPlace,
                    'rosary_time': rosaryTime,
                    'rosary_place': rosaryPlace,
                    'body_or_ashes': bodyOrAshes,
                    'funeral_place': funeralPlace,
                }).done(function(data) {
                    jQuery('#obituary-notice-create-form').addClass('d-none');
                    jQuery('#obituary-notice-create-success').removeClass('d-none');
                    jQuery('#obituary-notice-create-failure').addClass('d-none');

                    jQuery('#obituary-notice-create-url').removeClass('d-none');
                    let obituaryNoticeSlug = data['slug'];
                    let url = `${apiRoot}/cemetery-registers/${slug}/obituary-notices/${obituaryNoticeSlug}/payments/`;
                    jQuery('#obituary-notice-create-anchor').attr('href', url)
                }).fail(function(xhr) {
                    activateTooltips(xhr, 'obituary-notice-tooltip');
                    jQuery('#obituary-notice-create-failure').removeClass('d-none');
                });
            }

            $obituaryNoticeCreateButton = jQuery('#obituary-notice-create-button');
            $obituaryNoticeCreateButton.unbind().click(runCreateObituaryNotice);
        }

        function stripeSuccessSite(params) {
            let cemeteryRegisterSlug = params['cemeteryRegisterSlug'];
            let obituaryNoticeSlug = params['obituaryNoticeSlug'];
            let url = `${apiRoot}/cemetery-registers/${cemeteryRegisterSlug}/obituary-notices/${obituaryNoticeSlug}/`;
            $stripeSuccessAnchor = jQuery('#stripe-success-anchor');
            $stripeSuccessAnchor.attr('href', url);
            $stripeSuccessAnchor.removeClass('d-none');
        }

        function stripeCancelSite() {}

        function aboutSite() {
            $('#about-sample-obituary-notice-anchor').attr(
                'href', `${apiRoot}/cemetery-registers/sample/obituary-notices/sample/sample/`
            );
        }

        function hashChange() {
            const config = {
                'cemetery-register-search-site': ['', searchSite],
                'cemetery-register-retrieve-site': ['cemetery-registers/(?<slug>[\\w-]+)/', retrieveSite],
                'cemetery-register-create-site': ['cemetery-registers/', createSite],
                'obituary-notice-cemetery-register-create-site': [
                    'cemetery-registers/(?<slug>[\\w-]+)/obituary-notices/', createObituaryNoticeSite
                ],
                'stripe-success-site': [
                    'stripe/success/(?<cemeteryRegisterSlug>[\\w-]+)/(?<obituaryNoticeSlug>[\\w-]+)/', stripeSuccessSite
                ],
                'stripe-cancel-site': ['stripe/cancel/', stripeCancelSite],
                'about-site': ['about/', aboutSite],
            };

            function hideAndShow(ids, showId, displayNoneClass='d-none') {
                ids.forEach(function(id) {
                    $site = jQuery(`#${id}`);
                    if (id != showId) {
                        $site.addClass(displayNoneClass);
                    } else {
                        $site.removeClass(displayNoneClass);
                    }
                });
            }

            const ids = Object.keys(config);
            for (const [hashId, hashRoute] of Object.entries(config)) {
                let hashRegex = '^#/' + hashRoute[0] + '$';
                let regex = RegExp(hashRegex);
                let hash = window.location.hash;
                let params = hash.match(regex);
                let hashFunction = hashRoute[1];
                if (params != null) {
                    if (debug) {
                        console.log(`Hit ${hashId}.`)
                    }
                    hideAndShow(ids, hashId);
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
