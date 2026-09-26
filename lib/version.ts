import pkg from "@/package.json";

/** The released version (package.json), shown in the footer and reported by /api/health. */
export const version: string = pkg.version;
