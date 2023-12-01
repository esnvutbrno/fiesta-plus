import Alpine from "alpinejs";

Alpine.data('mapWidget', (locationData, initialZoomLevel = 30) => ({
    location: locationData,
    zoomLevel: initialZoomLevel,
    mapUrl: '',

    init() {
        this.mapUrl = this.generateMapUrl(this.location.latitude, this.location.longitude, this.zoomLevel);
    },

    generateMapUrl(latitude, longitude, zoomLevel) {
        // Adjust the bounding box based on the zoom level
        const delta = 0.05 / zoomLevel;
        const bbox = [
            longitude - delta,  // left
            latitude - delta,   // bottom
            longitude + delta,  // right
            latitude + delta    // top
        ];
        return `https://www.openstreetmap.org/export/embed.html?bbox=${bbox.join(',')}&layer=mapnik&marker=${latitude},${longitude}`;
    },
}));