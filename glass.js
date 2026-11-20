const artefactImages = new Map([
    ["imagination", 3],
    ["intuition", 2],
    ["sense of humor", 8],
    ["abstract existential reflection", 9],
    ["moral reasoning", 1],
    ["wisdom", 4],
    ["free will", 5],
    ["self-awareness", 6],
    ["hope", 13],
    ["despair", 14],
    ["nostalgia", 19],
    ["pride", 15],
    ["shame", 16],
    ["jealousy", 17],
    ["awe", 18],
    ["grief", 20],
    ["spiritual experience", 7],
    ["embodied learning", 10],
    ["love", 11],
    ["compassion", 12],
]);

function artefactKey(url) {
    return url.searchParams.get('artefact')?.toLowerCase();
}

function setArtwork(element, name) {
    const image = artefactImages.get(name);
    if (image) element.style.setProperty('--artefact-image', "url('./images/" + image + ".jpg')");
}

const currentURL = new URL(location.href);
const galleryArtwork = new Map();
for (const link of document.querySelectorAll('.artefact-link')) {
    const name = artefactKey(new URL(link.href));
    const artwork = link.querySelector('.block-image');
    setArtwork(artwork, name);
    galleryArtwork.set(name, artwork);
}

const detailHeader = document.querySelector('.detail-header');
if (detailHeader) setArtwork(detailHeader, artefactKey(currentURL));

function connectArtwork(event, otherEntry) {
    if (!event.viewTransition || !otherEntry?.url) return;
    const otherURL = new URL(otherEntry.url);
    const name = artefactKey(detailHeader ? currentURL : otherURL);
    const destination = detailHeader ? currentURL : otherURL;
    const homepage = detailHeader ? otherURL : currentURL;
    if (destination.pathname !== new URL('artefact.html', homepage).pathname ||
        homepage.pathname !== new URL('index.html', destination).pathname &&
        homepage.pathname !== new URL('.', destination).pathname) return;
    const artwork = detailHeader ?? galleryArtwork.get(name);
    if (!artwork || !artefactImages.has(name)) return;
    artwork.style.viewTransitionName = 'artefact-visual';
    const clearName = () => artwork.style.removeProperty('view-transition-name');
    event.viewTransition.finished.then(clearName, clearName);
}

window.addEventListener('pageswap', event => connectArtwork(event, event.activation?.entry));
window.addEventListener('pagereveal', event => connectArtwork(event, window.navigation?.activation?.from));
