// A Google Drive "share" link (the one the "Share" button gives you --
// https://drive.google.com/file/d/FILE_ID/view?usp=sharing) points to
// an HTML viewer page, not the image itself. Using it directly as an
// <img src="..."> silently fails (no error, just a broken image),
// which is exactly what was reported. This converts the common share-
// link shapes to Drive's direct-content URL
// (https://drive.google.com/uc?export=view&id=FILE_ID) so a pasted
// share link actually renders. The file still has to be shared as
// "Anyone with the link can view" -- this can't fix a permissions
// problem, only a URL-shape one. Not Google-supported/guaranteed long
// -term; a real image host is more reliable for anyone who hits
// trouble with this.
export function toDirectImageUrl(url: string): string {
  if (!url) return url;
  const trimmed = url.trim();

  const fileMatch = trimmed.match(/drive\.google\.com\/file\/d\/([^/]+)/);
  if (fileMatch) {
    return `https://drive.google.com/uc?export=view&id=${fileMatch[1]}`;
  }

  const openMatch = trimmed.match(/drive\.google\.com\/open\?id=([^&]+)/);
  if (openMatch) {
    return `https://drive.google.com/uc?export=view&id=${openMatch[1]}`;
  }

  return trimmed;
}
