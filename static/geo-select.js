(() => {
    "use strict";

    const entitySelect = document.getElementById(
        "entity"
    );

    const municipalitySelect = document.getElementById(
        "municipality"
    );

    const statusText = document.getElementById(
        "geo_status"
    );

    if (
        !entitySelect
        || !municipalitySelect
        || !statusText
    ) {
        return;
    }

    const catalogUrl = entitySelect.dataset.catalogUrl;

    if (!catalogUrl) {
        return;
    }

    let catalog = null;

    const getAllMunicipalitiesLabel = (
        entityCode
    ) => (
        entityCode === "09"
            ? "Todas las alcaldías"
            : "Todos los municipios"
    );

    const createOption = (
        value,
        label,
    ) => {
        const option = document.createElement(
            "option"
        );

        option.value = value;
        option.textContent = label;

        return option;
    };

    const populateMunicipalities = (
        entityCode,
        selectedMunicipality = "0",
    ) => {
        const entity = catalog.entities.find(
            (item) => item.code === entityCode
        );

        municipalitySelect.replaceChildren(
            createOption(
                "0",
                getAllMunicipalitiesLabel(
                    entityCode
                ),
            )
        );

        if (!entity) {
            municipalitySelect.value = "0";

            statusText.textContent = (
                "No se encontraron municipios para "
                + "la entidad seleccionada."
            );

            return;
        }

        entity.municipalities.forEach(
            (municipality) => {
                municipalitySelect.append(
                    createOption(
                        municipality.code,
                        municipality.name,
                    )
                );
            }
        );

        const municipalityExists = Array.from(
            municipalitySelect.options
        ).some(
            (option) => (
                option.value === selectedMunicipality
            )
        );

        municipalitySelect.value = (
            municipalityExists
                ? selectedMunicipality
                : "0"
        );

        const unitLabel = (
            entityCode === "09"
                ? "alcaldías"
                : "municipios"
        );

        statusText.textContent = (
            `${entity.municipalities.length} `
            + `${unitLabel} disponibles.`
        );
    };

    const loadCatalog = async () => {
        if (catalog) {
            return catalog;
        }

        statusText.textContent = (
            "Cargando catálogo territorial..."
        );

        const response = await fetch(
            catalogUrl,
            {
                cache: "force-cache",
                headers: {
                    "Accept": "application/json",
                },
            }
        );

        if (!response.ok) {
            throw new Error(
                `HTTP ${response.status}`
            );
        }

        const data = await response.json();

        if (!Array.isArray(data.entities)) {
            throw new Error(
                "El catálogo territorial no tiene "
                + "el formato esperado."
            );
        }

        catalog = data;

        return catalog;
    };

    const initialize = async () => {
        const selectedMunicipality = (
            municipalitySelect.dataset
                .selectedMunicipality
            || municipalitySelect.value
            || "0"
        );

        try {
            await loadCatalog();

            populateMunicipalities(
                entitySelect.value,
                selectedMunicipality,
            );
        } catch (error) {
            statusText.textContent = (
                "No fue posible cargar el catálogo "
                + "territorial. Conservamos las opciones "
                + "disponibles en la página."
            );

            console.error(
                "Error al cargar el catálogo "
                + "territorial:",
                error
            );
        }
    };

    entitySelect.addEventListener(
        "change",
        async () => {
            try {
                await loadCatalog();

                populateMunicipalities(
                    entitySelect.value,
                    "0",
                );
            } catch {
                return;
            }
        }
    );

    initialize();
})();
