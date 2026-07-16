(() => {
    "use strict";

    const searchInput = document.getElementById("scian_search");
    const codeInput = document.getElementById("activity_class");
    const resultsBox = document.getElementById("scian_results");
    const statusText = document.getElementById("scian_status");
    const selectedBox = document.getElementById("scian_selected");
    const selectedName = document.getElementById(
        "scian_selected_name"
    );
    const selectedCode = document.getElementById(
        "scian_selected_code"
    );
    const clearButton = document.getElementById(
        "scian_clear"
    );

    if (
        !searchInput
        || !codeInput
        || !resultsBox
        || !statusText
        || !selectedBox
        || !selectedName
        || !selectedCode
        || !clearButton
    ) {
        return;
    }

    const catalogUrl = resultsBox.dataset.catalogUrl;
    const maximumResults = 8;

    let catalog = [];
    let catalogPromise = null;
    let currentResults = [];
    let activeResultIndex = -1;

    const normalizeText = (value) => (
        String(value ?? "")
            .normalize("NFD")
            .replace(/[\u0300-\u036f]/g, "")
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, " ")
            .trim()
    );

    const hideResults = () => {
        resultsBox.hidden = true;
        resultsBox.replaceChildren();
        currentResults = [];
        activeResultIndex = -1;
        searchInput.setAttribute("aria-expanded", "false");
        searchInput.removeAttribute("aria-activedescendant");
    };

    const hideSelectedActivity = () => {
        selectedBox.hidden = true;
        selectedName.textContent = "";
        selectedCode.textContent = "";
    };

    const showSelectedActivity = (activity) => {
        selectedName.textContent = activity.name;
        selectedCode.textContent = `SCIAN ${activity.code}`;
        selectedBox.hidden = false;
    };

    const findByCode = (code) => (
        catalog.find((activity) => activity.code === code)
        ?? null
    );

    const synchronizeSelectedActivity = () => {
        const code = codeInput.value.trim();

        if (code === "0") {
            showSelectedActivity({
                code: "0",
                name: "Todas las actividades económicas",
            });
            return;
        }

        const activity = findByCode(code);

        if (activity) {
            showSelectedActivity(activity);
            return;
        }

        hideSelectedActivity();
    };

    const loadCatalog = async () => {
        if (catalog.length > 0) {
            return catalog;
        }

        if (!catalogPromise) {
            statusText.textContent = (
                "Cargando catálogo SCIAN 2023..."
            );

            catalogPromise = fetch(
                catalogUrl,
                {
                    cache: "force-cache",
                    headers: {
                        "Accept": "application/json",
                    },
                }
            )
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(
                            `HTTP ${response.status}`
                        );
                    }

                    return response.json();
                })
                .then((data) => {
                    if (!Array.isArray(data.classes)) {
                        throw new Error(
                            "El catálogo no tiene el formato esperado."
                        );
                    }

                    catalog = data.classes.map((activity) => ({
                        code: String(activity.code),
                        name: String(activity.name),
                        searchableName: normalizeText(
                            activity.name
                        ),
                    }));

                    statusText.textContent = (
                        "Escribe al menos 2 caracteres y "
                        + "selecciona una actividad."
                    );

                    synchronizeSelectedActivity();

                    return catalog;
                })
                .catch((error) => {
                    catalogPromise = null;
                    statusText.textContent = (
                        "No fue posible cargar el catálogo SCIAN. "
                        + "Puedes escribir la clave manualmente."
                    );

                    console.error(
                        "Error al cargar el catálogo SCIAN:",
                        error
                    );

                    throw error;
                });
        }

        return catalogPromise;
    };

    const scoreActivity = (
        activity,
        normalizedQuery,
        queryTerms
    ) => {
        if (activity.code === normalizedQuery) {
            return 0;
        }

        if (activity.code.startsWith(normalizedQuery)) {
            return 1;
        }

        if (activity.searchableName === normalizedQuery) {
            return 2;
        }

        if (
            activity.searchableName.startsWith(
                normalizedQuery
            )
        ) {
            return 3;
        }

        const phrasePosition = (
            activity.searchableName.indexOf(
                normalizedQuery
            )
        );

        if (phrasePosition >= 0) {
            return 4 + phrasePosition / 1000;
        }

        const allTermsMatch = queryTerms.every(
            (term) => (
                activity.searchableName.includes(term)
            )
        );

        if (allTermsMatch) {
            return 10;
        }

        return Number.POSITIVE_INFINITY;
    };

    const searchCatalog = (query) => {
        const normalizedQuery = normalizeText(query);

        if (normalizedQuery.length < 2) {
            return [];
        }

        const queryTerms = normalizedQuery
            .split(" ")
            .filter(Boolean);

        return catalog
            .map((activity) => ({
                activity,
                score: scoreActivity(
                    activity,
                    normalizedQuery,
                    queryTerms
                ),
            }))
            .filter((item) => Number.isFinite(item.score))
            .sort((first, second) => (
                first.score - second.score
                || first.activity.name.localeCompare(
                    second.activity.name,
                    "es"
                )
            ))
            .slice(0, maximumResults)
            .map((item) => item.activity);
    };

    const setActiveResult = (index) => {
        const options = Array.from(
            resultsBox.querySelectorAll(
                ".scian-result-option"
            )
        );

        options.forEach((option) => {
            option.classList.remove("is-active");
            option.setAttribute(
                "aria-selected",
                "false"
            );
        });

        if (options.length === 0) {
            activeResultIndex = -1;
            searchInput.removeAttribute(
                "aria-activedescendant"
            );
            return;
        }

        activeResultIndex = (
            (index + options.length) % options.length
        );

        const activeOption = options[
            activeResultIndex
        ];

        activeOption.classList.add("is-active");
        activeOption.setAttribute(
            "aria-selected",
            "true"
        );

        searchInput.setAttribute(
            "aria-activedescendant",
            activeOption.id
        );

        activeOption.scrollIntoView({
            block: "nearest",
        });
    };

    const selectActivity = (activity) => {
        codeInput.value = activity.code;
        searchInput.value = activity.name;
        searchInput.dataset.selectedName = activity.name;
        showSelectedActivity(activity);
        hideResults();

        statusText.textContent = (
            "Actividad seleccionada. "
            + "La clave SCIAN se completó automáticamente."
        );

        codeInput.dispatchEvent(
            new Event("change", {
                bubbles: true,
            })
        );
    };

    const renderResults = (results) => {
        resultsBox.replaceChildren();
        currentResults = results;
        activeResultIndex = -1;

        if (results.length === 0) {
            const emptyMessage = document.createElement(
                "p"
            );

            emptyMessage.className = (
                "scian-results-empty"
            );

            emptyMessage.textContent = (
                "No encontramos coincidencias. "
                + "Prueba otra palabra o escribe "
                + "la clave SCIAN manualmente."
            );

            resultsBox.append(emptyMessage);
            resultsBox.hidden = false;

            searchInput.setAttribute(
                "aria-expanded",
                "true"
            );

            statusText.textContent = (
                "Sin coincidencias en las clases SCIAN."
            );

            return;
        }

        results.forEach((activity, index) => {
            const option = document.createElement(
                "button"
            );

            option.type = "button";
            option.id = `scian_option_${index}`;
            option.className = "scian-result-option";
            option.setAttribute("role", "option");
            option.setAttribute(
                "aria-selected",
                "false"
            );

            const optionCode = document.createElement(
                "span"
            );

            optionCode.className = (
                "scian-result-code"
            );

            optionCode.textContent = (
                `SCIAN ${activity.code}`
            );

            const optionName = document.createElement(
                "span"
            );

            optionName.className = (
                "scian-result-name"
            );

            optionName.textContent = activity.name;

            option.append(
                optionCode,
                optionName
            );

            option.addEventListener(
                "click",
                () => selectActivity(activity)
            );

            option.addEventListener(
                "mousemove",
                () => setActiveResult(index)
            );

            resultsBox.append(option);
        });

        resultsBox.hidden = false;

        searchInput.setAttribute(
            "aria-expanded",
            "true"
        );

        statusText.textContent = (
            `${results.length} coincidencia`
            + `${results.length === 1 ? "" : "s"} `
            + "mostrada"
            + `${results.length === 1 ? "" : "s"}.`
        );
    };

    const handleSearchInput = async () => {
        const query = searchInput.value.trim();
        const selectedSearchName = (
            searchInput.dataset.selectedName ?? ""
        );

        if (
            query
            && query !== selectedSearchName
        ) {
            codeInput.value = "";
            searchInput.dataset.selectedName = "";
            hideSelectedActivity();
        }

        if (query.length < 2) {
            hideResults();

            statusText.textContent = (
                "Escribe al menos 2 caracteres y "
                + "selecciona una actividad."
            );

            return;
        }

        try {
            await loadCatalog();
            renderResults(searchCatalog(query));
        } catch {
            hideResults();
        }
    };

    searchInput.addEventListener(
        "focus",
        () => {
            loadCatalog().catch(() => {});
        }
    );

    searchInput.addEventListener(
        "input",
        handleSearchInput
    );

    searchInput.addEventListener(
        "keydown",
        (event) => {
            if (
                resultsBox.hidden
                || currentResults.length === 0
            ) {
                return;
            }

            if (event.key === "ArrowDown") {
                event.preventDefault();
                setActiveResult(
                    activeResultIndex + 1
                );
                return;
            }

            if (event.key === "ArrowUp") {
                event.preventDefault();
                setActiveResult(
                    activeResultIndex - 1
                );
                return;
            }

            if (
                event.key === "Enter"
                && activeResultIndex >= 0
            ) {
                event.preventDefault();

                selectActivity(
                    currentResults[activeResultIndex]
                );

                return;
            }

            if (event.key === "Escape") {
                event.preventDefault();
                hideResults();
            }
        }
    );

    codeInput.addEventListener(
        "input",
        () => {
            searchInput.value = "";
            searchInput.dataset.selectedName = "";
            hideResults();
            synchronizeSelectedActivity();
        }
    );

    clearButton.addEventListener(
        "click",
        () => {
            searchInput.value = "";
            searchInput.dataset.selectedName = "";
            codeInput.value = "";
            hideSelectedActivity();
            hideResults();

            statusText.textContent = (
                "Escribe al menos 2 caracteres y "
                + "selecciona una actividad."
            );

            searchInput.focus();
        }
    );

    document.addEventListener(
        "click",
        (event) => {
            if (
                !resultsBox.contains(event.target)
                && event.target !== searchInput
            ) {
                hideResults();
            }
        }
    );

    loadCatalog().catch(() => {});
})();
