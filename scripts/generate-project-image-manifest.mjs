import { readdir, writeFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const projectRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const imageRoot = resolve(projectRoot, 'assets');
const projectFolders = ['airgrid', 'hackjudge', 'healthchain', 'self-driving-car', 'campusxchange', 'achievements'];
const imageExtensions = new Set(['.avif', '.bmp', '.gif', '.jpeg', '.jpg', '.png', '.svg', '.webp']);

const manifest = {};

for (const folder of projectFolders) {
    let files = [];
    try {
        files = await readdir(resolve(imageRoot, folder), { withFileTypes: true });
    } catch (error) {
        if (error.code !== 'ENOENT') throw error;
    }

    const webpStems = new Set(files
        .filter(file => file.isFile() && file.name.toLowerCase().endsWith('.webp'))
        .map(file => file.name.slice(0, -5).toLowerCase()));

    manifest[folder] = files
        .filter(file => {
            if (!file.isFile()) return false;
            const extension = file.name.slice(file.name.lastIndexOf('.')).toLowerCase();
            if (!imageExtensions.has(extension)) return false;
            const stem = file.name.slice(0, file.name.lastIndexOf('.')).toLowerCase();
            return extension === '.webp' || extension === '.svg' || !webpStems.has(stem);
        })
        .map(file => file.name)
        .sort((left, right) => left.localeCompare(right, undefined, { numeric: true, sensitivity: 'base' }));
}

await writeFile(resolve(imageRoot, 'project-images.json'), `${JSON.stringify(manifest, null, 2)}\n`);
console.log(`Generated project image manifest for ${Object.values(manifest).reduce((sum, files) => sum + files.length, 0)} images.`);
